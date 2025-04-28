#!/usr/bin/env python
"""
Script de ejecución para sincronizar datos entre Google Sheets y el sistema de predicción.
Este archivo se puede programar para ejecuciones automáticas diarias o periódicas.
"""
import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                          "logs", "sincronizacion_auto.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ejecutar_sincronizacion")

# Agregar el directorio principal al path para importar módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

try:
    # Importar la función de sincronización
    from scripts.sincronizar_sheets import sincronizar_google_sheets
    
    # Registrar inicio de sincronización
    logger.info(f"Iniciando sincronización programada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar sincronización
    result = sincronizar_google_sheets()
    
    # Registrar resultado
    if result:
        logger.info("Sincronización programada completada con éxito")
    else:
        logger.error("La sincronización programada falló")
    
except Exception as e:
    logger.error(f"Error durante la sincronización programada: {str(e)}")
    
finally:
    logger.info(f"Sincronización programada finalizada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 