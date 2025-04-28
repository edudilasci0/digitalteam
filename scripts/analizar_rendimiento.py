"""
Módulo para analizar el rendimiento de campañas de marketing y calcular métricas clave.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calcular_metricas_rendimiento(datos_crm, datos_planificacion=None):
    """
    Calcula métricas clave de rendimiento para campañas de marketing.
    
    Args:
        datos_crm (pandas.DataFrame): DataFrame con datos de leads y matrículas.
        datos_planificacion (pandas.DataFrame, opcional): DataFrame con datos de planificación.
        
    Returns:
        pandas.DataFrame: DataFrame con métricas calculadas.
    """
    # Crear una copia para no modificar el original
    df_metricas = datos_crm.copy()
    
    # Calcular tasas de conversión (CR)
    df_metricas['Tasa Conversión'] = np.where(
        df_metricas['Leads'] > 0,
        df_metricas['Matrículas'] / df_metricas['Leads'],
        0
    )
    
    # Unir con datos de planificación si están disponibles
    if datos_planificacion is not None:
        # Crear identificadores únicos para unir los DataFrames
        df_metricas['ID'] = df_metricas['Marca'] + '_' + df_metricas['Canal'] + '_' + df_metricas['ID Convocatoria']
        datos_planificacion['ID'] = datos_planificacion['Marca'] + '_' + datos_planificacion['Canal'] + '_' + datos_planificacion['ID Convocatoria']
        
        # Realizar la unión
        df_metricas = pd.merge(
            df_metricas,
            datos_planificacion[['ID', 'Presupuesto Asignado (USD)', 'Objetivo Leads', 'Objetivo Matrículas']],
            on='ID',
            how='left'
        )
        
        # Calcular CPA (Costo Por Adquisición)
        df_metricas['CPA'] = np.where(
            df_metricas['Matrículas'] > 0,
            df_metricas['Presupuesto Asignado (USD)'] / df_metricas['Matrículas'],
            float('inf')
        )
        
        # Calcular CPL (Costo Por Lead)
        df_metricas['CPL'] = np.where(
            df_metricas['Leads'] > 0,
            df_metricas['Presupuesto Asignado (USD)'] / df_metricas['Leads'],
            float('inf')
        )
        
        # Calcular % de cumplimiento de objetivos
        df_metricas['% Cumplimiento Leads'] = np.where(
            df_metricas['Objetivo Leads'] > 0,
            df_metricas['Leads'] / df_metricas['Objetivo Leads'] * 100,
            0
        )
        
        df_metricas['% Cumplimiento Matrículas'] = np.where(
            df_metricas['Objetivo Matrículas'] > 0,
            df_metricas['Matrículas'] / df_metricas['Objetivo Matrículas'] * 100,
            0
        )
        
        # Eliminar la columna de ID temporal
        df_metricas.drop('ID', axis=1, inplace=True)
    
    return df_metricas


def calcular_tendencias(datos_metricas, periodo='mensual'):
    """
    Calcula tendencias de métricas a lo largo del tiempo.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas calculadas.
        periodo (str): Periodo para agrupar los datos ('mensual', 'semanal', 'diario').
        
    Returns:
        pandas.DataFrame: DataFrame con tendencias calculadas.
    """
    # Verificar que exista columna de fecha
    if 'Fecha' not in datos_metricas.columns:
        raise ValueError("El DataFrame debe contener una columna 'Fecha'")
    
    # Asegurar que la columna Fecha sea datetime
    datos_metricas['Fecha'] = pd.to_datetime(datos_metricas['Fecha'])
    
    # Definir la función de agrupación según el periodo
    if periodo == 'mensual':
        datos_metricas['Periodo'] = datos_metricas['Fecha'].dt.strftime('%Y-%m')
    elif periodo == 'semanal':
        datos_metricas['Periodo'] = datos_metricas['Fecha'].dt.strftime('%Y-%U')
    elif periodo == 'diario':
        datos_metricas['Periodo'] = datos_metricas['Fecha'].dt.strftime('%Y-%m-%d')
    else:
        raise ValueError("Periodo no válido. Use 'mensual', 'semanal' o 'diario'")
    
    # Agrupar por periodo y canal
    tendencias = datos_metricas.groupby(['Periodo', 'Marca', 'Canal']).agg({
        'Leads': 'sum',
        'Matrículas': 'sum',
        'Presupuesto Asignado (USD)': 'sum'
    }).reset_index()
    
    # Calcular métricas agregadas
    tendencias['Tasa Conversión'] = np.where(
        tendencias['Leads'] > 0,
        tendencias['Matrículas'] / tendencias['Leads'],
        0
    )
    
    tendencias['CPA'] = np.where(
        tendencias['Matrículas'] > 0,
        tendencias['Presupuesto Asignado (USD)'] / tendencias['Matrículas'],
        float('inf')
    )
    
    tendencias['CPL'] = np.where(
        tendencias['Leads'] > 0,
        tendencias['Presupuesto Asignado (USD)'] / tendencias['Leads'],
        float('inf')
    )
    
    return tendencias


def identificar_oportunidades_mejora(datos_metricas, umbral_cpa=None, umbral_cr=None):
    """
    Identifica oportunidades de mejora basadas en métricas de rendimiento.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas calculadas.
        umbral_cpa (float, opcional): Umbral de CPA para considerar como alto.
        umbral_cr (float, opcional): Umbral de tasa de conversión para considerar como baja.
        
    Returns:
        dict: Diccionario con oportunidades de mejora identificadas.
    """
    # Si no se proporcionan umbrales, calcularlos automáticamente
    if umbral_cpa is None:
        # Usar el percentil 75 como umbral para CPA alto
        umbral_cpa = datos_metricas['CPA'].quantile(0.75)
    
    if umbral_cr is None:
        # Usar el percentil 25 como umbral para CR bajo
        umbral_cr = datos_metricas['Tasa Conversión'].quantile(0.25)
    
    # Identificar canales con CPA alto
    cpa_alto = datos_metricas[
        (datos_metricas['CPA'] > umbral_cpa) & 
        (datos_metricas['CPA'] != float('inf'))
    ]
    
    # Identificar canales con tasa de conversión baja
    cr_bajo = datos_metricas[
        (datos_metricas['Tasa Conversión'] < umbral_cr) & 
        (datos_metricas['Leads'] > 0)
    ]
    
    # Identificar canales con alta desviación respecto a objetivos
    desviacion_alta = datos_metricas[
        (datos_metricas['% Cumplimiento Matrículas'] < 80) | 
        (datos_metricas['% Cumplimiento Matrículas'] > 120)
    ]
    
    return {
        'cpa_alto': cpa_alto,
        'cr_bajo': cr_bajo,
        'desviacion_alta': desviacion_alta,
        'umbral_cpa': umbral_cpa,
        'umbral_cr': umbral_cr
    }


if __name__ == "__main__":
    # Ejemplo de uso
    from cargar_datos import cargar_datos_crm, cargar_datos_planificacion
    
    datos_crm = cargar_datos_crm("../datos/leads_matriculas_reales.csv")
    datos_planificacion = cargar_datos_planificacion("../datos/planificacion_quincenal.csv")
    
    print("Calculando métricas de rendimiento...")
    metricas = calcular_metricas_rendimiento(datos_crm, datos_planificacion)
    print(metricas.head())
    
    print("\nCalculando tendencias mensuales...")
    tendencias = calcular_tendencias(metricas, periodo='mensual')
    print(tendencias.head())
    
    print("\nIdentificando oportunidades de mejora...")
    oportunidades = identificar_oportunidades_mejora(metricas)
    print(f"Canales con CPA alto (>{oportunidades['umbral_cpa']:.2f}):")
    print(oportunidades['cpa_alto'][['Marca', 'Canal', 'CPA']])
    
    print(f"\nCanales con tasa de conversión baja (<{oportunidades['umbral_cr']:.2%}):")
    print(oportunidades['cr_bajo'][['Marca', 'Canal', 'Tasa Conversión']]) 