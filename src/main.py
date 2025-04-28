"""
Script principal del sistema de predicción y optimización de matrículas basado en CPA.
Coordina la carga de datos, procesamiento, entrenamiento de modelos y generación de reportes.
"""

import argparse
import logging
import pandas as pd
from pathlib import Path
import sys
import os
from datetime import datetime

# Asegurar que el directorio raíz está en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.procesador_datos import ProcesadorDatos
from src.models.model_manager import ModelManager
from src.models.evaluador_modelos import EvaluadorModelos
from src.visualizacion.visualizador import Visualizador
from src.utils.config import get_config, update_config
from src.utils.logging import setup_logging

def parse_argumentos():
    """
    Analiza los argumentos de línea de comandos.
    
    Returns:
        argparse.Namespace: Objeto con los argumentos procesados
    """
    parser = argparse.ArgumentParser(description='Sistema de predicción y optimización de matrículas')
    
    # Argumentos para rutas de datos
    parser.add_argument('--datos-leads', type=str, 
                      help='Ruta al archivo CSV de leads')
    parser.add_argument('--datos-matriculas', type=str, 
                      help='Ruta al archivo CSV de matrículas')
    
    # Argumentos de configuración
    parser.add_argument('--config', type=str, 
                      help='Ruta al archivo de configuración YAML')
    parser.add_argument('--guardar-resultados', action='store_true', 
                      help='Guardar resultados en disco')
    parser.add_argument('--dir-salida', type=str, 
                      help='Directorio para guardar resultados')
    
    # Argumentos para modelo
    parser.add_argument('--tipo-modelo', type=str, default='ridge', 
                      choices=['linear', 'ridge', 'lasso', 'random_forest', 'gradient_boosting'],
                      help='Tipo de modelo a entrenar')
    parser.add_argument('--target', type=str, default='convertido',
                      help='Columna objetivo para el modelo')
    
    # Argumentos de ejecución
    parser.add_argument('--solo-carga', action='store_true',
                      help='Solo cargar y preprocesar datos, sin entrenar modelo')
    parser.add_argument('--solo-evaluar', action='store_true',
                      help='Evaluar modelo ya entrenado sin volver a entrenar')
    parser.add_argument('--ruta-modelo', type=str,
                      help='Ruta a un modelo guardado para evaluar')
    
    # Analizar argumentos
    return parser.parse_args()

def setup_directorios():
    """
    Configura los directorios necesarios para la ejecución.
    
    Returns:
        dict: Diccionario con rutas de directorios
    """
    config = get_config()
    
    # Obtener rutas desde configuración
    dirs = {
        'datos': Path(config['paths']['data']),
        'output': Path(config['paths']['output']),
        'logs': Path(config['paths']['logs']),
        'modelos': Path(config['paths'].get('models', 
                                         str(Path(config['paths']['output']) / 'models'))),
        'reportes': Path(config['paths']['output']) / 'reportes',
        'graficos': Path(config['paths']['output']) / 'graficos'
    }
    
    # Crear directorios si no existen
    for nombre, dir_path in dirs.items():
        os.makedirs(dir_path, exist_ok=True)
        logging.info(f"Directorio '{nombre}' configurado en: {dir_path}")
    
    return dirs

def cargar_preprocesar_datos(args, procesador):
    """
    Carga y preprocesa los datos de leads y matrículas.
    
    Args:
        args (argparse.Namespace): Argumentos de línea de comandos
        procesador (ProcesadorDatos): Instancia del procesador de datos
        
    Returns:
        pd.DataFrame: DataFrame con datos procesados
    """
    config = get_config()
    
    # Determinar rutas de datos
    if args.datos_leads:
        ruta_leads = args.datos_leads
    else:
        ruta_leads = config['paths']['data'] + '/leads.csv'
        
    if args.datos_matriculas:
        ruta_matriculas = args.datos_matriculas
    else:
        ruta_matriculas = config['paths']['data'] + '/matriculas.csv'
    
    logging.info(f"Cargando datos de leads desde: {ruta_leads}")
    datos_leads = procesador.cargar_datos(ruta_leads)
    
    logging.info(f"Cargando datos de matrículas desde: {ruta_matriculas}")
    datos_matriculas = procesador.cargar_datos(ruta_matriculas)
    
    # Validar datos
    leads_valido, _ = procesador.validar_datos(datos_leads, 'leads')
    matriculas_valido, _ = procesador.validar_datos(datos_matriculas, 'matriculas')
    
    if not (leads_valido and matriculas_valido):
        logging.warning("Los datos no cumplen con todos los requisitos de validación")
    
    # Convertir tipos de datos
    datos_leads = procesador.convertir_tipos_datos(datos_leads, 'leads')
    datos_matriculas = procesador.convertir_tipos_datos(datos_matriculas, 'matriculas')
    
    # Limpiar datos
    datos_leads = procesador.limpiar_datos(datos_leads)
    datos_matriculas = procesador.limpiar_datos(datos_matriculas)
    
    # Unir datos
    datos_unidos = procesador.unir_leads_matriculas(datos_leads, datos_matriculas)
    
    # Crear características
    datos_procesados = procesador.crear_caracteristicas(datos_unidos)
    
    return datos_procesados

