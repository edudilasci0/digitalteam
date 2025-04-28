"""
Módulo para implementar una matriz de decisión para la reasignación dinámica de presupuesto
en base a rendimiento y puntos de control semanales para campañas.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class MatrizDecision:
    """
    Clase que implementa una matriz de decisión para reasignación dinámica de presupuesto.
    """
    
    def __init__(self):
        """Inicializa la matriz de decisión con valores predeterminados."""
        # Matriz de reglas para decisiones basadas en rendimiento
        self.matriz_reglas = {
            # Alto rendimiento (CPA bajo respecto al objetivo)
            'ALTO': {
                'ALTO': {'accion': 'AUMENTAR', 'factor': 0.3, 'descripcion': 'Aumentar presupuesto significativamente'},
                'MEDIO': {'accion': 'AUMENTAR', 'factor': 0.2, 'descripcion': 'Aumentar presupuesto moderadamente'},
                'BAJO': {'accion': 'MANTENER', 'factor': 0.0, 'descripcion': 'Mantener presupuesto y monitorear'}
            },
            # Rendimiento medio (CPA cercano al objetivo)
            'MEDIO': {
                'ALTO': {'accion': 'AUMENTAR', 'factor': 0.15, 'descripcion': 'Aumentar presupuesto ligeramente'},
                'MEDIO': {'accion': 'MANTENER', 'factor': 0.0, 'descripcion': 'Mantener presupuesto actual'},
                'BAJO': {'accion': 'REDUCIR', 'factor': -0.1, 'descripcion': 'Reducir presupuesto ligeramente'}
            },
            # Bajo rendimiento (CPA alto respecto al objetivo)
            'BAJO': {
                'ALTO': {'accion': 'MANTENER', 'factor': 0.0, 'descripcion': 'Mantener presupuesto y revisar estrategia'},
                'MEDIO': {'accion': 'REDUCIR', 'factor': -0.2, 'descripcion': 'Reducir presupuesto moderadamente'},
                'BAJO': {'accion': 'REDUCIR', 'factor': -0.4, 'descripcion': 'Reducir presupuesto significativamente'}
            }
        }
        
        # Umbrales para clasificar rendimiento
        self.umbrales_rendimiento = {
            'ALTO': lambda cpa_actual, cpa_objetivo: cpa_actual <= cpa_objetivo * 0.8,
            'MEDIO': lambda cpa_actual, cpa_objetivo: cpa_objetivo * 0.8 < cpa_actual <= cpa_objetivo * 1.2,
            'BAJO': lambda cpa_actual, cpa_objetivo: cpa_actual > cpa_objetivo * 1.2
        }
        
        # Umbrales para clasificar potencial
        self.umbrales_potencial = {
            'ALTO': lambda conversion, promedio: conversion >= promedio * 1.2,
            'MEDIO': lambda conversion, promedio: promedio * 0.8 <= conversion < promedio * 1.2,
            'BAJO': lambda conversion, promedio: conversion < promedio * 0.8
        }
    
    def actualizar_umbrales(self, umbrales_rendimiento=None, umbrales_potencial=None):
        """
        Actualiza los umbrales utilizados para clasificar rendimiento y potencial.
        
        Args:
            umbrales_rendimiento (dict, optional): Nuevos umbrales de rendimiento.
            umbrales_potencial (dict, optional): Nuevos umbrales de potencial.
        """
        if umbrales_rendimiento:
            self.umbrales_rendimiento = umbrales_rendimiento
        
        if umbrales_potencial:
            self.umbrales_potencial = umbrales_potencial
    
    def actualizar_matriz(self, nueva_matriz):
        """
        Actualiza la matriz de reglas.
        
        Args:
            nueva_matriz (dict): Nueva matriz de reglas.
        """
        self.matriz_reglas = nueva_matriz
    
    def _clasificar_rendimiento(self, cpa_actual, cpa_objetivo):
        """
        Clasifica el rendimiento de un canal según su CPA.
        
        Args:
            cpa_actual (float): CPA actual del canal.
            cpa_objetivo (float): CPA objetivo del canal.
            
        Returns:
            str: Clasificación del rendimiento ('ALTO', 'MEDIO', 'BAJO').
        """
        for nivel, func_umbral in self.umbrales_rendimiento.items():
            if func_umbral(cpa_actual, cpa_objetivo):
                return nivel
        
        return 'MEDIO'  # Valor predeterminado si hay algún problema
    
    def _clasificar_potencial(self, tasa_conversion, tasa_promedio):
        """
        Clasifica el potencial de un canal según su tasa de conversión.
        
        Args:
            tasa_conversion (float): Tasa de conversión del canal.
            tasa_promedio (float): Tasa de conversión promedio de todos los canales.
            
        Returns:
            str: Clasificación del potencial ('ALTO', 'MEDIO', 'BAJO').
        """
        for nivel, func_umbral in self.umbrales_potencial.items():
            if func_umbral(tasa_conversion, tasa_promedio):
                return nivel
        
        return 'MEDIO'  # Valor predeterminado si hay algún problema
    
    def generar_decisiones(self, df_canales):
        """
        Genera decisiones de reasignación de presupuesto basadas en la matriz.
        
        Args:
            df_canales (pandas.DataFrame): DataFrame con datos de canales activos.
            
        Returns:
            pandas.DataFrame: DataFrame con decisiones de reasignación.
        """
        # Verificar columnas necesarias
        columnas_requeridas = ['CPA Actual (USD)', 'CPA Objetivo (USD)', 'Tasa de Conversión (%)', 'Presupuesto Asignado (USD)']
        for col in columnas_requeridas:
            if col not in df_canales.columns:
                raise ValueError(f"El DataFrame debe contener la columna '{col}'")
        
        # Calcular tasa de conversión promedio
        tasa_promedio = df_canales['Tasa de Conversión (%)'].mean()
        
        # Crear una copia del DataFrame para no modificar el original
        df_decisiones = df_canales.copy()
        
        # Añadir columnas de clasificación y decisión
        df_decisiones['Rendimiento'] = df_decisiones.apply(
            lambda row: self._clasificar_rendimiento(row['CPA Actual (USD)'], row['CPA Objetivo (USD)']),
            axis=1
        )
        
        df_decisiones['Potencial'] = df_decisiones.apply(
            lambda row: self._clasificar_potencial(row['Tasa de Conversión (%)'], tasa_promedio),
            axis=1
        )
        
        # Aplicar matriz de decisión
        def obtener_decision(rendimiento, potencial):
            return self.matriz_reglas[rendimiento][potencial]
        
        df_decisiones['Decision'] = df_decisiones.apply(
            lambda row: obtener_decision(row['Rendimiento'], row['Potencial']),
            axis=1
        )
        
        # Extraer valores de decisión
        df_decisiones['Acción'] = df_decisiones['Decision'].apply(lambda x: x['accion'])
        df_decisiones['Factor Ajuste'] = df_decisiones['Decision'].apply(lambda x: x['factor'])
        df_decisiones['Descripción'] = df_decisiones['Decision'].apply(lambda x: x['descripcion'])
        
        # Calcular nuevo presupuesto
        df_decisiones['Presupuesto Nuevo (USD)'] = df_decisiones.apply(
            lambda row: row['Presupuesto Asignado (USD)'] * (1 + row['Factor Ajuste']),
            axis=1
        )
        
        # Calcular cambio absoluto y porcentual
        df_decisiones['Cambio Presupuesto (USD)'] = df_decisiones['Presupuesto Nuevo (USD)'] - df_decisiones['Presupuesto Asignado (USD)']
        df_decisiones['Cambio Porcentual (%)'] = (df_decisiones['Cambio Presupuesto (USD)'] / df_decisiones['Presupuesto Asignado (USD)']) * 100
        
        # Eliminar columna intermedia de decisión
        df_decisiones.drop(columns=['Decision'], inplace=True)
        
        return df_decisiones
    
    def equilibrar_presupuesto(self, df_decisiones, presupuesto_total=None):
        """
        Equilibra el presupuesto para asegurar que el total coincida con el presupuesto disponible.
        
        Args:
            df_decisiones (pandas.DataFrame): DataFrame con decisiones iniciales.
            presupuesto_total (float, optional): Presupuesto total disponible. Si es None,
                                               se mantiene el presupuesto total original.
            
        Returns:
            pandas.DataFrame: DataFrame con presupuesto equilibrado.
        """
        # Crear copia para no modificar el original
        df_equilibrado = df_decisiones.copy()
        
        # Calcular presupuesto original y nuevo
        presupuesto_original = df_equilibrado['Presupuesto Asignado (USD)'].sum()
        presupuesto_nuevo = df_equilibrado['Presupuesto Nuevo (USD)'].sum()
        
        # Si no se especifica un presupuesto total, mantener el original
        if presupuesto_total is None:
            presupuesto_total = presupuesto_original
        
        # Calcular factor de ajuste proporcional
        factor_ajuste = presupuesto_total / presupuesto_nuevo if presupuesto_nuevo > 0 else 1
        
        # Aplicar ajuste proporcional
        df_equilibrado['Presupuesto Equilibrado (USD)'] = df_equilibrado['Presupuesto Nuevo (USD)'] * factor_ajuste
        
        # Recalcular cambios con presupuesto equilibrado
        df_equilibrado['Cambio Equilibrado (USD)'] = df_equilibrado['Presupuesto Equilibrado (USD)'] - df_equilibrado['Presupuesto Asignado (USD)']
        df_equilibrado['Cambio Equilibrado (%)'] = (df_equilibrado['Cambio Equilibrado (USD)'] / df_equilibrado['Presupuesto Asignado (USD)']) * 100
        
        return df_equilibrado
    
    def generar_plan_implementacion(self, df_decisiones, fecha_inicio=None):
        """
        Genera un plan de implementación para la reasignación de presupuesto.
        
        Args:
            df_decisiones (pandas.DataFrame): DataFrame con decisiones de presupuesto.
            fecha_inicio (datetime, optional): Fecha para iniciar la implementación.
            
        Returns:
            pandas.DataFrame: Plan de implementación con fechas y acciones.
        """
        if fecha_inicio is None:
            fecha_inicio = datetime.now() + timedelta(days=1)
        
        # Crear DataFrame para el plan
        planes = []
        
        # Ordenar por cambio porcentual (absoluto) para priorizar cambios mayores
        df_priorizado = df_decisiones.copy()
        
        # Usar Cambio Equilibrado si está disponible, de lo contrario usar Cambio Porcentual
        if 'Cambio Equilibrado (%)' in df_priorizado.columns:
            df_priorizado['Cambio Abs (%)'] = abs(df_priorizado['Cambio Equilibrado (%)'])
            cambio_col = 'Cambio Equilibrado (%)'
            presupuesto_col = 'Presupuesto Equilibrado (USD)'
        else:
            df_priorizado['Cambio Abs (%)'] = abs(df_priorizado['Cambio Porcentual (%)'])
            cambio_col = 'Cambio Porcentual (%)'
            presupuesto_col = 'Presupuesto Nuevo (USD)'
        
        df_priorizado = df_priorizado.sort_values(by='Cambio Abs (%)', ascending=False)
        
        # Definir umbrales para categorizar los cambios
        for idx, fila in df_priorizado.iterrows():
            # Extraer datos de canal
            canal_info = {
                'Marca': fila['Marca'] if 'Marca' in fila else '',
                'Canal': fila['Canal'] if 'Canal' in fila else '',
                'ID Convocatoria': fila['ID Convocatoria'] if 'ID Convocatoria' in fila else '',
                'Fecha Implementación': None,
                'Acción': None,
                'Urgencia': None,
                'Presupuesto Anterior (USD)': fila['Presupuesto Asignado (USD)'],
                'Presupuesto Nuevo (USD)': fila[presupuesto_col],
                'Cambio (USD)': fila[presupuesto_col] - fila['Presupuesto Asignado (USD)'],
                'Cambio (%)': fila[cambio_col],
                'Rendimiento': fila['Rendimiento'],
                'Potencial': fila['Potencial']
            }
            
            # Determinar urgencia y fecha basado en magnitud del cambio
            cambio_abs = abs(fila[cambio_col])
            
            if cambio_abs > 20:
                canal_info['Urgencia'] = 'Alta'
                canal_info['Fecha Implementación'] = fecha_inicio + timedelta(days=1)
            elif cambio_abs > 10:
                canal_info['Urgencia'] = 'Media'
                canal_info['Fecha Implementación'] = fecha_inicio + timedelta(days=3)
            else:
                canal_info['Urgencia'] = 'Baja'
                canal_info['Fecha Implementación'] = fecha_inicio + timedelta(days=7)
            
            # Determinar acción
            cambio = fila[presupuesto_col] - fila['Presupuesto Asignado (USD)']
            if cambio > 0:
                canal_info['Acción'] = f"Aumentar presupuesto en {abs(cambio):.2f} USD"
            elif cambio < 0:
                canal_info['Acción'] = f"Reducir presupuesto en {abs(cambio):.2f} USD"
            else:
                canal_info['Acción'] = "Mantener presupuesto actual"
            
            planes.append(canal_info)
        
        return pd.DataFrame(planes)


def configurar_puntos_control(df_convocatorias, frecuencia='semanal', dias_semana=None):
    """
    Configura puntos de control para el seguimiento y ajuste de campañas.
    
    Args:
        df_convocatorias (pandas.DataFrame): DataFrame con información de convocatorias.
        frecuencia (str): Frecuencia de los puntos de control ('semanal', 'quincenal', 'mensual').
        dias_semana (list, optional): Lista de días de la semana para los puntos de control (0=lunes, 6=domingo).
        
    Returns:
        pandas.DataFrame: DataFrame con puntos de control programados.
    """
    # Verificar columnas requeridas
    columnas_requeridas = ['ID Convocatoria', 'Fecha Inicio', 'Fecha Fin']
    for col in columnas_requeridas:
        if col not in df_convocatorias.columns:
            raise ValueError(f"El DataFrame debe contener la columna '{col}'")
    
    # Convertir fechas a datetime si no lo están
    df_convocatorias = df_convocatorias.copy()
    for col in ['Fecha Inicio', 'Fecha Fin']:
        if not pd.api.types.is_datetime64_dtype(df_convocatorias[col]):
            df_convocatorias[col] = pd.to_datetime(df_convocatorias[col])
    
    # Configurar días por defecto según frecuencia
    if dias_semana is None:
        if frecuencia == 'semanal':
            dias_semana = [0]  # Lunes
        elif frecuencia == 'quincenal':
            dias_semana = [0, 7]  # Lunes cada dos semanas
        elif frecuencia == 'mensual':
            dias_semana = [0]  # Primer lunes del mes
        else:
            dias_semana = [0]  # Valor por defecto: lunes
    
    # Calcular puntos de control para cada convocatoria
    puntos_control = []
    
    for idx, conv in df_convocatorias.iterrows():
        fecha_actual = conv['Fecha Inicio']
        fecha_fin = conv['Fecha Fin']
        
        # Iterar hasta la fecha fin
        while fecha_actual <= fecha_fin:
            # Determinar si es un día de control según la frecuencia
            es_punto_control = False
            
            if frecuencia == 'semanal':
                # Cada semana en los días especificados
                es_punto_control = fecha_actual.weekday() in dias_semana
            
            elif frecuencia == 'quincenal':
                # Cada dos semanas
                semana_desde_inicio = ((fecha_actual - conv['Fecha Inicio']).days // 7) % 2
                es_punto_control = fecha_actual.weekday() in dias_semana and semana_desde_inicio == 0
            
            elif frecuencia == 'mensual':
                # Una vez al mes (primer día especificado de cada mes)
                # Verificar si es el primer día especificado del mes
                primer_dia_mes = fecha_actual.replace(day=1)
                dias_transcurridos = (fecha_actual - primer_dia_mes).days
                semana_mes = dias_transcurridos // 7
                es_punto_control = fecha_actual.weekday() in dias_semana and semana_mes == 0
            
            # Si es un punto de control, agregar a la lista
            if es_punto_control:
                # Calcular progreso de la convocatoria
                duracion_total = (conv['Fecha Fin'] - conv['Fecha Inicio']).days
                dias_transcurridos = (fecha_actual - conv['Fecha Inicio']).days
                
                if duracion_total > 0:
                    progreso = (dias_transcurridos / duracion_total) * 100
                else:
                    progreso = 100
                
                punto = {
                    'ID Convocatoria': conv['ID Convocatoria'],
                    'Fecha Control': fecha_actual,
                    'Progreso (%)': progreso,
                    'Días Restantes': (conv['Fecha Fin'] - fecha_actual).days,
                    'Fase': 'Inicial' if progreso < 33 else 'Media' if progreso < 66 else 'Final',
                    'Requiere Ajuste': progreso < 90  # No ajustar en la fase final
                }
                
                # Añadir otros campos disponibles en la convocatoria
                for campo in ['Marca', 'Canal', 'Presupuesto Asignado (USD)', 'CPA Objetivo (USD)']:
                    if campo in conv:
                        punto[campo] = conv[campo]
                
                puntos_control.append(punto)
            
            # Avanzar al siguiente día
            fecha_actual += timedelta(days=1)
    
    # Convertir a DataFrame y ordenar por fecha
    df_puntos = pd.DataFrame(puntos_control)
    df_puntos = df_puntos.sort_values(by='Fecha Control')
    
    return df_puntos


def visualizar_matriz_decision(matriz):
    """
    Genera una visualización de la matriz de decisión.
    
    Args:
        matriz (dict): La matriz de decisión a visualizar.
        
    Returns:
        matplotlib.figure.Figure: Figura con la visualización generada.
    """
    # Extraer niveles
    niveles_rendimiento = list(matriz.keys())
    niveles_potencial = list(matriz[niveles_rendimiento[0]].keys())
    
    # Crear matriz para visualización
    matriz_visual = np.zeros((len(niveles_rendimiento), len(niveles_potencial)))
    
    # Mapear acciones a valores numéricos
    mapa_acciones = {
        'AUMENTAR': 1,
        'MANTENER': 0,
        'REDUCIR': -1
    }
    
    # Llenar la matriz
    for i, rendimiento in enumerate(niveles_rendimiento):
        for j, potencial in enumerate(niveles_potencial):
            accion = matriz[rendimiento][potencial]['accion']
            matriz_visual[i, j] = mapa_acciones.get(accion, 0)
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Colores para diferentes acciones
    cmap = plt.cm.RdYlGn
    
    # Crear heatmap
    im = ax.imshow(matriz_visual, cmap=cmap, vmin=-1, vmax=1)
    
    # Configurar etiquetas de ejes
    ax.set_xticks(np.arange(len(niveles_potencial)))
    ax.set_yticks(np.arange(len(niveles_rendimiento)))
    ax.set_xticklabels(niveles_potencial)
    ax.set_yticklabels(niveles_rendimiento)
    
    # Rotar etiquetas del eje x
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Añadir etiquetas y título
    ax.set_xlabel('Potencial (Tasa de Conversión)')
    ax.set_ylabel('Rendimiento (CPA vs Objetivo)')
    ax.set_title('Matriz de Decisión para Reasignación de Presupuesto')
    
    # Añadir texto en cada celda
    for i in range(len(niveles_rendimiento)):
        for j in range(len(niveles_potencial)):
            accion = matriz[niveles_rendimiento[i]][niveles_potencial[j]]['accion']
            factor = matriz[niveles_rendimiento[i]][niveles_potencial[j]]['factor']
            
            texto = f"{accion}\n({factor:+.0%})"
            ax.text(j, i, texto, ha="center", va="center", color="black")
    
    # Añadir leyenda
    from matplotlib.patches import Patch
    elementos_leyenda = [
        Patch(facecolor=cmap(0.8), label='AUMENTAR'),
        Patch(facecolor=cmap(0.5), label='MANTENER'),
        Patch(facecolor=cmap(0.2), label='REDUCIR')
    ]
    ax.legend(handles=elementos_leyenda, loc='upper right')
    
    # Ajustar layout
    fig.tight_layout()
    
    return fig


def visualizar_plan_implementacion(df_plan):
    """
    Genera una visualización del plan de implementación.
    
    Args:
        df_plan (pandas.DataFrame): DataFrame con el plan de implementación.
        
    Returns:
        matplotlib.figure.Figure: Figura con la visualización generada.
    """
    # Crear figura
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [1, 2]})
    
    # 1. Gráfico de barras para cambios de presupuesto
    df_ordenado = df_plan.sort_values('Cambio (%)')
    
    # Crear barras horizontales
    barras = ax1.barh(
        df_ordenado['Canal'] + ' - ' + df_ordenado['Marca'],
        df_ordenado['Cambio (%)'],
        color=[
            'green' if x > 0 else 'red' if x < 0 else 'gray'
            for x in df_ordenado['Cambio (%)']
        ],
        alpha=0.7
    )
    
    # Añadir etiquetas de valores
    for i, bar in enumerate(barras):
        width = bar.get_width()
        label_x_pos = width + 1 if width > 0 else width - 6
        ax1.text(
            label_x_pos,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.1f}%",
            va='center',
            color='black'
        )
    
    # Configurar gráfico
    ax1.set_title('Cambios de Presupuesto por Canal')
    ax1.set_xlabel('Cambio Porcentual (%)')
    ax1.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax1.grid(axis='x', linestyle='--', alpha=0.3)
    
    # 2. Gráfico de línea de tiempo para implementación
    # Convertir fechas a números para el gráfico
    fechas_unicas = df_plan['Fecha Implementación'].unique()
    fechas_unicas = sorted(fechas_unicas)
    
    # Agrupar por fecha y urgencia
    grupos_fecha = df_plan.groupby(['Fecha Implementación', 'Urgencia']).size().unstack(fill_value=0)
    
    # Crear una columna para la posición en el gráfico
    for i, fecha in enumerate(fechas_unicas):
        df_plan.loc[df_plan['Fecha Implementación'] == fecha, 'Posición'] = i
    
    # Colores por urgencia
    colores_urgencia = {
        'Alta': 'red',
        'Media': 'orange',
        'Baja': 'green'
    }
    
    # Dibujar línea de tiempo
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=2)
    
    # Añadir eventos en la línea de tiempo
    for idx, fila in df_plan.iterrows():
        y_pos = 0
        x_pos = fila['Posición']
        
        # Crear marcador
        color = colores_urgencia.get(fila['Urgencia'], 'gray')
        ax2.scatter(x_pos, y_pos, s=100, color=color, alpha=0.7, zorder=10)
        
        # Añadir etiqueta con info del cambio
        texto = f"{fila['Canal']} - {fila['Marca']}\n{fila['Acción']}"
        ax2.annotate(
            texto,
            xy=(x_pos, y_pos),
            xytext=(0, 20 if idx % 2 == 0 else -40),
            textcoords='offset points',
            ha='center',
            va='center',
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2", color=color)
        )
    
    # Configurar eje X con fechas
    ax2.set_xticks(range(len(fechas_unicas)))
    ax2.set_xticklabels([fecha.strftime('%d-%m-%Y') for fecha in fechas_unicas])
    plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
    
    # Ocultar eje Y
    ax2.set_yticks([])
    
    # Título y leyenda
    ax2.set_title('Cronograma de Implementación')
    
    # Crear leyenda manual
    from matplotlib.lines import Line2D
    elementos_leyenda = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Alta Urgencia'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label='Media Urgencia'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Baja Urgencia')
    ]
    ax2.legend(handles=elementos_leyenda, loc='upper right')
    
    # Ajustar layout
    fig.tight_layout()
    
    return fig


if __name__ == "__main__":
    # Ejemplo de uso
    from cargar_datos import cargar_datos_crm, cargar_datos_planificacion
    from validar_datos import validar_datos_crm, validar_datos_planificacion
    from predecir_matriculas import predecir_matriculas
    
    try:
        datos_crm = cargar_datos_crm("../datos/leads_matriculas_reales.csv")
        datos_planificacion = cargar_datos_planificacion("../datos/planificacion_quincenal.csv")
        
        validar_datos_crm(datos_crm)
        validar_datos_planificacion(datos_planificacion)
        
        prediccion = predecir_matriculas(datos_crm, datos_planificacion)
        
        # Simular datos de rendimiento actual
        df_rendimiento = prediccion.copy()
        df_rendimiento['CPA Actual (USD)'] = df_rendimiento['CPA Esperado (USD)'] * np.random.uniform(0.7, 1.3, len(df_rendimiento))
        df_rendimiento['CPA Objetivo (USD)'] = 200  # Ejemplo de CPA objetivo
        
        # Inicializar matriz de decisión
        matriz = MatrizDecision()
        
        # Generar decisiones
        decisiones = matriz.generar_decisiones(df_rendimiento)
        
        print("Decisiones de reasignación de presupuesto:")
        print(decisiones[['Marca', 'Canal', 'Rendimiento', 'Potencial', 
                         'Acción', 'Factor Ajuste', 'Presupuesto Asignado (USD)', 
                         'Presupuesto Nuevo (USD)', 'Cambio Porcentual (%)']])
        
        # Equilibrar presupuesto
        decisiones_equilibradas = matriz.equilibrar_presupuesto(decisiones, presupuesto_total=50000)
        
        print("\nDecisiones con presupuesto equilibrado:")
        print(decisiones_equilibradas[['Marca', 'Canal', 'Presupuesto Asignado (USD)', 
                                      'Presupuesto Equilibrado (USD)', 'Cambio Equilibrado (%)']])
        
        # Generar plan de implementación
        plan = matriz.generar_plan_implementacion(decisiones_equilibradas)
        
        print("\nPlan de implementación:")
        print(plan[['Marca', 'Canal', 'Fecha Implementación', 'Acción', 'Urgencia']])
        
        # Configurar puntos de control
        puntos_control = configurar_puntos_control(datos_planificacion, frecuencia='semanal')
        
        print("\nPuntos de control semanales:")
        print(puntos_control[['ID Convocatoria', 'Fecha Control', 'Progreso (%)', 'Fase']])
        
        # Visualizar matriz de decisión
        fig_matriz = visualizar_matriz_decision(matriz.matriz_reglas)
        plt.savefig("../salidas/matriz_decision.png")
        plt.close(fig_matriz)
        
        # Visualizar plan de implementación
        fig_plan = visualizar_plan_implementacion(plan)
        plt.savefig("../salidas/plan_implementacion.png")
        plt.close(fig_plan)
        
        print("\nVisualizaciones guardadas en:")
        print("- ../salidas/matriz_decision.png")
        print("- ../salidas/plan_implementacion.png")
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 