"""
Módulo para gestionar la base de datos SQLite del Motor de Decisión.
Proporciona funciones para crear, leer, actualizar y eliminar datos en la BD.
"""

import os
import sqlite3
import pandas as pd
from pathlib import Path
import json
from typing import Dict, List, Optional, Tuple, Union
import logging

from src.utils.config import get_config

logger = logging.getLogger(__name__)

class DBManager:
    """
    Clase para gestionar la base de datos SQLite del Motor de Decisión.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa el gestor de base de datos.
        
        Args:
            db_path: Ruta opcional a la base de datos. Si no se proporciona,
                     se utilizará la ruta configurada en config.yaml.
        """
        self.config = get_config()
        
        # Usar ruta proporcionada o la de configuración
        if db_path:
            self.db_path = db_path
        else:
            # Crear directorio de datos si no existe
            data_dir = Path(self.config['paths']['data'])
            data_dir.mkdir(exist_ok=True)
            
            # Establecer ruta de la base de datos
            self.db_path = str(data_dir / 'motor_decision.db')
        
        logger.info(f"Base de datos configurada en: {self.db_path}")
        
        # Crear las tablas si no existen
        self._crear_tablas()
    
    def _conectar(self) -> sqlite3.Connection:
        """
        Establece conexión con la base de datos.
        
        Returns:
            Conexión a la base de datos SQLite.
        """
        return sqlite3.connect(self.db_path)
    
    def _crear_tablas(self):
        """Crea las tablas necesarias en la base de datos si no existen."""
        try:
            conn = self._conectar()
            cursor = conn.cursor()
            
            # Tabla de leads
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                fecha_creacion TEXT,
                programa TEXT,
                origen TEXT,
                marca TEXT,
                costo REAL,
                utm_source TEXT,
                utm_medium TEXT,
                utm_campaign TEXT,
                datos_adicionales TEXT
            )
            ''')
            
            # Tabla de matrículas
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS matriculas (
                id TEXT PRIMARY KEY,
                id_lead TEXT,
                fecha_matricula TEXT,
                programa TEXT,
                valor_matricula REAL,
                modalidad TEXT,
                sede TEXT,
                FOREIGN KEY (id_lead) REFERENCES leads (id)
            )
            ''')
            
            # Tabla para historial de cargas
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial_cargas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                tipo_datos TEXT,
                archivo TEXT,
                filas INTEGER,
                estado TEXT
            )
            ''')
            
            # Tabla para configuración
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT,
                tipo TEXT
            )
            ''')
            
            conn.commit()
            logger.info("Tablas creadas o verificadas correctamente")
            
        except sqlite3.Error as e:
            logger.error(f"Error al crear tablas: {str(e)}")
            raise
            
        finally:
            if conn:
                conn.close()
    
    def guardar_leads(self, df: pd.DataFrame) -> int:
        """
        Guarda datos de leads en la base de datos.
        
        Args:
            df: DataFrame con datos de leads.
            
        Returns:
            Número de registros insertados.
        """
        try:
            conn = self._conectar()
            
            # Asegurar que el DataFrame tiene las columnas esperadas
            columnas_requeridas = ['id', 'fecha_creacion', 'programa', 'origen', 'marca']
            for col in columnas_requeridas:
                if col not in df.columns:
                    raise ValueError(f"Columna requerida faltante: {col}")
            
            # Convertir columnas de fecha a texto para SQLite
            if 'fecha_creacion' in df.columns:
                df['fecha_creacion'] = pd.to_datetime(df['fecha_creacion']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Gestionar columnas adicionales como JSON
            columnas_adicionales = [col for col in df.columns if col not in [
                'id', 'fecha_creacion', 'programa', 'origen', 'marca', 'costo', 
                'utm_source', 'utm_medium', 'utm_campaign'
            ]]
            
            if columnas_adicionales:
                df['datos_adicionales'] = df.apply(
                    lambda row: json.dumps({col: row[col] for col in columnas_adicionales if pd.notna(row[col])}),
                    axis=1
                )
            else:
                df['datos_adicionales'] = '{}'
            
            # Seleccionar columnas para insertar
            df_to_insert = df[['id', 'fecha_creacion', 'programa', 'origen', 'marca', 'costo', 
                             'utm_source', 'utm_medium', 'utm_campaign', 'datos_adicionales']]
            
            # Reemplazar valores NaN con None para SQLite
            df_to_insert = df_to_insert.where(pd.notna(df_to_insert), None)
            
            # Insertar datos
            registros_insertados = df_to_insert.to_sql('leads', conn, if_exists='append', index=False)
            
            conn.commit()
            logger.info(f"Guardados {registros_insertados} registros de leads en la BD")
            
            return registros_insertados
            
        except Exception as e:
            logger.error(f"Error al guardar leads: {str(e)}")
            raise
            
        finally:
            if conn:
                conn.close()
    
    def guardar_matriculas(self, df: pd.DataFrame) -> int:
        """
        Guarda datos de matrículas en la base de datos.
        
        Args:
            df: DataFrame con datos de matrículas.
            
        Returns:
            Número de registros insertados.
        """
        try:
            conn = self._conectar()
            
            # Asegurar que el DataFrame tiene las columnas esperadas
            columnas_requeridas = ['id', 'id_lead', 'fecha_matricula', 'programa', 'valor_matricula']
            for col in columnas_requeridas:
                if col not in df.columns:
                    raise ValueError(f"Columna requerida faltante: {col}")
            
            # Convertir columnas de fecha a texto para SQLite
            if 'fecha_matricula' in df.columns:
                df['fecha_matricula'] = pd.to_datetime(df['fecha_matricula']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Seleccionar columnas para insertar
            df_to_insert = df[['id', 'id_lead', 'fecha_matricula', 'programa', 
                             'valor_matricula', 'modalidad', 'sede']]
            
            # Reemplazar valores NaN con None para SQLite
            df_to_insert = df_to_insert.where(pd.notna(df_to_insert), None)
            
            # Insertar datos
            registros_insertados = df_to_insert.to_sql('matriculas', conn, if_exists='append', index=False)
            
            conn.commit()
            logger.info(f"Guardados {registros_insertados} registros de matrículas en la BD")
            
            return registros_insertados
            
        except Exception as e:
            logger.error(f"Error al guardar matrículas: {str(e)}")
            raise
            
        finally:
            if conn:
                conn.close()
    
    def obtener_leads(self, filtros: Optional[Dict] = None) -> pd.DataFrame:
        """
        Obtiene datos de leads desde la base de datos con filtros opcionales.
        
        Args:
            filtros: Diccionario de filtros a aplicar.
                    Ejemplo: {'origen': 'Facebook', 'fecha_desde': '2023-01-01'}
            
        Returns:
            DataFrame con datos de leads.
        """
        try:
            conn = self._conectar()
            
            # Iniciar consulta base
            query = "SELECT * FROM leads"
            params = []
            
            # Añadir filtros si existen
            if filtros:
                where_clauses = []
                
                if 'programa' in filtros:
                    where_clauses.append("programa = ?")
                    params.append(filtros['programa'])
                
                if 'origen' in filtros:
                    where_clauses.append("origen = ?")
                    params.append(filtros['origen'])
                
                if 'marca' in filtros:
                    where_clauses.append("marca = ?")
                    params.append(filtros['marca'])
                
                if 'fecha_desde' in filtros:
                    where_clauses.append("fecha_creacion >= ?")
                    params.append(filtros['fecha_desde'])
                
                if 'fecha_hasta' in filtros:
                    where_clauses.append("fecha_creacion <= ?")
                    params.append(filtros['fecha_hasta'])
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            # Ejecutar consulta
            df = pd.read_sql(query, conn, params=params)
            
            # Procesar datos JSON adicionales
            if not df.empty and 'datos_adicionales' in df.columns:
                # Expandir columnas JSON
                df_adicionales = pd.json_normalize(
                    df['datos_adicionales'].apply(
                        lambda x: json.loads(x) if pd.notna(x) and x != '{}' else {}
                    )
                )
                
                # Si hay columnas adicionales, añadirlas al DataFrame original
                if not df_adicionales.empty and len(df_adicionales.columns) > 0:
                    for col in df_adicionales.columns:
                        df[col] = df_adicionales[col]
                
                # Eliminar columna de datos adicionales
                df = df.drop('datos_adicionales', axis=1)
            
            logger.info(f"Obtenidos {len(df)} registros de leads desde la BD")
            return df
            
        except Exception as e:
            logger.error(f"Error al obtener leads: {str(e)}")
            raise
            
        finally:
            if conn:
                conn.close()
    
    def obtener_matriculas(self, filtros: Optional[Dict] = None) -> pd.DataFrame:
        """
        Obtiene datos de matrículas desde la base de datos con filtros opcionales.
        
        Args:
            filtros: Diccionario de filtros a aplicar.
                    Ejemplo: {'programa': 'MBA', 'fecha_desde': '2023-01-01'}
            
        Returns:
            DataFrame con datos de matrículas.
        """
        try:
            conn = self._conectar()
            
            # Iniciar consulta base
            query = "SELECT * FROM matriculas"
            params = []
            
            # Añadir filtros si existen
            if filtros:
                where_clauses = []
                
                if 'programa' in filtros:
                    where_clauses.append("programa = ?")
                    params.append(filtros['programa'])
                
                if 'id_lead' in filtros:
                    where_clauses.append("id_lead = ?")
                    params.append(filtros['id_lead'])
                
                if 'fecha_desde' in filtros:
                    where_clauses.append("fecha_matricula >= ?")
                    params.append(filtros['fecha_desde'])
                
                if 'fecha_hasta' in filtros:
                    where_clauses.append("fecha_matricula <= ?")
                    params.append(filtros['fecha_hasta'])
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            # Ejecutar consulta
            df = pd.read_sql(query, conn, params=params)
            
            logger.info(f"Obtenidos {len(df)} registros de matrículas desde la BD")
            return df
            
        except Exception as e:
            logger.error(f"Error al obtener matrículas: {str(e)}")
            raise
            
        finally:
            if conn:
                conn.close()
    
    def obtener_leads_con_matriculas(self, filtros: Optional[Dict] = None) -> pd.DataFrame:
        """
        Obtiene los datos de leads unidos con sus matrículas correspondientes.
        
        Args:
            filtros: Diccionario de filtros a aplicar.
            
        Returns:
            DataFrame con los datos unidos.
        """
        try:
            conn = self._conectar()
            
            # Consulta base para unión
            query = """
            SELECT l.*, m.id as id_matricula, m.fecha_matricula, m.valor_matricula, 
                   m.modalidad, m.sede
            FROM leads l
            LEFT JOIN matriculas m ON l.id = m.id_lead
            """
            params = []
            
            # Añadir filtros si existen
            if filtros:
                where_clauses = []
                
                if 'programa' in filtros:
                    where_clauses.append("l.programa = ?")
                    params.append(filtros['programa'])
                
                if 'origen' in filtros:
                    where_clauses.append("l.origen = ?")
                    params.append(filtros['origen'])
                
                if 'marca' in filtros:
                    where_clauses.append("l.marca = ?")
                    params.append(filtros['marca'])
                
                if 'fecha_desde' in filtros:
                    where_clauses.append("l.fecha_creacion >= ?")
                    params.append(filtros['fecha_desde'])
                
                if 'fecha_hasta' in filtros:
                    where_clauses.append("l.fecha_creacion <= ?")
                    params.append(filtros['fecha_hasta'])
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            # Ejecutar consulta
            df = pd.read_sql(query, conn, params=params)
            
            # Procesar datos JSON adicionales
            if not df.empty and 'datos_adicionales' in df.columns:
                # Expandir columnas JSON
                df_adicionales = pd.json_normalize(
                    df['datos_adicionales'].apply(
                        lambda x: json.loads(x) if pd.notna(x) and x != '{}' else {}
                    )
                )
                
                # Si hay columnas adicionales, añadirlas al DataFrame original
                if not df_adicionales.empty and len(df_adicionales.columns) > 0:
                    for col in df_adicionales.columns:
                        df[col] = df_adicionales[col]
                
                # Eliminar columna de datos adicionales
                df = df.drop('datos_adicionales', axis=1)
            
            # Crear columna de conversión
            df['convertido'] = df['id_matricula'].notna()
            
            logger.info(f"Obtenidos {len(df)} registros de leads con matrículas desde la BD")
            return df
            
        except Exception as e:
            logger.error(f"Error al obtener leads con matrículas: {str(e)}")
            raise
            
        finally:
            if conn:
                conn.close()
    
    def registrar_carga(self, tipo_datos: str, archivo: str, filas: int, estado: str) -> int:
        """
        Registra una carga de datos en el historial.
        
        Args:
            tipo_datos: Tipo de datos cargados ('leads' o 'matriculas').
            archivo: Nombre del archivo de origen.
            filas: Número de filas cargadas.
            estado: Estado de la carga ('completado' o mensaje de error).
            
        Returns:
            ID del registro creado.
        """
        try:
            conn = self._conectar()
            cursor = conn.cursor()
            
            # Insertar registro
            cursor.execute(
                """
                INSERT INTO historial_cargas (fecha, tipo_datos, archivo, filas, estado)
                VALUES (datetime('now'), ?, ?, ?, ?)
                """,
                (tipo_datos, archivo, filas, estado)
            )
            
            conn.commit()
            id_registro = cursor.lastrowid
            
            logger.info(f"Registrada carga {id_registro} en historial")
            return id_registro
            
        except Exception as e:
            logger.error(f"Error al registrar carga: {str(e)}")
            raise
            
        finally:
            if conn:
                conn.close()
    
    def obtener_historial_cargas(self, limite: int = 100) -> pd.DataFrame:
        """
        Obtiene el historial de cargas de datos.
        
        Args:
            limite: Límite de registros a obtener.
            
        Returns:
            DataFrame con el historial de cargas.
        """
        try:
            conn = self._conectar()
            
            # Consulta para obtener historial
            query = f"""
            SELECT id, fecha, tipo_datos, archivo, filas, estado
            FROM historial_cargas
            ORDER BY fecha DESC
            LIMIT {limite}
            """
            
            # Ejecutar consulta
            df = pd.read_sql(query, conn)
            
            logger.info(f"Obtenidos {len(df)} registros de historial de cargas")
            return df
            
        except Exception as e:
            logger.error(f"Error al obtener historial de cargas: {str(e)}")
            raise
            
        finally:
            if conn:
                conn.close()
    
    def guardar_configuracion(self, clave: str, valor: Union[str, int, float, bool, Dict, List]) -> bool:
        """
        Guarda un valor de configuración en la base de datos.
        
        Args:
            clave: Identificador de la configuración.
            valor: Valor a guardar (se convertirá a JSON si es necesario).
            
        Returns:
            True si se guardó correctamente.
        """
        try:
            conn = self._conectar()
            cursor = conn.cursor()
            
            # Determinar tipo de dato
            tipo = type(valor).__name__
            
            # Convertir a JSON si es necesario
            if isinstance(valor, (dict, list)):
                valor_str = json.dumps(valor)
            else:
                valor_str = str(valor)
            
            # Insertar o actualizar configuración
            cursor.execute(
                """
                INSERT OR REPLACE INTO configuracion (clave, valor, tipo)
                VALUES (?, ?, ?)
                """,
                (clave, valor_str, tipo)
            )
            
            conn.commit()
            logger.info(f"Guardada configuración: {clave}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al guardar configuración: {str(e)}")
            raise
            
        finally:
            if conn:
                conn.close()
    
    def obtener_configuracion(self, clave: str) -> Optional[Union[str, int, float, bool, Dict, List]]:
        """
        Obtiene un valor de configuración desde la base de datos.
        
        Args:
            clave: Identificador de la configuración.
            
        Returns:
            Valor de configuración o None si no existe.
        """
        try:
            conn = self._conectar()
            cursor = conn.cursor()
            
            # Consultar configuración
            cursor.execute(
                "SELECT valor, tipo FROM configuracion WHERE clave = ?",
                (clave,)
            )
            
            resultado = cursor.fetchone()
            
            if not resultado:
                return None
            
            valor_str, tipo = resultado
            
            # Convertir según tipo
            if tipo == 'dict':
                return json.loads(valor_str)
            elif tipo == 'list':
                return json.loads(valor_str)
            elif tipo == 'int':
                return int(valor_str)
            elif tipo == 'float':
                return float(valor_str)
            elif tipo == 'bool':
                return valor_str.lower() == 'true'
            else:
                return valor_str
            
        except Exception as e:
            logger.error(f"Error al obtener configuración: {str(e)}")
            return None
            
        finally:
            if conn:
                conn.close()
    
    def realizar_backup(self, ruta_backup: Optional[str] = None) -> str:
        """
        Realiza una copia de seguridad de la base de datos.
        
        Args:
            ruta_backup: Ruta donde guardar el backup.
                         Si no se proporciona, se usará el directorio de datos.
            
        Returns:
            Ruta del archivo de backup creado.
        """
        try:
            # Determinar ruta de backup
            if not ruta_backup:
                data_dir = Path(self.config['paths']['data'])
                timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                ruta_backup = str(data_dir / f"backup_{timestamp}.db")
            
            # Crear conexión al archivo actual
            conn = self._conectar()
            
            # Crear conexión al archivo de backup
            conn_backup = sqlite3.connect(ruta_backup)
            
            # Realizar backup
            conn.backup(conn_backup)
            
            logger.info(f"Backup creado en: {ruta_backup}")
            return ruta_backup
            
        except Exception as e:
            logger.error(f"Error al realizar backup: {str(e)}")
            raise
            
        finally:
            if conn:
                conn.close()
            if conn_backup:
                conn_backup.close() 