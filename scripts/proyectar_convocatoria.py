"""
Módulo para proyectar el cierre de matrícula basado en el ritmo actual
de leads y matrículas, incluyendo escenarios de mejora o caída en la conversión.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime, timedelta


def calcular_ritmo_actual(datos_actuales, info_convocatoria):
    """
    Calcula el ritmo actual de generación de leads y conversión a matrículas.
    
    Args:
        datos_actuales (pandas.DataFrame): DataFrame con datos actuales de leads y matrículas.
        info_convocatoria (pandas.DataFrame): DataFrame con información de la convocatoria.
        
    Returns:
        pandas.DataFrame: DataFrame con el ritmo actual calculado.
    """
    # Verificar columnas necesarias
    columnas_datos = ['Fecha', 'Marca', 'Canal', 'ID Convocatoria', 'Leads', 'Matrículas']
    for col in columnas_datos:
        if col not in datos_actuales.columns:
            raise ValueError(f"El DataFrame de datos actuales debe contener la columna '{col}'")
    
    columnas_info = ['Marca', 'Canal', 'ID Convocatoria', 'Fecha Inicio', 'Fecha Fin']
    for col in columnas_info:
        if col not in info_convocatoria.columns:
            raise ValueError(f"El DataFrame de información de convocatoria debe contener la columna '{col}'")
    
    # Asegurar que las fechas sean datetime
    datos_actuales['Fecha'] = pd.to_datetime(datos_actuales['Fecha'])
    info_convocatoria['Fecha Inicio'] = pd.to_datetime(info_convocatoria['Fecha Inicio'])
    info_convocatoria['Fecha Fin'] = pd.to_datetime(info_convocatoria['Fecha Fin'])
    
    # Agrupar datos actuales por marca, canal y convocatoria
    datos_agrupados = datos_actuales.groupby(['Marca', 'Canal', 'ID Convocatoria']).agg({
        'Leads': 'sum',
        'Matrículas': 'sum'
    }).reset_index()
    
    # Calcular tasa de conversión actual
    datos_agrupados['Tasa Conversión Actual'] = np.where(
        datos_agrupados['Leads'] > 0,
        datos_agrupados['Matrículas'] / datos_agrupados['Leads'],
        0
    )
    
    # Fecha actual para cálculos
    fecha_actual = datetime.now()
    
    # Unir con información de convocatoria
    df_convocatoria = pd.merge(
        datos_agrupados,
        info_convocatoria[['Marca', 'Canal', 'ID Convocatoria', 'Fecha Inicio', 'Fecha Fin']],
        on=['Marca', 'Canal', 'ID Convocatoria'],
        how='left'
    )
    
    # Calcular duración total de la convocatoria en días
    df_convocatoria['Duración Total (días)'] = (df_convocatoria['Fecha Fin'] - df_convocatoria['Fecha Inicio']).dt.days
    
    # Calcular días transcurridos de la convocatoria
    df_convocatoria['Días Transcurridos'] = (fecha_actual - df_convocatoria['Fecha Inicio']).dt.days
    
    # Ajustar días transcurridos (no negativos y no mayores a la duración total)
    df_convocatoria['Días Transcurridos'] = df_convocatoria['Días Transcurridos'].clip(0, df_convocatoria['Duración Total (días)'])
    
    # Calcular días restantes
    df_convocatoria['Días Restantes'] = df_convocatoria['Duración Total (días)'] - df_convocatoria['Días Transcurridos']
    
    # Calcular porcentaje de avance de la convocatoria
    df_convocatoria['Porcentaje Avance (%)'] = (df_convocatoria['Días Transcurridos'] / df_convocatoria['Duración Total (días)']) * 100
    
    # Calcular ritmo diario de leads
    df_convocatoria['Promedio Leads Diarios'] = np.where(
        df_convocatoria['Días Transcurridos'] > 0,
        df_convocatoria['Leads'] / df_convocatoria['Días Transcurridos'],
        0
    )
    
    # Calcular ritmo diario de matrículas
    df_convocatoria['Promedio Matrículas Diarias'] = np.where(
        df_convocatoria['Días Transcurridos'] > 0,
        df_convocatoria['Matrículas'] / df_convocatoria['Días Transcurridos'],
        0
    )
    
    return df_convocatoria


def proyectar_cierre_matricula(datos_ritmo, escenarios_conversion=None):
    """
    Proyecta el cierre de matrícula basado en el ritmo actual y genera escenarios.
    
    Args:
        datos_ritmo (pandas.DataFrame): DataFrame con el ritmo actual calculado.
        escenarios_conversion (list, opcional): Lista de escenarios de variación en la tasa de conversión (en puntos porcentuales).
        
    Returns:
        pandas.DataFrame: DataFrame con proyecciones de cierre para diferentes escenarios.
    """
    # Definir escenarios de conversion si no se proporcionan
    if escenarios_conversion is None:
        escenarios_conversion = [-0.05, -0.01, 0, 0.01, 0.05]
    
    # Crear lista para almacenar proyecciones
    proyecciones = []
    
    # Generar proyecciones para cada convocatoria y escenario
    for _, conv in datos_ritmo.iterrows():
        # Calcular proyección base (sin cambios en conversión)
        leads_proyectados_periodo = conv['Promedio Leads Diarios'] * conv['Duración Total (días)']
        leads_proyectados_restantes = conv['Promedio Leads Diarios'] * conv['Días Restantes']
        leads_proyectados_cierre = conv['Leads'] + leads_proyectados_restantes
        
        # Para cada escenario de conversión
        for variacion in escenarios_conversion:
            # Calcular nueva tasa de conversión
            tasa_conversion_ajustada = conv['Tasa Conversión Actual'] + variacion
            
            # Asegurar que la tasa esté entre 0 y 1
            tasa_conversion_ajustada = max(0, min(1, tasa_conversion_ajustada))
            
            # Calcular matrículas proyectadas
            matriculas_actuales = conv['Matrículas']
            matriculas_proyectadas_restantes = leads_proyectados_restantes * tasa_conversion_ajustada
            matriculas_proyectadas_cierre = matriculas_actuales + matriculas_proyectadas_restantes
            
            # Calcular tasa de conversión global al cierre
            tasa_conversion_cierre = np.where(
                leads_proyectados_cierre > 0,
                matriculas_proyectadas_cierre / leads_proyectados_cierre,
                0
            )
            
            # Guardar resultados
            proyecciones.append({
                'Marca': conv['Marca'],
                'Canal': conv['Canal'],
                'ID Convocatoria': conv['ID Convocatoria'],
                'Fecha Inicio': conv['Fecha Inicio'],
                'Fecha Fin': conv['Fecha Fin'],
                'Días Transcurridos': conv['Días Transcurridos'],
                'Días Restantes': conv['Días Restantes'],
                'Porcentaje Avance (%)': conv['Porcentaje Avance (%)'],
                
                'Escenario': f"{'Mejora' if variacion > 0 else 'Caída' if variacion < 0 else 'Base'} {abs(variacion)*100:.0f}%" if variacion != 0 else 'Base',
                'Variación Conversión (pp)': variacion,
                
                'Leads Actuales': conv['Leads'],
                'Matrículas Actuales': conv['Matrículas'],
                'Tasa Conversión Actual': conv['Tasa Conversión Actual'],
                
                'Leads Proyectados Restantes': leads_proyectados_restantes,
                'Leads Proyectados Cierre': leads_proyectados_cierre,
                
                'Tasa Conversión Ajustada': tasa_conversion_ajustada,
                'Matrículas Proyectadas Restantes': matriculas_proyectadas_restantes,
                'Matrículas Proyectadas Cierre': matriculas_proyectadas_cierre,
                'Tasa Conversión Cierre': tasa_conversion_cierre
            })
    
    # Convertir a DataFrame
    df_proyecciones = pd.DataFrame(proyecciones)
    
    # Redondear valores numéricos
    columnas_redondeo = [
        'Porcentaje Avance (%)', 'Tasa Conversión Actual', 'Tasa Conversión Ajustada',
        'Tasa Conversión Cierre', 'Leads Proyectados Restantes', 'Leads Proyectados Cierre',
        'Matrículas Proyectadas Restantes', 'Matrículas Proyectadas Cierre'
    ]
    
    for col in columnas_redondeo:
        if col in df_proyecciones.columns:
            df_proyecciones[col] = df_proyecciones[col].round(2)
    
    return df_proyecciones


def visualizar_proyeccion_matricula(datos_proyeccion, directorio=None):
    """
    Genera visualizaciones de la proyección de cierre de matrícula.
    
    Args:
        datos_proyeccion (pandas.DataFrame): DataFrame con proyecciones de cierre.
        directorio (str, opcional): Directorio donde guardar las visualizaciones.
        
    Returns:
        dict: Diccionario con rutas de los archivos generados.
    """
    # Configurar estilo de visualización
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("Set2")
    
    # Crear directorio si no existe
    if directorio is None:
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        directorio = os.path.join('../reportes', fecha_actual)
        if not os.path.exists(directorio):
            os.makedirs(directorio)
    
    archivos_generados = {}
    
    # 1. Gráfico de barras: Matrículas proyectadas por escenario
    plt.figure(figsize=(14, 10))
    
    # Obtener convocatorias únicas
    convocatorias = datos_proyeccion[['Marca', 'Canal', 'ID Convocatoria']].drop_duplicates()
    
    # Número de subgráficos
    n_convocatorias = len(convocatorias)
    n_filas = (n_convocatorias + 1) // 2  # Redondear hacia arriba
    n_columnas = min(2, n_convocatorias)
    
    # Crear gráfico para cada convocatoria
    for i, (_, conv) in enumerate(convocatorias.iterrows()):
        # Crear subgráfico
        ax = plt.subplot(n_filas, n_columnas, i+1)
        
        # Filtrar datos para esta convocatoria
        df_conv = datos_proyeccion[
            (datos_proyeccion['Marca'] == conv['Marca']) &
            (datos_proyeccion['Canal'] == conv['Canal']) &
            (datos_proyeccion['ID Convocatoria'] == conv['ID Convocatoria'])
        ]
        
        # Ordenar por escenario para visualización consistente
        orden_escenarios = df_conv.sort_values('Variación Conversión (pp)')['Escenario'].tolist()
        
        # Crear gráfico de barras apiladas
        sns.barplot(
            data=df_conv,
            x='Escenario',
            y='Matrículas Proyectadas Cierre',
            order=orden_escenarios,
            ax=ax
        )
        
        # Añadir barras de matrículas actuales
        matriculas_actuales = df_conv['Matrículas Actuales'].iloc[0]
        
        # Añadir etiquetas
        for j, bar in enumerate(ax.patches):
            height = bar.get_height()
            total = df_conv.iloc[j]['Matrículas Proyectadas Cierre']
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height + 2,
                f'{total:.0f}',
                ha='center',
                fontsize=9
            )
        
        # Dibujar línea para matrículas actuales
        ax.axhline(y=matriculas_actuales, color='red', linestyle='--', alpha=0.7)
        ax.text(
            len(orden_escenarios) - 1,
            matriculas_actuales + 2,
            f'Actual: {matriculas_actuales:.0f}',
            color='red',
            ha='right',
            fontsize=9
        )
        
        # Configurar títulos y etiquetas
        plt.title(f"Matrículas Proyectadas - {conv['Marca']} - {conv['Canal']} - {conv['ID Convocatoria']}", fontsize=11)
        plt.xlabel('Escenario', fontsize=9)
        plt.ylabel('Matrículas', fontsize=9)
        plt.xticks(rotation=45, ha='right')
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    ruta_archivo = os.path.join(directorio, 'proyeccion_matriculas_por_escenario.png')
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos_generados['proyeccion_escenarios'] = ruta_archivo
    
    # 2. Gráfico de progreso: Avance actual y proyección
    plt.figure(figsize=(14, 10))
    
    for i, (_, conv) in enumerate(convocatorias.iterrows()):
        # Crear subgráfico
        ax = plt.subplot(n_filas, n_columnas, i+1)
        
        # Filtrar datos para esta convocatoria
        df_conv = datos_proyeccion[
            (datos_proyeccion['Marca'] == conv['Marca']) &
            (datos_proyeccion['Canal'] == conv['Canal']) &
            (datos_proyeccion['ID Convocatoria'] == conv['ID Convocatoria'])
        ]
        
        # Seleccionar datos del escenario base
        datos_base = df_conv[df_conv['Escenario'] == 'Base'].iloc[0]
        
        # Crear datos para gráfico de progreso
        dias_totales = datos_base['Días Transcurridos'] + datos_base['Días Restantes']
        porcentaje_avance = datos_base['Porcentaje Avance (%)']
        
        # Crear gráfico de progreso
        ax.barh(
            y=0, 
            width=porcentaje_avance,
            height=0.5,
            color='green',
            alpha=0.7,
            label=f"Avance: {porcentaje_avance:.1f}%"
        )
        
        ax.barh(
            y=0,
            width=100 - porcentaje_avance,
            height=0.5,
            left=porcentaje_avance,
            color='gray',
            alpha=0.3,
            label=f"Restante: {100 - porcentaje_avance:.1f}%"
        )
        
        # Añadir marcadores de matrículas
        leads_actuales = datos_base['Leads Actuales']
        leads_proyectados = datos_base['Leads Proyectados Cierre']
        
        matriculas_actuales = datos_base['Matrículas Actuales']
        matriculas_proyectadas = datos_base['Matrículas Proyectadas Cierre']
        
        # Crear eje secundario para matrículas
        ax2 = ax.twinx()
        
        # Matrículas actuales
        ax2.barh(
            y=0.8, 
            width=porcentaje_avance,
            height=0.3,
            color='blue',
            alpha=0.7,
            label=f"Matrículas Actuales: {matriculas_actuales:.0f}"
        )
        
        # Matrículas proyectadas restantes
        ax2.barh(
            y=0.8,
            width=100 - porcentaje_avance,
            height=0.3,
            left=porcentaje_avance,
            color='blue',
            alpha=0.3,
            label=f"Mat. Proyectadas: {matriculas_proyectadas:.0f}"
        )
        
        # Configurar ejes y etiquetas
        ax.set_yticks([])
        ax.set_xlim(0, 100)
        ax.set_xlabel('Porcentaje de Avance (%)', fontsize=9)
        ax.axvline(x=porcentaje_avance, color='black', linestyle='--', alpha=0.5)
        
        # Añadir información adicional
        info_text = (
            f"Inicio: {datos_base['Fecha Inicio'].strftime('%d/%m/%Y')}\n"
            f"Fin: {datos_base['Fecha Fin'].strftime('%d/%m/%Y')}\n"
            f"Días Transcurridos: {datos_base['Días Transcurridos']:.0f}\n"
            f"Días Restantes: {datos_base['Días Restantes']:.0f}\n\n"
            f"Leads Act.: {leads_actuales:.0f}\n"
            f"Leads Proy.: {leads_proyectados:.0f}\n\n"
            f"Mat. Act.: {matriculas_actuales:.0f}\n"
            f"Mat. Proy.: {matriculas_proyectadas:.0f}\n\n"
            f"Conv. Act.: {(datos_base['Tasa Conversión Actual']*100):.1f}%\n"
            f"Conv. Cierre: {(datos_base['Tasa Conversión Cierre']*100):.1f}%"
        )
        
        plt.text(
            105, 
            0,
            info_text,
            fontsize=8,
            verticalalignment='center'
        )
        
        # Título
        plt.title(f"Progreso - {conv['Marca']} - {conv['Canal']} - {conv['ID Convocatoria']}", fontsize=11)
        
        # Leyendas
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=8)
        ax2.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3), ncol=2, fontsize=8)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    ruta_archivo = os.path.join(directorio, 'progreso_convocatorias.png')
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos_generados['progreso'] = ruta_archivo
    
    # 3. Gráfico de comparación: % Aumento/Disminución de matrículas por escenario
    plt.figure(figsize=(14, 8))
    
    for i, (_, conv) in enumerate(convocatorias.iterrows()):
        # Crear subgráfico
        ax = plt.subplot(n_filas, n_columnas, i+1)
        
        # Filtrar datos para esta convocatoria
        df_conv = datos_proyeccion[
            (datos_proyeccion['Marca'] == conv['Marca']) &
            (datos_proyeccion['Canal'] == conv['Canal']) &
            (datos_proyeccion['ID Convocatoria'] == conv['ID Convocatoria'])
        ]
        
        # Ordenar por variación de conversión
        df_conv = df_conv.sort_values('Variación Conversión (pp)')
        
        # Calcular datos del escenario base
        base = df_conv[df_conv['Escenario'] == 'Base']['Matrículas Proyectadas Cierre'].values[0]
        
        # Calcular porcentaje de cambio respecto al escenario base
        df_conv['% Cambio Base'] = ((df_conv['Matrículas Proyectadas Cierre'] - base) / base) * 100
        
        # Crear paleta de colores
        colores = []
        for _, row in df_conv.iterrows():
            if row['Escenario'] == 'Base':
                colores.append('gray')
            elif row['% Cambio Base'] > 0:
                colores.append('green')
            else:
                colores.append('red')
        
        # Crear gráfico de barras
        sns.barplot(
            data=df_conv,
            x='Escenario',
            y='% Cambio Base',
            palette=colores,
            ax=ax
        )
        
        # Añadir línea en y=0
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Añadir etiquetas
        for j, bar in enumerate(ax.patches):
            height = bar.get_height()
            if df_conv.iloc[j]['Escenario'] != 'Base':
                ax.text(
                    bar.get_x() + bar.get_width() / 2.,
                    height + (0.5 if height >= 0 else -1.5),
                    f"{height:.1f}%",
                    ha='center',
                    fontsize=8
                )
        
        # Configurar títulos y etiquetas
        plt.title(f"Cambio % vs Base - {conv['Marca']} - {conv['Canal']} - {conv['ID Convocatoria']}", fontsize=11)
        plt.xlabel('Escenario', fontsize=9)
        plt.ylabel('% Cambio en Matrículas', fontsize=9)
        plt.xticks(rotation=45, ha='right')
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    ruta_archivo = os.path.join(directorio, 'comparacion_cambio_porcentual.png')
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos_generados['cambio_porcentual'] = ruta_archivo
    
    return archivos_generados


def generar_reporte_proyeccion(datos_actuales, info_convocatoria, escenarios_conversion=None, directorio=None):
    """
    Genera un reporte completo de proyección de cierre de matrícula.
    
    Args:
        datos_actuales (pandas.DataFrame): DataFrame con datos actuales de leads y matrículas.
        info_convocatoria (pandas.DataFrame): DataFrame con información de la convocatoria.
        escenarios_conversion (list, opcional): Lista de escenarios de variación en la tasa de conversión.
        directorio (str, opcional): Directorio donde guardar el reporte.
        
    Returns:
        dict: Diccionario con resultados y rutas de archivos generados.
    """
    # Crear directorio si no existe
    if directorio is None:
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        directorio = os.path.join('../reportes', fecha_actual)
        if not os.path.exists(directorio):
            os.makedirs(directorio)
    
    # Calcular ritmo actual
    datos_ritmo = calcular_ritmo_actual(datos_actuales, info_convocatoria)
    
    # Proyectar cierre de matrícula
    datos_proyeccion = proyectar_cierre_matricula(datos_ritmo, escenarios_conversion)
    
    # Generar visualizaciones
    archivos_generados = visualizar_proyeccion_matricula(datos_proyeccion, directorio)
    
    # Generar reporte Excel
    ruta_excel = os.path.join(directorio, 'proyeccion_cierre_matricula.xlsx')
    
    # Crear libro Excel
    writer = pd.ExcelWriter(ruta_excel, engine='xlsxwriter')
    
    # Guardar datos de ritmo actual
    datos_ritmo.to_excel(writer, sheet_name='Ritmo Actual', index=False)
    
    # Guardar proyecciones
    datos_proyeccion.to_excel(writer, sheet_name='Proyecciones Cierre', index=False)
    
    # Crear resumen por convocatoria y escenario
    resumen_conv_escenario = datos_proyeccion.groupby(['Marca', 'Canal', 'ID Convocatoria', 'Escenario']).agg({
        'Leads Actuales': 'first',
        'Matrículas Actuales': 'first',
        'Leads Proyectados Cierre': 'first',
        'Matrículas Proyectadas Cierre': 'first',
        'Tasa Conversión Cierre': 'first'
    }).reset_index()
    
    # Guardar resumen en Excel
    resumen_conv_escenario.to_excel(writer, sheet_name='Resumen por Escenario', index=False)
    
    # Crear resumen global por escenario
    resumen_global = datos_proyeccion.groupby(['Escenario']).agg({
        'Leads Actuales': 'sum',
        'Matrículas Actuales': 'sum',
        'Leads Proyectados Cierre': 'sum',
        'Matrículas Proyectadas Cierre': 'sum'
    }).reset_index()
    
    # Calcular tasa de conversión global
    resumen_global['Tasa Conversión Global Cierre'] = resumen_global['Matrículas Proyectadas Cierre'] / resumen_global['Leads Proyectados Cierre']
    
    # Calcular escenario base para comparaciones
    matriculas_base = resumen_global[resumen_global['Escenario'] == 'Base']['Matrículas Proyectadas Cierre'].values[0]
    
    # Calcular diferencias respecto al escenario base
    resumen_global['Diferencia vs Base'] = resumen_global['Matrículas Proyectadas Cierre'] - matriculas_base
    resumen_global['% Diferencia vs Base'] = (resumen_global['Diferencia vs Base'] / matriculas_base) * 100
    
    # Guardar resumen global en Excel
    resumen_global.to_excel(writer, sheet_name='Resumen Global', index=False)
    
    # Guardar Excel
    writer.close()
    
    archivos_generados['excel'] = ruta_excel
    
    return {
        'ritmo_actual': datos_ritmo,
        'proyecciones': datos_proyeccion,
        'resumen_convocatoria': resumen_conv_escenario,
        'resumen_global': resumen_global,
        'archivos': archivos_generados
    }


if __name__ == "__main__":
    # Ejemplo de uso
    from cargar_datos import cargar_datos_crm, cargar_datos_planificacion
    
    try:
        print("Cargando datos actuales...")
        datos_actuales = cargar_datos_crm("../datos/leads_matriculas_reales.csv")
        
        print("Cargando información de convocatorias...")
        info_convocatoria = cargar_datos_planificacion("../datos/planificacion_quincenal.csv")
        
        # Definir escenarios de variación de conversión (en puntos porcentuales)
        escenarios = [-0.05, -0.01, 0, 0.01, 0.05]
        
        print("Generando proyección de cierre de matrícula...")
        resultado = generar_reporte_proyeccion(
            datos_actuales,
            info_convocatoria,
            escenarios_conversion=escenarios
        )
        
        print(f"Reporte generado en: {resultado['archivos']['excel']}")
        print("\nResumen global por escenario:")
        print(resultado['resumen_global'][['Escenario', 'Matrículas Proyectadas Cierre', '% Diferencia vs Base']])
        
    except Exception as e:
        print(f"Error: {e}") 