"""
Módulo para exportar datos del sistema a formatos compatibles con Power BI Online.
"""
import pandas as pd
import os
from datetime import datetime, timedelta


def crear_estructura_powerbi(dict_metricas, datos_prediccion, dir_salida="outputs"):
    """
    Genera archivos Excel estructurados y optimizados para importar en Power BI Online.
    
    Args:
        dict_metricas (dict): Diccionario con DataFrames de métricas calculadas.
        datos_prediccion (pandas.DataFrame): DataFrame con predicciones.
        dir_salida (str): Directorio donde guardar los archivos.
        
    Returns:
        str: Ruta al archivo Excel generado.
    """
    # Crear directorio si no existe
    os.makedirs(dir_salida, exist_ok=True)
    
    # Obtener fecha actual para nombre de archivo
    fecha = datetime.now().strftime("%Y%m%d")
    archivo_excel = f"{dir_salida}/PowerBI_Matriculas_{fecha}.xlsx"
    
    # Crear un Excel con múltiples hojas, optimizado para Power BI
    with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
        # Tabla de hechos principal - Métricas combinadas (para modelos relacionales)
        dict_metricas['complete_report'].to_excel(writer, sheet_name='Hechos_Metricas', index=False)
        
        # Tabla de hechos - Predicciones (más detallada)
        columnas_clave = ['Marca', 'Canal', 'ID Convocatoria', 'Duracion Semanas', 
                         'Leads Actuales', 'Matrículas Actuales', 'Matrículas Esperadas',
                         'CPL Real (USD)', 'CPA Real (USD)', 'CPA Esperado (USD)',
                         'Tasa de Conversión (%)', 'Porcentaje Avance (%)', 'Estado Convocatoria']
        
        # Seleccionar solo columnas relevantes y asegurar que existan
        columnas_disponibles = [col for col in columnas_clave if col in datos_prediccion.columns]
        datos_prediccion_clean = datos_prediccion[columnas_disponibles].copy()
        
        # Añadir columna de fecha para relacionar con dimensión tiempo
        datos_prediccion_clean['Fecha Reporte'] = datetime.now().strftime("%Y-%m-%d")
        datos_prediccion_clean.to_excel(writer, sheet_name='Hechos_Predicciones', index=False)
        
        # Dimensión Tiempo (para filtrados por fecha en Power BI)
        crear_dimension_tiempo(writer)
        
        # Dimensión Convocatorias
        crear_dimension_convocatorias(datos_prediccion, writer)
        
        # Dimensión Canales
        crear_dimension_canales(dict_metricas['complete_report'], writer)
        
        # Dimensión Marcas
        crear_dimension_marcas(dict_metricas['complete_report'], writer)
    
    print(f"Archivo Excel para Power BI generado: {archivo_excel}")
    return archivo_excel


def crear_dimension_tiempo(writer):
    """
    Crea una tabla de dimensión de tiempo para usar en Power BI.
    
    Args:
        writer: Objeto ExcelWriter donde escribir la tabla.
    """
    # Crear rango de fechas desde 3 meses atrás hasta 6 meses adelante
    hoy = datetime.now()
    fecha_inicio = (hoy - timedelta(days=90)).replace(day=1)  # Primer día de hace 3 meses
    fecha_fin = (hoy + timedelta(days=180))  # 6 meses en el futuro
    
    # Generar todas las fechas en el rango
    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin)
    
    # Crear DataFrame con dimensiones de tiempo útiles para Power BI
    calendario = pd.DataFrame({
        'Fecha': fechas,
        'Fecha_Key': fechas.strftime('%Y%m%d'),  # Clave para relaciones
        'Año': fechas.year,
        'Trimestre': fechas.quarter,
        'Mes': fechas.month,
        'Mes_Nombre': fechas.strftime('%B'),
        'Semana': fechas.isocalendar().week,
        'Dia': fechas.day,
        'DiaSemana': fechas.dayofweek,
        'DiaSemana_Nombre': fechas.strftime('%A'),
        'EsFeriado': False,  # Se podría mejorar con una lista de feriados
        'EsFinDeSemana': fechas.dayofweek >= 5
    })
    
    # Guardar en Excel
    calendario.to_excel(writer, sheet_name='Dim_Tiempo', index=False)


def crear_dimension_convocatorias(datos_prediccion, writer):
    """
    Crea una tabla de dimensión de convocatorias para usar en Power BI.
    
    Args:
        datos_prediccion (pandas.DataFrame): DataFrame con datos de predicción.
        writer: Objeto ExcelWriter donde escribir la tabla.
    """
    if 'ID Convocatoria' in datos_prediccion.columns:
        # Extraer información única de convocatorias
        convocatorias = datos_prediccion[['ID Convocatoria', 'Fecha Inicio', 
                                        'Fecha Fin', 'Duracion Semanas']].drop_duplicates()
        
        # Añadir campos adicionales útiles para Power BI
        if 'Fecha Inicio' in convocatorias.columns and 'Fecha Fin' in convocatorias.columns:
            convocatorias['Duración Días'] = (pd.to_datetime(convocatorias['Fecha Fin']) - 
                                             pd.to_datetime(convocatorias['Fecha Inicio'])).dt.days
            
            # Categorizar las convocatorias por duración
            def categorizar_duracion(semanas):
                if semanas <= 6:
                    return 'Corta'
                elif semanas <= 12:
                    return 'Media'
                else:
                    return 'Larga'
            
            convocatorias['Categoría Duración'] = convocatorias['Duracion Semanas'].apply(categorizar_duracion)
        
        # Guardar en Excel
        convocatorias.to_excel(writer, sheet_name='Dim_Convocatorias', index=False)


