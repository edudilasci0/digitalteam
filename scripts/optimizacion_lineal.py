"""
Módulo para implementar la optimización de presupuesto mediante programación lineal.
Permite establecer restricciones mínimas y máximas por canal para una asignación óptima.
"""
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt


def optimizar_presupuesto_lineal(df_prediccion, presupuesto_total, 
                                restricciones_canal=None, min_porcentaje=0.05, max_porcentaje=0.4):
    """
    Optimiza la asignación de presupuesto usando programación lineal con restricciones.
    
    Args:
        df_prediccion (pandas.DataFrame): DataFrame con predicción de matrículas.
        presupuesto_total (float): Presupuesto total disponible para asignar.
        restricciones_canal (dict, optional): Diccionario con restricciones específicas por canal.
        min_porcentaje (float): Porcentaje mínimo del presupuesto que debe asignarse a cada canal.
        max_porcentaje (float): Porcentaje máximo del presupuesto que puede asignarse a cada canal.
        
    Returns:
        pandas.DataFrame: DataFrame con la asignación optimizada aplicando programación lineal.
    """
    # Seleccionar solo canales activos (convocatorias aún no finalizadas)
    df_activos = df_prediccion[df_prediccion['Estado Convocatoria'] != 'Finalizada'].copy()
    
    if df_activos.empty:
        return pd.DataFrame({"Mensaje": ["No hay campañas activas para optimizar presupuesto"]})
    
    # Preparar datos para la optimización lineal
    canales = df_activos[['Marca', 'Canal', 'ID Convocatoria']].values
    n_canales = len(canales)
    
    # Calcular coeficiente para la función objetivo (negativo porque queremos maximizar)
    # Usamos el inverso del CPA esperado como coeficiente de eficiencia
    c = -1.0 / df_activos['CPA Esperado (USD)'].values
    
    # Restricción de presupuesto total
    A_eq = np.ones((1, n_canales))
    b_eq = np.array([presupuesto_total])
    
    # Restricciones de límites por canal
    A_ub = np.vstack([
        np.eye(n_canales),      # Para límites máximos
        -np.eye(n_canales)      # Para límites mínimos
    ])
    
    # Establecer límites mínimos y máximos predeterminados
    limites_maximos = np.ones(n_canales) * presupuesto_total * max_porcentaje
    limites_minimos = np.ones(n_canales) * presupuesto_total * min_porcentaje
    
    # Aplicar restricciones específicas si se proporcionan
    if restricciones_canal is not None:
        for i, (marca, canal, id_conv) in enumerate(canales):
            clave = f"{marca}_{canal}_{id_conv}"
            if clave in restricciones_canal:
                restriccion = restricciones_canal[clave]
                if 'min' in restriccion:
                    limites_minimos[i] = restriccion['min']
                if 'max' in restriccion:
                    limites_maximos[i] = restriccion['max']
    
    # Combinar límites para A_ub
    b_ub = np.concatenate([limites_maximos, -limites_minimos])
    
    # Resolver el problema de optimización lineal
    resultado = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, method='highs')
    
    if not resultado.success:
        raise ValueError(f"La optimización no pudo encontrar una solución: {resultado.message}")
    
    # Obtener la asignación óptima
    presupuesto_optimo = resultado.x
    
    # Crear DataFrame con resultados
    df_resultado = df_activos.copy()
    df_resultado['Presupuesto Actual (USD)'] = df_activos['Presupuesto Asignado (USD)']
    df_resultado['Presupuesto Óptimo (USD)'] = presupuesto_optimo
    df_resultado['Cambio Presupuesto (USD)'] = df_resultado['Presupuesto Óptimo (USD)'] - df_resultado['Presupuesto Actual (USD)']
    df_resultado['Cambio Porcentual (%)'] = (df_resultado['Cambio Presupuesto (USD)'] / df_resultado['Presupuesto Actual (USD)']) * 100
    
    # Calcular porcentaje del presupuesto total
    df_resultado['Porcentaje del Presupuesto (%)'] = (df_resultado['Presupuesto Óptimo (USD)'] / presupuesto_total) * 100
    
    # Estimar impacto en matrículas
    ratio_presupuesto = df_resultado['Presupuesto Óptimo (USD)'] / df_resultado['Presupuesto Actual (USD)']
    df_resultado['Matrículas Estimadas Original'] = df_resultado['Matrículas Esperadas']
    
    # Aplicar un modelo de respuesta con elasticidad para estimar el impacto en matrículas
    # Para una aproximación simple, usamos una relación log-lineal
    elasticidad = 0.8  # Valor predeterminado si no tenemos datos específicos
    df_resultado['Matrículas Estimadas Optimizado'] = df_resultado['Matrículas Estimadas Original'] * (ratio_presupuesto ** elasticidad)
    df_resultado['Incremento Matrículas'] = df_resultado['Matrículas Estimadas Optimizado'] - df_resultado['Matrículas Estimadas Original']
    
    # Calcular nuevo CPA esperado
    df_resultado['CPA Optimizado (USD)'] = df_resultado['Presupuesto Óptimo (USD)'] / df_resultado['Matrículas Estimadas Optimizado']
    
    # Organizar y ordenar el resultado
    df_final = df_resultado[[
        'Marca', 'Canal', 'ID Convocatoria', 'Estado Convocatoria',
        'Presupuesto Actual (USD)', 'Presupuesto Óptimo (USD)', 'Cambio Presupuesto (USD)', 'Cambio Porcentual (%)',
        'Porcentaje del Presupuesto (%)',
        'Matrículas Estimadas Original', 'Matrículas Estimadas Optimizado', 'Incremento Matrículas',
        'CPA Esperado (USD)', 'CPA Optimizado (USD)'
    ]].sort_values(by='Cambio Presupuesto (USD)', ascending=False)
    
    return df_final


