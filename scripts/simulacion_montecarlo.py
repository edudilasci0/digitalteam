"""
Módulo para realizar simulaciones Monte Carlo que permiten estimar el rango de resultados
posibles bajo incertidumbre en los parámetros de rendimiento de campañas.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


def simular_distribucion_leads(cpl_medio, presupuesto, n_simulaciones=1000, 
                              desviacion_cpl=0.2, factor_forma=3):
    """
    Simula la distribución de leads generados dado un CPL medio y un presupuesto,
    considerando la variabilidad del CPL.
    
    Args:
        cpl_medio (float): CPL medio esperado.
        presupuesto (float): Presupuesto asignado.
        n_simulaciones (int): Número de simulaciones a realizar.
        desviacion_cpl (float): Desviación relativa del CPL (como fracción del CPL medio).
        factor_forma (float): Factor de forma para la distribución gamma.
        
    Returns:
        numpy.array: Array con las simulaciones de leads generados.
    """
    # Parámetros para la distribución gamma del CPL
    # Usamos gamma porque CPL no puede ser negativo y suele tener asimetría positiva
    escala = cpl_medio / factor_forma
    forma = factor_forma
    
    # Simular CPL siguiendo una distribución gamma
    cpls_simulados = np.random.gamma(shape=forma, scale=escala, size=n_simulaciones)
    
    # Simular leads generados (presupuesto / CPL)
    leads_simulados = presupuesto / cpls_simulados
    
    return leads_simulados


def simular_distribucion_conversion(leads, tasa_conversion_media, n_simulaciones=1000, 
                                   desviacion_tasa=0.1):
    """
    Simula la distribución de matrículas generadas dado un número de leads y una tasa de conversión.
    
    Args:
        leads (float): Número de leads.
        tasa_conversion_media (float): Tasa de conversión media esperada (entre 0 y 1).
        n_simulaciones (int): Número de simulaciones a realizar.
        desviacion_tasa (float): Desviación de la tasa de conversión (como fracción de la tasa media).
        
    Returns:
        numpy.array: Array con las simulaciones de matrículas generadas.
    """
    # Parámetros para la distribución beta de la tasa de conversión
    # Usamos beta porque la tasa de conversión debe estar entre 0 y 1
    varianza = (desviacion_tasa * tasa_conversion_media) ** 2
    
    # Calcular parámetros alfa y beta
    if varianza >= tasa_conversion_media * (1 - tasa_conversion_media):
        # Ajustar varianza si es demasiado grande
        varianza = tasa_conversion_media * (1 - tasa_conversion_media) * 0.9
        
    media_x_media_menos_media_al_cuadrado_menos_varianza = (
        tasa_conversion_media * (1 - tasa_conversion_media) - varianza)
    
    alfa = tasa_conversion_media * (
        tasa_conversion_media * (1 - tasa_conversion_media) / varianza - 1)
    beta = (1 - tasa_conversion_media) * (
        tasa_conversion_media * (1 - tasa_conversion_media) / varianza - 1)
    
    # Ajustar si los parámetros son demasiado pequeños
    alfa = max(alfa, 0.5)
    beta = max(beta, 0.5)
    
    # Simular tasas de conversión siguiendo una distribución beta
    tasas_simuladas = np.random.beta(a=alfa, b=beta, size=n_simulaciones)
    
    # Simular matrículas generadas (leads * tasa_conversion)
    matriculas_simuladas = leads * tasas_simuladas
    
    return matriculas_simuladas


def simular_campana_montecarlo(datos_canal, n_simulaciones=1000):
    """
    Realiza una simulación Monte Carlo completa para un canal específico.
    
    Args:
        datos_canal (pandas.Series): Serie con los datos del canal a simular.
        n_simulaciones (int): Número de simulaciones a realizar.
        
    Returns:
        dict: Diccionario con resultados de la simulación y estadísticas.
    """
    # Extraer datos relevantes
    presupuesto = datos_canal['Presupuesto Asignado (USD)']
    cpl_esperado = datos_canal['CPL Esperado (USD)']
    tasa_conversion = datos_canal['Tasa de Conversión (%)'] / 100
    
    # Parámetros de variabilidad (podrían ajustarse según datos históricos)
    desviacion_cpl = 0.25  # 25% de variabilidad en CPL
    desviacion_tasa = 0.20  # 20% de variabilidad en tasa de conversión
    
    # Simular leads generados
    leads_simulados = simular_distribucion_leads(
        cpl_esperado, 
        presupuesto, 
        n_simulaciones, 
        desviacion_cpl
    )
    
    # Para cada valor simulado de leads, simular matrículas
    matriculas_simuladas = np.zeros(n_simulaciones)
    cpa_simulado = np.zeros(n_simulaciones)
    
    for i in range(n_simulaciones):
        # Simular conversiones con una distribución binomial
        # La binomial es apropiada para eventos de éxito/fracaso discretos
        matriculas_simuladas[i] = np.random.binomial(
            n=int(leads_simulados[i]), 
            p=tasa_conversion
        )
        
        # Calcular CPA simulado
        cpa_simulado[i] = presupuesto / matriculas_simuladas[i] if matriculas_simuladas[i] > 0 else np.inf
    
    # Filtrar valores infinitos para los cálculos estadísticos
    cpa_finito = cpa_simulado[np.isfinite(cpa_simulado)]
    
    # Calcular estadísticas
    resultados = {
        'Leads': {
            'Media': np.mean(leads_simulados),
            'Mediana': np.median(leads_simulados),
            'Desviación Estándar': np.std(leads_simulados),
            'Mínimo': np.min(leads_simulados),
            'Máximo': np.max(leads_simulados),
            'Percentil 10': np.percentile(leads_simulados, 10),
            'Percentil 90': np.percentile(leads_simulados, 90),
            'Simulaciones': leads_simulados
        },
        'Matrículas': {
            'Media': np.mean(matriculas_simuladas),
            'Mediana': np.median(matriculas_simuladas),
            'Desviación Estándar': np.std(matriculas_simuladas),
            'Mínimo': np.min(matriculas_simuladas),
            'Máximo': np.max(matriculas_simuladas),
            'Percentil 10': np.percentile(matriculas_simuladas, 10),
            'Percentil 90': np.percentile(matriculas_simuladas, 90),
            'Simulaciones': matriculas_simuladas
        },
        'CPA': {
            'Media': np.mean(cpa_finito) if len(cpa_finito) > 0 else np.inf,
            'Mediana': np.median(cpa_finito) if len(cpa_finito) > 0 else np.inf,
            'Desviación Estándar': np.std(cpa_finito) if len(cpa_finito) > 0 else np.inf,
            'Mínimo': np.min(cpa_finito) if len(cpa_finito) > 0 else np.inf,
            'Máximo': np.max(cpa_finito) if len(cpa_finito) > 0 else np.inf,
            'Percentil 10': np.percentile(cpa_finito, 10) if len(cpa_finito) > 0 else np.inf,
            'Percentil 90': np.percentile(cpa_finito, 90) if len(cpa_finito) > 0 else np.inf,
            'Simulaciones': cpa_simulado
        },
        'Probabilidad 0 Matrículas': np.mean(matriculas_simuladas == 0) * 100
    }
    
    return resultados


def simular_asignacion_presupuesto(df_canales, presupuesto_total, 
                                 n_simulaciones=1000, semilla=None):
    """
    Simula diferentes asignaciones de presupuesto y su impacto en matrículas totales.
    
    Args:
        df_canales (pandas.DataFrame): DataFrame con datos de canales.
        presupuesto_total (float): Presupuesto total disponible.
        n_simulaciones (int): Número de simulaciones por asignación.
        semilla (int, optional): Semilla para reproducibilidad.
        
    Returns:
        pandas.DataFrame: DataFrame con resultados de simulaciones.
    """
    if semilla is not None:
        np.random.seed(semilla)
    
    # Generar diferentes asignaciones de presupuesto
    n_canales = len(df_canales)
    n_asignaciones = 50  # Número de asignaciones a probar
    
    resultados = []
    
    for i in range(n_asignaciones):
        # Generar pesos aleatorios para distribución de presupuesto
        pesos = np.random.dirichlet(np.ones(n_canales))
        
        # Asignar presupuesto según los pesos
        presupuesto_asignado = pesos * presupuesto_total
        
        # Simular resultados para cada canal con esta asignación
        matriculas_totales_sim = np.zeros(n_simulaciones)
        
        for j, (idx, canal) in enumerate(df_canales.iterrows()):
            # Crear copia de los datos del canal con el nuevo presupuesto
            canal_modificado = canal.copy()
            canal_modificado['Presupuesto Asignado (USD)'] = presupuesto_asignado[j]
            
            # Simular resultados para este canal
            resultados_canal = simular_campana_montecarlo(canal_modificado, n_simulaciones)
            
            # Agregar matrículas simuladas al total
            matriculas_totales_sim += resultados_canal['Matrículas']['Simulaciones']
        
        # Calcular estadísticas de esta asignación
        resultados.append({
            'ID Asignación': i + 1,
            'Matrículas Media': np.mean(matriculas_totales_sim),
            'Matrículas Mediana': np.median(matriculas_totales_sim),
            'Matrículas Desv. Estándar': np.std(matriculas_totales_sim),
            'Matrículas P10': np.percentile(matriculas_totales_sim, 10),
            'Matrículas P90': np.percentile(matriculas_totales_sim, 90),
            'CPA Medio': presupuesto_total / np.mean(matriculas_totales_sim),
            'Distribución': dict(zip(df_canales['Canal'].values, (pesos * 100).round(1))),
            'Simulaciones': matriculas_totales_sim
        })
    
    # Convertir a DataFrame y ordenar por mediana de matrículas
    df_resultados = pd.DataFrame(resultados).sort_values('Matrículas Mediana', ascending=False)
    
    return df_resultados


def visualizar_resultados_montecarlo(resultados_simulacion, nombre_canal, directorio=None):
    """
    Genera visualizaciones de los resultados de la simulación Monte Carlo.
    
    Args:
        resultados_simulacion (dict): Diccionario con resultados de la simulación.
        nombre_canal (str): Nombre del canal para los títulos.
        directorio (str, optional): Directorio donde guardar las visualizaciones.
        
    Returns:
        dict: Diccionario con rutas de archivos generados.
    """
    if directorio is None:
        directorio = '../salidas'
    
    archivos = {}
    
    # Configurar estilo de visualización
    sns.set_style('whitegrid')
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12
    
    # 1. Distribución de leads
    plt.figure(figsize=(12, 6))
    sns.histplot(resultados_simulacion['Leads']['Simulaciones'], kde=True, color='blue')
    plt.axvline(resultados_simulacion['Leads']['Media'], color='red', linestyle='--', label=f"Media: {resultados_simulacion['Leads']['Media']:.1f}")
    plt.axvline(resultados_simulacion['Leads']['Percentil 10'], color='green', linestyle='--', label=f"P10: {resultados_simulacion['Leads']['Percentil 10']:.1f}")
    plt.axvline(resultados_simulacion['Leads']['Percentil 90'], color='orange', linestyle='--', label=f"P90: {resultados_simulacion['Leads']['Percentil 90']:.1f}")
    
    plt.title(f'Distribución Simulada de Leads - {nombre_canal}')
    plt.xlabel('Número de Leads')
    plt.ylabel('Frecuencia')
    plt.legend()
    
    ruta_archivo = f"{directorio}/montecarlo_leads_{nombre_canal.replace(' ', '_')}.png"
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos['leads'] = ruta_archivo
    
    # 2. Distribución de matrículas
    plt.figure(figsize=(12, 6))
    sns.histplot(resultados_simulacion['Matrículas']['Simulaciones'], kde=True, color='green', discrete=True)
    plt.axvline(resultados_simulacion['Matrículas']['Media'], color='red', linestyle='--', label=f"Media: {resultados_simulacion['Matrículas']['Media']:.1f}")
    plt.axvline(resultados_simulacion['Matrículas']['Percentil 10'], color='blue', linestyle='--', label=f"P10: {resultados_simulacion['Matrículas']['Percentil 10']:.1f}")
    plt.axvline(resultados_simulacion['Matrículas']['Percentil 90'], color='orange', linestyle='--', label=f"P90: {resultados_simulacion['Matrículas']['Percentil 90']:.1f}")
    
    plt.title(f'Distribución Simulada de Matrículas - {nombre_canal}')
    plt.xlabel('Número de Matrículas')
    plt.ylabel('Frecuencia')
    plt.legend()
    
    ruta_archivo = f"{directorio}/montecarlo_matriculas_{nombre_canal.replace(' ', '_')}.png"
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos['matriculas'] = ruta_archivo
    
    # 3. Distribución de CPA (excluir infinitos)
    cpa_finito = resultados_simulacion['CPA']['Simulaciones'][np.isfinite(resultados_simulacion['CPA']['Simulaciones'])]
    
    if len(cpa_finito) > 0:
        plt.figure(figsize=(12, 6))
        sns.histplot(cpa_finito, kde=True, color='purple')
        plt.axvline(resultados_simulacion['CPA']['Media'], color='red', linestyle='--', label=f"Media: {resultados_simulacion['CPA']['Media']:.1f}")
        plt.axvline(resultados_simulacion['CPA']['Percentil 10'], color='blue', linestyle='--', label=f"P10: {resultados_simulacion['CPA']['Percentil 10']:.1f}")
        plt.axvline(resultados_simulacion['CPA']['Percentil 90'], color='orange', linestyle='--', label=f"P90: {resultados_simulacion['CPA']['Percentil 90']:.1f}")
        
        plt.title(f'Distribución Simulada de CPA - {nombre_canal}')
        plt.xlabel('CPA (USD)')
        plt.ylabel('Frecuencia')
        plt.legend()
        
        ruta_archivo = f"{directorio}/montecarlo_cpa_{nombre_canal.replace(' ', '_')}.png"
        plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
        plt.close()
        
        archivos['cpa'] = ruta_archivo
    
    return archivos


def visualizar_comparacion_asignaciones(df_simulaciones, top_n=5, directorio=None):
    """
    Genera visualizaciones comparando diferentes asignaciones de presupuesto.
    
    Args:
        df_simulaciones (pandas.DataFrame): DataFrame con resultados de simulaciones.
        top_n (int): Número de mejores asignaciones a mostrar.
        directorio (str, optional): Directorio donde guardar las visualizaciones.
        
    Returns:
        dict: Diccionario con rutas de archivos generados.
    """
    if directorio is None:
        directorio = '../salidas'
    
    archivos = {}
    
    # Filtrar top N asignaciones
    top_asignaciones = df_simulaciones.head(top_n).copy()
    
    # 1. Boxplot de matrículas por asignación
    plt.figure(figsize=(14, 8))
    data_plot = []
    labels = []
    
    for i, row in top_asignaciones.iterrows():
        data_plot.append(row['Simulaciones'])
        labels.append(f"Asig. {row['ID Asignación']}")
    
    plt.boxplot(data_plot, labels=labels, patch_artist=True)
    plt.title('Comparación de Distribuciones de Matrículas por Asignación de Presupuesto')
    plt.xlabel('Asignación')
    plt.ylabel('Matrículas Totales')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    ruta_archivo = f"{directorio}/comparacion_asignaciones_boxplot.png"
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos['boxplot'] = ruta_archivo
    
    # 2. Gráfico de barras apiladas con distribución de presupuesto
    plt.figure(figsize=(14, 8))
    
    # Convertir diccionarios de distribución a DataFrame
    datos_distribucion = []
    for i, row in top_asignaciones.iterrows():
        for canal, porcentaje in row['Distribución'].items():
            datos_distribucion.append({
                'ID Asignación': f"Asig. {row['ID Asignación']}",
                'Canal': canal,
                'Porcentaje': porcentaje
            })
    
    df_dist = pd.DataFrame(datos_distribucion)
    
    # Crear gráfico de barras apiladas
    df_pivot = df_dist.pivot(index='ID Asignación', columns='Canal', values='Porcentaje')
    df_pivot.plot(kind='bar', stacked=True, figsize=(14, 8), colormap='tab20')
    
    plt.title('Distribución de Presupuesto por Canal en las Mejores Asignaciones')
    plt.xlabel('Asignación')
    plt.ylabel('Porcentaje del Presupuesto (%)')
    plt.legend(title='Canal', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    ruta_archivo = f"{directorio}/comparacion_asignaciones_distribucion.png"
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos['distribucion'] = ruta_archivo
    
    # 3. Gráfico de dispersión: Media vs. Desviación Estándar
    plt.figure(figsize=(12, 8))
    
    # Todas las asignaciones
    plt.scatter(
        df_simulaciones['Matrículas Media'],
        df_simulaciones['Matrículas Desv. Estándar'],
        alpha=0.6,
        color='gray',
        label='Todas las asignaciones'
    )
    
    # Top asignaciones
    plt.scatter(
        top_asignaciones['Matrículas Media'],
        top_asignaciones['Matrículas Desv. Estándar'],
        alpha=0.9,
        color='red',
        s=100,
        label='Top 5 asignaciones'
    )
    
    # Etiquetar top asignaciones
    for i, row in top_asignaciones.iterrows():
        plt.annotate(
            f"Asig. {row['ID Asignación']}",
            (row['Matrículas Media'], row['Matrículas Desv. Estándar']),
            textcoords="offset points",
            xytext=(0, 10),
            ha='center'
        )
    
    plt.title('Relación entre Media y Desviación Estándar de Matrículas')
    plt.xlabel('Media de Matrículas')
    plt.ylabel('Desviación Estándar')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    ruta_archivo = f"{directorio}/comparacion_asignaciones_dispersion.png"
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos['dispersion'] = ruta_archivo
    
    return archivos


def generar_reporte_montecarlo(df_prediccion, presupuesto_total, 
                             n_simulaciones=1000, directorio=None):
    """
    Genera un reporte completo de simulación Monte Carlo para optimización de presupuesto.
    
    Args:
        df_prediccion (pandas.DataFrame): DataFrame con predicción de matrículas.
        presupuesto_total (float): Presupuesto total disponible.
        n_simulaciones (int): Número de simulaciones por escenario.
        directorio (str, optional): Directorio donde guardar el reporte.
        
    Returns:
        dict: Diccionario con resultados y rutas de archivos generados.
    """
    # Crear directorio si no existe
    if directorio is None:
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        directorio = f'../salidas/{fecha_actual}'
        
    import os
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    
    # Filtrar solo campañas activas
    df_activas = df_prediccion[df_prediccion['Estado Convocatoria'] != 'Finalizada'].copy()
    
    if df_activas.empty:
        return {'error': 'No hay campañas activas para simular'}
    
    # 1. Simular cada canal individualmente
    resultados_canales = {}
    archivos_visualizacion = {}
    
    # Para cada canal, ejecutar simulación Monte Carlo
    for idx, canal in df_activas.iterrows():
        nombre_canal = f"{canal['Marca']}_{canal['Canal']}"
        
        # Ejecutar simulación
        resultados = simular_campana_montecarlo(canal, n_simulaciones)
        resultados_canales[nombre_canal] = resultados
        
        # Generar visualizaciones
        archivos = visualizar_resultados_montecarlo(resultados, nombre_canal, directorio)
        archivos_visualizacion[nombre_canal] = archivos
    
    # 2. Simular diferentes asignaciones de presupuesto
    simulaciones_asignacion = simular_asignacion_presupuesto(df_activas, presupuesto_total, n_simulaciones)
    
    # Visualizar comparación de asignaciones
    archivos_comparacion = visualizar_comparacion_asignaciones(simulaciones_asignacion, top_n=5, directorio=directorio)
    
    # 3. Preparar resumen de resultados por canal
    resumen_canales = []
    
    for nombre_canal, resultados in resultados_canales.items():
        canal_info = {
            'Canal': nombre_canal,
            'Leads - Media': resultados['Leads']['Media'],
            'Leads - P10-P90': f"{resultados['Leads']['Percentil 10']:.1f} - {resultados['Leads']['Percentil 90']:.1f}",
            'Matrículas - Media': resultados['Matrículas']['Media'],
            'Matrículas - P10-P90': f"{resultados['Matrículas']['Percentil 10']:.1f} - {resultados['Matrículas']['Percentil 90']:.1f}",
            'CPA - Media': resultados['CPA']['Media'],
            'CPA - P10-P90': f"{resultados['CPA']['Percentil 10']:.1f} - {resultados['CPA']['Percentil 90']:.1f}",
            'Prob. 0 Matrículas (%)': resultados['Probabilidad 0 Matrículas']
        }
        resumen_canales.append(canal_info)
    
    df_resumen = pd.DataFrame(resumen_canales)
    
    # 4. Preparar resumen de mejores asignaciones
    top_asignaciones = simulaciones_asignacion.head(5)[
        ['ID Asignación', 'Matrículas Media', 'Matrículas P10', 'Matrículas P90', 
         'CPA Medio', 'Distribución']
    ].copy()
    
    # 5. Generar archivo Excel con resultados
    ruta_excel = f"{directorio}/reporte_montecarlo.xlsx"
    
    # Crear Excel
    writer = pd.ExcelWriter(ruta_excel, engine='xlsxwriter')
    
    # Guardar resumen de canales
    df_resumen.to_excel(writer, sheet_name='Resumen por Canal', index=False)
    
    # Guardar mejores asignaciones
    # Convertir columna de distribución a formato legible
    top_asignaciones['Distribución'] = top_asignaciones['Distribución'].apply(
        lambda x: ', '.join([f"{canal}: {porcentaje}%" for canal, porcentaje in x.items()])
    )
    top_asignaciones.to_excel(writer, sheet_name='Mejores Asignaciones', index=False)
    
    # Guardar todas las asignaciones simuladas
    simulaciones_exportar = simulaciones_asignacion.drop(columns=['Simulaciones']).copy()
    simulaciones_exportar['Distribución'] = simulaciones_exportar['Distribución'].apply(
        lambda x: ', '.join([f"{canal}: {porcentaje}%" for canal, porcentaje in x.items()])
    )
    simulaciones_exportar.to_excel(writer, sheet_name='Todas las Asignaciones', index=False)
    
    # Guardar Excel
    writer.close()
    
    # 6. Retornar resultados
    return {
        'resumen_canales': df_resumen,
        'mejores_asignaciones': top_asignaciones,
        'todas_asignaciones': simulaciones_asignacion,
        'archivos': {
            'excel': ruta_excel,
            'visualizaciones': archivos_visualizacion,
            'comparaciones': archivos_comparacion
        }
    }


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
        
        # Simular para un presupuesto total de 50,000 USD
        presupuesto_total = 50000
        
        print("Generando reporte de simulación Monte Carlo...")
        reporte = generar_reporte_montecarlo(
            prediccion, 
            presupuesto_total,
            n_simulaciones=500  # Reducido para ejemplo, en producción usar 1000+
        )
        
        print(f"Reporte generado en: {reporte['archivos']['excel']}")
        
        print("\nResumen por Canal:")
        print(reporte['resumen_canales'])
        
        print("\nMejores Asignaciones de Presupuesto:")
        print(reporte['mejores_asignaciones'])
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 