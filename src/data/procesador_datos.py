"""
Módulo para procesamiento de datos.
Contiene funciones para preparar, limpiar y transformar datos para el entrenamiento de modelos.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Union, Optional

from src.utils.config import get_config
from src.utils.logging import get_module_logger

logger = get_module_logger(__name__)

class ProcesadorDatos:
    """
    Clase para procesar y preparar datos para entrenamiento y predicción.
    Incluye funciones para limpieza, transformación y validación de datos.
    """
    
    def __init__(self):
        """
        Inicializa el procesador de datos.
        """
        self.config = get_config()
        self.columnas_requeridas = {
            'leads': [
                'id_lead', 'fecha_creacion', 'origen', 'programa',
                'marca', 'costo', 'estado'
            ],
            'matriculas': [
                'id_matricula', 'id_lead', 'fecha_matricula', 'programa',
                'marca', 'valor_matricula'
            ]
        }
    
    def cargar_datos(self, ruta_archivo: str) -> pd.DataFrame:
        """
        Carga datos desde un archivo CSV o Excel.
        
        Args:
            ruta_archivo (str): Ruta al archivo de datos
            
        Returns:
            pd.DataFrame: DataFrame con los datos cargados
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el formato del archivo no es válido
        """
        ruta = Path(ruta_archivo)
        
        if not ruta.exists():
            mensaje = f"El archivo {ruta} no existe"
            logger.error(mensaje)
            raise FileNotFoundError(mensaje)
        
        extension = ruta.suffix.lower()
        
        try:
            if extension == '.csv':
                datos = pd.read_csv(ruta)
            elif extension in ['.xlsx', '.xls']:
                datos = pd.read_excel(ruta)
            else:
                mensaje = f"Formato de archivo no soportado: {extension}"
                logger.error(mensaje)
                raise ValueError(mensaje)
                
            logger.info(f"Datos cargados desde {ruta}: {datos.shape[0]} filas, {datos.shape[1]} columnas")
            return datos
            
        except Exception as e:
            mensaje = f"Error al cargar los datos desde {ruta}: {str(e)}"
            logger.error(mensaje)
            raise
    
    def validar_datos(self, datos: pd.DataFrame, tipo_datos: str) -> Tuple[bool, List[str]]:
        """
        Valida que los datos contengan las columnas requeridas.
        
        Args:
            datos (pd.DataFrame): DataFrame a validar
            tipo_datos (str): Tipo de datos ('leads' o 'matriculas')
            
        Returns:
            Tuple[bool, List[str]]: (es_valido, columnas_faltantes)
        """
        if tipo_datos not in self.columnas_requeridas:
            mensaje = f"Tipo de datos no reconocido: {tipo_datos}"
            logger.error(mensaje)
            raise ValueError(mensaje)
            
        columnas_requeridas = self.columnas_requeridas[tipo_datos]
        columnas_faltantes = [col for col in columnas_requeridas if col not in datos.columns]
        
        es_valido = len(columnas_faltantes) == 0
        
        if not es_valido:
            mensaje = f"Faltan columnas requeridas para {tipo_datos}: {columnas_faltantes}"
            logger.warning(mensaje)
            
        return es_valido, columnas_faltantes
    
    def limpiar_datos(self, datos: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia los datos eliminando duplicados y valores nulos según configuración.
        
        Args:
            datos (pd.DataFrame): DataFrame a limpiar
            
        Returns:
            pd.DataFrame: DataFrame limpio
        """
        # Guardar dimensiones originales para log
        filas_orig = datos.shape[0]
        
        # Eliminar filas duplicadas
        datos = datos.drop_duplicates()
        filas_tras_dedup = datos.shape[0]
        
        # Reportar duplicados eliminados
        duplicados_eliminados = filas_orig - filas_tras_dedup
        if duplicados_eliminados > 0:
            logger.info(f"Se eliminaron {duplicados_eliminados} filas duplicadas")
        
        # Contar valores nulos
        nulos_por_columna = datos.isnull().sum()
        columnas_con_nulos = nulos_por_columna[nulos_por_columna > 0]
        
        if not columnas_con_nulos.empty:
            logger.info(f"Valores nulos por columna: {columnas_con_nulos.to_dict()}")
        
        return datos
    
    def convertir_tipos_datos(self, datos: pd.DataFrame, tipo_datos: str) -> pd.DataFrame:
        """
        Convierte las columnas al tipo de dato correcto.
        
        Args:
            datos (pd.DataFrame): DataFrame a convertir
            tipo_datos (str): Tipo de datos ('leads' o 'matriculas')
            
        Returns:
            pd.DataFrame: DataFrame con tipos de datos convertidos
        """
        datos_conv = datos.copy()
        
        # Convertir columnas de fecha
        if tipo_datos == 'leads' and 'fecha_creacion' in datos_conv.columns:
            datos_conv['fecha_creacion'] = pd.to_datetime(
                datos_conv['fecha_creacion'], errors='coerce'
            )
            
        if tipo_datos == 'matriculas' and 'fecha_matricula' in datos_conv.columns:
            datos_conv['fecha_matricula'] = pd.to_datetime(
                datos_conv['fecha_matricula'], errors='coerce'
            )
        
        # Convertir columnas numéricas
        if tipo_datos == 'leads' and 'costo' in datos_conv.columns:
            datos_conv['costo'] = pd.to_numeric(datos_conv['costo'], errors='coerce')
            
        if tipo_datos == 'matriculas' and 'valor_matricula' in datos_conv.columns:
            datos_conv['valor_matricula'] = pd.to_numeric(
                datos_conv['valor_matricula'], errors='coerce'
            )
        
        return datos_conv
    
    def filtrar_datos(self, 
                     datos: pd.DataFrame, 
                     filtros: Dict[str, Union[str, List[str], int, float]] = None
                     ) -> pd.DataFrame:
        """
        Filtra los datos según criterios especificados.
        
        Args:
            datos (pd.DataFrame): DataFrame a filtrar
            filtros (Dict): Diccionario con criterios de filtrado {columna: valor}
                          Los valores pueden ser escalares o listas
            
        Returns:
            pd.DataFrame: DataFrame filtrado
        """
        if filtros is None or not filtros:
            return datos
            
        datos_filtrados = datos.copy()
        filas_orig = datos_filtrados.shape[0]
        
        for columna, valor in filtros.items():
            if columna not in datos_filtrados.columns:
                logger.warning(f"La columna '{columna}' no existe en los datos, se omite el filtro")
                continue
                
            if isinstance(valor, list):
                datos_filtrados = datos_filtrados[datos_filtrados[columna].isin(valor)]
            else:
                datos_filtrados = datos_filtrados[datos_filtrados[columna] == valor]
        
        filas_filtradas = filas_orig - datos_filtrados.shape[0]
        logger.info(f"Se filtraron {filas_filtradas} filas según los criterios especificados")
        
        return datos_filtrados
    
    def unir_leads_matriculas(self, 
                             datos_leads: pd.DataFrame, 
                             datos_matriculas: pd.DataFrame
                             ) -> pd.DataFrame:
        """
        Une datos de leads con datos de matrículas.
        
        Args:
            datos_leads (pd.DataFrame): DataFrame con datos de leads
            datos_matriculas (pd.DataFrame): DataFrame con datos de matrículas
            
        Returns:
            pd.DataFrame: DataFrame con datos unidos
        """
        # Validar columnas requeridas
        leads_valido, _ = self.validar_datos(datos_leads, 'leads')
        matriculas_valido, _ = self.validar_datos(datos_matriculas, 'matriculas')
        
        if not (leads_valido and matriculas_valido):
            logger.warning("Los datos no contienen todas las columnas requeridas, la unión puede ser incorrecta")
        
        # Verificar clave de unión
        if 'id_lead' not in datos_leads.columns or 'id_lead' not in datos_matriculas.columns:
            mensaje = "No se puede unir los datos: falta la columna 'id_lead'"
            logger.error(mensaje)
            raise ValueError(mensaje)
        
        # Unir datos con left join
        datos_unidos = datos_leads.merge(
            datos_matriculas,
            on='id_lead',
            how='left',
            suffixes=('_lead', '_matricula')
        )
        
        # Crear columna de conversión (True si hay matrícula, False si no)
        datos_unidos['convertido'] = datos_unidos['id_matricula'].notna()
        
        # Calcular tasa de conversión para log
        total_leads = datos_leads.shape[0]
        total_matriculas = datos_unidos['convertido'].sum()
        tasa_conversion = (total_matriculas / total_leads) * 100 if total_leads > 0 else 0
        
        logger.info(f"Datos unidos: {datos_unidos.shape[0]} filas, {datos_unidos.shape[1]} columnas")
        logger.info(f"Tasa de conversión: {tasa_conversion:.2f}% ({total_matriculas}/{total_leads})")
        
        return datos_unidos
    
    def crear_caracteristicas(self, datos: pd.DataFrame) -> pd.DataFrame:
        """
        Crea características adicionales para el modelado.
        
        Args:
            datos (pd.DataFrame): DataFrame con datos
            
        Returns:
            pd.DataFrame: DataFrame con nuevas características
        """
        datos_procesados = datos.copy()
        
        # Características temporales (si hay columnas de fecha)
        columnas_fecha = [col for col in datos_procesados.columns 
                        if 'fecha' in col.lower() and 
                        pd.api.types.is_datetime64_any_dtype(datos_procesados[col])]
        
        for col_fecha in columnas_fecha:
            # Extraer componentes de fecha
            datos_procesados[f'{col_fecha}_mes'] = datos_procesados[col_fecha].dt.month
            datos_procesados[f'{col_fecha}_dia_semana'] = datos_procesados[col_fecha].dt.dayofweek
            datos_procesados[f'{col_fecha}_trimestre'] = datos_procesados[col_fecha].dt.quarter
            
            # Si hay dos columnas de fecha, calcular diferencia en días
            if len(columnas_fecha) >= 2 and col_fecha != columnas_fecha[0]:
                col1, col2 = columnas_fecha[0], col_fecha
                datos_procesados[f'dias_entre_{col1}_y_{col2}'] = (
                    datos_procesados[col2] - datos_procesados[col1]
                ).dt.days
        
        # Características categóricas (one-hot encoding básico)
        for col in ['origen', 'programa', 'marca']:
            if col in datos_procesados.columns:
                # Limitar a las 10 categorías más frecuentes para evitar demasiadas columnas
                top_categorias = datos_procesados[col].value_counts().nlargest(10).index
                for categoria in top_categorias:
                    datos_procesados[f'{col}_{categoria}'] = (datos_procesados[col] == categoria).astype(int)
        
        logger.info(f"Se crearon {datos_procesados.shape[1] - datos.shape[1]} nuevas características")
        
        return datos_procesados
    
    def dividir_datos_entrenamiento(self, 
                                   datos: pd.DataFrame,
                                   columna_objetivo: str,
                                   columnas_caracteristicas: List[str] = None,
                                   test_size: float = 0.2,
                                   random_state: int = 42
                                   ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Divide los datos en conjuntos de entrenamiento y prueba.
        
        Args:
            datos (pd.DataFrame): DataFrame con datos
            columna_objetivo (str): Nombre de la columna objetivo
            columnas_caracteristicas (List[str]): Lista de columnas a usar como características
            test_size (float): Proporción del conjunto de prueba
            random_state (int): Semilla para reproducibilidad
            
        Returns:
            Tuple: (X_train, X_test, y_train, y_test)
        """
        from sklearn.model_selection import train_test_split
        
        if columna_objetivo not in datos.columns:
            mensaje = f"La columna objetivo '{columna_objetivo}' no existe en los datos"
            logger.error(mensaje)
            raise ValueError(mensaje)
        
        # Si no se especifican columnas, usar todas excepto la objetivo
        if columnas_caracteristicas is None:
            columnas_caracteristicas = [col for col in datos.columns 
                                      if col != columna_objetivo]
        
        # Verificar columnas
        columnas_faltantes = [col for col in columnas_caracteristicas 
                            if col not in datos.columns]
        
        if columnas_faltantes:
            mensaje = f"Las siguientes columnas no existen en los datos: {columnas_faltantes}"
            logger.error(mensaje)
            raise ValueError(mensaje)
        
        # Dividir datos
        X = datos[columnas_caracteristicas]
        y = datos[columna_objetivo]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        logger.info(f"Datos divididos en entrenamiento ({X_train.shape[0]} filas) y prueba ({X_test.shape[0]} filas)")
        
        return X_train, X_test, y_train, y_test 