def analizar_sensibilidad_restricciones(df_prediccion, presupuesto_total, 
                                      rango_min=(0.01, 0.2), rango_max=(0.2, 0.6),
                                      pasos=5):
    """
    Analiza la sensibilidad del modelo de optimización a diferentes niveles de restricciones.
    
    Args:
        df_prediccion (pandas.DataFrame): DataFrame con predicción de matrículas.
        presupuesto_total (float): Presupuesto total disponible para asignar.
        rango_min (tuple): Rango de porcentajes mínimos a probar.
        rango_max (tuple): Rango de porcentajes máximos a probar.
        pasos (int): Número de pasos para el análisis de sensibilidad.
        
    Returns:
        pandas.DataFrame: DataFrame con los resultados del análisis de sensibilidad.
    """
    resultados = []
    
    # Crear rangos de valores para mínimos y máximos
    mins = np.linspace(rango_min[0], rango_min[1], pasos)
    maxs = np.linspace(rango_max[0], rango_max[1], pasos)
    
    # Probar diferentes combinaciones
    for min_porc in mins:
        for max_porc in maxs:
            if min_porc >= max_porc:
                continue  # Ignorar combinaciones inválidas
            
            try:
                # Ejecutar optimización con estos parámetros
                resultado = optimizar_presupuesto_lineal(
                    df_prediccion, 
                    presupuesto_total,
                    min_porcentaje=min_porc,
                    max_porcentaje=max_porc
                )
                
                # Calcular métricas agregadas
                matriculas_totales = resultado['Matrículas Estimadas Optimizado'].sum()
                cpa_promedio = resultado['CPA Optimizado (USD)'].mean()
                diversificacion = len(resultado[resultado['Presupuesto Óptimo (USD)'] > 100])
                
                # Guardar resultados
                resultados.append({
                    'Mínimo (%)': min_porc * 100,
                    'Máximo (%)': max_porc * 100,
                    'Matrículas Totales': matriculas_totales,
                    'CPA Promedio (USD)': cpa_promedio,
                    'Canales Activos': diversificacion,
                    'Concentración (Gini)': calcular_indice_gini(resultado['Presupuesto Óptimo (USD)'])
                })
                
            except Exception as e:
                print(f"Error con min={min_porc}, max={max_porc}: {e}")
    
    return pd.DataFrame(resultados)


def calcular_indice_gini(valores):
    """
    Calcula el índice de Gini para medir la concentración de la distribución.
    
    Args:
        valores (numpy.array): Array con los valores a analizar.
        
    Returns:
        float: Índice de Gini (0=perfecta igualdad, 1=perfecta desigualdad).
    """
    # Ordenar valores
    valores = np.sort(valores)
    n = len(valores)
    
    # Normalizar al total
    valores = valores / np.sum(valores)
    
    # Calcular índice de Gini
    index = np.arange(1, n + 1)
    return np.sum((2 * index - n - 1) * valores) / n


