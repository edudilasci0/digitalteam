"""
Módulo para optimizar la asignación de presupuesto publicitario basado en rendimiento de CPA.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def optimizar_asignacion(df_prediccion, presupuesto_total):
    """
    Optimiza la asignación del presupuesto publicitario entre diferentes canales y marcas
    basado en el rendimiento histórico y proyección de CPA.
    
    Args:
        df_prediccion (pandas.DataFrame): DataFrame con predicción de matrículas.
        presupuesto_total (float): Presupuesto total disponible para asignar.
        
    Returns:
        pandas.DataFrame: DataFrame con la asignación optimizada.
    """
    # Seleccionar solo canales activos (convocatorias aún no finalizadas)
    df_activos = df_prediccion[df_prediccion['Estado Convocatoria'] != 'Finalizada'].copy()
    
    if df_activos.empty:
        return pd.DataFrame({"Mensaje": ["No hay campañas activas para optimizar presupuesto"]})
    
    # Calcular puntuación inversa del CPA (menor CPA = mejor rendimiento = mayor puntuación)
    maximo_cpa = df_activos['CPA Esperado (USD)'].max() * 1.5  # Multiplicador para evitar valores extremos
    
    # Invertir la relación: Mayor puntuación = mejor rendimiento
    df_activos['Puntuación CPA'] = maximo_cpa / df_activos['CPA Esperado (USD)']
    
    # Ajustar por estado de convocatoria (priorizar las que están en curso)
    df_activos['Puntuación Ajustada'] = df_activos['Puntuación CPA']
    df_activos.loc[df_activos['Estado Convocatoria'] == 'No Iniciada', 'Puntuación Ajustada'] *= 0.9
    
    # Calcular la distribución proporcional basada en la puntuación ajustada
    suma_puntuaciones = df_activos['Puntuación Ajustada'].sum()
    df_activos['Proporción Asignación'] = df_activos['Puntuación Ajustada'] / suma_puntuaciones
    
    # Calcular el presupuesto asignado óptimo
    df_activos['Presupuesto Óptimo (USD)'] = df_activos['Proporción Asignación'] * presupuesto_total
    
    # Calcular el cambio respecto a la asignación original
    df_activos['Presupuesto Actual (USD)'] = df_activos['Presupuesto Asignado (USD)']
    df_activos['Cambio Presupuesto (USD)'] = df_activos['Presupuesto Óptimo (USD)'] - df_activos['Presupuesto Actual (USD)']
    df_activos['Cambio Porcentual (%)'] = (df_activos['Cambio Presupuesto (USD)'] / df_activos['Presupuesto Actual (USD)']) * 100
    
    # Estimar el impacto en matrículas con la nueva asignación
    # Asumimos una relación lineal entre presupuesto y leads generados
    tasa_conversion = df_activos['Tasa de Conversión (%)'] / 100
    factor_cambio = df_activos['Presupuesto Óptimo (USD)'] / df_activos['Presupuesto Actual (USD)']
    
    # Evitar divisiones por cero y valores extremos
    factor_cambio = factor_cambio.clip(0.5, 2.0)
    
    df_activos['Matrículas Estimadas Original'] = df_activos['Matrículas Esperadas']
    df_activos['Matrículas Estimadas Optimizado'] = df_activos['Matrículas Estimadas Original'] * factor_cambio
    df_activos['Incremento Matrículas'] = df_activos['Matrículas Estimadas Optimizado'] - df_activos['Matrículas Estimadas Original']
    
    # Calcular nuevo CPA esperado
    df_activos['CPA Optimizado (USD)'] = df_activos['Presupuesto Óptimo (USD)'] / df_activos['Matrículas Estimadas Optimizado']
    
    # Organizar y ordenar el resultado
    df_resultado = df_activos[[
        'Marca', 'Canal', 'ID Convocatoria', 'Estado Convocatoria',
        'Presupuesto Actual (USD)', 'Presupuesto Óptimo (USD)', 'Cambio Presupuesto (USD)', 'Cambio Porcentual (%)',
        'Matrículas Estimadas Original', 'Matrículas Estimadas Optimizado', 'Incremento Matrículas',
        'CPA Esperado (USD)', 'CPA Optimizado (USD)'
    ]].sort_values(by='Cambio Presupuesto (USD)', ascending=False)
    
    return df_resultado


def generar_plan_implementacion(df_optimizacion, fecha_inicio=None):
    """
    Genera un plan de implementación para la nueva asignación de presupuesto.
    
    Args:
        df_optimizacion (pandas.DataFrame): DataFrame con la asignación optimizada.
        fecha_inicio (datetime, optional): Fecha para iniciar la implementación.
        
    Returns:
        pandas.DataFrame: Plan de implementación con fechas y acciones.
    """
    if fecha_inicio is None:
        fecha_inicio = datetime.now() + timedelta(days=1)
    
    # Crear DataFrame para el plan
    planes = []
    
    # Ordenar por cambio porcentual (absoluto) para priorizar cambios mayores
    df_priorizado = df_optimizacion.copy()
    df_priorizado['Cambio Abs (%)'] = abs(df_priorizado['Cambio Porcentual (%)'])
    df_priorizado = df_priorizado.sort_values(by='Cambio Abs (%)', ascending=False)
    
    # Definir umbrales para categorizar los cambios
    for idx, fila in df_priorizado.iterrows():
        plan = {
            'Marca': fila['Marca'],
            'Canal': fila['Canal'],
            'ID Convocatoria': fila['ID Convocatoria'],
            'Fecha Implementación': None,
            'Acción': None,
            'Urgencia': None,
            'Presupuesto Anterior (USD)': fila['Presupuesto Actual (USD)'],
            'Presupuesto Nuevo (USD)': fila['Presupuesto Óptimo (USD)'],
            'Cambio (USD)': fila['Cambio Presupuesto (USD)'],
            'Cambio (%)': fila['Cambio Porcentual (%)']
        }
        
        # Determinar urgencia y fecha basado en magnitud del cambio
        cambio_abs = abs(fila['Cambio Porcentual (%)'])
        
        if cambio_abs > 20:
            plan['Urgencia'] = 'Alta'
            plan['Fecha Implementación'] = fecha_inicio + timedelta(days=1)
        elif cambio_abs > 10:
            plan['Urgencia'] = 'Media'
            plan['Fecha Implementación'] = fecha_inicio + timedelta(days=3)
        else:
            plan['Urgencia'] = 'Baja'
            plan['Fecha Implementación'] = fecha_inicio + timedelta(days=7)
        
        # Determinar acción
        if fila['Cambio Presupuesto (USD)'] > 0:
            plan['Acción'] = f"Aumentar presupuesto en {abs(fila['Cambio Presupuesto (USD)']):.2f} USD"
        elif fila['Cambio Presupuesto (USD)'] < 0:
            plan['Acción'] = f"Reducir presupuesto en {abs(fila['Cambio Presupuesto (USD)']):.2f} USD"
        else:
            plan['Acción'] = "Mantener presupuesto actual"
        
        planes.append(plan)
    
    return pd.DataFrame(planes)


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
        
        # Optimizar presupuesto total de 50,000 USD
        optimizacion = optimizar_asignacion(prediccion, 50000)
        
        print("Optimización de presupuesto:")
        print(optimizacion[['Marca', 'Canal', 'Presupuesto Actual (USD)', 
                            'Presupuesto Óptimo (USD)', 'Cambio Presupuesto (USD)',
                            'CPA Esperado (USD)', 'CPA Optimizado (USD)']])
        
        # Generar plan de implementación
        plan = generar_plan_implementacion(optimizacion)
        
        print("\nPlan de implementación:")
        print(plan[['Marca', 'Canal', 'Fecha Implementación', 'Acción', 'Urgencia']])
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 