def entrenar_evaluar_modelo(datos, args):
    """
    Entrena y evalúa un modelo con los datos procesados.
    
    Args:
        datos (pd.DataFrame): DataFrame con datos procesados
        args (argparse.Namespace): Argumentos de línea de comandos
        
    Returns:
        tuple: (ModelManager, dict) - Gestor de modelos y métricas de evaluación
    """
    # Inicializar componentes
    model_manager = ModelManager(model_name="modelo_principal")
    evaluador = EvaluadorModelos()
    procesador = ProcesadorDatos()
    
    # Dividir datos
    logging.info("Dividiendo datos para entrenamiento y evaluación")
    X_train, X_test, y_train, y_test = procesador.dividir_datos_entrenamiento(
        datos, 
        columna_objetivo=args.target,
        test_size=0.2,
        random_state=42
    )
    
    # Configurar parámetros según tipo de modelo
    model_params = {}
    if args.tipo_modelo == 'random_forest':
        model_params = {'n_estimators': 100, 'max_depth': 10}
    elif args.tipo_modelo == 'gradient_boosting':
        model_params = {'n_estimators': 100, 'learning_rate': 0.1}
    elif args.tipo_modelo == 'ridge':
        model_params = {'alpha': 1.0}
    elif args.tipo_modelo == 'lasso':
        model_params = {'alpha': 0.1}
    
    # Si se proporcionó una ruta de modelo para evaluar
    if args.ruta_modelo:
        logging.info(f"Cargando modelo desde: {args.ruta_modelo}")
        model_manager.load(args.ruta_modelo)
    # Si no hay que entrenar un nuevo modelo
    elif not args.solo_evaluar:
        logging.info(f"Entrenando modelo de tipo: {args.tipo_modelo}")
        
        # Obtener características categóricas
        cat_features = [col for col in X_train.columns if col in ['origen', 'programa', 'marca']]
        
        # Entrenar modelo
        metricas_entrenamiento = model_manager.train(
            datos,
            target_column=args.target,
            model_type=args.tipo_modelo,
            model_params=model_params,
            categorical_features=cat_features
        )
        
        logging.info(f"Modelo entrenado. Métricas: {metricas_entrenamiento}")
    
    # Evaluar modelo
    if model_manager.model is not None:
        logging.info("Evaluando modelo...")
        
        # Realizar predicciones
        y_pred = model_manager.predict(X_test)
        
        # Evaluar según el tipo de variable objetivo
        if pd.api.types.is_bool_dtype(y_test) or pd.api.types.is_categorical_dtype(y_test):
            metricas = evaluador.evaluar_clasificacion(
                y_test.values, y_pred, nombre_modelo=args.tipo_modelo
            )
        else:
            metricas = evaluador.evaluar_regresion(
                y_test.values, y_pred, nombre_modelo=args.tipo_modelo
            )
        
        logging.info(f"Evaluación completada. Métricas: {metricas}")
        
        # Guardar modelo entrenado si se solicitó
        if args.guardar_resultados and not args.solo_evaluar:
            ruta_modelo = model_manager.save()
            logging.info(f"Modelo guardado en: {ruta_modelo}")
        
        return model_manager, metricas
    else:
        logging.error("No se pudo entrenar o cargar el modelo")
        return None, None

