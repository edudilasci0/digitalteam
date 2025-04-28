"""
Módulo para crear reportes visuales con barras de progreso y estado.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime


def configurar_estilo_grafico():
    """Configura el estilo de los gráficos."""
    sns.set(style="whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12


def crear_reporte_cpl(datos_metricas, dir_salida="../outputs"):
    """
    Crea un reporte visual del CPL por marca y canal.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas de CPL.
        dir_salida (str): Directorio donde guardar el reporte.
    
    Returns:
        str: Ruta al archivo de reporte generado.
    """
    configurar_estilo_grafico()
    
    # Crear gráfico de barras para CPL
    plt.figure(figsize=(14, 8))
    
    ax = sns.barplot(x='Marca', y='CPL Real (USD)', hue='Canal', data=datos_metricas)
    
    # Añadir línea de CPL objetivo
    for i, fila in datos_metricas.iterrows():
        plt.hlines(y=fila['CPL Objetivo (USD)'], 
                  xmin=i-0.4, 
                  xmax=i+0.4, 
                  colors='red', 
                  linestyles='dashed')
    
    plt.title('CPL Real vs Objetivo por Marca y Canal')
    plt.ylabel('CPL (USD)')
    plt.xlabel('Marca')
    plt.tight_layout()
    
    # Crear directorio si no existe
    os.makedirs(dir_salida, exist_ok=True)
    
    # Generar nombre de archivo con fecha
    fecha = datetime.now().strftime("%Y%m%d")
    nombre_archivo = f"{dir_salida}/cpl_report_{fecha}.png"
    
    # Guardar gráfico
    plt.savefig(nombre_archivo)
    plt.close()
    
    return nombre_archivo


def crear_reporte_cpa(datos_metricas, dir_salida="../outputs"):
    """
    Crea un reporte visual del CPA por marca y canal.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas de CPA.
        dir_salida (str): Directorio donde guardar el reporte.
    
    Returns:
        str: Ruta al archivo de reporte generado.
    """
    configurar_estilo_grafico()
    
    # Crear gráfico de barras para CPA
    plt.figure(figsize=(14, 8))
    
    ax = sns.barplot(x='Marca', y='CPA Real (USD)', hue='Canal', data=datos_metricas)
    
    plt.title('CPA Real por Marca y Canal')
    plt.ylabel('CPA (USD)')
    plt.xlabel('Marca')
    plt.tight_layout()
    
    # Crear directorio si no existe
    os.makedirs(dir_salida, exist_ok=True)
    
    # Generar nombre de archivo con fecha
    fecha = datetime.now().strftime("%Y%m%d")
    nombre_archivo = f"{dir_salida}/cpa_report_{fecha}.png"
    
    # Guardar gráfico
    plt.savefig(nombre_archivo)
    plt.close()
    
    return nombre_archivo


def crear_reporte_conversion(datos_metricas, dir_salida="../outputs"):
    """
    Crea un reporte visual de la tasa de conversión por marca y canal.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas de conversión.
        dir_salida (str): Directorio donde guardar el reporte.
    
    Returns:
        str: Ruta al archivo de reporte generado.
    """
    configurar_estilo_grafico()
    
    # Crear gráfico de barras para tasa de conversión
    plt.figure(figsize=(14, 8))
    
    ax = sns.barplot(x='Marca', y='Tasa de Conversión (%)', hue='Canal', data=datos_metricas)
    
    plt.title('Tasa de Conversión por Marca y Canal')
    plt.ylabel('Tasa de Conversión (%)')
    plt.xlabel('Marca')
    plt.tight_layout()
    
    # Crear directorio si no existe
    os.makedirs(dir_salida, exist_ok=True)
    
    # Generar nombre de archivo con fecha
    fecha = datetime.now().strftime("%Y%m%d")
    nombre_archivo = f"{dir_salida}/conversion_report_{fecha}.png"
    
    # Guardar gráfico
    plt.savefig(nombre_archivo)
    plt.close()
    
    return nombre_archivo


def crear_reporte_prediccion(datos_prediccion, dir_salida="../outputs"):
    """
    Crea un reporte visual de la predicción de matrículas.
    
    Args:
        datos_prediccion (pandas.DataFrame): DataFrame con predicciones.
        dir_salida (str): Directorio donde guardar el reporte.
    
    Returns:
        str: Ruta al archivo de reporte generado.
    """
    configurar_estilo_grafico()
    
    # Crear gráfico de barras para matrículas actuales vs esperadas
    plt.figure(figsize=(14, 8))
    
    # Preparar datos para graficación
    datos_grafico = datos_prediccion.melt(
        id_vars=['Marca', 'Canal', 'ID Convocatoria'],
        value_vars=['Matrículas Actuales', 'Matrículas Esperadas'],
        var_name='Tipo',
        value_name='Cantidad'
    )
    
    ax = sns.barplot(x='Marca', y='Cantidad', hue='Tipo', data=datos_grafico)
    
    plt.title('Matrículas Actuales vs Esperadas por Marca y Canal')
    plt.ylabel('Cantidad de Matrículas')
    plt.xlabel('Marca')
    plt.tight_layout()
    
    # Crear directorio si no existe
    os.makedirs(dir_salida, exist_ok=True)
    
    # Generar nombre de archivo con fecha
    fecha = datetime.now().strftime("%Y%m%d")
    nombre_archivo = f"{dir_salida}/prediction_report_{fecha}.png"
    
    # Guardar gráfico
    plt.savefig(nombre_archivo)
    plt.close()
    
    return nombre_archivo


def crear_reporte_progreso_convocatoria(datos_prediccion, dir_salida="../outputs"):
    """
    Crea un reporte visual del progreso de las convocatorias.
    
    Args:
        datos_prediccion (pandas.DataFrame): DataFrame con predicciones.
        dir_salida (str): Directorio donde guardar el reporte.
    
    Returns:
        str: Ruta al archivo de reporte generado.
    """
    configurar_estilo_grafico()
    
    # Crear gráfico de barras para el progreso de las convocatorias
    plt.figure(figsize=(14, 8))
    
    # Ordenar por ID Convocatoria
    datos_prediccion = datos_prediccion.sort_values(['ID Convocatoria', 'Marca', 'Canal'])
    
    # Crear barras horizontales que muestran el progreso
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Crear etiquetas combinadas para el eje Y
    datos_prediccion['Etiqueta'] = datos_prediccion['ID Convocatoria'] + ' - ' + datos_prediccion['Marca'] + ' (' + datos_prediccion['Canal'] + ')'
    
    # Ordenar por duración para mejor visualización
    datos_prediccion = datos_prediccion.sort_values(['Duracion Semanas', 'ID Convocatoria', 'Marca'])
    
    # Crear barras de progreso
    ax.barh(datos_prediccion['Etiqueta'], datos_prediccion['Duracion Semanas'] * 7, 
            color='lightgrey', edgecolor='grey', alpha=0.5)
    
    ax.barh(datos_prediccion['Etiqueta'], datos_prediccion['Tiempo Transcurrido (días)'], 
            color='steelblue', edgecolor='darkblue')
    
    # Agregar porcentaje de avance como texto
    for i, fila in datos_prediccion.iterrows():
        ax.text(fila['Tiempo Transcurrido (días)'] + 0.5, i, 
                f"{fila['Porcentaje Avance (%)']:.1f}%", 
                va='center', color='darkblue')
    
    # Agregar estado de la convocatoria
    for i, fila in datos_prediccion.iterrows():
        ax.text(fila['Duracion Semanas'] * 7 + 1, i, 
                fila['Estado Convocatoria'], 
                va='center', color='grey')
    
    plt.title('Progreso de las Convocatorias')
    plt.xlabel('Días')
    plt.ylabel('Convocatoria')
    plt.tight_layout()
    
    # Crear directorio si no existe
    os.makedirs(dir_salida, exist_ok=True)
    
    # Generar nombre de archivo con fecha
    fecha = datetime.now().strftime("%Y%m%d")
    nombre_archivo = f"{dir_salida}/conv_progress_report_{fecha}.png"
    
    # Guardar gráfico
    plt.savefig(nombre_archivo)
    plt.close()
    
    return nombre_archivo


def generar_todos_reportes(dict_metricas, datos_prediccion, dir_salida="../outputs"):
    """
    Genera todos los reportes visuales.
    
    Args:
        dict_metricas (dict): Diccionario con DataFrames de métricas.
        datos_prediccion (pandas.DataFrame): DataFrame con predicciones.
        dir_salida (str): Directorio donde guardar los reportes.
    
    Returns:
        dict: Diccionario con rutas a los archivos de reportes generados.
    """
    reportes = {}
    
    reportes['cpl'] = crear_reporte_cpl(dict_metricas['cpl'], dir_salida)
    reportes['cpa'] = crear_reporte_cpa(dict_metricas['cpa'], dir_salida)
    reportes['conversion'] = crear_reporte_conversion(dict_metricas['conversion'], dir_salida)
    reportes['prediction'] = crear_reporte_prediccion(datos_prediccion, dir_salida)
    reportes['conv_progress'] = crear_reporte_progreso_convocatoria(datos_prediccion, dir_salida)
    
    return reportes


# Mantener compatibilidad con el código existente
setup_plot_style = configurar_estilo_grafico
create_cpl_report = crear_reporte_cpl
create_cpa_report = crear_reporte_cpa
create_conversion_report = crear_reporte_conversion
create_prediction_report = crear_reporte_prediccion
create_convocation_progress_report = crear_reporte_progreso_convocatoria
generate_all_reports = generar_todos_reportes


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
        
        reportes = generar_todos_reportes(metricas, prediccion)
        
        print("Reportes generados:")
        for tipo_reporte, ruta_archivo in reportes.items():
            print(f"- {tipo_reporte}: {ruta_archivo}")
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 