def visualizar_optimizacion_lineal(df_original, df_optimizado):
    """
    Genera visualizaciones comparativas entre la asignación original y la optimizada.
    
    Args:
        df_original (pandas.DataFrame): DataFrame con la asignación original.
        df_optimizado (pandas.DataFrame): DataFrame con la asignación optimizada.
        
    Returns:
        matplotlib.figure.Figure: Figura con las visualizaciones generadas.
    """
    # Crear figura con 2 subgráficos
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Preparar datos para visualización
    marcas = df_optimizado['Marca'].unique()
    colores = plt.cm.Set2(np.linspace(0, 1, len(marcas)))
    color_dict = dict(zip(marcas, colores))
    
    # 1. Comparación de Presupuesto por Canal
    df_comp = df_optimizado.copy()
    df_comp['Canal_Marca'] = df_comp['Canal'] + ' - ' + df_comp['Marca']
    
    # Ordenar por cambio presupuestario
    df_comp = df_comp.sort_values('Cambio Presupuesto (USD)', ascending=True)
    
    # Crear barras horizontales
    y_pos = np.arange(len(df_comp))
    
    # Barras para presupuesto actual
    ax1.barh(y_pos, df_comp['Presupuesto Actual (USD)'], 
            color='lightgray', alpha=0.7, label='Actual')
    
    # Barras para presupuesto optimizado
    ax1.barh(y_pos, df_comp['Presupuesto Óptimo (USD)'], 
            color=[color_dict[m] for m in df_comp['Marca']], alpha=0.7, label='Optimizado')
    
    # Etiquetas y título
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(df_comp['Canal_Marca'])
    ax1.set_xlabel('Presupuesto (USD)')
    ax1.set_title('Comparación de Presupuesto por Canal')
    ax1.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Agregar leyenda para marcas
    import matplotlib.patches as mpatches
    handles = [mpatches.Patch(color=color_dict[m], label=m) for m in marcas]
    ax1.legend(handles=handles, title='Marca', loc='upper right')
    
    # 2. Comparación de Matrículas Estimadas
    x = np.arange(len(df_comp))
    width = 0.35
    
    # Barras para matrículas originales
    ax2.bar(x - width/2, df_comp['Matrículas Estimadas Original'], 
           width, label='Original', color='lightgray')
    
    # Barras para matrículas optimizadas
    ax2.bar(x + width/2, df_comp['Matrículas Estimadas Optimizado'], 
           width, label='Optimizado', color=[color_dict[m] for m in df_comp['Marca']])
    
    # Etiquetas y título
    ax2.set_ylabel('Matrículas Estimadas')
    ax2.set_title('Impacto en Matrículas Estimadas')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df_comp['Canal_Marca'], rotation=45, ha='right')
    ax2.legend()
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Ajustar diseño
    plt.tight_layout()
    
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
        
        # Definir restricciones específicas para canales importantes
        restricciones = {
            "Marca1_Facebook_C001": {"min": 5000, "max": 15000},
            "Marca2_Google_C003": {"min": 8000, "max": 20000}
        }
        
        # Optimizar presupuesto de 50,000 USD con restricciones
        optimizacion = optimizar_presupuesto_lineal(
            prediccion, 
            50000,
            restricciones_canal=restricciones,
            min_porcentaje=0.05,
            max_porcentaje=0.3
        )
        
        print("Optimización de presupuesto con programación lineal:")
        print(optimizacion[['Marca', 'Canal', 'Presupuesto Actual (USD)', 
                           'Presupuesto Óptimo (USD)', 'Cambio Presupuesto (USD)',
                           'Porcentaje del Presupuesto (%)',
                           'CPA Optimizado (USD)']])
        
        # Visualizar resultados
        fig = visualizar_optimizacion_lineal(prediccion, optimizacion)
        plt.savefig("../salidas/optimizacion_lineal.png")
        print("\nVisualización guardada en: ../salidas/optimizacion_lineal.png")
        
        # Ejecutar análisis de sensibilidad
        sensibilidad = analizar_sensibilidad_restricciones(
            prediccion,
            50000,
            rango_min=(0.01, 0.1),
            rango_max=(0.2, 0.5),
            pasos=3
        )
        
        print("\nAnálisis de sensibilidad a restricciones:")
        print(sensibilidad)
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 