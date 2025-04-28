"""
Módulo para validar que los datos cargados contengan las columnas necesarias.
"""
import pandas as pd


def validar_datos_crm(df):
    """
    Valida que el DataFrame de CRM contenga las columnas necesarias.
    
    Args:
        df (pandas.DataFrame): DataFrame con datos de leads y matrículas.
        
    Returns:
        bool: True si el DataFrame es válido, False en caso contrario.
        
    Raises:
        ValueError: Si faltan columnas requeridas.
    """
    columnas_requeridas = ['Fecha', 'Marca', 'Canal', 'Tipo', 'Estado']
    
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    
    if columnas_faltantes:
        raise ValueError(f"Faltan columnas requeridas en los datos CRM: {', '.join(columnas_faltantes)}")
    
    return True


def validar_datos_planificacion(df):
    """
    Valida que el DataFrame de planificación contenga las columnas necesarias.
    
    Args:
        df (pandas.DataFrame): DataFrame con datos de planificación.
        
    Returns:
        bool: True si el DataFrame es válido, False en caso contrario.
        
    Raises:
        ValueError: Si faltan columnas requeridas.
    """
    columnas_requeridas = ['Quincena', 'Marca', 'Canal', 'Presupuesto Asignado (USD)', 'CPL Objetivo (USD)',
                        'ID Convocatoria', 'Fecha Inicio', 'Fecha Fin', 'Duracion Semanas']
    
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    
    if columnas_faltantes:
        raise ValueError(f"Faltan columnas requeridas en los datos de planificación: {', '.join(columnas_faltantes)}")
    
    # Validar que las fechas tengan el formato correcto
    try:
        df['Fecha Inicio'] = pd.to_datetime(df['Fecha Inicio'])
        df['Fecha Fin'] = pd.to_datetime(df['Fecha Fin'])
    except Exception as e:
        raise ValueError(f"Error al convertir fechas: {e}")
    
    # Validar que la duración sea un número positivo
    if (df['Duracion Semanas'] <= 0).any():
        raise ValueError("La duración de las convocatorias debe ser un número positivo")
    
    return True


# Mantener compatibilidad con el código existente
validate_crm_data = validar_datos_crm
validate_planning_data = validar_datos_planificacion


if __name__ == "__main__":
    # Ejemplo de uso
    from load_data import cargar_datos_crm, cargar_datos_planificacion
    
    try:
        datos_crm = cargar_datos_crm("../data/leads_matriculas_reales.csv")
        datos_planificacion = cargar_datos_planificacion("../data/planificacion_quincenal.csv")
        
        if validar_datos_crm(datos_crm):
            print("Datos CRM válidos.")
        
        if validar_datos_planificacion(datos_planificacion):
            print("Datos de planificación válidos.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}") 