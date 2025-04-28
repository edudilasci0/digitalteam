"""
Módulo para cargar datos CSV/Excel del CRM y de planificación.
"""
import os
import pandas as pd


def cargar_datos_crm(ruta_archivo):
    """
    Carga datos de leads y matrículas desde un archivo CSV o Excel.
    
    Args:
        ruta_archivo (str): Ruta al archivo CSV o Excel.
        
    Returns:
        pandas.DataFrame: DataFrame con los datos cargados.
    """
    _, ext = os.path.splitext(ruta_archivo)
    
    if ext.lower() == '.csv':
        df = pd.read_csv(ruta_archivo)
    elif ext.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(ruta_archivo)
    else:
        raise ValueError(f"Formato de archivo no soportado: {ext}")
    
    return df


def cargar_datos_planificacion(ruta_archivo):
    """
    Carga datos de planificación quincenal desde un archivo CSV o Excel.
    
    Args:
        ruta_archivo (str): Ruta al archivo CSV o Excel.
        
    Returns:
        pandas.DataFrame: DataFrame con los datos de planificación.
    """
    _, ext = os.path.splitext(ruta_archivo)
    
    if ext.lower() == '.csv':
        df = pd.read_csv(ruta_archivo)
    elif ext.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(ruta_archivo)
    else:
        raise ValueError(f"Formato de archivo no soportado: {ext}")
    
    return df


# Mantener compatibilidad con el código existente
load_crm_data = cargar_datos_crm
load_planning_data = cargar_datos_planificacion


if __name__ == "__main__":
    # Ejemplo de uso
    try:
        datos_crm = cargar_datos_crm("../data/leads_matriculas_reales.csv")
        datos_planificacion = cargar_datos_planificacion("../data/planificacion_quincenal.csv")
        
        print("Datos CRM cargados:")
        print(datos_crm.head())
        print("\nDatos de planificación cargados:")
        print(datos_planificacion.head())
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}") 