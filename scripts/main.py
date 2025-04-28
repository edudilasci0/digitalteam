"""
Script principal que integra todos los módulos del sistema de predicción y optimización.
"""
import os
import pandas as pd
from datetime import datetime

# Importar módulos del sistema
from load_data import cargar_datos_crm, cargar_datos_planificacion
from validate_data import validar_datos_crm, validar_datos_planificacion
from calculate_metrics import generar_reporte_metricas
from rule_based_predictor import predecir_matriculas
from generate_report import generar_todos_reportes


def ejecutar_pipeline(ruta_archivo_crm, ruta_archivo_planificacion, dir_salida="outputs"):
    """
    Ejecuta el pipeline completo del sistema.
    
    Args:
        ruta_archivo_crm (str): Ruta al archivo de datos CRM.
        ruta_archivo_planificacion (str): Ruta al archivo de planificación.
        dir_salida (str): Directorio para guardar los reportes.
        
    Returns:
        dict: Diccionario con referencias a los reportes generados.
    """
    print(f"Iniciando pipeline con datos de {ruta_archivo_crm} y {ruta_archivo_planificacion}")
    
    # 1. Cargar datos
    print("1. Cargando datos...")
    datos_crm = cargar_datos_crm(ruta_archivo_crm)
    datos_planificacion = cargar_datos_planificacion(ruta_archivo_planificacion)
    
    # 2. Validar datos
    print("2. Validando estructura de datos...")
    validar_datos_crm(datos_crm)
    validar_datos_planificacion(datos_planificacion)
    
    # 3. Calcular métricas
    print("3. Calculando métricas: CPL, CPA y Tasa de Conversión...")
    metricas = generar_reporte_metricas(datos_crm, datos_planificacion)
    
    # 4. Realizar predicción
    print("4. Realizando predicción basada en la duración de las convocatorias...")
    prediccion = predecir_matriculas(datos_crm, datos_planificacion)
    
    # 5. Generar reportes
    print("5. Generando reportes visuales...")
    reportes = generar_todos_reportes(metricas, prediccion, dir_salida)
    
    print("Pipeline completado exitosamente.")
    return reportes


# Mantener compatibilidad con el código existente
run_pipeline = ejecutar_pipeline


if __name__ == "__main__":
    # Datos de ejemplo para ejecutar el pipeline
    # Usar rutas relativas al directorio actual donde está main.py
    ruta_archivo_crm = "data/leads_matriculas_reales.csv"
    ruta_archivo_planificacion = "data/planificacion_quincenal.csv"
    
    # Crear directorio de salida si no existe
    dir_salida = "outputs"
    os.makedirs(dir_salida, exist_ok=True)
    
    try:
        reportes = ejecutar_pipeline(ruta_archivo_crm, ruta_archivo_planificacion, dir_salida)
        
        print("\nReportes generados:")
        for tipo_reporte, ruta_archivo in reportes.items():
            print(f"- {tipo_reporte}: {ruta_archivo}")
        
    except Exception as e:
        print(f"Error al ejecutar el pipeline: {e}") 