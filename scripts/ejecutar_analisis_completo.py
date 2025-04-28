#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script integrador que ejecuta todos los análisis avanzados y genera datos para el dashboard.
Este script centraliza la ejecución de simulaciones, análisis de elasticidad, predicciones
y métricas de confianza, guardando los resultados para su visualización en Power BI.
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import traceback
import importlib
import json

# Configurar logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/analisis_completo_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

# Directorio de salida para resultados
DIRECTORIO_RESULTADOS = 'dashboard/datos/resultados_analisis'

def configurar_entorno():
    """Prepara el entorno para ejecutar todos los análisis."""
    # Crear directorios necesarios
    os.makedirs(DIRECTORIO_RESULTADOS, exist_ok=True)
    
    # Asegurar que scripts/ esté en el path para importar módulos
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    if script_dir not in sys.path:
        sys.path.append(script_dir)
        
    logging.info("Entorno configurado correctamente")

def importar_modulo_seguro(nombre_modulo):
    """Importa un módulo de forma segura, manejando excepciones."""
    try:
        return importlib.import_module(nombre_modulo)
    except (ImportError, ModuleNotFoundError) as e:
        logging.error(f"No se pudo importar el módulo {nombre_modulo}: {str(e)}")
        return None

def ejecutar_carga_datos():
    """Ejecuta el proceso de carga de datos."""
    try:
        logging.info("Iniciando carga de datos...")
        
        # Importar módulo de carga de datos
        cargar_datos = importar_modulo_seguro("cargar_datos")
        if not cargar_datos:
            logging.error("No se pudo importar el módulo de carga de datos")
            return None
        
        # Ejecutar carga de datos CRM
        df_crm = cargar_datos.cargar_datos_crm()
        logging.info(f"Datos CRM cargados: {len(df_crm)} registros")
        
        # Ejecutar carga de datos de planificación
        df_planificacion = cargar_datos.cargar_datos_planificacion()
        logging.info(f"Datos de planificación cargados: {len(df_planificacion)} registros")
        
        return {
            "df_crm": df_crm,
            "df_planificacion": df_planificacion
        }
    except Exception as e:
        logging.error(f"Error en carga de datos: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def ejecutar_analisis_estacionalidad(datos):
    """Ejecuta el análisis de estacionalidad de leads y matrículas."""
    try:
        logging.info("Iniciando análisis de estacionalidad...")
        
        # Importar módulo de estacionalidad
        analisis_estacionalidad = importar_modulo_seguro("analisis_estacionalidad")
        if not analisis_estacionalidad:
            logging.error("No se pudo importar el módulo de análisis de estacionalidad")
            return None
        
        # Preparar datos temporales para análisis
        datos_temporales = analisis_estacionalidad.preparar_datos_temporales(
            datos["df_crm"], 
            "M",  # Frecuencia mensual 
            "fecha_creacion"
        )
        
        # Ejecutar análisis para leads
        resultados_leads = analisis_estacionalidad.analizar_estacionalidad(
            datos_temporales, 
            "leads", 
            periodo_descomposicion="multiplicative"
        )
        
        # Ejecutar análisis para matrículas
        resultados_matriculas = analisis_estacionalidad.analizar_estacionalidad(
            datos_temporales, 
            "matriculas", 
            periodo_descomposicion="multiplicative"
        )
        
        # Guardar resultados
        indices_estacionales_leads = pd.DataFrame(resultados_leads["indices_estacionales"])
        indices_estacionales_matriculas = pd.DataFrame(resultados_matriculas["indices_estacionales"])
        
        # Guardar en formato para Power BI
        indices_estacionales_leads.to_csv(f"{DIRECTORIO_RESULTADOS}/estacionalidad_leads.csv", index=False)
        indices_estacionales_matriculas.to_csv(f"{DIRECTORIO_RESULTADOS}/estacionalidad_matriculas.csv", index=False)
        
        logging.info("Análisis de estacionalidad completado y guardado")
        
        return {
            "estacionalidad_leads": resultados_leads,
            "estacionalidad_matriculas": resultados_matriculas
        }
    except Exception as e:
        logging.error(f"Error en análisis de estacionalidad: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def ejecutar_prediccion_matriculas(datos, resultados_estacionalidad):
    """Ejecuta las predicciones de matrículas."""
    try:
        logging.info("Iniciando predicción de matrículas...")
        
        # Importar módulo de predicción
        predecir_matriculas = importar_modulo_seguro("predecir_matriculas")
        if not predecir_matriculas:
            logging.error("No se pudo importar el módulo de predicción de matrículas")
            return None
        
        # Ejecutar entrenamiento de modelo
        modelo, metricas_evaluacion = predecir_matriculas.entrenar_modelo_prediccion(
            datos["df_crm"],
            resultados_estacionalidad["estacionalidad_leads"]["indices_estacionales"],
            resultados_estacionalidad["estacionalidad_matriculas"]["indices_estacionales"]
        )
        
        # Generar predicciones futuras
        predicciones = predecir_matriculas.generar_prediccion_futura(
            modelo, 
            datos["df_crm"],
            resultados_estacionalidad["estacionalidad_leads"]["indices_estacionales"],
            resultados_estacionalidad["estacionalidad_matriculas"]["indices_estacionales"],
            horizonte_meses=6
        )
        
        # Guardar resultados para Power BI
        df_predicciones = pd.DataFrame(predicciones)
        df_predicciones.to_csv(f"{DIRECTORIO_RESULTADOS}/predicciones_matriculas.csv", index=False)
        
        # Guardar métricas de evaluación
        with open(f"{DIRECTORIO_RESULTADOS}/metricas_prediccion.json", 'w') as f:
            json.dump(metricas_evaluacion, f)
        
        logging.info("Predicción de matrículas completada y guardada")
        
        return {
            "predicciones": predicciones,
            "metricas": metricas_evaluacion
        }
    except Exception as e:
        logging.error(f"Error en predicción de matrículas: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def ejecutar_simulacion_montecarlo(datos, predicciones):
    """Ejecuta simulaciones de Monte Carlo para análisis de escenarios."""
    try:
        logging.info("Iniciando simulación de Monte Carlo...")
        
        # Importar módulo de simulación
        simulacion_montecarlo = importar_modulo_seguro("simulacion_montecarlo")
        if not simulacion_montecarlo:
            logging.error("No se pudo importar el módulo de simulación de Monte Carlo")
            return None
        
        # Ejecutar simulación
        resultados_simulacion = simulacion_montecarlo.ejecutar_simulacion(
            predicciones["predicciones"],
            num_simulaciones=1000,
            variabilidad=0.15  # 15% de variabilidad
        )
        
        # Calcular intervalos de confianza
        intervalos_confianza = simulacion_montecarlo.calcular_intervalos_confianza(
            resultados_simulacion,
            niveles_confianza=[0.80, 0.90, 0.95]
        )
        
        # Guardar resultados para Power BI
        df_intervalos = pd.DataFrame(intervalos_confianza)
        df_intervalos.to_csv(f"{DIRECTORIO_RESULTADOS}/intervalos_confianza.csv", index=False)
        
        # Guardar distribución completa de simulaciones (muestreo para no hacer archivo demasiado grande)
        muestreo_simulaciones = simulacion_montecarlo.generar_muestreo_resultados(
            resultados_simulacion,
            tamaño_muestra=100
        )
        df_simulaciones = pd.DataFrame(muestreo_simulaciones)
        df_simulaciones.to_csv(f"{DIRECTORIO_RESULTADOS}/muestreo_simulaciones.csv", index=False)
        
        logging.info("Simulación de Monte Carlo completada y guardada")
        
        return {
            "intervalos_confianza": intervalos_confianza,
            "muestreo_simulaciones": muestreo_simulaciones
        }
    except Exception as e:
        logging.error(f"Error en simulación de Monte Carlo: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def ejecutar_analisis_elasticidad(datos):
    """Ejecuta análisis de elasticidad para determinar sensibilidad de leads a diferentes factores."""
    try:
        logging.info("Iniciando análisis de elasticidad...")
        
        # Importar módulo de elasticidad
        analizar_elasticidad = importar_modulo_seguro("analizar_elasticidad")
        if not analizar_elasticidad:
            logging.error("No se pudo importar el módulo de análisis de elasticidad")
            return None
        
        # Ejecutar análisis
        resultados_elasticidad = analizar_elasticidad.calcular_elasticidad(
            datos["df_crm"],
            datos["df_planificacion"]
        )
        
        # Calcular recomendaciones de inversión
        recomendaciones = analizar_elasticidad.generar_recomendaciones_inversion(
            resultados_elasticidad,
            datos["df_planificacion"]
        )
        
        # Guardar resultados para Power BI
        df_elasticidad = pd.DataFrame(resultados_elasticidad)
        df_elasticidad.to_csv(f"{DIRECTORIO_RESULTADOS}/elasticidad_factores.csv", index=False)
        
        df_recomendaciones = pd.DataFrame(recomendaciones)
        df_recomendaciones.to_csv(f"{DIRECTORIO_RESULTADOS}/recomendaciones_inversion.csv", index=False)
        
        logging.info("Análisis de elasticidad completado y guardado")
        
        return {
            "elasticidad": resultados_elasticidad,
            "recomendaciones": recomendaciones
        }
    except Exception as e:
        logging.error(f"Error en análisis de elasticidad: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def generar_resumen_confianza(resultados):
    """Genera un resumen de confianza de los diferentes análisis para el dashboard."""
    try:
        logging.info("Generando resumen de confianza...")
        
        # Crear dataframe de resumen
        resumen = {
            "metrica": [],
            "valor": [],
            "confianza": [],
            "descripcion": []
        }
        
        # Agregar métricas de predicción
        for metrica, valor in resultados["prediccion"]["metricas"].items():
            resumen["metrica"].append(f"prediccion_{metrica}")
            resumen["valor"].append(valor)
            # Asignar nivel de confianza basado en la métrica
            if metrica == "r2":
                confianza = min(valor * 100, 100)
            elif metrica == "mape":
                confianza = max(100 - valor*10, 0)
            else:
                confianza = 50  # Valor por defecto
            resumen["confianza"].append(confianza)
            resumen["descripcion"].append(f"Métrica de evaluación: {metrica}")
        
        # Agregar métricas de intervalos de confianza
        for nivel, intervalo in resultados["montecarlo"]["intervalos_confianza"].items():
            if isinstance(intervalo, dict) and "promedio" in intervalo:
                resumen["metrica"].append(f"intervalo_confianza_{nivel}")
                resumen["valor"].append(intervalo["promedio"]["amplitud"])
                resumen["confianza"].append(float(nivel) * 100)
                resumen["descripcion"].append(f"Amplitud promedio del intervalo de confianza al {float(nivel)*100}%")
        
        # Guardar resumen para Power BI
        df_resumen = pd.DataFrame(resumen)
        df_resumen.to_csv(f"{DIRECTORIO_RESULTADOS}/resumen_confianza.csv", index=False)
        
        logging.info("Resumen de confianza generado y guardado")
        
        return df_resumen
    except Exception as e:
        logging.error(f"Error generando resumen de confianza: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def actualizar_datos_dashboard():
    """Actualiza los datos procesados para el dashboard Power BI."""
    try:
        logging.info("Actualizando datos para dashboard Power BI...")
        
        # Importar script de actualización
        sys.path.append(os.path.abspath('dashboard'))
        actualizar_datos = importar_modulo_seguro("actualizar_datos")
        if not actualizar_datos:
            logging.error("No se pudo importar el módulo de actualización de datos")
            return False
        
        # Ejecutar actualización
        resultado = actualizar_datos.ejecutar_actualizacion()
        
        if resultado:
            logging.info("Datos del dashboard actualizados correctamente")
        else:
            logging.error("Error actualizando datos del dashboard")
        
        return resultado
    except Exception as e:
        logging.error(f"Error en actualización de datos: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def ejecutar_analisis_completo():
    """Función principal que ejecuta todos los análisis secuencialmente."""
    inicio = datetime.now()
    logging.info("=== INICIANDO EJECUCIÓN DE ANÁLISIS COMPLETO ===")
    
    try:
        # Configurar entorno
        configurar_entorno()
        
        # 1. Cargar datos
        datos = ejecutar_carga_datos()
        if not datos:
            logging.error("Terminando ejecución: fallo en carga de datos")
            return False
        
        # 2. Ejecutar análisis de estacionalidad
        resultados_estacionalidad = ejecutar_analisis_estacionalidad(datos)
        if not resultados_estacionalidad:
            logging.error("Terminando ejecución: fallo en análisis de estacionalidad")
            return False
        
        # 3. Ejecutar predicción de matrículas
        resultados_prediccion = ejecutar_prediccion_matriculas(datos, resultados_estacionalidad)
        if not resultados_prediccion:
            logging.error("Terminando ejecución: fallo en predicción de matrículas")
            return False
        
        # 4. Ejecutar simulación Monte Carlo
        resultados_montecarlo = ejecutar_simulacion_montecarlo(datos, resultados_prediccion)
        if not resultados_montecarlo:
            logging.error("Terminando ejecución: fallo en simulación Monte Carlo")
            return False
        
        # 5. Ejecutar análisis de elasticidad
        resultados_elasticidad = ejecutar_analisis_elasticidad(datos)
        if not resultados_elasticidad:
            logging.error("Terminando ejecución: fallo en análisis de elasticidad")
            return False
        
        # 6. Generar resumen de confianza
        resultados_completos = {
            "estacionalidad": resultados_estacionalidad,
            "prediccion": resultados_prediccion,
            "montecarlo": resultados_montecarlo,
            "elasticidad": resultados_elasticidad
        }
        resumen_confianza = generar_resumen_confianza(resultados_completos)
        
        # 7. Actualizar datos del dashboard
        actualizar_datos_dashboard()
        
        # Registrar tiempos de ejecución
        fin = datetime.now()
        duracion = (fin - inicio).total_seconds()
        logging.info(f"=== ANÁLISIS COMPLETO FINALIZADO EN {duracion:.2f} SEGUNDOS ===")
        
        return True
    
    except Exception as e:
        logging.error(f"Error crítico en ejecución de análisis completo: {str(e)}")
        logging.error(traceback.format_exc())
        
        fin = datetime.now()
        duracion = (fin - inicio).total_seconds()
        logging.error(f"=== ANÁLISIS COMPLETO FALLIDO DESPUÉS DE {duracion:.2f} SEGUNDOS ===")
        
        return False
    
if __name__ == "__main__":
    ejecutar_analisis_completo() 