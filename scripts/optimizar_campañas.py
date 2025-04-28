"""
Módulo para optimizar campañas de marketing mediante la aplicación de algoritmos
y recomendaciones basadas en los datos históricos.
"""
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from datetime import datetime, timedelta


def optimizar_asignacion_presupuesto(datos_historicos, presupuesto_total, restricciones=None):
    """
    Optimiza la asignación de presupuesto entre canales utilizando un algoritmo de optimización.
    
    Args:
        datos_historicos (pandas.DataFrame): DataFrame con datos históricos de rendimiento.
        presupuesto_total (float): Presupuesto total disponible para asignar.
        restricciones (dict, opcional): Diccionario con restricciones para la optimización.
        
    Returns:
        pandas.DataFrame: DataFrame con la asignación optimizada de presupuesto.
    """
    # Verificar que se tengan las columnas necesarias
    columnas_requeridas = ['Marca', 'Canal', 'Leads', 'Matrículas', 'Presupuesto Asignado (USD)']
    for col in columnas_requeridas:
        if col not in datos_historicos.columns:
            raise ValueError(f"El DataFrame debe contener la columna '{col}'")
    
    # Agrupar datos por marca y canal
    df_agrupado = datos_historicos.groupby(['Marca', 'Canal']).agg({
        'Leads': 'sum',
        'Matrículas': 'sum',
        'Presupuesto Asignado (USD)': 'sum'
    }).reset_index()
    
    # Calcular CPA y eficiencia
    df_agrupado['CPA'] = np.where(
        df_agrupado['Matrículas'] > 0,
        df_agrupado['Presupuesto Asignado (USD)'] / df_agrupado['Matrículas'],
        float('inf')
    )
    
    df_agrupado['Eficiencia'] = np.where(
        df_agrupado['CPA'] > 0,
        1 / df_agrupado['CPA'],
        0
    )
    
    # Eliminar canales con eficiencia cero
    df_optimizacion = df_agrupado[df_agrupado['Eficiencia'] > 0].copy()
    
    if df_optimizacion.empty:
        raise ValueError("No hay canales con eficiencia positiva para optimizar")
    
    # Definir función objetivo (maximizar matrículas)
    def objetivo(x):
        return -np.sum(x * df_optimizacion['Eficiencia'])
    
    # Restricción: la suma de presupuestos debe ser igual al presupuesto total
    def restriccion_presupuesto(x):
        return np.sum(x) - presupuesto_total
    
    # Definir restricciones
    constraints = [{'type': 'eq', 'fun': restriccion_presupuesto}]
    
    # Agregar restricciones personalizadas si se proporcionan
    if restricciones is not None:
        # Restricciones de presupuesto mínimo por canal
        if 'min_presupuesto' in restricciones:
            min_presupuesto = restricciones['min_presupuesto']
            bounds = [(min_presupuesto, None) for _ in range(len(df_optimizacion))]
        else:
            bounds = [(0, None) for _ in range(len(df_optimizacion))]
        
        # Restricciones de presupuesto máximo por canal
        if 'max_presupuesto' in restricciones:
            max_presupuesto = restricciones['max_presupuesto']
            bounds = [(b[0], max_presupuesto) for b in bounds]
    else:
        bounds = [(0, None) for _ in range(len(df_optimizacion))]
    
    # Valor inicial: distribución proporcional a la eficiencia
    x0 = df_optimizacion['Eficiencia'] / df_optimizacion['Eficiencia'].sum() * presupuesto_total
    
    # Ejecutar optimización
    resultado = minimize(
        objetivo,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    if not resultado.success:
        raise RuntimeError(f"La optimización no convergió: {resultado.message}")
    
    # Asignar presupuesto optimizado
    df_optimizacion['Presupuesto Optimizado'] = resultado.x
    
    # Calcular objetivos basados en el presupuesto optimizado
    df_optimizacion['Matrículas Esperadas'] = df_optimizacion['Presupuesto Optimizado'] * df_optimizacion['Eficiencia']
    
    # Calcular leads esperados basados en tasa de conversión histórica
    df_optimizacion['Tasa Conversión'] = np.where(
        df_optimizacion['Leads'] > 0,
        df_optimizacion['Matrículas'] / df_optimizacion['Leads'],
        0
    )
    
    df_optimizacion['Leads Esperados'] = np.where(
        df_optimizacion['Tasa Conversión'] > 0,
        df_optimizacion['Matrículas Esperadas'] / df_optimizacion['Tasa Conversión'],
        0
    )
    
    # Redondear valores
    df_optimizacion['Presupuesto Optimizado'] = df_optimizacion['Presupuesto Optimizado'].round(2)
    df_optimizacion['Matrículas Esperadas'] = df_optimizacion['Matrículas Esperadas'].round(0)
    df_optimizacion['Leads Esperados'] = df_optimizacion['Leads Esperados'].round(0)
    
    # Seleccionar columnas para el resultado
    resultado_final = df_optimizacion[['Marca', 'Canal', 'Presupuesto Optimizado', 
                                     'Leads Esperados', 'Matrículas Esperadas']]
    
    # Renombrar columnas para consistencia
    resultado_final = resultado_final.rename(columns={
        'Presupuesto Optimizado': 'Presupuesto Asignado (USD)',
        'Leads Esperados': 'Objetivo Leads',
        'Matrículas Esperadas': 'Objetivo Matrículas'
    })
    
    return resultado_final


def generar_recomendaciones_optimizacion(datos_historicos, datos_optimizados):
    """
    Genera recomendaciones para optimizar las campañas basadas en datos históricos.
    
    Args:
        datos_historicos (pandas.DataFrame): DataFrame con datos históricos de rendimiento.
        datos_optimizados (pandas.DataFrame): DataFrame con asignación optimizada de presupuesto.
        
    Returns:
        dict: Diccionario con recomendaciones y justificaciones.
    """
    recomendaciones = {
        'reasignacion_presupuesto': [],
        'mejora_conversion': [],
        'canales_eficientes': [],
        'canales_ineficientes': []
    }
    
    # Verificar que ambos DataFrames contengan las columnas necesarias
    historico_cols = ['Marca', 'Canal', 'Presupuesto Asignado (USD)', 'Leads', 'Matrículas']
    optimizado_cols = ['Marca', 'Canal', 'Presupuesto Asignado (USD)', 'Objetivo Leads', 'Objetivo Matrículas']
    
    for cols, df, nombre in [(historico_cols, datos_historicos, 'datos_historicos'), 
                            (optimizado_cols, datos_optimizados, 'datos_optimizados')]:
        for col in cols:
            if col not in df.columns:
                raise ValueError(f"El DataFrame {nombre} debe contener la columna '{col}'")
    
    # Preparar datos para comparación
    hist_agrupado = datos_historicos.groupby(['Marca', 'Canal']).agg({
        'Presupuesto Asignado (USD)': 'sum',
        'Leads': 'sum',
        'Matrículas': 'sum'
    }).reset_index()
    
    # Agregar métricas de eficiencia
    hist_agrupado['CPA'] = np.where(
        hist_agrupado['Matrículas'] > 0,
        hist_agrupado['Presupuesto Asignado (USD)'] / hist_agrupado['Matrículas'],
        float('inf')
    )
    
    hist_agrupado['Tasa Conversión'] = np.where(
        hist_agrupado['Leads'] > 0,
        hist_agrupado['Matrículas'] / hist_agrupado['Leads'],
        0
    )
    
    # Unir datos históricos con optimizados
    comparativa = pd.merge(
        hist_agrupado,
        datos_optimizados,
        on=['Marca', 'Canal'],
        how='outer',
        suffixes=('_Histórico', '_Optimizado')
    )
    
    # Calcular diferencias
    comparativa['Diferencia Presupuesto'] = comparativa['Presupuesto Asignado (USD)_Optimizado'] - \
                                         comparativa['Presupuesto Asignado (USD)_Histórico']
    
    comparativa['% Cambio Presupuesto'] = np.where(
        comparativa['Presupuesto Asignado (USD)_Histórico'] > 0,
        comparativa['Diferencia Presupuesto'] / comparativa['Presupuesto Asignado (USD)_Histórico'] * 100,
        0
    )
    
    # 1. Recomendaciones de reasignación de presupuesto
    aumentos = comparativa[comparativa['% Cambio Presupuesto'] > 20].sort_values('% Cambio Presupuesto', ascending=False)
    reducciones = comparativa[comparativa['% Cambio Presupuesto'] < -20].sort_values('% Cambio Presupuesto')
    
    for _, row in aumentos.iterrows():
        recomendaciones['reasignacion_presupuesto'].append({
            'tipo': 'aumento',
            'marca': row['Marca'],
            'canal': row['Canal'],
            'cambio_porcentual': row['% Cambio Presupuesto'],
            'cambio_absoluto': row['Diferencia Presupuesto'],
            'justificacion': f"El canal {row['Canal']} para la marca {row['Marca']} tiene un CPA histórico de {row['CPA']:.2f}, "
                          f"lo que indica una buena eficiencia. Aumentar el presupuesto podría generar un mayor retorno."
        })
    
    for _, row in reducciones.iterrows():
        recomendaciones['reasignacion_presupuesto'].append({
            'tipo': 'reduccion',
            'marca': row['Marca'],
            'canal': row['Canal'],
            'cambio_porcentual': row['% Cambio Presupuesto'],
            'cambio_absoluto': row['Diferencia Presupuesto'],
            'justificacion': f"El canal {row['Canal']} para la marca {row['Marca']} tiene un CPA histórico de {row['CPA']:.2f}, "
                          f"lo que indica una baja eficiencia. Reducir el presupuesto permitiría reasignar recursos a canales más eficientes."
        })
    
    # 2. Recomendaciones de mejora de conversión
    baja_conversion = hist_agrupado[hist_agrupado['Tasa Conversión'] < hist_agrupado['Tasa Conversión'].quantile(0.25)]
    
    for _, row in baja_conversion.iterrows():
        recomendaciones['mejora_conversion'].append({
            'marca': row['Marca'],
            'canal': row['Canal'],
            'tasa_conversion': row['Tasa Conversión'],
            'justificacion': f"La tasa de conversión para {row['Canal']} en {row['Marca']} es de {row['Tasa Conversión']:.2%}, "
                          f"por debajo del percentil 25. Revisar la calidad de los leads y el proceso de conversión podría mejorar los resultados."
        })
    
    # 3. Identificar canales más eficientes
    canales_eficientes = hist_agrupado.sort_values('CPA').head(3)
    
    for _, row in canales_eficientes.iterrows():
        recomendaciones['canales_eficientes'].append({
            'marca': row['Marca'],
            'canal': row['Canal'],
            'cpa': row['CPA'],
            'justificacion': f"El canal {row['Canal']} para {row['Marca']} tiene un CPA de {row['CPA']:.2f}, "
                          f"lo que lo convierte en uno de los canales más eficientes. Considerar aumentar la inversión y replicar estrategias."
        })
    
    # 4. Identificar canales menos eficientes
    canales_ineficientes = hist_agrupado[hist_agrupado['CPA'] < float('inf')].sort_values('CPA', ascending=False).head(3)
    
    for _, row in canales_ineficientes.iterrows():
        recomendaciones['canales_ineficientes'].append({
            'marca': row['Marca'],
            'canal': row['Canal'],
            'cpa': row['CPA'],
            'justificacion': f"El canal {row['Canal']} para {row['Marca']} tiene un CPA de {row['CPA']:.2f}, "
                          f"lo que lo hace menos rentable. Evaluar si vale la pena mantener la inversión o rediseñar la estrategia."
        })
    
    return recomendaciones


def aplicar_ajustes_estacionales(optimizacion, factores_estacionales=None):
    """
    Aplica ajustes estacionales al plan de presupuesto optimizado.
    
    Args:
        optimizacion (pandas.DataFrame): DataFrame con asignación optimizada de presupuesto.
        factores_estacionales (dict, opcional): Diccionario con factores de ajuste por mes o periodo.
        
    Returns:
        pandas.DataFrame: DataFrame con presupuesto ajustado por estacionalidad.
    """
    # Si no se proporcionan factores estacionales, utilizar valores predeterminados
    if factores_estacionales is None:
        # Factores de ajuste por mes (ejemplo: mayor inversión en periodos de alta demanda)
        factores_estacionales = {
            1: 0.9,   # Enero
            2: 1.0,   # Febrero
            3: 1.1,   # Marzo
            4: 1.0,   # Abril
            5: 0.9,   # Mayo
            6: 0.8,   # Junio
            7: 0.7,   # Julio
            8: 0.9,   # Agosto
            9: 1.2,   # Septiembre
            10: 1.3,  # Octubre
            11: 1.1,  # Noviembre
            12: 0.8   # Diciembre
        }
    
    # Crear copia para no modificar el original
    ajustado = optimizacion.copy()
    
    # Determinar el mes actual
    mes_actual = datetime.now().month
    
    # Aplicar factor de ajuste para el mes actual
    factor_ajuste = factores_estacionales.get(mes_actual, 1.0)
    
    # Ajustar presupuesto y objetivos
    ajustado['Presupuesto Asignado (USD)'] = ajustado['Presupuesto Asignado (USD)'] * factor_ajuste
    ajustado['Objetivo Leads'] = ajustado['Objetivo Leads'] * factor_ajuste
    ajustado['Objetivo Matrículas'] = ajustado['Objetivo Matrículas'] * factor_ajuste
    
    # Redondear valores
    ajustado['Presupuesto Asignado (USD)'] = ajustado['Presupuesto Asignado (USD)'].round(2)
    ajustado['Objetivo Leads'] = ajustado['Objetivo Leads'].round(0)
    ajustado['Objetivo Matrículas'] = ajustado['Objetivo Matrículas'].round(0)
    
    # Agregar información del ajuste
    ajustado['Factor Estacional'] = factor_ajuste
    ajustado['Mes Aplicado'] = mes_actual
    
    return ajustado


if __name__ == "__main__":
    # Ejemplo de uso
    from cargar_datos import cargar_datos_crm
    from analizar_rendimiento import calcular_metricas_rendimiento
    
    # Cargar datos históricos
    print("Cargando datos históricos...")
    datos_crm = cargar_datos_crm("../datos/leads_matriculas_reales.csv")
    
    # Calcular métricas de rendimiento histórico
    print("Calculando métricas de rendimiento...")
    metricas_historicas = calcular_metricas_rendimiento(datos_crm)
    
    # Definir restricciones para la optimización
    restricciones = {
        'min_presupuesto': 1000,  # Presupuesto mínimo por canal
        'max_presupuesto': 20000  # Presupuesto máximo por canal
    }
    
    # Optimizar asignación de presupuesto
    print("Optimizando asignación de presupuesto...")
    presupuesto_total = 50000  # USD
    presupuesto_optimizado = optimizar_asignacion_presupuesto(
        metricas_historicas, 
        presupuesto_total,
        restricciones
    )
    
    print("\nAsignación optimizada de presupuesto:")
    print(presupuesto_optimizado)
    
    # Aplicar ajustes estacionales
    print("\nAplicando ajustes estacionales...")
    presupuesto_ajustado = aplicar_ajustes_estacionales(presupuesto_optimizado)
    
    print("\nPresupuesto con ajustes estacionales:")
    print(presupuesto_ajustado[['Marca', 'Canal', 'Presupuesto Asignado (USD)', 'Factor Estacional']])
    
    # Generar recomendaciones
    print("\nGenerando recomendaciones...")
    recomendaciones = generar_recomendaciones_optimizacion(metricas_historicas, presupuesto_optimizado)
    
    # Mostrar recomendaciones
    print("\nRecomendaciones de reasignación de presupuesto:")
    for r in recomendaciones['reasignacion_presupuesto']:
        print(f"- {r['tipo'].upper()} para {r['marca']} - {r['canal']}: {r['cambio_porcentual']:.1f}% ({r['cambio_absoluto']:.2f} USD)")
    
    print("\nCanales más eficientes:")
    for r in recomendaciones['canales_eficientes']:
        print(f"- {r['marca']} - {r['canal']}: CPA = {r['cpa']:.2f} USD") 