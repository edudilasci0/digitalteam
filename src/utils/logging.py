"""
Módulo para configuración y gestión avanzada de logging en el Motor de Decisión.
Proporciona funciones para configurar y obtener loggers con rotación de archivos y niveles configurables.
"""

import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import sys
from typing import Dict, Optional
from pathlib import Path
import json
import datetime

from src.utils.config import get_config

# Configuración de formatos
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DETAILED_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'

# Mapeo de niveles de log desde texto
LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

# Registro global de loggers
_loggers = {}

def setup_logging(
    name: str, 
    level: Optional[str] = None, 
    log_file: Optional[str] = None,
    console: bool = True,
    file_rotation: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB por defecto
    backup_count: int = 5,
    detailed_format: bool = False
) -> logging.Logger:
    """
    Configura y devuelve un logger con las opciones especificadas.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (debug, info, warning, error, critical)
        log_file: Ruta al archivo de log
        console: Si se debe enviar logs a la consola
        file_rotation: Si se debe usar rotación de archivos de log
        max_bytes: Tamaño máximo de archivo para rotación por tamaño
        backup_count: Número de archivos de backup a mantener
        detailed_format: Si se debe usar formato detallado (incluye archivo y línea)
        
    Returns:
        Un logger configurado
    """
    # Evitar configurar el mismo logger múltiples veces
    if name in _loggers:
        return _loggers[name]
    
    # Obtener configuración
    config = get_config()
    
    # Determinar nivel de log
    if level is None:
        level = config.get('logging', {}).get('level', 'info')
    
    log_level = LOG_LEVELS.get(level.lower(), logging.INFO)
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False  # Evitar duplicación de logs
    
    # Determinar formato de log
    if detailed_format:
        log_format = DETAILED_LOG_FORMAT
    else:
        log_format = DEFAULT_LOG_FORMAT
    
    formatter = logging.Formatter(log_format)
    
    # Añadir handler de consola si se solicita
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Configurar handler de archivo si se solicita
    if log_file is None and config.get('paths', {}).get('logs'):
        # Usar directorio de logs de configuración
        log_dir = Path(config['paths']['logs'])
        log_dir.mkdir(exist_ok=True)
        
        # Usar nombre con fecha
        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"{name}_{timestamp}.log"
    
    if log_file:
        if file_rotation:
            # Rotación por tamaño
            file_handler = RotatingFileHandler(
                log_file, 
                maxBytes=max_bytes, 
                backupCount=backup_count
            )
        else:
            # Sin rotación
            file_handler = logging.FileHandler(log_file)
        
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Registrar logger para reutilizar
    _loggers[name] = logger
    
    logger.info(f"Logger {name} configurado con nivel {level}")
    return logger

def get_module_logger(module_name: str) -> logging.Logger:
    """
    Obtiene un logger para un módulo específico.
    
    Args:
        module_name: Nombre del módulo (normalmente __name__)
        
    Returns:
        Un logger configurado para el módulo
    """
    # Obtener configuración
    config = get_config()
    
    # Usar valores de configuración o predeterminados
    level = config.get('logging', {}).get('level', 'info')
    detailed = config.get('logging', {}).get('detailed', False)
    
    # Nombre base del módulo (sin paquetes)
    base_name = module_name.split('.')[-1]
    
    # Crear logger
    return setup_logging(
        module_name,
        level=level,
        detailed_format=detailed
    )

def configurar_logger_excepciones():
    """
    Configura un handler global para excepciones no capturadas.
    Todas las excepciones no capturadas se registrarán en el archivo de errores.
    """
    config = get_config()
    log_dir = Path(config['paths']['logs'])
    log_dir.mkdir(exist_ok=True)
    
    # Archivo específico para excepciones no capturadas
    error_log = log_dir / "excepciones_no_capturadas.log"
    
    # Configurar handler
    handler = logging.FileHandler(error_log)
    handler.setLevel(logging.ERROR)
    handler.setFormatter(logging.Formatter(DETAILED_LOG_FORMAT))
    
    # Obtener logger de excepciones
    logger = logging.getLogger('excepciones')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    
    # Función para manejar excepciones no capturadas
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # No capturar interrupciones de teclado
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Registrar excepción
        logger.error("Excepción no capturada:", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Establecer handler global
    sys.excepthook = handle_exception
    
    return logger

def registrar_inicio_app():
    """
    Registra el inicio de la aplicación con información del sistema.
    Útil para diagnóstico y seguimiento de ejecuciones.
    """
    import platform
    
    logger = get_module_logger("sistema")
    
    # Registrar información del sistema
    info_sistema = {
        "python_version": platform.python_version(),
        "system": platform.system(),
        "release": platform.release(),
        "hostname": platform.node(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    logger.info(f"Iniciando Motor de Decisión - Info del sistema: {json.dumps(info_sistema)}")
    
    return logger 