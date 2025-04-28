"""
Módulo para generar dashboards comerciales con visualizaciones simples para el equipo de ventas.
Incluye seguimiento de progreso, comparaciones con estimaciones y observaciones del estado actual.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import powerbi_tools  # Módulo hipotético para integración con Power BI

def estimar_rango_leads(datos_historicos, periodo_actual, margen_error=0.20):
    """
    Estima un rango total de leads esperados para toda la convocatoria.
    
    Args:
        datos_historicos (pandas.DataFrame): DataFrame con datos históricos.
        periodo_actual (str): Identificador del periodo actual (ej: "2023Q2").
        margen_error (float): Margen de error para el rango (0.20 = ±20%).
        
    Returns:
        dict: Diccionario con estimación base, límite inferior y superior.
    """
    # Verificar que hay datos históricos suficientes
    if datos_historicos is None or len(datos_historicos) == 0:
        raise ValueError("No se proporcionaron datos históricos suficientes")
    
    # Agrupar por periodo para obtener total de leads por convocatoria
    if 'Periodo' in datos_historicos.columns and 'Leads' in datos_historicos.columns:
        leads_por_periodo = datos_historicos.groupby('Periodo')['Leads'].sum()
    else:
        # Intentar agrupar por periodo si las columnas tienen otro nombre
        cols = datos_historicos.columns
        col_periodo = [c for c in cols if 'periodo' in c.lower() or 'convocatoria' in c.lower()]
        col_leads = [c for c in cols if 'lead' in c.lower()]
        
        if not col_periodo or not col_leads:
            raise ValueError("No se encontraron columnas para periodo o leads en los datos")
            
        leads_por_periodo = datos_historicos.groupby(col_periodo[0])[col_leads[0]].sum()
    
    # Calcular promedio de leads de periodos anteriores
    estimacion_base = leads_por_periodo.mean()
    
    # Calcular límites del rango
    limite_inferior = estimacion_base * (1 - margen_error)
    limite_superior = estimacion_base * (1 + margen_error)
    
    return {
        'estimacion_base': estimacion_base,
        'limite_inferior': limite_inferior,
        'limite_superior': limite_superior,
        'margen_error': margen_error,
        'periodos_analizados': len(leads_por_periodo)
    }


def calcular_avance_actual(datos_actuales, fecha_inicio, fecha_fin, fecha_corte=None):
    """
    Calcula el avance actual de leads y matrículas en la convocatoria.
    
    Args:
        datos_actuales (pandas.DataFrame): DataFrame con datos de la convocatoria actual.
        fecha_inicio (str): Fecha de inicio de la convocatoria (formato 'YYYY-MM-DD').
        fecha_fin (str): Fecha de fin de la convocatoria (formato 'YYYY-MM-DD').
        fecha_corte (str, optional): Fecha de corte para el análisis (por defecto, fecha actual).
        
    Returns:
        dict: Diccionario con métricas de avance (leads, matrículas, tiempo).
    """
    # Convertir fechas a datetime
    fecha_inicio = pd.to_datetime(fecha_inicio)
    fecha_fin = pd.to_datetime(fecha_fin)
    
    if fecha_corte is None:
        fecha_corte = datetime.now()
    else:
        fecha_corte = pd.to_datetime(fecha_corte)
    
    # Limitar fecha de corte a fecha fin si la sobrepasa
    if fecha_corte > fecha_fin:
        fecha_corte = fecha_fin
    
    # Calcular duración total y transcurrida
    duracion_total = (fecha_fin - fecha_inicio).days
    tiempo_transcurrido = (fecha_corte - fecha_inicio).days
    
    # Verificar que tiempo transcurrido no sea negativo
    tiempo_transcurrido = max(0, tiempo_transcurrido)
    
    # Calcular porcentaje de tiempo transcurrido
    porcentaje_tiempo = (tiempo_transcurrido / duracion_total) * 100 if duracion_total > 0 else 0
    
    # Preparar datos actuales
    if 'Fecha' not in datos_actuales.columns:
        # Buscar columna de fecha con otro nombre
        cols = datos_actuales.columns
        col_fecha = [c for c in cols if 'fecha' in c.lower() or 'date' in c.lower()]
        
        if not col_fecha:
            raise ValueError("No se encontró columna de fecha en los datos")
        
        # Renombrar columna de fecha para procesamiento
        datos_procesados = datos_actuales.copy()
        datos_procesados['Fecha'] = pd.to_datetime(datos_procesados[col_fecha[0]])
    else:
        datos_procesados = datos_actuales.copy()
        datos_procesados['Fecha'] = pd.to_datetime(datos_procesados['Fecha'])
    
    # Filtrar datos hasta la fecha de corte
    datos_filtrados = datos_procesados[datos_procesados['Fecha'] <= fecha_corte]
    
    # Contar leads y matrículas acumulados
    if 'Tipo' in datos_filtrados.columns:
        leads_acumulados = datos_filtrados[datos_filtrados['Tipo'] == 'Lead'].shape[0]
        matriculas_acumuladas = datos_filtrados[datos_filtrados['Tipo'] == 'Matrícula'].shape[0]
    else:
        # Intentar identificar leads y matrículas por otras columnas
        cols = datos_filtrados.columns
        col_tipo = [c for c in cols if 'tipo' in c.lower() or 'type' in c.lower()]
        
        if col_tipo:
            tipo_col = col_tipo[0]
            leads_acumulados = datos_filtrados[datos_filtrados[tipo_col].str.lower().str.contains('lead')].shape[0]
            matriculas_acumuladas = datos_filtrados[datos_filtrados[tipo_col].str.lower().str.contains('matrícula')].shape[0]
        else:
            # Si no hay columna de tipo, buscar columnas separadas
            col_leads = [c for c in cols if 'lead' in c.lower()]
            col_matriculas = [c for c in cols if 'matrícula' in c.lower() or 'enrollment' in c.lower()]
            
            if col_leads and col_matriculas:
                leads_acumulados = datos_filtrados[col_leads[0]].sum()
                matriculas_acumuladas = datos_filtrados[col_matriculas[0]].sum()
            else:
                # Si no se puede determinar, asumir que todos son leads
                leads_acumulados = len(datos_filtrados)
                matriculas_acumuladas = 0
    
    # Calcular tasa de conversión
    tasa_conversion = (matriculas_acumuladas / leads_acumulados * 100) if leads_acumulados > 0 else 0
    
    # Obtener datos agrupados por quincena para análisis de tendencia
    datos_filtrados['Quincena'] = datos_filtrados['Fecha'].dt.to_period('Q')
    leads_por_quincena = datos_filtrados[datos_filtrados['Tipo'] == 'Lead'].groupby('Quincena').size()
    matriculas_por_quincena = datos_filtrados[datos_filtrados['Tipo'] == 'Matrícula'].groupby('Quincena').size()
    
    return {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'fecha_corte': fecha_corte,
        'duracion_total_dias': duracion_total,
        'tiempo_transcurrido_dias': tiempo_transcurrido,
        'porcentaje_tiempo': porcentaje_tiempo,
        'leads_acumulados': leads_acumulados,
        'matriculas_acumuladas': matriculas_acumuladas,
        'tasa_conversion': tasa_conversion,
        'leads_por_quincena': leads_por_quincena,
        'matriculas_por_quincena': matriculas_por_quincena
    }


def calcular_porcentaje_avance(avance_actual, estimacion_leads):
    """
    Calcula el porcentaje de avance contra la estimación de leads.
    
    Args:
        avance_actual (dict): Resultado de calcular_avance_actual().
        estimacion_leads (dict): Resultado de estimar_rango_leads().
        
    Returns:
        dict: Diccionario con porcentajes de avance vs. estimaciones.
    """
    leads_acumulados = avance_actual['leads_acumulados']
    
    # Calcular porcentajes de avance contra estimaciones
    porcentaje_vs_base = (leads_acumulados / estimacion_leads['estimacion_base']) * 100 if estimacion_leads['estimacion_base'] > 0 else 0
    porcentaje_vs_inferior = (leads_acumulados / estimacion_leads['limite_inferior']) * 100 if estimacion_leads['limite_inferior'] > 0 else 0
    porcentaje_vs_superior = (leads_acumulados / estimacion_leads['limite_superior']) * 100 if estimacion_leads['limite_superior'] > 0 else 0
    
    # Calcular relación entre avance de tiempo y avance de leads
    eficiencia_tiempo_leads = porcentaje_vs_base / avance_actual['porcentaje_tiempo'] if avance_actual['porcentaje_tiempo'] > 0 else 0
    
    # Determinar si el avance está dentro, por encima o por debajo del rango
    if leads_acumulados < estimacion_leads['limite_inferior'] * (avance_actual['porcentaje_tiempo'] / 100):
        estado = "POR DEBAJO"
    elif leads_acumulados > estimacion_leads['limite_superior'] * (avance_actual['porcentaje_tiempo'] / 100):
        estado = "POR ENCIMA"
    else:
        estado = "DENTRO DEL RANGO"
    
    return {
        'porcentaje_vs_base': porcentaje_vs_base,
        'porcentaje_vs_inferior': porcentaje_vs_inferior,
        'porcentaje_vs_superior': porcentaje_vs_superior,
        'eficiencia_tiempo_leads': eficiencia_tiempo_leads,
        'estado': estado
    }


def generar_observacion_avance(avance_actual, porcentaje_avance, estimacion_leads):
    """
    Genera una observación textual sobre el estado actual del avance.
    
    Args:
        avance_actual (dict): Resultado de calcular_avance_actual().
        porcentaje_avance (dict): Resultado de calcular_porcentaje_avance().
        estimacion_leads (dict): Resultado de estimar_rango_leads().
        
    Returns:
        str: Texto con observaciones sobre el avance actual.
    """
    leads_acumulados = avance_actual['leads_acumulados']
    matriculas_acumuladas = avance_actual['matriculas_acumuladas']
    porcentaje_tiempo = avance_actual['porcentaje_tiempo']
    tasa_conversion = avance_actual['tasa_conversion']
    
    # Formatear datos para el texto
    tiempo_format = f"{porcentaje_tiempo:.1f}%"
    leads_format = f"{leads_acumulados:,}".replace(',', '.')
    matriculas_format = f"{matriculas_acumuladas:,}".replace(',', '.')
    tasa_format = f"{tasa_conversion:.1f}%"
    
    # Estimar leads faltantes según tiempo
    tiempo_restante_porc = 100 - porcentaje_tiempo
    leads_esperados_total = estimacion_leads['estimacion_base']
    leads_esperados_restantes = leads_esperados_total * (tiempo_restante_porc / 100)
    leads_diarios_necesarios = leads_esperados_restantes / max(1, (avance_actual['duracion_total_dias'] - avance_actual['tiempo_transcurrido_dias']))
    
    # Formatear estimaciones
    leads_esperados_format = f"{leads_esperados_total:,.0f}".replace(',', '.')
    leads_restantes_format = f"{leads_esperados_restantes:,.0f}".replace(',', '.')
    leads_diarios_format = f"{leads_diarios_necesarios:,.1f}".replace(',', '.')
    
    # Generar texto base con datos actuales
    observacion = f"ESTADO DE AVANCE AL {avance_actual['fecha_corte'].strftime('%d/%m/%Y')}\n\n"
    observacion += f"• Tiempo transcurrido: {tiempo_format} ({avance_actual['tiempo_transcurrido_dias']} de {avance_actual['duracion_total_dias']} días)\n"
    observacion += f"• Leads acumulados: {leads_format}\n"
    observacion += f"• Matrículas acumuladas: {matriculas_format}\n"
    observacion += f"• Tasa de conversión: {tasa_format}\n\n"
    
    # Añadir interpretación según el estado
    if porcentaje_avance['estado'] == "POR DEBAJO":
        observacion += f"ALERTA: El avance de leads está POR DEBAJO del rango esperado.\n"
        observacion += f"• Avance respecto a estimación base: {porcentaje_avance['porcentaje_vs_base']:.1f}%\n"
        observacion += f"• Para alcanzar la meta estimada ({leads_esperados_format} leads), se necesitan:\n"
        observacion += f"  - {leads_restantes_format} leads adicionales\n"
        observacion += f"  - Un promedio de {leads_diarios_format} leads diarios hasta el final\n"
        
        # Recomendaciones
        observacion += "\nRECOMENDACIONES:\n"
        observacion += "• Intensificar la inversión en canales que están generando mejor ROI\n"
        observacion += "• Revisar el presupuesto de marketing para posible reasignación\n"
        observacion += "• Implementar promociones especiales para estimular conversiones\n"
        
    elif porcentaje_avance['estado'] == "POR ENCIMA":
        observacion += f"EXCELENTE: El avance de leads está POR ENCIMA del rango esperado.\n"
        observacion += f"• Avance respecto a estimación base: {porcentaje_avance['porcentaje_vs_base']:.1f}%\n"
        observacion += f"• Si la tendencia continúa, se podrían superar los {leads_esperados_format} leads estimados.\n"
        
        # Recomendaciones
        observacion += "\nRECOMENDACIONES:\n"
        observacion += "• Mantener la estrategia actual de marketing\n"
        observacion += "• Considerar ajustar recursos para mejorar la tasa de conversión\n"
        observacion += "• Preparar al equipo comercial para el volumen incrementado de leads\n"
        
    else:  # DENTRO DEL RANGO
        observacion += f"NORMAL: El avance de leads está DENTRO DEL RANGO esperado.\n"
        observacion += f"• Avance respecto a estimación base: {porcentaje_avance['porcentaje_vs_base']:.1f}%\n"
        observacion += f"• Para alcanzar la meta estimada ({leads_esperados_format} leads), se necesitan:\n"
        observacion += f"  - {leads_restantes_format} leads adicionales\n"
        observacion += f"  - Un promedio de {leads_diarios_format} leads diarios hasta el final\n"
        
        # Recomendaciones
        observacion += "\nRECOMENDACIONES:\n"
        observacion += "• Continuar con la estrategia actual\n"
        observacion += "• Monitorear semanalmente el avance para detectar cambios de tendencia\n"
        observacion += "• Optimizar canales que presenten mejor desempeño\n"
    
    # Añadir información sobre la tasa de conversión
    if tasa_conversion < 5:
        observacion += "\nALERTA DE CONVERSIÓN: La tasa de conversión está por debajo del 5%.\n"
        observacion += "• Reforzar seguimiento comercial\n"
        observacion += "• Verificar calidad de leads\n"
    elif tasa_conversion > 15:
        observacion += "\nEXCELENTE CONVERSIÓN: La tasa de conversión supera el 15%.\n"
        observacion += "• Analizar factores de éxito para replicar\n"
    
    return observacion


def generar_visualizacion_barras_progreso(avance_actual, porcentaje_avance, estimacion_leads, ruta_salida=None):
    """
    Genera una visualización de barras de progreso horizontal para tiempo, leads y matrículas.
    
    Args:
        avance_actual (dict): Resultado de calcular_avance_actual().
        porcentaje_avance (dict): Resultado de calcular_porcentaje_avance().
        estimacion_leads (dict): Resultado de estimar_rango_leads().
        ruta_salida (str, optional): Ruta donde guardar la figura generada.
        
    Returns:
        matplotlib.figure.Figure: Figura generada con las barras de progreso.
    """
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Datos para las barras
    categorias = ['Tiempo', 'Leads', 'Matrículas']
    porcentajes = [
        avance_actual['porcentaje_tiempo'],
        porcentaje_avance['porcentaje_vs_base'],
        # Para matrículas, calcular contra la estimación ajustada por la tasa de conversión
        (avance_actual['matriculas_acumuladas'] / (estimacion_leads['estimacion_base'] * (avance_actual['tasa_conversion']/100))) * 100 
        if avance_actual['tasa_conversion'] > 0 else 0
    ]
    
    # Limitar porcentajes a 100% para visualización
    porcentajes_vis = [min(p, 100) for p in porcentajes]
    
    # Colores según estado
    colores = []
    for i, p in enumerate(porcentajes):
        if i == 0:  # Tiempo siempre en azul
            colores.append('#3498db')
        elif p < 85:  # Por debajo
            colores.append('#e74c3c')
        elif p > 115:  # Por encima
            colores.append('#2ecc71')
        else:  # Normal
            colores.append('#f39c12')
    
    # Crear barras horizontales
    y_pos = np.arange(len(categorias))
    barras = ax.barh(y_pos, porcentajes_vis, height=0.5, color=colores)
    
    # Añadir etiquetas con porcentajes exactos
    for i, (bar, porcentaje) in enumerate(zip(barras, porcentajes)):
        if porcentaje > 0:
            # Posición de la etiqueta (dentro o fuera según el tamaño de la barra)
            if porcentaje > 10:
                label_pos = bar.get_width() - 5
                ha = 'right'
                color = 'white'
            else:
                label_pos = bar.get_width() + 1
                ha = 'left'
                color = 'black'
            
            # Añadir valor real incluso si está por encima del 100%
            ax.text(label_pos, bar.get_y() + bar.get_height()/2, f'{porcentaje:.1f}%', 
                    va='center', ha=ha, color=color, fontweight='bold')
    
    # Añadir línea vertical en 100%
    ax.axvline(x=100, color='gray', linestyle='--', alpha=0.7)
    
    # Añadir etiquetas de cantidades reales
    valores_reales = [
        f"{avance_actual['tiempo_transcurrido_dias']} de {avance_actual['duracion_total_dias']} días",
        f"{avance_actual['leads_acumulados']} de {int(estimacion_leads['estimacion_base'])} leads",
        f"{avance_actual['matriculas_acumuladas']} matrículas"
    ]
    
    for i, (cat, val) in enumerate(zip(categorias, valores_reales)):
        ax.text(-5, i, f"{cat}: {val}", va='center', ha='right', fontweight='bold')
    
    # Configurar ejes
    ax.set_yticks([])  # Ocultar etiquetas del eje Y
    ax.set_xlim(0, 120)  # Límite hasta 120% para visualizar excesos
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
    
    # Añadir título y ajustar diseño
    ax.set_title('Avance de Campaña', fontsize=14, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Añadir fecha de actualización
    plt.figtext(0.02, 0.02, f"Actualizado al: {avance_actual['fecha_corte'].strftime('%d/%m/%Y')}", 
                ha='left', fontsize=8, style='italic')
    
    plt.tight_layout()
    
    # Guardar figura si se proporciona ruta
    if ruta_salida:
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        plt.savefig(ruta_salida, dpi=300, bbox_inches='tight')
    
    return fig


def generar_grafico_avance_vs_estimado(datos_actuales, avance_actual, estimacion_leads, ruta_salida=None):
    """
    Genera un gráfico comparativo del avance actual vs. el rango estimado.
    
    Args:
        datos_actuales (pandas.DataFrame): DataFrame con datos de la convocatoria actual.
        avance_actual (dict): Resultado de calcular_avance_actual().
        estimacion_leads (dict): Resultado de estimar_rango_leads().
        ruta_salida (str, optional): Ruta donde guardar la figura generada.
        
    Returns:
        matplotlib.figure.Figure: Figura generada con la comparación.
    """
    # Preparar datos para el gráfico
    fecha_inicio = avance_actual['fecha_inicio']
    fecha_fin = avance_actual['fecha_fin']
    fecha_corte = avance_actual['fecha_corte']
    
    # Generar fechas para el eje X
    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
    
    # Calcular rangos esperados para cada fecha
    dias_totales = (fecha_fin - fecha_inicio).days
    porc_tiempo = [(fecha - fecha_inicio).days / dias_totales for fecha in fechas]
    
    # Estimaciones diarias (asumiendo crecimiento lineal)
    estimado_base = [estimacion_leads['estimacion_base'] * p for p in porc_tiempo]
    estimado_inferior = [estimacion_leads['limite_inferior'] * p for p in porc_tiempo]
    estimado_superior = [estimacion_leads['limite_superior'] * p for p in porc_tiempo]
    
    # Preparar datos reales acumulados
    if 'Fecha' not in datos_actuales.columns:
        # Buscar columna de fecha con otro nombre
        cols = datos_actuales.columns
        col_fecha = [c for c in cols if 'fecha' in c.lower() or 'date' in c.lower()]
        
        if not col_fecha:
            raise ValueError("No se encontró columna de fecha en los datos")
        
        # Renombrar columna para procesamiento
        datos_procesados = datos_actuales.copy()
        datos_procesados['Fecha'] = pd.to_datetime(datos_procesados[col_fecha[0]])
    else:
        datos_procesados = datos_actuales.copy()
        datos_procesados['Fecha'] = pd.to_datetime(datos_procesados['Fecha'])
    
    # Filtrar datos hasta la fecha de corte
    datos_filtrados = datos_procesados[datos_procesados['Fecha'] <= fecha_corte]
    
    # Agrupar por fecha y calcular acumulados
    if 'Tipo' in datos_filtrados.columns:
        leads_diarios = datos_filtrados[datos_filtrados['Tipo'] == 'Lead'].groupby(datos_filtrados['Fecha'].dt.date).size()
    else:
        # Intentar identificar leads por otras columnas
        cols = datos_filtrados.columns
        col_tipo = [c for c in cols if 'tipo' in c.lower() or 'type' in c.lower()]
        
        if col_tipo:
            tipo_col = col_tipo[0]
            leads_diarios = datos_filtrados[datos_filtrados[tipo_col].str.lower().str.contains('lead')].groupby(datos_filtrados['Fecha'].dt.date).size()
        else:
            # Si no hay columna de tipo, buscar columnas de leads
            col_leads = [c for c in cols if 'lead' in c.lower()]
            
            if col_leads:
                leads_diarios = datos_filtrados.groupby(datos_filtrados['Fecha'].dt.date)[col_leads[0]].sum()
            else:
                # Si no se puede determinar, contar todas las filas
                leads_diarios = datos_filtrados.groupby(datos_filtrados['Fecha'].dt.date).size()
    
    # Convertir índice a datetime para alineación con fechas estimadas
    leads_diarios.index = pd.to_datetime(leads_diarios.index)
    
    # Calcular acumulado
    leads_acumulados = leads_diarios.cumsum()
    
    # Preparar datos faltantes (extender últimos datos conocidos hasta fecha corte)
    fechas_conocidas = set(leads_acumulados.index)
    fechas_completas = pd.date_range(start=fecha_inicio, end=fecha_corte)
    
    leads_acumulados_completo = pd.Series(index=fechas_completas)
    ultimo_valor = 0
    
    for fecha in fechas_completas:
        if fecha in fechas_conocidas:
            ultimo_valor = leads_acumulados.loc[fecha]
        leads_acumulados_completo.loc[fecha] = ultimo_valor
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Área sombreada para el rango estimado
    ax.fill_between(fechas, estimado_inferior, estimado_superior, color='lightgray', alpha=0.5, label='Rango Estimado (±20%)')
    
    # Línea de estimación base
    ax.plot(fechas, estimado_base, '--', color='gray', linewidth=1.5, label='Estimación Base')
    
    # Línea de leads acumulados reales
    ax.plot(leads_acumulados_completo.index, leads_acumulados_completo.values, '-', color='blue', linewidth=2.5, label='Leads Acumulados')
    
    # Línea vertical para fecha de corte
    ax.axvline(x=fecha_corte, color='red', linestyle='--', linewidth=1, label='Fecha de Corte')
    
    # Añadir anotación sobre el último valor
    ultimo_leads = leads_acumulados_completo.iloc[-1]
    ax.annotate(f'{int(ultimo_leads)} leads', 
                xy=(fecha_corte, ultimo_leads),
                xytext=(10, 0), textcoords='offset points',
                va='center', fontweight='bold', color='blue')
    
    # Configurar ejes
    ax.set_xlim(fecha_inicio, fecha_fin)
    ax.set_ylim(0, estimado_superior[-1] * 1.1)  # Límite superior con margen
    
    # Formatear eje X con fechas
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    fig.autofmt_xdate()
    
    # Formatear eje Y con separador de miles
    def format_miles(x, pos):
        return f'{int(x):,}'.replace(',', '.')
    
    ax.yaxis.set_major_formatter(FuncFormatter(format_miles))
    
    # Añadir cuadrícula
    ax.grid(True, alpha=0.3)
    
    # Añadir leyenda, título y etiquetas
    ax.legend(loc='upper left')
    ax.set_title('Comparación de Leads Acumulados vs. Estimación', fontsize=14, fontweight='bold')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Leads Acumulados')
    
    # Añadir fecha de actualización
    plt.figtext(0.02, 0.02, f"Actualizado al: {avance_actual['fecha_corte'].strftime('%d/%m/%Y')}", 
                ha='left', fontsize=8, style='italic')
    
    plt.tight_layout()
    
    # Guardar figura si se proporciona ruta
    if ruta_salida:
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        plt.savefig(ruta_salida, dpi=300, bbox_inches='tight')
    
    return fig


def generar_dashboard_comercial(datos_historicos, datos_actuales, fecha_inicio, fecha_fin, 
                               fecha_corte=None, periodo_actual=None, directorio_salida=None):
    """
    Genera un dashboard completo para el equipo comercial.
    
    Args:
        datos_historicos (pandas.DataFrame): DataFrame con datos históricos.
        datos_actuales (pandas.DataFrame): DataFrame con datos de la convocatoria actual.
        fecha_inicio (str): Fecha de inicio de la convocatoria (formato 'YYYY-MM-DD').
        fecha_fin (str): Fecha de fin de la convocatoria (formato 'YYYY-MM-DD').
        fecha_corte (str, optional): Fecha de corte para el análisis.
        periodo_actual (str, optional): Identificador del periodo actual.
        directorio_salida (str, optional): Directorio donde guardar los archivos generados.
        
    Returns:
        dict: Diccionario con resultados y rutas de archivos generados.
    """
    # Configurar directorio de salida
    if directorio_salida is None:
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        directorio_salida = f'../salidas/dashboard_comercial/{fecha_actual}'
    
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Establecer periodo actual si no se proporciona
    if periodo_actual is None:
        # Intentar determinar el periodo a partir de las fechas
        fecha_inicio_dt = pd.to_datetime(fecha_inicio)
        ano = fecha_inicio_dt.year
        
        # Determinar trimestre o semestre
        if fecha_inicio_dt.month <= 3:
            periodo_actual = f"{ano}Q1"
        elif fecha_inicio_dt.month <= 6:
            periodo_actual = f"{ano}Q2"
        elif fecha_inicio_dt.month <= 9:
            periodo_actual = f"{ano}Q3"
        else:
            periodo_actual = f"{ano}Q4"
    
    # Calcular estimación de leads
    estimacion_leads = estimar_rango_leads(datos_historicos, periodo_actual)
    
    # Calcular avance actual
    avance_actual = calcular_avance_actual(datos_actuales, fecha_inicio, fecha_fin, fecha_corte)
    
    # Calcular porcentaje de avance
    porcentaje_avance = calcular_porcentaje_avance(avance_actual, estimacion_leads)
    
    # Generar observación
    observacion = generar_observacion_avance(avance_actual, porcentaje_avance, estimacion_leads)
    
    # Guardar observación en archivo de texto
    ruta_observacion = os.path.join(directorio_salida, 'observaciones.txt')
    with open(ruta_observacion, 'w', encoding='utf-8') as f:
        f.write(observacion)
    
    # Generar visualizaciones
    ruta_barras = os.path.join(directorio_salida, 'barras_progreso.png')
    fig_barras = generar_visualizacion_barras_progreso(
        avance_actual, porcentaje_avance, estimacion_leads, ruta_barras
    )
    
    ruta_comparacion = os.path.join(directorio_salida, 'comparacion_avance.png')
    fig_comparacion = generar_grafico_avance_vs_estimado(
        datos_actuales, avance_actual, estimacion_leads, ruta_comparacion
    )
    
    # Cerrar figuras para liberar memoria
    plt.close(fig_barras)
    plt.close(fig_comparacion)
    
    # Generar dashboard en formatos adicionales
    try:
        # Generar versión HTML
        ruta_html = os.path.join(directorio_salida, 'dashboard_comercial.html')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard Comercial - {periodo_actual}</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                h1, h2, h3 {{ color: #333; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; margin-bottom: 20px; }}
                .section {{ background-color: white; margin-bottom: 30px; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
                .image-container {{ margin: 15px 0; text-align: center; }}
                img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
                .obs-text {{ white-space: pre-line; font-family: monospace; font-size: 14px; line-height: 1.5; }}
                .alert {{ background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; }}
                .success {{ background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; }}
                .normal {{ background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Dashboard Comercial</h1>
                    <p>Periodo: {periodo_actual} - Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                </div>
                
                <div class="section">
                    <h2>Avance de Campaña</h2>
                    <div class="image-container">
                        <img src="barras_progreso.png" alt="Barras de Progreso">
                    </div>
                    
                    <h3>Métricas Clave</h3>
                    <ul>
                        <li><strong>Leads Acumulados:</strong> {avance_actual['leads_acumulados']:,}</li>
                        <li><strong>Matrículas Acumuladas:</strong> {avance_actual['matriculas_acumuladas']:,}</li>
                        <li><strong>Tasa de Conversión:</strong> {avance_actual['tasa_conversion']:.1f}%</li>
                        <li><strong>Tiempo Transcurrido:</strong> {avance_actual['porcentaje_tiempo']:.1f}% ({avance_actual['tiempo_transcurrido_dias']} de {avance_actual['duracion_total_dias']} días)</li>
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Comparación con Estimación</h2>
                    <div class="image-container">
                        <img src="comparacion_avance.png" alt="Comparación de Avance">
                    </div>
                    
                    <h3>Estimaciones</h3>
                    <ul>
                        <li><strong>Estimación Base:</strong> {estimacion_leads['estimacion_base']:,.0f} leads</li>
                        <li><strong>Rango Estimado:</strong> {estimacion_leads['limite_inferior']:,.0f} a {estimacion_leads['limite_superior']:,.0f} leads</li>
                        <li><strong>Avance vs. Estimación Base:</strong> {porcentaje_avance['porcentaje_vs_base']:.1f}%</li>
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Observaciones y Recomendaciones</h2>
                    <div class="{
                        'alert' if porcentaje_avance['estado'] == 'POR DEBAJO' else 
                        'success' if porcentaje_avance['estado'] == 'POR ENCIMA' else 'normal'
                    }">
                        <strong>Estado:</strong> {porcentaje_avance['estado']}
                    </div>
                    <div class="obs-text">
                        {observacion}
                    </div>
                </div>
                
                <div class="footer">
                    <p>Generado por el Sistema Predictor de Matrículas</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(ruta_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Intentar generar versión para Power BI (hipotético)
        try:
            ruta_powerbi = os.path.join(directorio_salida, 'datos_powerbi.json')
            
            # Datos para Power BI
            datos_powerbi = {
                'meta_datos': {
                    'periodo': periodo_actual,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'fecha_corte': avance_actual['fecha_corte'].strftime('%Y-%m-%d'),
                    'fecha_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                'metricas': {
                    'leads_acumulados': avance_actual['leads_acumulados'],
                    'matriculas_acumuladas': avance_actual['matriculas_acumuladas'],
                    'tasa_conversion': avance_actual['tasa_conversion'],
                    'tiempo_transcurrido_porcentaje': avance_actual['porcentaje_tiempo'],
                    'tiempo_transcurrido_dias': avance_actual['tiempo_transcurrido_dias'],
                    'tiempo_total_dias': avance_actual['duracion_total_dias']
                },
                'estimaciones': {
                    'estimacion_base': estimacion_leads['estimacion_base'],
                    'limite_inferior': estimacion_leads['limite_inferior'],
                    'limite_superior': estimacion_leads['limite_superior'],
                    'porcentaje_vs_base': porcentaje_avance['porcentaje_vs_base'],
                    'porcentaje_vs_inferior': porcentaje_avance['porcentaje_vs_inferior'],
                    'porcentaje_vs_superior': porcentaje_avance['porcentaje_vs_superior'],
                    'estado': porcentaje_avance['estado']
                },
                'tendencia': {
                    'leads_por_quincena': avance_actual['leads_por_quincena'].to_dict(),
                    'matriculas_por_quincena': avance_actual['matriculas_por_quincena'].to_dict()
                }
            }
            
            import json
            with open(ruta_powerbi, 'w', encoding='utf-8') as f:
                json.dump(datos_powerbi, f, indent=4)
            
            # Hipotética integración con Power BI
            # powerbi_tools.actualizar_dataset(ruta_powerbi, "Dashboard Comercial")
            
        except Exception as e:
            print(f"Error al generar datos para Power BI: {str(e)}")
        
    except Exception as e:
        print(f"Error al generar versiones adicionales del dashboard: {str(e)}")
    
    # Devolver resultados y rutas
    return {
        'estimacion_leads': estimacion_leads,
        'avance_actual': avance_actual,
        'porcentaje_avance': porcentaje_avance,
        'observacion': observacion,
        'archivos': {
            'observaciones': ruta_observacion,
            'barras_progreso': ruta_barras,
            'comparacion_avance': ruta_comparacion,
            'dashboard_html': ruta_html if 'ruta_html' in locals() else None,
            'datos_powerbi': ruta_powerbi if 'ruta_powerbi' in locals() else None
        }
    }


if __name__ == "__main__":
    # Ejemplo de uso del módulo
    try:
        # Importar módulos necesarios
        from cargar_datos import cargar_datos_crm
        
        # Cargar datos históricos y actuales
        datos_historicos = cargar_datos_crm("../datos/historico/leads_matriculas_historicos.csv")
        datos_actuales = cargar_datos_crm("../datos/actual/leads_matriculas_actual.csv")
        
        # Definir fechas de la convocatoria actual
        fecha_inicio = "2023-10-01"
        fecha_fin = "2023-12-31"
        
        # Generar dashboard comercial
        resultado = generar_dashboard_comercial(
            datos_historicos, 
            datos_actuales, 
            fecha_inicio, 
            fecha_fin, 
            periodo_actual="2023Q4"
        )
        
        print("Dashboard comercial generado correctamente.")
        print(f"Archivos generados en: {os.path.dirname(resultado['archivos']['dashboard_html'])}")
        
    except Exception as e:
        print(f"Error: {e}") 