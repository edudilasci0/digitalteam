"""
Módulo para configuración centralizada de logging.
Proporciona funciones para configurar loggers personalizados para diferentes módulos.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

# Importar configuración
from src.utils.config import get_config, ROOT_DIR

def setup_logging(name, level=logging.INFO, log_to_file=True):
    """
    Configura un logger con handlers para consola y opcionalmente archivo.
    
    Args:
        name (str): Nombre del logger, generalmente __name__ del módulo
        level (int): Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file (bool): Si se debe guardar el log en archivo
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicación de handlers si ya está configurado
    if logger.handlers:
        return logger
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formato común
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo si está habilitado
    if log_to_file:
        config = get_config()
        log_dir = config['paths']['logs']
        
        # Crear directorio si no existe
        os.makedirs(log_dir, exist_ok=True)
        
        # Nombre de archivo basado en el nombre del logger y fecha
        log_filename = f"{name.replace('.', '_')}_{datetime.now().strftime('%Y%m%d')}.log"
        file_path = os.path.join(log_dir, log_filename)
        
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_module_logger(module_name=None):
    """
    Obtiene un logger ya configurado para un módulo específico.
    Si no existe, lo crea con la configuración estándar.
    
    Args:
        module_name (str, opcional): Nombre del módulo. Si no se proporciona,
                                    se utiliza '__main__'.
    
    Returns:
        logging.Logger: Logger configurado para el módulo
    """
    if module_name is None:
        module_name = '__main__'
        
    # Verificar si ya está configurado
    logger = logging.getLogger(module_name)
    if logger.handlers:
        return logger
    
    # Si no está configurado, configurarlo
    return setup_logging(module_name)

# Configurar logger para este módulo
logger = get_module_logger(__name__) 