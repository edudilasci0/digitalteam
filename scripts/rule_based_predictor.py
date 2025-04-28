"""
Módulo para realizar predicciones mediante reglas deterministas.
"""
import pandas as pd
import numpy as np
from datetime import datetime


def predecir_matriculas(df_leads, df_planificacion):
    """
    Realiza una predicción determinista de matrículas basada en:
    - Avance de tiempo transcurrido en la convocatoria
    - Cantidad actual de leads
    - Tasa de conversión histórica
    
    Args:
        df_leads (pandas.DataFrame): DataFrame con datos de leads y matrículas.
        df_planificacion (pandas.DataFrame): DataFrame con datos de planificación.
        
    Returns:
        pandas.DataFrame: DataFrame con la predicción de matrículas.
    """
    # Obtener la fecha actual
    fecha_actual = datetime.now()
    
    # Asegurar que las fechas estén en formato datetime
    df_planificacion['Fecha Inicio'] = pd.to_datetime(df_planificacion['Fecha Inicio'])
    df_planificacion['Fecha Fin'] = pd.to_datetime(df_planificacion['Fecha Fin'])
    
    # Calcular tasa de conversión histórica
    conteo_leads = df_leads[df_leads['Tipo'] == 'Lead'].groupby(['Marca', 'Canal']).size().reset_index(name='Leads Actuales')
    conteo_matriculas = df_leads[df_leads['Tipo'] == 'Matrícula'].groupby(['Marca', 'Canal']).size().reset_index(name='Matrículas Actuales')
    
    datos_combinados = pd.merge(conteo_leads, conteo_matriculas, on=['Marca', 'Canal'], how='left')
    datos_combinados['Matrículas Actuales'] = datos_combinados['Matrículas Actuales'].fillna(0)
    datos_combinados['Tasa de Conversión (%)'] = (datos_combinados['Matrículas Actuales'] / datos_combinados['Leads Actuales']) * 100
    
    # Agrupar por convocatoria para obtener datos únicos
    convocatorias = df_planificacion.drop_duplicates(subset=['ID Convocatoria', 'Marca', 'Canal'])
    
    # Unir con datos de planificación
    datos_prediccion = pd.merge(datos_combinados, convocatorias, on=['Marca', 'Canal'], how='left')
    
    # Calcular el progreso de tiempo para cada convocatoria
    datos_prediccion['Tiempo Total (días)'] = (datos_prediccion['Fecha Fin'] - datos_prediccion['Fecha Inicio']).dt.days
    datos_prediccion['Tiempo Transcurrido (días)'] = (fecha_actual - datos_prediccion['Fecha Inicio']).dt.days
    
    # Ajustar valores negativos o mayores que el total (convocatorias que no han comenzado o ya terminaron)
    datos_prediccion['Tiempo Transcurrido (días)'] = datos_prediccion['Tiempo Transcurrido (días)'].clip(0, datos_prediccion['Tiempo Total (días)'])
    
    # Calcular el porcentaje de avance de la convocatoria
    datos_prediccion['Porcentaje Avance (%)'] = (datos_prediccion['Tiempo Transcurrido (días)'] / datos_prediccion['Tiempo Total (días)']) * 100
    
    # Estimar leads totales esperados basados en el avance de tiempo de la convocatoria
    datos_prediccion['Porcentaje Avance Decimal'] = datos_prediccion['Porcentaje Avance (%)'] / 100
    # Evitar división por cero
    datos_prediccion['Porcentaje Avance Decimal'] = datos_prediccion['Porcentaje Avance Decimal'].replace(0, 0.001)
    
    datos_prediccion['Leads Esperados Total'] = datos_prediccion['Leads Actuales'] / datos_prediccion['Porcentaje Avance Decimal']
    
    # Predecir matrículas esperadas
    datos_prediccion['Matrículas Esperadas'] = datos_prediccion['Leads Esperados Total'] * (datos_prediccion['Tasa de Conversión (%)'] / 100)
    
    # Calcular el CPA esperado
    datos_prediccion['CPA Esperado (USD)'] = datos_prediccion['Presupuesto Asignado (USD)'] / datos_prediccion['Matrículas Esperadas']
    
    # Determinar el estado de la convocatoria
    condiciones = [
        (datos_prediccion['Tiempo Transcurrido (días)'] == 0),
        (datos_prediccion['Tiempo Transcurrido (días)'] == datos_prediccion['Tiempo Total (días)']),
        (datos_prediccion['Tiempo Transcurrido (días)'] > 0)
    ]
    opciones = ['No Iniciada', 'Finalizada', 'En Curso']
    datos_prediccion['Estado Convocatoria'] = np.select(condiciones, opciones, default='Desconocido')
    
    # Para las convocatorias en curso o finalizadas, verificar cumplimiento de objetivos
    if 'Leads Estimados' in datos_prediccion.columns:
        conversion_esperada = datos_prediccion['Tasa de Conversión (%)'] / 100
        matriculas_esperadas = datos_prediccion['Leads Estimados'] * conversion_esperada
        datos_prediccion['Cumplimiento Esperado (%)'] = (datos_prediccion['Matrículas Esperadas'] / matriculas_esperadas) * 100
    
    # Agregar información sobre la duración en semanas
    datos_prediccion['Semana Actual'] = (datos_prediccion['Tiempo Transcurrido (días)'] / 7).round().astype(int)
    
    return datos_prediccion


# Mantener compatibilidad con el código existente
predict_matriculations = predecir_matriculas


if __name__ == "__main__":
    # Ejemplo de uso
    from load_data import cargar_datos_crm, cargar_datos_planificacion
    from validate_data import validar_datos_crm, validar_datos_planificacion
    
    try:
        datos_crm = cargar_datos_crm("../data/leads_matriculas_reales.csv")
        datos_planificacion = cargar_datos_planificacion("../data/planificacion_quincenal.csv")
        
        validar_datos_crm(datos_crm)
        validar_datos_planificacion(datos_planificacion)
        
        prediccion = predecir_matriculas(datos_crm, datos_planificacion)
        
        print("Predicción de matrículas:")
        print(prediccion[['Marca', 'Canal', 'Duracion Semanas', 'Semana Actual', 'Porcentaje Avance (%)',
                          'Leads Actuales', 'Matrículas Actuales', 
                          'Leads Esperados Total', 'Matrículas Esperadas', 'CPA Esperado (USD)',
                          'Estado Convocatoria']])
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 