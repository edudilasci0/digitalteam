"""
Módulo para estimar valores faltantes en los datos de leads y matrículas.
Específicamente, distribuye el presupuesto total invertido entre los leads y calcula métricas básicas.
"""
import pandas as pd
import numpy as np
from datetime import datetime


def distribuir_costo_leads(df_leads, presupuesto_total=None, datos_planificacion=None):
    """
    Distribuye el presupuesto total invertido entre los leads generados.
    
    Args:
        df_leads (pandas.DataFrame): DataFrame con datos de leads.
        presupuesto_total (float, optional): Presupuesto total invertido en el período.
            Si no se proporciona, se intentará calcular desde datos_planificacion.
        datos_planificacion (pandas.DataFrame, optional): DataFrame con datos de planificación
            que incluya información de presupuesto.
    
    Returns:
        pandas.DataFrame: DataFrame original con una columna adicional 'costo_estimado'.
    """
    # Crear una copia del DataFrame para no modificar el original
    df_con_costo = df_leads.copy()
    
    # Si no se proporciona presupuesto, usar un valor predeterminado
    if presupuesto_total is None:
        if datos_planificacion is not None:
            # Intentar obtener el presupuesto desde los datos de planificación
            presupuesto_total = datos_planificacion['Presupuesto Asignado (USD)'].sum()
        else:
            # Usar un valor predeterminado si no hay datos disponibles
            presupuesto_total = 1000.0
            print("ADVERTENCIA: Usando un presupuesto predeterminado de $1000 USD")
    
    # Número total de leads
    total_leads = len(df_leads)
    
    if total_leads > 0:
        # Distribuir el presupuesto equitativamente entre todos los leads
        costo_por_lead = presupuesto_total / total_leads
        df_con_costo['costo_estimado'] = costo_por_lead
        
        # Opcionalmente, podríamos ponderar por origen o marca si tenemos información adicional
        # Ejemplo: distribuir más presupuesto a leads de canales más costosos
        
        print(f"Presupuesto total: ${presupuesto_total:.2f}")
        print(f"Número total de leads: {total_leads}")
        print(f"Costo promedio por lead: ${costo_por_lead:.2f}")
    else:
        df_con_costo['costo_estimado'] = 0
        print("No hay leads para distribuir el costo")
    
    return df_con_costo


def calcular_metricas_basicas(df_leads_con_costo, df_matriculas):
    """
    Calcula métricas básicas de eficiencia de marketing sin asignar valores a las matrículas.
    
    Args:
        df_leads_con_costo (pandas.DataFrame): DataFrame de leads con columna 'costo_estimado'.
        df_matriculas (pandas.DataFrame): DataFrame de matrículas.
    
    Returns:
        dict: Diccionario con métricas básicas.
    """
    # Costo total de adquisición
    costo_total = df_leads_con_costo['costo_estimado'].sum()
    
    # Total de leads y matrículas
    total_leads = len(df_leads_con_costo)
    total_matriculas = len(df_matriculas)
    
    # Costo por lead (CPL)
    cpl = costo_total / total_leads if total_leads > 0 else 0
    
    # Costo por matrícula (CPM o CPA - Cost per Acquisition)
    cpa = costo_total / total_matriculas if total_matriculas > 0 else 0
    
    # Tasa de conversión
    tasa_conversion = (total_matriculas / total_leads) * 100 if total_leads > 0 else 0
    
    # Métricas por marca
    metricas_por_marca = {}
    for marca in df_leads_con_costo['marca'].unique():
        # Leads y costos para esta marca
        leads_marca = len(df_leads_con_costo[df_leads_con_costo['marca'] == marca])
        costo_marca = df_leads_con_costo[df_leads_con_costo['marca'] == marca]['costo_estimado'].sum()
        
        # Matrículas para esta marca
        matriculas_marca = len(df_matriculas[df_matriculas['marca'] == marca])
        
        # Cálculos para esta marca
        cpl_marca = costo_marca / leads_marca if leads_marca > 0 else 0
        cpa_marca = costo_marca / matriculas_marca if matriculas_marca > 0 else 0
        tasa_conversion_marca = (matriculas_marca / leads_marca) * 100 if leads_marca > 0 else 0
        
        metricas_por_marca[marca] = {
            'leads': leads_marca,
            'matriculas': matriculas_marca,
            'costo_total': costo_marca,
            'cpl': cpl_marca,
            'cpa': cpa_marca,
            'tasa_conversion': tasa_conversion_marca
        }
    
    # Métricas por origen
    metricas_por_origen = {}
    for origen in df_leads_con_costo['origen'].unique():
        # Leads y costos para este origen
        leads_origen = len(df_leads_con_costo[df_leads_con_costo['origen'] == origen])
        costo_origen = df_leads_con_costo[df_leads_con_costo['origen'] == origen]['costo_estimado'].sum()
        
        # Para matrículas, necesitamos cruzar con la tabla de leads
        leads_ids = df_leads_con_costo[df_leads_con_costo['origen'] == origen]['id_lead'].tolist()
        matriculas_origen = len(df_matriculas[df_matriculas['id_lead'].isin(leads_ids)])
        
        # Cálculos para este origen
        cpl_origen = costo_origen / leads_origen if leads_origen > 0 else 0
        cpa_origen = costo_origen / matriculas_origen if matriculas_origen > 0 else 0
        tasa_conversion_origen = (matriculas_origen / leads_origen) * 100 if leads_origen > 0 else 0
        
        metricas_por_origen[origen] = {
            'leads': leads_origen,
            'matriculas': matriculas_origen,
            'costo_total': costo_origen,
            'cpl': cpl_origen,
            'cpa': cpa_origen,
            'tasa_conversion': tasa_conversion_origen
        }
    
    # Métricas por programa
    metricas_por_programa = {}
    for programa in df_leads_con_costo['programa'].unique():
        # Leads y costos para este programa
        leads_programa = len(df_leads_con_costo[df_leads_con_costo['programa'] == programa])
        costo_programa = df_leads_con_costo[df_leads_con_costo['programa'] == programa]['costo_estimado'].sum()
        
        # Matrículas para este programa
        matriculas_programa = len(df_matriculas[df_matriculas['programa'] == programa])
        
        # Cálculos para este programa
        cpl_programa = costo_programa / leads_programa if leads_programa > 0 else 0
        cpa_programa = costo_programa / matriculas_programa if matriculas_programa > 0 else 0
        tasa_conversion_programa = (matriculas_programa / leads_programa) * 100 if leads_programa > 0 else 0
        
        metricas_por_programa[programa] = {
            'leads': leads_programa,
            'matriculas': matriculas_programa,
            'costo_total': costo_programa,
            'cpl': cpl_programa,
            'cpa': cpa_programa,
            'tasa_conversion': tasa_conversion_programa
        }
    
    # Nota: ROAS (Return on Ad Spend) requeriría valores de matrículas, que actualmente no están disponibles
    # Cuando estén disponibles, se calculará como: ROAS = Ingresos / Gasto en Publicidad
    
    return {
        'costo_total': costo_total,
        'total_leads': total_leads,
        'total_matriculas': total_matriculas,
        'cpl': cpl,  # Costo por lead
        'cpa': cpa,  # Costo por adquisición (matrícula)
        'tasa_conversion': tasa_conversion,  # Tasa de conversión general
        'metricas_por_marca': metricas_por_marca,
        'metricas_por_origen': metricas_por_origen,
        'metricas_por_programa': metricas_por_programa
    }


