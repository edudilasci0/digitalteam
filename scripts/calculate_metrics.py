"""
Módulo para calcular CPL, CPA y Tasa de Conversión reales.
"""
import pandas as pd
import numpy as np


def calcular_cpl(df_leads, df_planificacion):
    """
    Calcula el Costo por Lead (CPL) real por marca y canal.
    
    Args:
        df_leads (pandas.DataFrame): DataFrame con datos de leads.
        df_planificacion (pandas.DataFrame): DataFrame con datos de planificación.
        
    Returns:
        pandas.DataFrame: DataFrame con el CPL real calculado.
    """
    # Filtrar solo los leads
    solo_leads = df_leads[df_leads['Tipo'] == 'Lead']
    
    # Agrupar por Marca y Canal
    conteo_leads = solo_leads.groupby(['Marca', 'Canal']).size().reset_index(name='Leads Obtenidos')
    
    # Unir con la planificación
    combinado = pd.merge(conteo_leads, df_planificacion, on=['Marca', 'Canal'], how='left')
    
    # Calcular CPL real
    combinado['CPL Real (USD)'] = combinado['Presupuesto Asignado (USD)'] / combinado['Leads Obtenidos']
    
    # Calcular diferencia con el objetivo
    combinado['Diferencia CPL (USD)'] = combinado['CPL Real (USD)'] - combinado['CPL Objetivo (USD)']
    combinado['Diferencia CPL (%)'] = (combinado['Diferencia CPL (USD)'] / combinado['CPL Objetivo (USD)']) * 100
    
    return combinado


def calcular_cpa(df_leads, df_planificacion):
    """
    Calcula el Costo por Matrícula (CPA) real por marca y canal.
    
    Args:
        df_leads (pandas.DataFrame): DataFrame con datos de leads y matrículas.
        df_planificacion (pandas.DataFrame): DataFrame con datos de planificación.
        
    Returns:
        pandas.DataFrame: DataFrame con el CPA real calculado.
    """
    # Filtrar matrículas
    matriculas = df_leads[df_leads['Tipo'] == 'Matrícula']
    
    # Contar matrículas por Marca y Canal
    conteo_matriculas = matriculas.groupby(['Marca', 'Canal']).size().reset_index(name='Matrículas Obtenidas')
    
    # Unir con la planificación
    combinado = pd.merge(conteo_matriculas, df_planificacion, on=['Marca', 'Canal'], how='left')
    
    # Calcular CPA real
    combinado['CPA Real (USD)'] = combinado['Presupuesto Asignado (USD)'] / combinado['Matrículas Obtenidas']
    
    return combinado


def calcular_tasa_conversion(df_leads):
    """
    Calcula la tasa de conversión (Lead a Matrícula) por marca y canal.
    
    Args:
        df_leads (pandas.DataFrame): DataFrame con datos de leads y matrículas.
        
    Returns:
        pandas.DataFrame: DataFrame con la tasa de conversión calculada.
    """
    # Contar leads por Marca y Canal
    leads = df_leads[df_leads['Tipo'] == 'Lead'].groupby(['Marca', 'Canal']).size().reset_index(name='Leads')
    
    # Contar matrículas por Marca y Canal
    matriculas = df_leads[df_leads['Tipo'] == 'Matrícula'].groupby(['Marca', 'Canal']).size().reset_index(name='Matrículas')
    
    # Unir ambos DataFrames
    combinado = pd.merge(leads, matriculas, on=['Marca', 'Canal'], how='left')
    
    # Calcular tasa de conversión
    combinado['Matrículas'] = combinado['Matrículas'].fillna(0)
    combinado['Tasa de Conversión (%)'] = (combinado['Matrículas'] / combinado['Leads']) * 100
    
    return combinado


def generar_reporte_metricas(df_leads, df_planificacion):
    """
    Genera un reporte completo de métricas: CPL, CPA y Tasa de Conversión.
    
    Args:
        df_leads (pandas.DataFrame): DataFrame con datos de leads y matrículas.
        df_planificacion (pandas.DataFrame): DataFrame con datos de planificación.
        
    Returns:
        dict: Diccionario con los DataFrames de cada métrica.
    """
    df_cpl = calcular_cpl(df_leads, df_planificacion)
    df_cpa = calcular_cpa(df_leads, df_planificacion)
    df_conversion = calcular_tasa_conversion(df_leads)
    
    # Unir todos los DataFrames para un reporte completo
    reporte_combinado = pd.merge(df_cpl, df_cpa[['Marca', 'Canal', 'Matrículas Obtenidas', 'CPA Real (USD)']], 
                            on=['Marca', 'Canal'], how='left')
    
    reporte_final = pd.merge(reporte_combinado, df_conversion[['Marca', 'Canal', 'Tasa de Conversión (%)']], 
                           on=['Marca', 'Canal'], how='left')
    
    return {
        'cpl': df_cpl,
        'cpa': df_cpa,
        'conversion': df_conversion,
        'complete_report': reporte_final
    }


# Mantener compatibilidad con el código existente
calculate_cpl = calcular_cpl
calculate_cpa = calcular_cpa
calculate_conversion_rate = calcular_tasa_conversion
generate_metrics_report = generar_reporte_metricas


if __name__ == "__main__":
    # Ejemplo de uso
    from load_data import cargar_datos_crm, cargar_datos_planificacion
    from validate_data import validar_datos_crm, validar_datos_planificacion
    
    try:
        datos_crm = cargar_datos_crm("../data/leads_matriculas_reales.csv")
        datos_planificacion = cargar_datos_planificacion("../data/planificacion_quincenal.csv")
        
        validar_datos_crm(datos_crm)
        validar_datos_planificacion(datos_planificacion)
        
        metricas = generar_reporte_metricas(datos_crm, datos_planificacion)
        
        print("Reporte completo de métricas:")
        print(metricas['complete_report'])
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 