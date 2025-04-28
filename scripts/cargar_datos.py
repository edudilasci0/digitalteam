"""
Módulo para cargar datos de CRM y planificación de campañas de marketing.
"""
import pandas as pd
import os
from datetime import datetime


def cargar_datos_crm(ruta_archivo):
    """
    Carga datos de leads y matrículas desde un archivo CSV.
    
    Args:
        ruta_archivo (str): Ruta al archivo CSV con los datos de CRM.
        
    Returns:
        pandas.DataFrame: DataFrame con los datos cargados.
        
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
        columnas_requeridas = ['Marca', 'Canal', 'ID Convocatoria', 'Fecha', 'Leads', 'Matrículas']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            raise ValueError(f"Faltan columnas requeridas en el archivo: {columnas_faltantes}")
            
        # Convertir columnas de fecha
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        
        # Asegurar tipos de datos
        df['Leads'] = df['Leads'].astype(int)
        df['Matrículas'] = df['Matrículas'].astype(int)
        
        return df
    
    except pd.errors.ParserError:
        raise ValueError("El archivo no tiene el formato CSV esperado")
    except Exception as e:
        raise ValueError(f"Error al cargar los datos: {str(e)}")


def cargar_datos_planificacion(ruta_archivo):
    """
    Carga datos de planificación de campañas desde un archivo CSV.
    
    Args:
        ruta_archivo (str): Ruta al archivo CSV con los datos de planificación.
        
    Returns:
        pandas.DataFrame: DataFrame con los datos de planificación.
        
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
        columnas_requeridas = [
            'Marca', 'Canal', 'ID Convocatoria', 'Fecha Inicio', 'Fecha Fin',
            'Presupuesto Asignado (USD)', 'Objetivo Leads', 'Objetivo Matrículas'
        ]
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            raise ValueError(f"Faltan columnas requeridas en el archivo: {columnas_faltantes}")
            
        # Convertir columnas de fecha
        df['Fecha Inicio'] = pd.to_datetime(df['Fecha Inicio'])
        df['Fecha Fin'] = pd.to_datetime(df['Fecha Fin'])
        
        # Asegurar tipos de datos
        df['Presupuesto Asignado (USD)'] = df['Presupuesto Asignado (USD)'].astype(float)
        df['Objetivo Leads'] = df['Objetivo Leads'].astype(int)
        df['Objetivo Matrículas'] = df['Objetivo Matrículas'].astype(int)
        
        return df
    
    except pd.errors.ParserError:
        raise ValueError("El archivo no tiene el formato CSV esperado")
    except Exception as e:
        raise ValueError(f"Error al cargar los datos: {str(e)}")


if __name__ == "__main__":
    # Ejemplo de uso
    try:
        print("Cargando datos de CRM...")
        datos_crm = cargar_datos_crm("../datos/leads_matriculas_reales.csv")
        print(f"Datos cargados: {len(datos_crm)} registros")
        print(datos_crm.head())
        
        print("\nCargando datos de planificación...")
        datos_planificacion = cargar_datos_planificacion("../datos/planificacion_quincenal.csv")
        print(f"Datos cargados: {len(datos_planificacion)} registros")
        print(datos_planificacion.head())
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 