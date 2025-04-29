"""
Módulo para gestión segura de secretos y credenciales.
Utiliza archivos .env para almacenar configuraciones sensibles sin incluirlas en el código.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging
from dotenv import load_dotenv

from src.utils.logging import get_module_logger

logger = get_module_logger(__name__)

class SecretsManager:
    """
    Clase para gestionar secretos y credenciales de forma segura.
    Permite cargar y acceder a credenciales desde archivos .env.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Inicializa el gestor de secretos.
        
        Args:
            env_file: Ruta al archivo .env. Si no se proporciona,
                     se busca en el directorio raíz del proyecto.
        """
        # Cargar archivo .env
        self.env_loaded = False
        
        if env_file:
            # Usar archivo específico
            self.env_file = env_file
            self.env_loaded = load_dotenv(env_file)
        else:
            # Buscar en ubicaciones comunes
            possible_locations = [
                '.env',
                '../.env',
                '../../.env',
                os.path.join(os.path.dirname(__file__), '../../.env')
            ]
            
            for location in possible_locations:
                if os.path.isfile(location):
                    self.env_file = location
                    self.env_loaded = load_dotenv(location)
                    break
        
        if self.env_loaded:
            logger.info(f"Variables de entorno cargadas desde {self.env_file}")
        else:
            logger.warning("No se pudo cargar archivo .env. Se usarán variables de entorno del sistema.")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Obtiene un secreto desde las variables de entorno.
        
        Args:
            key: Clave del secreto
            default: Valor por defecto si no se encuentra la clave
            
        Returns:
            Valor del secreto o el valor por defecto
        """
        value = os.environ.get(key, default)
        return value
    
    def get_all_secrets(self, prefix: Optional[str] = None) -> Dict[str, str]:
        """
        Obtiene todos los secretos o los que comienzan con un prefijo específico.
        
        Args:
            prefix: Prefijo opcional para filtrar las variables
            
        Returns:
            Diccionario con los secretos
        """
        if prefix:
            return {k: v for k, v in os.environ.items() if k.startswith(prefix)}
        else:
            return dict(os.environ)
    
    def get_google_credentials(self) -> Dict[str, str]:
        """
        Obtiene credenciales de Google desde las variables de entorno o archivo de credenciales.
        
        Returns:
            Diccionario con las credenciales de Google
        """
        # Intentar cargar credenciales desde variables de entorno
        client_id = self.get_secret('GOOGLE_CLIENT_ID')
        client_secret = self.get_secret('GOOGLE_CLIENT_SECRET')
        refresh_token = self.get_secret('GOOGLE_REFRESH_TOKEN')
        
        if client_id and client_secret:
            credentials = {
                'client_id': client_id,
                'client_secret': client_secret
            }
            
            if refresh_token:
                credentials['refresh_token'] = refresh_token
                
            return credentials
        
        # Intentar cargar desde archivo
        credentials_file = self.get_secret('GOOGLE_CREDENTIALS_FILE')
        if credentials_file and os.path.isfile(credentials_file):
            try:
                with open(credentials_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error al cargar credenciales de Google: {str(e)}")
        
        logger.warning("No se encontraron credenciales de Google")
        return {}
    
    def get_db_credentials(self) -> Dict[str, str]:
        """
        Obtiene credenciales de base de datos desde las variables de entorno.
        
        Returns:
            Diccionario con las credenciales de la base de datos
        """
        db_host = self.get_secret('DB_HOST', 'localhost')
        db_port = self.get_secret('DB_PORT', '3306')
        db_user = self.get_secret('DB_USER')
        db_password = self.get_secret('DB_PASSWORD')
        db_name = self.get_secret('DB_NAME')
        
        credentials = {
            'host': db_host,
            'port': db_port
        }
        
        if db_user:
            credentials['user'] = db_user
        
        if db_password:
            credentials['password'] = db_password
            
        if db_name:
            credentials['database'] = db_name
            
        return credentials
    
    def get_email_credentials(self) -> Dict[str, str]:
        """
        Obtiene credenciales de email desde las variables de entorno.
        
        Returns:
            Diccionario con las credenciales de email
        """
        smtp_host = self.get_secret('SMTP_HOST')
        smtp_port = self.get_secret('SMTP_PORT', '587')
        smtp_user = self.get_secret('SMTP_USER')
        smtp_password = self.get_secret('SMTP_PASSWORD')
        smtp_from = self.get_secret('SMTP_FROM')
        
        credentials = {}
        
        if smtp_host:
            credentials['host'] = smtp_host
            credentials['port'] = smtp_port
        
        if smtp_user:
            credentials['user'] = smtp_user
        
        if smtp_password:
            credentials['password'] = smtp_password
            
        if smtp_from:
            credentials['from'] = smtp_from
            
        return credentials
    
    def create_env_template(self, output_file: str = '.env.template') -> str:
        """
        Crea un archivo de plantilla .env con variables comunes.
        
        Args:
            output_file: Ruta del archivo de plantilla a crear
            
        Returns:
            Ruta del archivo creado
        """
        template_content = """# Archivo de configuración de variables de entorno
# Copie este archivo a .env y complete los valores

# Configuración general
APP_ENV=development  # development, test, production
DEBUG=True

# Credenciales de Google
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=
GOOGLE_CREDENTIALS_FILE=

# Credenciales de Base de Datos
DB_HOST=localhost
DB_PORT=3306
DB_USER=
DB_PASSWORD=
DB_NAME=motor_decision

# Credenciales Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=

# Otros secretos
API_KEY=
"""
        
        try:
            with open(output_file, 'w') as f:
                f.write(template_content)
            
            logger.info(f"Plantilla .env creada en {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error al crear plantilla .env: {str(e)}")
            raise

# Instancia global del gestor de secretos
secrets_manager = SecretsManager()

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Función auxiliar para obtener un secreto desde la instancia global.
    
    Args:
        key: Clave del secreto
        default: Valor por defecto si no se encuentra la clave
        
    Returns:
        Valor del secreto o el valor por defecto
    """
    return secrets_manager.get_secret(key, default) 