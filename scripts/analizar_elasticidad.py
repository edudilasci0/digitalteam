"""
Módulo para analizar la elasticidad precio-demanda por carrera de interés.
Permite determinar qué carreras son más sensibles a cambios en inversión publicitaria.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


def calcular_elasticidad_por_carrera(df_leads, df_planificacion):
    """
    Calcula la elasticidad precio-demanda por carrera de interés.
    
    Args:
        df_leads (pandas.DataFrame): DataFrame con datos de leads y matrículas.
        df_planificacion (pandas.DataFrame): DataFrame con datos de planificación.
        
    Returns:
        pandas.DataFrame: DataFrame con la elasticidad calculada por carrera.
    """
    # Asegurar que tengamos la columna de Carrera
    if 'Carrera' not in df_leads.columns:
        raise ValueError("El DataFrame de leads debe contener la columna 'Carrera'")
    
    # Filtrar solo los leads
    leads = df_leads[df_leads['Tipo'] == 'Lead']
    
    # Agrupar leads por Marca, Canal y Carrera
    conteo_leads = leads.groupby(['Marca', 'Canal', 'Carrera']).size().reset_index(name='Cantidad Leads')
    
    # Unir con la planificación
    datos_combinados = pd.merge(conteo_leads, df_planificacion, on=['Marca', 'Canal'], how='left')
    
    # Calcular el costo por lead por carrera
    datos_combinados['CPL por Carrera (USD)'] = datos_combinados['Presupuesto Asignado (USD)'] * (
        datos_combinados['Cantidad Leads'] / datos_combinados.groupby(['Marca', 'Canal'])['Cantidad Leads'].transform('sum')
    )
    
    # Inicializar el DataFrame para almacenar resultados de elasticidad
    resultados_elasticidad = []
    
    # Calcular elasticidad para cada carrera agrupando por marca
    for marca in datos_combinados['Marca'].unique():
        datos_marca = datos_combinados[datos_combinados['Marca'] == marca]
        
        for carrera in datos_marca['Carrera'].unique():
            datos_carrera = datos_marca[datos_marca['Carrera'] == carrera]
            
            # Necesitamos al menos 2 puntos para calcular elasticidad
            if len(datos_carrera) < 2:
                continue
                
            # Calcular logaritmos para análisis de elasticidad
            log_presupuesto = np.log(datos_carrera['CPL por Carrera (USD)'])
            log_leads = np.log(datos_carrera['Cantidad Leads'])
            
            # Realizar regresión lineal para calcular elasticidad
            pendiente, intercepto, r_valor, p_valor, std_err = stats.linregress(log_presupuesto, log_leads)
            
            # La pendiente de la regresión es la elasticidad
            elasticidad = pendiente
            
            # Calcular R^2 para evaluar la calidad del modelo
            r_cuadrado = r_valor ** 2
            
            # Clasificar la elasticidad
            if abs(elasticidad) < 1:
                clasificacion = "Inelástica"
            elif abs(elasticidad) > 1:
                clasificacion = "Elástica"
            else:
                clasificacion = "Elasticidad Unitaria"
                
            # Calcular leads promedio y CPL promedio para esta carrera
            leads_promedio = datos_carrera['Cantidad Leads'].mean()
            cpl_promedio = datos_carrera['CPL por Carrera (USD)'].mean()
            
            # Agregar resultados
            resultados_elasticidad.append({
                'Marca': marca,
                'Carrera': carrera,
                'Elasticidad': elasticidad,
                'R^2': r_cuadrado,
                'P-valor': p_valor,
                'Leads Promedio': leads_promedio,
                'CPL Promedio (USD)': cpl_promedio,
                'Clasificación': clasificacion,
                'Cantidad Observaciones': len(datos_carrera)
            })
    
    return pd.DataFrame(resultados_elasticidad)


def calcular_elasticidad_alternativa(df_leads, df_planificacion, periodos_minimos=3):
    """
    Calcula la elasticidad de manera alternativa cuando no hay suficientes datos para 
    una regresión completa, utilizando cambios porcentuales entre periodos.
    
    Args:
        df_leads (pandas.DataFrame): DataFrame con datos de leads incluyendo fechas.
        df_planificacion (pandas.DataFrame): DataFrame con datos de planificación.
        periodos_minimos (int): Cantidad mínima de periodos para calcular elasticidad.
        
    Returns:
        pandas.DataFrame: DataFrame con la elasticidad calculada por carrera.
    """
    # Asegurar que tengamos las columnas necesarias
    if 'Carrera' not in df_leads.columns or 'Fecha' not in df_leads.columns:
        raise ValueError("El DataFrame de leads debe contener las columnas 'Carrera' y 'Fecha'")
    
    # Convertir la columna de fecha al formato datetime si no lo está
    df_leads['Fecha'] = pd.to_datetime(df_leads['Fecha'])
    
    # Agregar columna de periodo (semana o mes)
    df_leads['Periodo'] = df_leads['Fecha'].dt.to_period('W')  # 'W' para semana, 'M' para mes
    
    # Filtrar solo los leads
    leads = df_leads[df_leads['Tipo'] == 'Lead']
    
    # Agrupar por Marca, Canal, Carrera y Periodo
    conteo_por_periodo = leads.groupby(['Marca', 'Canal', 'Carrera', 'Periodo']).size().reset_index(name='Leads')
    
    # Unir con la planificación (asumiendo que hay datos de presupuesto por periodo)
    # Esto requeriría adaptar la estructura de df_planificacion
    
    # Inicializar resultados
    resultados = []
    
    # Para cada combinación de Marca, Canal y Carrera
    for (marca, canal, carrera), grupo in conteo_por_periodo.groupby(['Marca', 'Canal', 'Carrera']):
        # Ordenar por periodo
        grupo = grupo.sort_values('Periodo')
        
        # Si no hay suficientes periodos, continuar
        if len(grupo) < periodos_minimos:
            continue
            
        # Calcular cambios porcentuales entre periodos
        grupo['Leads_Ant'] = grupo['Leads'].shift(1)
        grupo['Cambio_Pct_Leads'] = (grupo['Leads'] - grupo['Leads_Ant']) / grupo['Leads_Ant'] * 100
        
        # Aquí necesitaríamos los datos de presupuesto por periodo para calcular:
        # grupo['Cambio_Pct_Presupuesto'] = (grupo['Presupuesto'] - grupo['Presupuesto_Ant']) / grupo['Presupuesto_Ant'] * 100
        
        # Como alternativa, podemos usar una aproximación con CPL constante
        # Elasticidad = Cambio_Pct_Leads / Cambio_Pct_Presupuesto
        
        # Agregar a resultados
        # Implementación a completar según estructura de datos disponible
        
    return pd.DataFrame(resultados)


def recomendar_carreras_prioritarias(df_elasticidad, umbral_elasticidad=1.2, umbral_r2=0.7):
    """
    Recomienda qué carreras priorizar en base a su elasticidad y calidad estadística.
    
    Args:
        df_elasticidad (pandas.DataFrame): DataFrame con los resultados de elasticidad.
        umbral_elasticidad (float): Umbral de elasticidad para considerar una carrera como prioritaria.
        umbral_r2 (float): Umbral de R^2 para considerar confiable el resultado.
        
    Returns:
        pandas.DataFrame: DataFrame con las recomendaciones de priorización.
    """
    # Filtrar carreras con buena calidad estadística
    df_confiable = df_elasticidad[df_elasticidad['R^2'] >= umbral_r2].copy()
    
    # Clasificar carreras según su elasticidad
    df_confiable['Prioridad'] = 'Media'
    df_confiable.loc[df_confiable['Elasticidad'] >= umbral_elasticidad, 'Prioridad'] = 'Alta'
    df_confiable.loc[df_confiable['Elasticidad'] < 0, 'Prioridad'] = 'Baja'
    
    # Agregar recomendación específica
    condiciones = [
        (df_confiable['Prioridad'] == 'Alta'),
        (df_confiable['Prioridad'] == 'Media'),
        (df_confiable['Prioridad'] == 'Baja')
    ]
    
    recomendaciones = [
        'Aumentar inversión - Alto retorno esperado',
        'Mantener inversión actual - Evaluar otros factores',
        'Reducir inversión - Bajo retorno esperado'
    ]
    
    df_confiable['Recomendación'] = np.select(condiciones, recomendaciones, default='Sin recomendación')
    
    # Ordenar por elasticidad descendente
    return df_confiable.sort_values('Elasticidad', ascending=False)


def visualizar_elasticidad_carreras(df_elasticidad):
    """
    Genera una visualización de la elasticidad por carrera.
    
    Args:
        df_elasticidad (pandas.DataFrame): DataFrame con los resultados de elasticidad.
        
    Returns:
        matplotlib.figure.Figure: Figura con la visualización generada.
    """
    # Filtrar para tener resultados confiables
    df_viz = df_elasticidad[df_elasticidad['R^2'] > 0.5].copy()
    
    # Ordenar por elasticidad
    df_viz = df_viz.sort_values('Elasticidad', ascending=False)
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Definir colores según elasticidad
    colores = ['#FF9999' if e < 0 else '#66B2FF' if e < 1 else '#99FF99' for e in df_viz['Elasticidad']]
    
    # Crear barras horizontales
    barras = ax.barh(df_viz['Carrera'], df_viz['Elasticidad'], color=colores)
    
    # Añadir una línea vertical en x=1 para marcar elasticidad unitaria
    ax.axvline(x=1, color='gray', linestyle='--', alpha=0.7)
    ax.axvline(x=0, color='black', alpha=0.9)
    
    # Etiquetas y título
    ax.set_xlabel('Coeficiente de Elasticidad')
    ax.set_ylabel('Carrera')
    ax.set_title('Elasticidad Precio-Demanda por Carrera de Interés')
    
    # Añadir valores de elasticidad al final de cada barra
    for i, v in enumerate(df_viz['Elasticidad']):
        ax.text(v + 0.1, i, f"{v:.2f}", va='center')
    
    # Añadir leyenda
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#99FF99', label='Elástica (>1): Alta sensibilidad'),
        Patch(facecolor='#66B2FF', label='Inelástica (0-1): Baja sensibilidad'),
        Patch(facecolor='#FF9999', label='Negativa (<0): Comportamiento anómalo')
    ]
    ax.legend(handles=legend_elements, loc='lower right')
    
    # Ajustar diseño
    plt.tight_layout()
    
    return fig


if __name__ == "__main__":
    # Ejemplo de uso
    from cargar_datos import cargar_datos_crm, cargar_datos_planificacion
    from validar_datos import validar_datos_crm, validar_datos_planificacion
    
    try:
        datos_crm = cargar_datos_crm("../datos/leads_matriculas_reales.csv")
        datos_planificacion = cargar_datos_planificacion("../datos/planificacion_quincenal.csv")
        
        validar_datos_crm(datos_crm)
        validar_datos_planificacion(datos_planificacion)
        
        # Calcular elasticidad por carrera
        elasticidad = calcular_elasticidad_por_carrera(datos_crm, datos_planificacion)
        
        print("Análisis de Elasticidad por Carrera:")
        print(elasticidad[['Carrera', 'Elasticidad', 'R^2', 'Clasificación']])
        
        # Generar recomendaciones
        recomendaciones = recomendar_carreras_prioritarias(elasticidad)
        
        print("\nRecomendaciones de Priorización:")
        print(recomendaciones[['Carrera', 'Elasticidad', 'Prioridad', 'Recomendación']])
        
        # Visualizar resultados
        fig = visualizar_elasticidad_carreras(elasticidad)
        plt.savefig("../salidas/elasticidad_carreras.png")
        plt.close(fig)
        
        print("\nGráfico guardado en: ../salidas/elasticidad_carreras.png")
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 