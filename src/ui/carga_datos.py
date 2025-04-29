"""
Módulo de interfaz para la carga de datos.
Proporciona una interfaz de usuario simple para cargar datos al sistema.
"""

import os
import pandas as pd
import streamlit as st
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import datetime
import time
from io import StringIO
import hashlib

from src.data.procesador_datos import ProcesadorDatos
from src.utils.config import get_config, update_config
from src.utils.logging import get_module_logger

logger = get_module_logger(__name__)

# Configuración de la página y estilos en español
st.set_page_config(
    page_title="Motor de Decisión - Team Digital",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ocultar el menú de Streamlit y el footer con CSS
hide_menu_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {visibility: hidden;}
        
        /* Personalizar estilos */
        .stRadio [role="radiogroup"] {
            flex-direction: row !important;
        }
        
        /* Traducir textos de elementos de Streamlit */
        button[title="View fullscreen"] {
            visibility: hidden;
        }
        
        .uploadedFile {
            color: #FF6F00 !important;
        }
        
        /* Mensajes de error/info en español */
        div[data-baseweb="notification"] {
            background-color: #FF6F00 !important;
        }
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

def check_password():
    """
    Verifica la contraseña del usuario.
    Retorna True si la contraseña es correcta, False en caso contrario.
    """
    # Si ya está autenticado, retornar True
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        return True
    
    # Inicializar estado de sesión
    if 'password' not in st.session_state:
        st.session_state.password = ''
    if 'auth_failed' not in st.session_state:
        st.session_state.auth_failed = False
    
    # Crear formulario de inicio de sesión estilizado
    auth_container = st.empty()
    with auth_container.container():
        st.markdown(
            """
            <div style="display: flex; justify-content: center;">
                <h2>Motor de Decisión</h2>
            </div>
            <div style="display: flex; justify-content: center;">
                <h4>team digital <span style="color: #FF6F00;">❤️</span></h4>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        password = st.text_input(
            "Ingrese la contraseña", 
            type="password", 
            key="password_input",
            placeholder="Contraseña"
        )
        
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            login_button = st.button("Iniciar Sesión", use_container_width=True)
        
        if st.session_state.auth_failed:
            st.error("Contraseña incorrecta. Intente nuevamente.")
        
        st.markdown(
            """
            <div style="text-align: center; margin-top: 30px; font-size: 0.8em; color: #888;">
                Sistema exclusivo para uso interno de Digital Team.<br>
                © 2025 Digital Team
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Validar contraseña
    if login_button:
        # La contraseña correcta es "teamdigital"
        if password == "teamdigital":
            st.session_state.authenticated = True
            auth_container.empty()
            return True
        else:
            st.session_state.auth_failed = True
            return False
            
    return False

class InterfazCargaDatos:
    """
    Clase para la interfaz de carga de datos usando Streamlit.
    Proporciona un panel de carga simplificado y asistente de validación.
    """
    
    def __init__(self):
        """Inicializa la interfaz de carga de datos."""
        self.config = get_config()
        self.procesador = ProcesadorDatos()
        self.tipos_archivos_validos = ['csv', 'xlsx', 'xls', 'json']
        
        # Directorios para almacenamiento
        self.dir_datos = Path(self.config['paths']['data'])
        self.dir_datos.mkdir(exist_ok=True)
        
        # Estructura de datos esperada (para validación)
        self.estructura_esperada = {
            'leads': self.procesador.columnas_requeridas['leads'],
            'matriculas': self.procesador.columnas_requeridas['matriculas']
        }
        
        # Historial de cargas
        self.historial_file = self.dir_datos / 'historial_cargas.json'
        self.historial = self._cargar_historial()
    
    def _cargar_historial(self) -> Dict:
        """Carga el historial de cargas previas."""
        if self.historial_file.exists():
            try:
                with open(self.historial_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error al cargar historial: {str(e)}")
                return {'cargas': []}
        else:
            return {'cargas': []}
    
    def _guardar_historial(self):
        """Guarda el historial de cargas."""
        try:
            with open(self.historial_file, 'w') as f:
                json.dump(self.historial, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error al guardar historial: {str(e)}")
    
    def _actualizar_historial(self, tipo_datos: str, nombre_archivo: str, filas: int, estado: str):
        """Actualiza el historial con una nueva carga."""
        self.historial['cargas'].append({
            'fecha': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tipo_datos': tipo_datos,
            'archivo': nombre_archivo,
            'filas': filas,
            'estado': estado
        })
        self._guardar_historial()
    
    def detectar_tipo_datos(self, df: pd.DataFrame) -> str:
        """
        Detecta automáticamente el tipo de datos basado en las columnas.
        
        Args:
            df (pd.DataFrame): DataFrame a analizar
            
        Returns:
            str: Tipo de datos detectado ('leads', 'matriculas' o 'desconocido')
        """
        # Contar columnas que coinciden con cada tipo
        coincidencias = {}
        for tipo, columnas in self.estructura_esperada.items():
            columnas_presentes = set(columnas).intersection(set(df.columns))
            coincidencias[tipo] = len(columnas_presentes) / len(columnas)
        
        # Determinar el tipo con mayor coincidencia
        tipo_detectado = max(coincidencias, key=coincidencias.get)
        
        # Si la coincidencia es baja, marcar como desconocido
        if coincidencias[tipo_detectado] < 0.6:
            return 'desconocido'
            
        return tipo_detectado
    
    def validar_datos(self, df: pd.DataFrame, tipo_datos: str) -> Tuple[bool, List[Dict]]:
        """
        Valida los datos cargados y genera informe de problemas.
        
        Args:
            df (pd.DataFrame): DataFrame a validar
            tipo_datos (str): Tipo de datos esperado
            
        Returns:
            Tuple[bool, List[Dict]]: (es_valido, problemas)
        """
        problemas = []
        
        # Verificar columnas requeridas
        if tipo_datos in self.estructura_esperada:
            columnas_esperadas = self.estructura_esperada[tipo_datos]
            columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]
            
            if columnas_faltantes:
                problemas.append({
                    'tipo': 'columnas_faltantes',
                    'descripcion': f"Faltan columnas requeridas: {', '.join(columnas_faltantes)}",
                    'gravedad': 'alta'
                })
        
        # Verificar valores nulos
        columnas_con_nulos = df.columns[df.isnull().any()].tolist()
        if columnas_con_nulos:
            for col in columnas_con_nulos:
                porcentaje_nulos = (df[col].isnull().sum() / len(df)) * 100
                gravedad = 'baja' if porcentaje_nulos < 5 else ('media' if porcentaje_nulos < 20 else 'alta')
                
                problemas.append({
                    'tipo': 'valores_nulos',
                    'descripcion': f"La columna '{col}' tiene {porcentaje_nulos:.1f}% de valores nulos",
                    'gravedad': gravedad
                })
        
        # Verificar duplicados
        duplicados = df.duplicated().sum()
        if duplicados > 0:
            porcentaje_duplicados = (duplicados / len(df)) * 100
            gravedad = 'baja' if porcentaje_duplicados < 1 else ('media' if porcentaje_duplicados < 5 else 'alta')
            
            problemas.append({
                'tipo': 'duplicados',
                'descripcion': f"Se detectaron {duplicados} filas duplicadas ({porcentaje_duplicados:.1f}%)",
                'gravedad': gravedad
            })
        
        # Verificar tipos de datos esperados
        if tipo_datos == 'leads':
            # Verificar fechas
            if 'fecha_creacion' in df.columns:
                try:
                    pd.to_datetime(df['fecha_creacion'], errors='raise')
                except:
                    problemas.append({
                        'tipo': 'tipo_datos_incorrecto',
                        'descripcion': "La columna 'fecha_creacion' contiene valores que no son fechas válidas",
                        'gravedad': 'alta'
                    })
            
            # Verificar numéricos
            if 'costo' in df.columns:
                if not pd.api.types.is_numeric_dtype(df['costo']) and not all(pd.to_numeric(df['costo'], errors='coerce').notna()):
                    problemas.append({
                        'tipo': 'tipo_datos_incorrecto',
                        'descripcion': "La columna 'costo' contiene valores que no son numéricos",
                        'gravedad': 'alta'
                    })
        
        elif tipo_datos == 'matriculas':
            # Verificar fechas
            if 'fecha_matricula' in df.columns:
                try:
                    pd.to_datetime(df['fecha_matricula'], errors='raise')
                except:
                    problemas.append({
                        'tipo': 'tipo_datos_incorrecto',
                        'descripcion': "La columna 'fecha_matricula' contiene valores que no son fechas válidas",
                        'gravedad': 'alta'
                    })
            
            # Verificar numéricos
            if 'valor_matricula' in df.columns:
                if not pd.api.types.is_numeric_dtype(df['valor_matricula']) and not all(pd.to_numeric(df['valor_matricula'], errors='coerce').notna()):
                    problemas.append({
                        'tipo': 'tipo_datos_incorrecto',
                        'descripcion': "La columna 'valor_matricula' contiene valores que no son numéricos",
                        'gravedad': 'alta'
                    })
        
        # Determinar validez general
        es_valido = not any(p['gravedad'] == 'alta' for p in problemas)
        
        return es_valido, problemas
    
    def guardar_datos(self, df: pd.DataFrame, tipo_datos: str, nombre_archivo: str) -> str:
        """
        Guarda los datos validados en la ubicación adecuada.
        
        Args:
            df (pd.DataFrame): DataFrame a guardar
            tipo_datos (str): Tipo de datos
            nombre_archivo (str): Nombre base del archivo
            
        Returns:
            str: Ruta del archivo guardado
        """
        # Crear nombres de archivo con timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_base = f"{tipo_datos}_{timestamp}"
        
        # Determinar extensión original
        ext_original = Path(nombre_archivo).suffix.lower()
        if not ext_original or ext_original[1:] not in self.tipos_archivos_validos:
            ext_original = '.csv'  # Default a CSV
        
        # Guardar archivo
        ruta_guardado = self.dir_datos / f"{nombre_base}{ext_original}"
        
        try:
            if ext_original == '.csv':
                df.to_csv(ruta_guardado, index=False)
            elif ext_original in ['.xlsx', '.xls']:
                df.to_excel(ruta_guardado, index=False)
            elif ext_original == '.json':
                df.to_json(ruta_guardado, orient='records', date_format='iso')
            
            logger.info(f"Datos guardados en {ruta_guardado}")
            return str(ruta_guardado)
            
        except Exception as e:
            logger.error(f"Error al guardar datos: {str(e)}")
            raise
    
    def generar_informe_carga(self, df: pd.DataFrame, tipo_datos: str) -> Dict:
        """
        Genera un informe con estadísticas de los datos cargados.
        
        Args:
            df (pd.DataFrame): DataFrame analizado
            tipo_datos (str): Tipo de datos
            
        Returns:
            Dict: Estadísticas de los datos
        """
        informe = {
            'filas': len(df),
            'columnas': len(df.columns),
            'fecha_min': None,
            'fecha_max': None,
            'distribucion_categoricas': {},
            'estadisticas_numericas': {}
        }
        
        # Detectar columnas de fecha según tipo
        col_fecha = 'fecha_creacion' if tipo_datos == 'leads' else 'fecha_matricula'
        if col_fecha in df.columns:
            fechas = pd.to_datetime(df[col_fecha], errors='coerce')
            fechas_validas = fechas.dropna()
            if not fechas_validas.empty:
                informe['fecha_min'] = fechas_validas.min().strftime("%Y-%m-%d")
                informe['fecha_max'] = fechas_validas.max().strftime("%Y-%m-%d")
        
        # Estadísticas de categorías principales
        for col in ['origen', 'programa', 'marca']:
            if col in df.columns:
                conteo = df[col].value_counts().head(10).to_dict()  # Top 10
                informe['distribucion_categoricas'][col] = conteo
        
        # Estadísticas de columnas numéricas
        columnas_numericas = df.select_dtypes(include=['number']).columns
        for col in columnas_numericas:
            informe['estadisticas_numericas'][col] = {
                'min': float(df[col].min()) if not df[col].empty else None,
                'max': float(df[col].max()) if not df[col].empty else None,
                'media': float(df[col].mean()) if not df[col].empty else None,
                'nulos': int(df[col].isnull().sum())
            }
        
        return informe
    
    def mostrar_interfaz_carga(self):
        """
        Muestra la interfaz de carga de datos en Streamlit.
        """
        # Barra lateral con logo team digital
        st.sidebar.markdown(
            """
            <div style="text-align: center; margin-top: 20px;">
                <h3>team digital <span style="color: #FF6F00;">❤️</span></h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Agregar opciones de menú en la barra lateral
        st.sidebar.title("Menú Principal")
        opcion_menu = st.sidebar.radio(
            "",
            ["Carga de Datos", "Análisis", "Reportes", "Configuración"],
            index=0,
        )
        
        # Mostrar el usuario autenticado
        st.sidebar.markdown(
            """
            <div style="position: fixed; bottom: 30px; left: 30px; font-size: 0.8em;">
                🔒 Usuario autenticado
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Botón para cerrar sesión
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.authenticated = False
            st.experimental_rerun()
        
        st.title("Carga de Datos - Motor de Decisión")
        
        # Panel principal
        st.header("Selecciona los archivos a cargar")
        
        # Selector de tipo de datos
        tipo_datos = st.radio(
            "Tipo de datos a cargar:",
            ["Leads", "Matrículas", "Auto-detectar"],
            horizontal=True
        )
        tipo_datos = tipo_datos.lower() if tipo_datos != "Auto-detectar" else None
        
        # Carga de archivos
        uploaded_file = st.file_uploader(
            "Arrastra o selecciona archivos CSV, Excel o JSON", 
            type=self.tipos_archivos_validos,
            accept_multiple_files=False
        )
        
        # Opción alternativa: Google Sheets
        st.divider()
        st.subheader("O conecta con Google Sheets")
        sheet_url = st.text_input("URL de Google Sheets:")
        
        btn_conectar_sheets = st.button("Conectar con Google Sheets")
        
        # Información de última carga
        if self.historial['cargas']:
            ultima_carga = self.historial['cargas'][-1]
            st.info(f"Última carga: {ultima_carga['tipo_datos']} - {ultima_carga['fecha']} ({ultima_carga['filas']} filas)")
        
        # Procesamiento cuando se sube un archivo
        if uploaded_file is not None:
            # Mostrar barra de progreso para simular carga
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(101):
                progress_bar.progress(i)
                if i < 30:
                    status_text.text("Analizando archivo...")
                elif i < 60:
                    status_text.text("Detectando estructura...")
                elif i < 90:
                    status_text.text("Validando datos...")
                else:
                    status_text.text("Completando análisis...")
                time.sleep(0.01)
            
            # Leer datos
            try:
                # Determinar formato
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.json'):
                    df = pd.read_json(uploaded_file)
                
                # Auto-detectar tipo si no se especificó
                if tipo_datos is None:
                    tipo_datos = self.detectar_tipo_datos(df)
                    st.success(f"Tipo de datos auto-detectado: {tipo_datos.upper()}")
                
                # Validar datos
                es_valido, problemas = self.validar_datos(df, tipo_datos)
                
                # Mostrar vista previa
                st.subheader("Vista previa de datos")
                st.dataframe(df.head(5))
                
                # Mostrar estadísticas básicas
                st.subheader("Resumen de datos")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Filas: {len(df)}")
                    st.write(f"Columnas: {len(df.columns)}")
                
                with col2:
                    if 'fecha_creacion' in df.columns:
                        fechas = pd.to_datetime(df['fecha_creacion'], errors='coerce')
                        fechas_validas = fechas.dropna()
                        if not fechas_validas.empty:
                            st.write(f"Fecha más antigua: {fechas_validas.min().strftime('%Y-%m-%d')}")
                            st.write(f"Fecha más reciente: {fechas_validas.max().strftime('%Y-%m-%d')}")
                
                # Mostrar resultados de validación
                if problemas:
                    st.subheader("Problemas detectados")
                    for p in problemas:
                        if p['gravedad'] == 'alta':
                            st.error(p['descripcion'])
                        elif p['gravedad'] == 'media':
                            st.warning(p['descripcion'])
                        else:
                            st.info(p['descripcion'])
                
                # Botones de acción
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Descargar plantilla correcta", disabled=not problemas):
                        # Generar plantilla según tipo de datos
                        if tipo_datos in self.estructura_esperada:
                            columnas = self.estructura_esperada[tipo_datos]
                            df_plantilla = pd.DataFrame(columns=columnas)
                            
                            # Crear buffer y generar descarga
                            buffer = StringIO()
                            df_plantilla.to_csv(buffer, index=False)
                            
                            st.download_button(
                                label="Descargar plantilla CSV",
                                data=buffer.getvalue(),
                                file_name=f"plantilla_{tipo_datos}.csv",
                                mime="text/csv"
                            )
                
                with col2:
                    if st.button("Cargar y procesar datos", disabled=not es_valido and len(problemas) > 0):
                        try:
                            # Guardar datos
                            ruta_guardado = self.guardar_datos(df, tipo_datos, uploaded_file.name)
                            
                            # Actualizar historial
                            self._actualizar_historial(
                                tipo_datos=tipo_datos,
                                nombre_archivo=uploaded_file.name,
                                filas=len(df),
                                estado="completado"
                            )
                            
                            # Notificar éxito
                            st.success(f"Datos cargados exitosamente en {ruta_guardado}")
                            
                            # Generar informe detallado
                            informe = self.generar_informe_carga(df, tipo_datos)
                            
                            # Mostrar opción de continuar al análisis
                            st.subheader("¿Qué deseas hacer ahora?")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("Procesar y analizar datos"):
                                    st.info("Redirigiendo al módulo de análisis...")
                                    # Aquí se añadiría la redirección o el cambio de página
                            
                            with col2:
                                if st.button("Cargar más datos"):
                                    st.experimental_rerun()
                                    
                        except Exception as e:
                            st.error(f"Error al procesar datos: {str(e)}")
                            logger.error(f"Error en procesamiento: {str(e)}", exc_info=True)
                            
                            # Actualizar historial con error
                            self._actualizar_historial(
                                tipo_datos=tipo_datos,
                                nombre_archivo=uploaded_file.name,
                                filas=len(df),
                                estado=f"error: {str(e)}"
                            )
                            
            except Exception as e:
                st.error(f"Error al leer archivo: {str(e)}")
                logger.error(f"Error al leer archivo: {str(e)}", exc_info=True)
        
        # Procesamiento de Google Sheets
        elif btn_conectar_sheets and sheet_url:
            st.info("Conectando con Google Sheets...")
            # Aquí iría la lógica para conectar con Google Sheets
            # Por ahora es solo un placeholder
            st.warning("Funcionalidad en desarrollo")
        
        # Panel de opciones avanzadas
        with st.expander("Opciones avanzadas"):
            st.subheader("Configuración de procesamiento")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.checkbox("Eliminar duplicados automáticamente", value=True)
                st.checkbox("Limpiar valores nulos", value=False)
                st.checkbox("Convertir tipos de datos automáticamente", value=True)
            
            with col2:
                st.selectbox(
                    "Periodo a procesar",
                    ["Todo el conjunto", "Último mes", "Último trimestre", "Último año"]
                )
                
                st.multiselect(
                    "Canales a incluir",
                    ["Facebook", "Google", "Instagram", "LinkedIn", "Email", "Orgánico"],
                    default=["Facebook", "Google", "Instagram", "LinkedIn", "Email", "Orgánico"]
                )

def main():
    """Función principal para ejecutar la interfaz de carga de datos."""
    if check_password():
        interfaz = InterfazCargaDatos()
        interfaz.mostrar_interfaz_carga()

if __name__ == "__main__":
    main() 