def generar_visualizaciones(datos, modelo, metricas, args):
    """
    Genera visualizaciones y reportes basados en los resultados del modelo.
    
    Args:
        datos (pd.DataFrame): DataFrame con datos procesados
        modelo (ModelManager): Gestor de modelos entrenado
        metricas (dict): Métricas de evaluación del modelo
        args (argparse.Namespace): Argumentos de línea de comandos
    """
    visualizador = Visualizador()
    
    # Si no hay modelo, generar solo visualizaciones de datos
    if modelo is None:
        logging.info("Generando visualizaciones de datos...")
        
        # Visualizar distribución de datos por origen
        if 'origen' in datos.columns:
            visualizador.graficar_barras(
                datos, 
                columna_categoria='origen', 
                columna_valor=None,
                titulo='Distribución de leads por origen',
                orientacion='horizontal'
            )
        
        # Visualizar distribución por programa
        if 'programa' in datos.columns:
            visualizador.graficar_barras(
                datos, 
                columna_categoria='programa', 
                columna_valor=None,
                titulo='Distribución de leads por programa',
                orientacion='horizontal'
            )
        
        # Visualizar serie temporal si hay fecha
        if 'fecha_creacion' in datos.columns:
            # Agrupar por fecha
            datos_temp = datos.groupby(pd.Grouper(key='fecha_creacion', freq='W')).size().reset_index()
            datos_temp.columns = ['fecha_creacion', 'conteo']
            
            visualizador.graficar_serie_temporal(
                datos_temp,
                columna_fecha='fecha_creacion',
                columna_valor='conteo',
                titulo='Evolución de leads por semana'
            )
        
        return
    
    # Si hay modelo, generar visualizaciones de evaluación
    logging.info("Generando visualizaciones de evaluación del modelo...")
    
    evaluador = EvaluadorModelos()
    
    # Obtener predicciones para visualización
    X = datos[[col for col in datos.columns if col != args.target]]
    y_true = datos[args.target]
    y_pred = modelo.predict(X)
    
    # Visualizar predicciones vs reales para regresión
    if not pd.api.types.is_bool_dtype(y_true) and not pd.api.types.is_categorical_dtype(y_true):
        evaluador.graficar_predicciones_vs_reales(
            y_true.values, y_pred, nombre_modelo=args.tipo_modelo
        )
        
        evaluador.graficar_residuos(
            y_true.values, y_pred, nombre_modelo=args.tipo_modelo
        )
    
    # Si el modelo soporta importancia de características, visualizarla
    try:
        importancias = modelo.feature_importance()
        
        # Crear visualización de importancia de características
        if not importancias.empty:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            importancias_top = importancias.head(15)  # Mostrar top 15
            sns.barplot(x='importance', y='feature', data=importancias_top, ax=ax)
            
            ax.set_title('Importancia de características')
            ax.set_xlabel('Importancia')
            ax.set_ylabel('Característica')
            
            plt.tight_layout()
            plt.savefig(dirs['reportes'] / 'importancia_caracteristicas.png', dpi=300)
            
    except Exception as e:
        logging.warning(f"No se pudo generar visualización de importancia: {str(e)}")
    
    # Guardar métricas
    if args.guardar_resultados:
        ruta_metricas = evaluador.guardar_metricas()
        logging.info(f"Métricas guardadas en: {ruta_metricas}")

def main():
    """
    Función principal que coordina la ejecución del sistema.
    """
    # Analizar argumentos
    args = parse_argumentos()
    
    # Cargar configuración personalizada si se proporciona
    if args.config:
        from src.utils.config import load_config
        load_config(args.config)
    
    # Actualizar configuración con valores de línea de comandos
    config_updates = {}
    if args.dir_salida:
        config_updates['paths'] = {'output': args.dir_salida}
    
    if config_updates:
        update_config(config_updates)
    
    # Configurar logging
    logger = setup_logging("main")
    
    # Configurar directorios
    dirs = setup_directorios()
    
    # Mostrar información de ejecución
    logger.info("Iniciando sistema de predicción y optimización de matrículas")
    logger.info(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Tipo de modelo: {args.tipo_modelo}")
    logger.info(f"Variable objetivo: {args.target}")
    
    try:
        # Inicializar procesador de datos
        procesador = ProcesadorDatos()
        
        # Cargar y preprocesar datos
        logger.info("Cargando y preprocesando datos...")
        datos_procesados = cargar_preprocesar_datos(args, procesador)
        
        logger.info(f"Datos procesados: {datos_procesados.shape[0]} filas, {datos_procesados.shape[1]} columnas")
        
        # Si solo se solicita cargar datos, terminar aquí
        if args.solo_carga:
            logger.info("Ejecución completada (solo carga de datos)")
            return
        
        # Entrenar y evaluar modelo
        logger.info("Entrenando y evaluando modelo...")
        modelo, metricas = entrenar_evaluar_modelo(datos_procesados, args)
        
        # Generar visualizaciones
        logger.info("Generando visualizaciones...")
        generar_visualizaciones(datos_procesados, modelo, metricas, args)
        
        logger.info("Ejecución completada exitosamente")
        
    except Exception as e:
        logger.error(f"Error en la ejecución: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 