if __name__ == "__main__":
    try:
        # Importar funciones de carga de datos
        from cargar_datos_individuales import cargar_datos_leads, cargar_datos_matriculas
        
        # Cargar datos
        print("Cargando datos de leads...")
        df_leads = cargar_datos_leads("datos/leads_ejemplo.csv")
        
        print("\nCargando datos de matrículas...")
        df_matriculas = cargar_datos_matriculas("datos/matriculas_ejemplo.csv")
        
        # Definir el presupuesto total para el período (ejemplo)
        presupuesto_total = 1200.0  # USD
        
        # Distribuir costos entre los leads
        print("\nDistribuyendo costos entre los leads...")
        df_leads_con_costo = distribuir_costo_leads(df_leads, presupuesto_total)
        print("Ejemplo de leads con costos distribuidos:")
        print(df_leads_con_costo[['id_lead', 'origen', 'costo_estimado']].head())
        
        # Calcular métricas básicas
        print("\nCalculando métricas básicas...")
        metricas = calcular_metricas_basicas(df_leads_con_costo, df_matriculas)
        
        print(f"\nCosto total de adquisición: ${metricas['costo_total']:.2f}")
        print(f"Total de leads: {metricas['total_leads']}")
        print(f"Total de matrículas: {metricas['total_matriculas']}")
        print(f"Costo por lead (CPL): ${metricas['cpl']:.2f}")
        print(f"Costo por adquisición (CPA): ${metricas['cpa']:.2f}")
        print(f"Tasa de conversión general: {metricas['tasa_conversion']:.2f}%")
        
        print("\nMétricas por marca:")
        for marca, datos in metricas['metricas_por_marca'].items():
            print(f"  {marca}: Leads: {datos['leads']}, Matrículas: {datos['matriculas']}, "
                  f"Conversión: {datos['tasa_conversion']:.2f}%, CPA: ${datos['cpa']:.2f}")
        
        print("\nMétricas por origen (Top 3 por tasa de conversión):")
        origenes_ordenados = sorted(
            metricas['metricas_por_origen'].items(),
            key=lambda x: x[1]['tasa_conversion'],
            reverse=True
        )[:3]
        for origen, datos in origenes_ordenados:
            print(f"  {origen}: Leads: {datos['leads']}, Matrículas: {datos['matriculas']}, "
                  f"Conversión: {datos['tasa_conversion']:.2f}%, CPA: ${datos['cpa']:.2f}")
        
        print("\nMétricas por programa (Top 3 por tasa de conversión):")
        programas_ordenados = sorted(
            metricas['metricas_por_programa'].items(),
            key=lambda x: x[1]['tasa_conversion'],
            reverse=True
        )[:3]
        for programa, datos in programas_ordenados:
            print(f"  {programa}: Leads: {datos['leads']}, Matrículas: {datos['matriculas']}, "
                  f"Conversión: {datos['tasa_conversion']:.2f}%, CPA: ${datos['cpa']:.2f}")
            
        print("\nNota: El cálculo de ROAS (Return on Ad Spend) requiere valores de matrículas, que actualmente no están disponibles.")
        
    except (ImportError, FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 