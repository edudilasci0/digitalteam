"""
Módulo de configuración centralizada para el sistema.
Permite cargar configuraciones desde archivos YAML o variables de entorno.
"""

import os
import yaml
import logging
from pathlib import Path

# Determinar directorio raíz del proyecto
ROOT_DIR = Path(__file__).parent.parent.parent

# Configurar logging básico para este módulo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración global
_config = None

def load_config(config_path=None):
    """
    Carga la configuración desde un archivo YAML.
    
    Args:
        config_path (str, opcional): Ruta al archivo de configuración.
            Si no se proporciona, busca en la variable de entorno CONFIG_PATH
            o usa la ruta predeterminada.
    
    Returns:
        dict: Diccionario con la configuración cargada
    """
    global _config
    
    # Si no se proporciona una ruta, intentar usar variable de entorno
    if config_path is None:
        config_path = os.environ.get('CONFIG_PATH')
    
    # Si no hay variable de entorno, usar la ruta predeterminada
    if config_path is None:
        config_path = ROOT_DIR / 'config' / 'config.yaml'
    else:
        config_path = Path(config_path)
    
    try:
        with open(config_path, 'r') as file:
            _config = yaml.safe_load(file)
            logger.info(f"Configuración cargada desde {config_path}")
    except FileNotFoundError:
        logger.warning(f"Archivo de configuración no encontrado en {config_path}. "
                      f"Utilizando configuración predeterminada.")
        _config = _get_default_config()
    
    return _config

def _get_default_config():
    """
    Genera una configuración predeterminada.
    
    Returns:
        dict: Diccionario con configuración predeterminada
    """
    return {
        'paths': {
            'data': str(ROOT_DIR / 'datos'),
            'output': str(ROOT_DIR / 'output'),
            'logs': str(ROOT_DIR / 'logs'),
        },
        'analysis': {
            'monte_carlo': {
                'num_simulations': 1000,
                'confidence_level': 0.95
            },
            'estacionalidad': {
                'freq': 'W',
                'min_periods': 52
            }
        },
        'google_sheets': {
            'credentials_path': str(ROOT_DIR / 'config' / 'credentials.json'),
            'token_path': str(ROOT_DIR / 'config' / 'token.pickle')
        },
        'power_bi': {
            'export_format': 'csv',
            'delimiter': ',',
            'encoding': 'utf-8'
        }
    }

def get_config():
    """
    Obtiene la configuración actual.
    Si no se ha cargado, la carga automáticamente.
    
    Returns:
        dict: Diccionario con la configuración
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config

def update_config(new_config):
    """
    Actualiza la configuración actual con nuevos valores.
    
    Args:
        new_config (dict): Diccionario con los nuevos valores de configuración
    
    Returns:
        dict: Configuración actualizada
    """
    global _config
    if _config is None:
        _config = load_config()
    
    # Actualización recursiva
    def update_nested_dict(d, u):
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                d[k] = update_nested_dict(d[k], v)
            else:
                d[k] = v
        return d
    
    _config = update_nested_dict(_config, new_config)
    return _config

# Cargar configuración al importar el módulo
_config = load_config() 