def crear_dimension_canales(datos_metricas, writer):
    """
    Crea una tabla de dimensión de canales para usar en Power BI.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas calculadas.
        writer: Objeto ExcelWriter donde escribir la tabla.
    """
    if 'Canal' in datos_metricas.columns:
        # Extraer canales únicos
        canales = datos_metricas[['Canal']].drop_duplicates()
        
        # Añadir campos útiles para categorización
        canales['Tipo Canal'] = canales['Canal'].apply(categorizar_canal)
        
        # Guardar en Excel
        canales.to_excel(writer, sheet_name='Dim_Canales', index=False)


def crear_dimension_marcas(datos_metricas, writer):
    """
    Crea una tabla de dimensión de marcas para usar en Power BI.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas calculadas.
        writer: Objeto ExcelWriter donde escribir la tabla.
    """
    if 'Marca' in datos_metricas.columns:
        # Extraer marcas únicas
        marcas = datos_metricas[['Marca']].drop_duplicates()
        
        # Añadir campos útiles para categorización (ejemplo)
        marcas['Segmento'] = 'Educación Superior'  # Por defecto, se podría personalizar
        
        # Guardar en Excel
        marcas.to_excel(writer, sheet_name='Dim_Marcas', index=False)


def categorizar_canal(canal):
    """
    Categoriza un canal de marketing según su tipo.
    
    Args:
        canal (str): Nombre del canal.
        
    Returns:
        str: Categoría del canal.
    """
    canal = canal.lower()
    if 'facebook' in canal or 'instagram' in canal or 'twitter' in canal or 'linkedin' in canal:
        return 'Social Media'
    elif 'google' in canal or 'bing' in canal or 'search' in canal:
        return 'Search'
    elif 'email' in canal or 'mail' in canal:
        return 'Email Marketing'
    else:
        return 'Otros'


def generar_instrucciones_powerbi(archivo_excel, dir_salida="outputs"):
    """
    Genera un archivo de texto con instrucciones para importar el Excel en Power BI Online.
    
    Args:
        archivo_excel (str): Ruta al archivo Excel generado.
        dir_salida (str): Directorio donde guardar el archivo de instrucciones.
        
    Returns:
        str: Ruta al archivo de instrucciones.
    """
    instrucciones = f"""
INSTRUCCIONES PARA IMPORTAR DATOS EN POWER BI ONLINE

1. Accede a Power BI desde tu cuenta de Microsoft 365/Outlook en: https://app.powerbi.com

2. Sigue estos pasos para importar el archivo Excel:
   - Haz clic en "Mi área de trabajo" en el menú lateral
   - Haz clic en el botón "+ Nuevo" en la esquina superior derecha
   - Selecciona "Conjunto de datos"
   - Navega y selecciona el archivo: {os.path.basename(archivo_excel)}
   - Haz clic en "Abrir"

3. Para crear un informe a partir de estos datos:
   - Busca el conjunto de datos recién creado
   - Haz clic en el icono "Crear informe" junto al conjunto de datos

4. Estructura óptima del modelo de datos:
   - Relaciona "Hechos_Metricas" con "Dim_Canales" usando el campo "Canal"
   - Relaciona "Hechos_Metricas" con "Dim_Marcas" usando el campo "Marca"
   - Relaciona "Hechos_Predicciones" con "Dim_Convocatorias" usando "ID Convocatoria"
   - Relaciona "Hechos_Predicciones" con "Dim_Tiempo" usando "Fecha Reporte" y "Fecha"

5. Visualizaciones recomendadas:
   - Gráfico de barras para CPL Real vs Objetivo
   - Gráfico de barras para CPA Real
   - Tarjetas para mostrar KPIs principales
   - Gráfico de líneas para tendencia de conversión
   - Gráfico de medidor para % de avance de convocatorias
   - Tabla con detalle de métricas por marca y canal
   - Filtros por fecha, marca, canal y estado de convocatoria

Para obtener ayuda adicional, consulta la documentación de Power BI: 
https://docs.microsoft.com/es-es/power-bi/
    """
    
    # Escribir instrucciones en un archivo
    archivo_instrucciones = f"{dir_salida}/Instrucciones_PowerBI.txt"
    with open(archivo_instrucciones, 'w', encoding='utf-8') as f:
        f.write(instrucciones)
    
    return archivo_instrucciones


if __name__ == "__main__":
    # Ejemplo de uso
    from load_data import cargar_datos_crm, cargar_datos_planificacion
    from validate_data import validar_datos_crm, validar_datos_planificacion
    from calculate_metrics import generar_reporte_metricas
    from rule_based_predictor import predecir_matriculas
    
    try:
        datos_crm = cargar_datos_crm("../data/leads_matriculas_reales.csv")
        datos_planificacion = cargar_datos_planificacion("../data/planificacion_quincenal.csv")
        
        validar_datos_crm(datos_crm)
        validar_datos_planificacion(datos_planificacion)
        
        metricas = generar_reporte_metricas(datos_crm, datos_planificacion)
        prediccion = predecir_matriculas(datos_crm, datos_planificacion)
        
        # Generar archivo para Power BI
        archivo_excel = crear_estructura_powerbi(metricas, prediccion, "../outputs")
        
        # Generar instrucciones
        archivo_instrucciones = generar_instrucciones_powerbi(archivo_excel, "../outputs")
        
        print(f"Archivo de datos para Power BI generado: {archivo_excel}")
        print(f"Archivo de instrucciones generado: {archivo_instrucciones}")
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 