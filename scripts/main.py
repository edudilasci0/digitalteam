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
from export_powerbi import crear_estructura_powerbi, generar_instrucciones_powerbi


def ejecutar_pipeline(ruta_archivo_crm, ruta_archivo_planificacion, dir_salida="salidas", formato_reporte="png"):
    """
    Ejecuta el pipeline completo del sistema.
    
    Args:
        ruta_archivo_crm (str): Ruta al archivo de datos CRM.
        ruta_archivo_planificacion (str): Ruta al archivo de planificación.
        dir_salida (str): Directorio para guardar los reportes.
        formato_reporte (str): Formato de reporte: "png" o "powerbi".
        
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
    
    # 5. Generar reportes según el formato solicitado
    reportes = {}
    
    if formato_reporte == "png" or formato_reporte == "todos":
        print("5a. Generando reportes visuales en PNG...")
        reportes_png = generar_todos_reportes(metricas, prediccion, dir_salida)
        reportes.update(reportes_png)
    
    if formato_reporte == "powerbi" or formato_reporte == "todos":
        print("5b. Generando archivo Excel para Power BI...")
        archivo_excel = crear_estructura_powerbi(metricas, prediccion, dir_salida)
        archivo_instrucciones = generar_instrucciones_powerbi(archivo_excel, dir_salida)
        reportes['powerbi_excel'] = archivo_excel
        reportes['powerbi_instrucciones'] = archivo_instrucciones
    
    print("Pipeline completado exitosamente.")
    return reportes


# Mantener compatibilidad con el código existente
run_pipeline = ejecutar_pipeline


if __name__ == "__main__":
    import argparse
    
    # Crear parser para argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Sistema Predictor y Optimizador de Matrículas')
    parser.add_argument('--crm', dest='ruta_crm', default="datos/leads_matriculas_reales.csv", 
                        help='Ruta al archivo CSV de leads y matrículas')
    parser.add_argument('--plan', dest='ruta_plan', default="datos/planificacion_quincenal.csv",
                        help='Ruta al archivo CSV de planificación')
    parser.add_argument('--output', dest='dir_salida', default="salidas",
                        help='Directorio de salida para reportes')
    parser.add_argument('--formato', dest='formato', default="todos", choices=["png", "powerbi", "todos"],
                        help='Formato de reporte: png, powerbi o todos')
    
    args = parser.parse_args()
    
    # Crear directorio de salida si no existe
    os.makedirs(args.dir_salida, exist_ok=True)
    
    try:
        reportes = ejecutar_pipeline(args.ruta_crm, args.ruta_plan, args.dir_salida, args.formato)
        
        print("\nReportes generados:")
        for tipo_reporte, ruta_archivo in reportes.items():
            print(f"- {tipo_reporte}: {ruta_archivo}")
        
        if 'powerbi_excel' in reportes:
            print("\nPara usar los datos en Power BI Online:")
            print(f"1. Accede a Power BI desde tu cuenta de Microsoft 365/Outlook")
            print(f"2. Sigue las instrucciones en el archivo: {reportes['powerbi_instrucciones']}")
        
    except Exception as e:
        print(f"Error al ejecutar el pipeline: {e}") 