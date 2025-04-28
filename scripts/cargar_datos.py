"""
Módulo para cargar datos de CRM y planificación de campañas de marketing.
Esta versión adaptada utiliza los nuevos formatos de datos individuales de leads y matrículas.
"""
import pandas as pd
import os
from datetime import datetime
from cargar_datos_individuales import cargar_datos_leads, cargar_datos_matriculas


def cargar_y_consolidar_datos(ruta_leads, ruta_matriculas):
    """
    Carga datos de leads y matrículas y los consolida en un formato compatible con el sistema anterior.
    
    Args:
        ruta_leads (str): Ruta al archivo CSV con los datos de leads.
        ruta_matriculas (str): Ruta al archivo CSV con los datos de matrículas.
        
    Returns:
        pandas.DataFrame: DataFrame consolidado con datos de leads y matrículas.
    """
    # Cargar datos usando las nuevas funciones
    df_leads = cargar_datos_leads(ruta_leads)
    df_matriculas = cargar_datos_matriculas(ruta_matriculas)
    
    # Agrupar leads por fecha, marca, programa y origen
    df_leads_agrupados = df_leads.groupby(['fecha_creacion', 'marca', 'programa', 'origen']).size().reset_index(name='Leads')
    
    # Agrupar matrículas por fecha, marca y programa
    df_matriculas_agrupados = df_matriculas.groupby(['fecha_matricula', 'marca', 'programa']).size().reset_index(name='Matrículas')
    
    # Renombrar columnas para compatibilidad
    df_leads_agrupados = df_leads_agrupados.rename(columns={
        'fecha_creacion': 'Fecha',
        'marca': 'Marca',
        'programa': 'ID Convocatoria',  # Asumiendo que programa equivale a ID Convocatoria
        'origen': 'Canal'
    })
    
    # Consolidar los datos (agregados por día)
    # Nota: Esto es una simplificación, podría requerirse una lógica más compleja según el caso de uso
    df_consolidado = pd.merge(
        df_leads_agrupados,
        df_matriculas_agrupados.rename(columns={'fecha_matricula': 'Fecha'}),
        on=['Fecha', 'Marca', 'ID Convocatoria'],
        how='left'
    )
    
    # Rellenar NaNs en matrículas
    df_consolidado['Matrículas'] = df_consolidado['Matrículas'].fillna(0).astype(int)
    
    return df_consolidado


def cargar_datos_crm(ruta_leads, ruta_matriculas):
    """
    Función compatible con la versión anterior que ahora usa los nuevos formatos.
    
    Args:
        ruta_leads (str): Ruta al archivo CSV con los datos de leads.
        ruta_matriculas (str): Ruta al archivo CSV con los datos de matrículas.
        
    Returns:
        pandas.DataFrame: DataFrame con los datos consolidados.
    """
    return cargar_y_consolidar_datos(ruta_leads, ruta_matriculas)


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
    # Ejemplo de uso con los nuevos archivos
    try:
        print("Cargando datos de leads y matrículas...")
        datos_crm = cargar_datos_crm("datos/leads_ejemplo.csv", "datos/matriculas_ejemplo.csv")
        print(f"Datos consolidados: {len(datos_crm)} registros")
        print(datos_crm.head())
        
        print("\nCargando datos de planificación...")
        datos_planificacion = cargar_datos_planificacion("datos/planificacion_quincenal.csv")
        print(f"Datos cargados: {len(datos_planificacion)} registros")
        print(datos_planificacion.head())
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 