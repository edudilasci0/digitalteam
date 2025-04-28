"""
Módulo para cargar datos individuales de leads y matrículas.
"""
import pandas as pd
import os
from datetime import datetime


def cargar_datos_leads(ruta_archivo):
    """
    Carga datos individuales de leads desde un archivo CSV.
    
    Args:
        ruta_archivo (str): Ruta al archivo CSV con los datos de leads.
        
    Returns:
        pandas.DataFrame: DataFrame con los datos de leads.
        
    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el formato del archivo no es el esperado.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")
    
    try:
        # Cargar datos
        df = pd.read_csv(ruta_archivo)
        
        # Verificar columnas requeridas
        columnas_requeridas = ['id_lead', 'fecha_creacion', 'origen', 'programa', 'marca', 'estado']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            raise ValueError(f"Faltan columnas requeridas en el archivo: {columnas_faltantes}")
            
        # Convertir columnas de fecha
        df['fecha_creacion'] = pd.to_datetime(df['fecha_creacion'])
        
        return df
    
    except pd.errors.ParserError:
        raise ValueError("El archivo no tiene el formato CSV esperado")
    except Exception as e:
        raise ValueError(f"Error al cargar los datos: {str(e)}")


def cargar_datos_matriculas(ruta_archivo):
    """
    Carga datos individuales de matrículas desde un archivo CSV.
    
    Args:
        ruta_archivo (str): Ruta al archivo CSV con los datos de matrículas.
        
    Returns:
        pandas.DataFrame: DataFrame con los datos de matrículas.
        
    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el formato del archivo no es el esperado.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")
    
    try:
        # Cargar datos
        df = pd.read_csv(ruta_archivo)
        
        # Verificar columnas requeridas
        columnas_requeridas = ['id_matricula', 'id_lead', 'fecha_matricula', 'programa', 'marca']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            raise ValueError(f"Faltan columnas requeridas en el archivo: {columnas_faltantes}")
            
        # Convertir columnas de fecha
        df['fecha_matricula'] = pd.to_datetime(df['fecha_matricula'])
        
        return df
    
    except pd.errors.ParserError:
        raise ValueError("El archivo no tiene el formato CSV esperado")
    except Exception as e:
        raise ValueError(f"Error al cargar los datos: {str(e)}")


def calcular_conversion(df_leads, df_matriculas):
    """
    Calcula la tasa de conversión entre leads y matrículas.
    
    Args:
        df_leads (pandas.DataFrame): DataFrame con datos de leads.
        df_matriculas (pandas.DataFrame): DataFrame con datos de matrículas.
        
    Returns:
        dict: Diccionario con métricas de conversión.
    """
    total_leads = len(df_leads)
    total_matriculas = len(df_matriculas)
    
    # Calcular tasa de conversión general
    tasa_conversion = (total_matriculas / total_leads) * 100 if total_leads > 0 else 0
    
    # Calcular conversión por marca
    conversion_por_marca = {}
    for marca in df_leads['marca'].unique():
        leads_marca = len(df_leads[df_leads['marca'] == marca])
        matriculas_marca = len(df_matriculas[df_matriculas['marca'] == marca])
        
        tasa = (matriculas_marca / leads_marca) * 100 if leads_marca > 0 else 0
        conversion_por_marca[marca] = {
            'leads': leads_marca,
            'matriculas': matriculas_marca,
            'tasa_conversion': tasa
        }
    
    # Calcular conversión por programa
    conversion_por_programa = {}
    for programa in df_leads['programa'].unique():
        leads_programa = len(df_leads[df_leads['programa'] == programa])
        matriculas_programa = len(df_matriculas[df_matriculas['programa'] == programa])
        
        tasa = (matriculas_programa / leads_programa) * 100 if leads_programa > 0 else 0
        conversion_por_programa[programa] = {
            'leads': leads_programa,
            'matriculas': matriculas_programa,
            'tasa_conversion': tasa
        }
    
    # Calcular conversión por origen
    conversion_por_origen = {}
    for origen in df_leads['origen'].unique():
        leads_origen = len(df_leads[df_leads['origen'] == origen])
        
        # Para calcular matrículas por origen, necesitamos cruzar con la tabla de leads
        leads_id_origen = df_leads[df_leads['origen'] == origen]['id_lead'].tolist()
        matriculas_origen = len(df_matriculas[df_matriculas['id_lead'].isin(leads_id_origen)])
        
        tasa = (matriculas_origen / leads_origen) * 100 if leads_origen > 0 else 0
        conversion_por_origen[origen] = {
            'leads': leads_origen,
            'matriculas': matriculas_origen,
            'tasa_conversion': tasa
        }
    
    return {
        'total_leads': total_leads,
        'total_matriculas': total_matriculas,
        'tasa_conversion_general': tasa_conversion,
        'conversion_por_marca': conversion_por_marca,
        'conversion_por_programa': conversion_por_programa,
        'conversion_por_origen': conversion_por_origen
    }


if __name__ == "__main__":
    # Ejemplo de uso
    try:
        print("Cargando datos de leads...")
        df_leads = cargar_datos_leads("datos/leads_ejemplo.csv")
        print(f"Datos cargados: {len(df_leads)} registros")
        print(df_leads.head())
        
        print("\nCargando datos de matrículas...")
        df_matriculas = cargar_datos_matriculas("datos/matriculas_ejemplo.csv")
        print(f"Datos cargados: {len(df_matriculas)} registros")
        print(df_matriculas.head())
        
        print("\nCalculando métricas de conversión...")
        metricas = calcular_conversion(df_leads, df_matriculas)
        
        print(f"\nTotal leads: {metricas['total_leads']}")
        print(f"Total matrículas: {metricas['total_matriculas']}")
        print(f"Tasa de conversión general: {metricas['tasa_conversion_general']:.2f}%")
        
        print("\nConversión por marca:")
        for marca, datos in metricas['conversion_por_marca'].items():
            print(f"  {marca}: {datos['tasa_conversion']:.2f}% ({datos['matriculas']}/{datos['leads']})")
        
        print("\nConversión por programa (Top 3):")
        programas_ordenados = sorted(
            metricas['conversion_por_programa'].items(),
            key=lambda x: x[1]['tasa_conversion'],
            reverse=True
        )[:3]
        for programa, datos in programas_ordenados:
            print(f"  {programa}: {datos['tasa_conversion']:.2f}% ({datos['matriculas']}/{datos['leads']})")
        
        print("\nConversión por origen (Top 3):")
        origenes_ordenados = sorted(
            metricas['conversion_por_origen'].items(),
            key=lambda x: x[1]['tasa_conversion'],
            reverse=True
        )[:3]
        for origen, datos in origenes_ordenados:
            print(f"  {origen}: {datos['tasa_conversion']:.2f}% ({datos['matriculas']}/{datos['leads']})")
            
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 