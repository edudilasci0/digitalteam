"""
Módulo para planificar campañas de marketing y asignar presupuestos.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calcular_presupuesto_optimo(datos_historicos, presupuesto_total, objetivo_matriculas=None):
    """
    Calcula la distribución óptima de presupuesto entre canales basado en el rendimiento histórico.
    
    Args:
        datos_historicos (pandas.DataFrame): DataFrame con datos históricos de rendimiento.
        presupuesto_total (float): Presupuesto total disponible para asignar.
        objetivo_matriculas (int, opcional): Objetivo total de matrículas a conseguir.
        
    Returns:
        pandas.DataFrame: DataFrame con la asignación de presupuesto por canal.
    """
    # Verificar que se tengan las columnas necesarias
    columnas_requeridas = ['Marca', 'Canal', 'CPA', 'Tasa Conversión']
    for col in columnas_requeridas:
        if col not in datos_historicos.columns:
            raise ValueError(f"El DataFrame debe contener la columna '{col}'")
    
    # Filtrar datos con CPA y Tasa Conversión válidos
    df_valido = datos_historicos[
        (datos_historicos['CPA'] > 0) & 
        (datos_historicos['CPA'] != float('inf')) &
        (datos_historicos['Tasa Conversión'] > 0)
    ].copy()
    
    # Si no hay datos válidos, devolver DataFrame vacío
    if df_valido.empty:
        return pd.DataFrame(columns=['Marca', 'Canal', 'Presupuesto Asignado (USD)', 
                                     'Objetivo Leads', 'Objetivo Matrículas'])
    
    # Agrupar por marca y canal para obtener promedios
    df_agrupado = df_valido.groupby(['Marca', 'Canal']).agg({
        'CPA': 'mean',
        'Tasa Conversión': 'mean'
    }).reset_index()
    
    # Calcular eficiencia (inverso del CPA) y peso de asignación
    df_agrupado['Eficiencia'] = 1 / df_agrupado['CPA']
    df_agrupado['Peso Asignación'] = df_agrupado['Eficiencia'] / df_agrupado['Eficiencia'].sum()
    
    # Calcular presupuesto asignado por canal
    df_agrupado['Presupuesto Asignado (USD)'] = df_agrupado['Peso Asignación'] * presupuesto_total
    
    # Calcular objetivos de leads y matrículas
    df_agrupado['Objetivo Matrículas'] = df_agrupado['Presupuesto Asignado (USD)'] / df_agrupado['CPA']
    df_agrupado['Objetivo Leads'] = df_agrupado['Objetivo Matrículas'] / df_agrupado['Tasa Conversión']
    
    # Si se especifica un objetivo de matrículas, ajustar el presupuesto
    if objetivo_matriculas is not None:
        # Calcular factor de ajuste
        matriculas_esperadas = df_agrupado['Objetivo Matrículas'].sum()
        factor_ajuste = objetivo_matriculas / matriculas_esperadas
        
        # Ajustar presupuesto y objetivos
        df_agrupado['Presupuesto Asignado (USD)'] *= factor_ajuste
        df_agrupado['Objetivo Matrículas'] *= factor_ajuste
        df_agrupado['Objetivo Leads'] *= factor_ajuste
    
    # Redondear valores numéricos para mejor legibilidad
    df_agrupado['Presupuesto Asignado (USD)'] = df_agrupado['Presupuesto Asignado (USD)'].round(2)
    df_agrupado['Objetivo Matrículas'] = df_agrupado['Objetivo Matrículas'].round(0)
    df_agrupado['Objetivo Leads'] = df_agrupado['Objetivo Leads'].round(0)
    
    # Seleccionar columnas relevantes para el resultado
    resultado = df_agrupado[['Marca', 'Canal', 'Presupuesto Asignado (USD)', 
                            'Objetivo Leads', 'Objetivo Matrículas']]
    
    return resultado


def generar_planificacion_quincenal(datos_presupuesto, fecha_inicio=None, duracion_dias=15):
    """
    Genera un plan quincenal de campaña basado en la asignación de presupuesto.
    
    Args:
        datos_presupuesto (pandas.DataFrame): DataFrame con asignación de presupuesto por canal.
        fecha_inicio (datetime, opcional): Fecha de inicio de la campaña. Por defecto es la fecha actual.
        duracion_dias (int, opcional): Duración de la campaña en días.
        
    Returns:
        pandas.DataFrame: DataFrame con la planificación quincenal.
    """
    # Verificar que se tengan las columnas necesarias
    columnas_requeridas = ['Marca', 'Canal', 'Presupuesto Asignado (USD)', 
                           'Objetivo Leads', 'Objetivo Matrículas']
    for col in columnas_requeridas:
        if col not in datos_presupuesto.columns:
            raise ValueError(f"El DataFrame debe contener la columna '{col}'")
    
    # Establecer fecha de inicio
    if fecha_inicio is None:
        fecha_inicio = datetime.now()
    
    # Crear DataFrame con fechas
    fechas = [fecha_inicio + timedelta(days=i) for i in range(duracion_dias)]
    df_fechas = pd.DataFrame({'Fecha': fechas})
    
    # Crear ID de convocatoria
    convocatoria_id = fecha_inicio.strftime('%Y%m%d')
    
    # Expandir datos de presupuesto para cada día
    filas = []
    for idx, row in datos_presupuesto.iterrows():
        # Distribuir presupuesto y objetivos por día
        presupuesto_diario = row['Presupuesto Asignado (USD)'] / duracion_dias
        leads_diarios = row['Objetivo Leads'] / duracion_dias
        matriculas_diarias = row['Objetivo Matrículas'] / duracion_dias
        
        for fecha in fechas:
            filas.append({
                'Fecha': fecha,
                'Marca': row['Marca'],
                'Canal': row['Canal'],
                'ID Convocatoria': convocatoria_id,
                'Presupuesto Asignado (USD)': presupuesto_diario,
                'Objetivo Leads': leads_diarios,
                'Objetivo Matrículas': matriculas_diarias
            })
    
    # Crear DataFrame de planificación
    planificacion = pd.DataFrame(filas)
    
    # Redondear valores numéricos (solo para visualización)
    planificacion['Presupuesto Asignado (USD)'] = planificacion['Presupuesto Asignado (USD)'].round(2)
    planificacion['Objetivo Leads'] = planificacion['Objetivo Leads'].round(1)
    planificacion['Objetivo Matrículas'] = planificacion['Objetivo Matrículas'].round(1)
    
    return planificacion


def exportar_planificacion(planificacion, ruta_archivo):
    """
    Exporta la planificación a un archivo CSV.
    
    Args:
        planificacion (pandas.DataFrame): DataFrame con la planificación.
        ruta_archivo (str): Ruta donde guardar el archivo CSV.
        
    Returns:
        str: Ruta del archivo generado.
    """
    # Asegurar que la ruta termine en .csv
    if not ruta_archivo.endswith('.csv'):
        ruta_archivo += '.csv'
    
    # Guardar planificación en archivo CSV
    planificacion.to_csv(ruta_archivo, index=False)
    
    return ruta_archivo


def simular_resultados_campaña(planificacion, variabilidad=0.2):
    """
    Simula los resultados potenciales de una campaña basados en la planificación.
    
    Args:
        planificacion (pandas.DataFrame): DataFrame con la planificación.
        variabilidad (float, opcional): Factor de variabilidad para la simulación.
        
    Returns:
        pandas.DataFrame: DataFrame con resultados simulados.
    """
    # Crear copia para no modificar el original
    simulacion = planificacion.copy()
    
    # Generar números aleatorios para la variabilidad
    np.random.seed(42)  # Para reproducibilidad
    factor_leads = np.random.normal(1, variabilidad, len(simulacion))
    factor_conversion = np.random.normal(1, variabilidad / 2, len(simulacion))
    
    # Simular leads obtenidos
    simulacion['Leads Obtenidos'] = (simulacion['Objetivo Leads'] * factor_leads).round(0)
    simulacion['Leads Obtenidos'] = simulacion['Leads Obtenidos'].apply(lambda x: max(0, x))
    
    # Simular tasa de conversión y matrículas
    tasa_conversion_base = simulacion['Objetivo Matrículas'] / simulacion['Objetivo Leads']
    simulacion['Tasa Conversión Real'] = tasa_conversion_base * factor_conversion
    simulacion['Tasa Conversión Real'] = simulacion['Tasa Conversión Real'].apply(lambda x: min(max(0, x), 1))
    
    # Calcular matrículas obtenidas
    simulacion['Matrículas Obtenidas'] = (simulacion['Leads Obtenidos'] * simulacion['Tasa Conversión Real']).round(0)
    
    # Calcular métricas de rendimiento
    simulacion['CPA Real'] = np.where(
        simulacion['Matrículas Obtenidas'] > 0,
        simulacion['Presupuesto Asignado (USD)'] / simulacion['Matrículas Obtenidas'],
        float('inf')
    )
    
    simulacion['CPL Real'] = np.where(
        simulacion['Leads Obtenidos'] > 0,
        simulacion['Presupuesto Asignado (USD)'] / simulacion['Leads Obtenidos'],
        float('inf')
    )
    
    # Calcular desviaciones respecto a objetivos
    simulacion['% Desviación Leads'] = np.where(
        simulacion['Objetivo Leads'] > 0,
        (simulacion['Leads Obtenidos'] - simulacion['Objetivo Leads']) / simulacion['Objetivo Leads'] * 100,
        0
    )
    
    simulacion['% Desviación Matrículas'] = np.where(
        simulacion['Objetivo Matrículas'] > 0,
        (simulacion['Matrículas Obtenidas'] - simulacion['Objetivo Matrículas']) / simulacion['Objetivo Matrículas'] * 100,
        0
    )
    
    return simulacion


if __name__ == "__main__":
    # Ejemplo de uso
    from cargar_datos import cargar_datos_crm, cargar_datos_planificacion
    from analizar_rendimiento import calcular_metricas_rendimiento
    
    # Cargar datos históricos
    print("Cargando datos históricos...")
    datos_crm = cargar_datos_crm("../datos/leads_matriculas_reales.csv")
    
    # Calcular métricas de rendimiento histórico
    print("Calculando métricas de rendimiento...")
    metricas_historicas = calcular_metricas_rendimiento(datos_crm)
    
    # Calcular asignación óptima de presupuesto
    print("Calculando presupuesto óptimo...")
    presupuesto_total = 50000  # USD
    objetivo_matriculas = 200
    presupuesto_optimo = calcular_presupuesto_optimo(
        metricas_historicas, 
        presupuesto_total,
        objetivo_matriculas
    )
    
    print("\nAsignación óptima de presupuesto:")
    print(presupuesto_optimo)
    
    # Generar planificación quincenal
    print("\nGenerando planificación quincenal...")
    fecha_inicio = datetime.now() + timedelta(days=7)  # Iniciar en una semana
    planificacion = generar_planificacion_quincenal(
        presupuesto_optimo,
        fecha_inicio=fecha_inicio
    )
    
    print(f"Planificación generada para {len(planificacion)} días.")
    
    # Exportar planificación
    ruta_archivo = "../datos/planificacion_quincenal.csv"
    exportar_planificacion(planificacion, ruta_archivo)
    print(f"Planificación exportada a {ruta_archivo}")
    
    # Simular resultados
    print("\nSimulando resultados de la campaña...")
    resultados_simulados = simular_resultados_campaña(planificacion)
    
    # Mostrar resumen
    resumen = resultados_simulados.groupby(['Marca', 'Canal']).agg({
        'Presupuesto Asignado (USD)': 'sum',
        'Objetivo Leads': 'sum',
        'Leads Obtenidos': 'sum',
        'Objetivo Matrículas': 'sum',
        'Matrículas Obtenidas': 'sum'
    }).reset_index()
    
    print("\nResumen de resultados simulados:")
    print(resumen) 