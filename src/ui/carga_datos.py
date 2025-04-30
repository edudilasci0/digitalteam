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
import numpy as np

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
        self.dir_datos = Path(self.config['paths']['data']['actual'])
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
            "Seleccionar opción",
            ["Carga de Datos", "Análisis", "Reportes", "Reportes Avanzados", "Configuración"],
            index=0,
            label_visibility="collapsed"
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
        
        # Mostrar la interfaz según la opción seleccionada
        if opcion_menu == "Carga de Datos":
            self.mostrar_seccion_carga()
        elif opcion_menu == "Análisis":
            self.mostrar_seccion_analisis()
        elif opcion_menu == "Reportes":
            self.mostrar_seccion_reportes()
        elif opcion_menu == "Reportes Avanzados":
            self.mostrar_seccion_reportes_avanzados()
        elif opcion_menu == "Configuración":
            self.mostrar_seccion_configuracion()
    
    def mostrar_seccion_carga(self):
        """
        Muestra la interfaz de carga de datos.
        """
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
    
    def mostrar_seccion_analisis(self):
        """
        Muestra la interfaz de análisis de datos.
        """
        st.title("Análisis de Datos - Motor de Decisión")
        
        # Selector de tipo de análisis
        tipo_analisis = st.selectbox(
            "Tipo de análisis a realizar:",
            ["Análisis de conversión", "Análisis de ROI", "Análisis de tendencias", 
             "Análisis de canales", "Análisis de segmentos", "Análisis predictivo"]
        )
        
        # Parámetros comunes
        st.subheader("Parámetros de análisis")
        col1, col2 = st.columns(2)
        
        with col1:
            fecha_inicio = st.date_input("Fecha de inicio")
            st.selectbox("Programa", ["Todos", "Programa 1", "Programa 2", "Programa 3"])
            st.multiselect("Canales", ["Facebook", "Google", "Instagram", "LinkedIn", "Email", "Orgánico"])
        
        with col2:
            fecha_fin = st.date_input("Fecha de fin")
            st.selectbox("Marca", ["Todas", "Marca 1", "Marca 2", "Marca 3"])
            st.selectbox("Frecuencia", ["Diaria", "Semanal", "Mensual", "Trimestral"])
        
        # Parámetros específicos según tipo de análisis
        if tipo_analisis == "Análisis de conversión":
            st.subheader("Configuración de análisis de conversión")
            col1, col2 = st.columns(2)
            
            with col1:
                st.selectbox("Métricas principales", ["Tasa de conversión", "Costo por lead", "Costo por matrícula"])
                st.checkbox("Incluir datos históricos", value=True)
            
            with col2:
                st.selectbox("Desglosar por", ["Canal", "Programa", "Marca", "Período"])
                st.checkbox("Comparar con objetivo", value=False)
        
        elif tipo_analisis == "Análisis de ROI":
            st.subheader("Configuración de análisis de ROI")
            col1, col2 = st.columns(2)
            
            with col1:
                st.selectbox("Métricas de ROI", ["ROI total", "ROI por canal", "ROI por programa"])
                st.number_input("Valor promedio de matrícula", value=1000, step=100)
            
            with col2:
                st.selectbox("Horizonte temporal", ["30 días", "90 días", "180 días", "1 año"])
                st.checkbox("Incluir costos indirectos", value=False)
        
        elif tipo_analisis == "Análisis predictivo":
            st.subheader("Configuración de análisis predictivo")
            col1, col2 = st.columns(2)
            
            with col1:
                st.selectbox("Modelo predictivo", ["Regresión lineal", "Random Forest", "Gradient Boosting"])
                st.number_input("Horizonte de predicción (días)", value=30, step=10)
            
            with col2:
                st.selectbox("Variable a predecir", ["Matrículas", "Leads", "Conversión"])
                st.checkbox("Incluir intervalos de confianza", value=True)
        
        # Botón para ejecutar el análisis
        if st.button("Ejecutar análisis", type="primary", use_container_width=True):
            with st.spinner("Procesando análisis..."):
                # Simulación de procesamiento
                progress_bar = st.progress(0)
                for i in range(101):
                    progress_bar.progress(i)
                    time.sleep(0.02)
                
                # Resultados simulados
                st.success("Análisis completado correctamente")
                
                # Gráficos de ejemplo
                st.subheader("Resultados del análisis")
                
                # Gráfico de ejemplo 1
                chart_data = pd.DataFrame({
                    'Fecha': pd.date_range(start=fecha_inicio, end=fecha_fin),
                    'Valor': [100 + i * 2 + i * i * 0.1 + np.random.randint(-10, 10) for i in range((fecha_fin - fecha_inicio).days + 1)]
                })
                
                st.line_chart(chart_data.set_index('Fecha'))
                
                # Tabla de resultados
                st.subheader("Métricas principales")
                metrics_data = pd.DataFrame({
                    'Métrica': ['Tasa de conversión', 'Costo promedio', 'ROI estimado', 'Tendencia'],
                    'Valor': ['8.5%', '$45.32', '324%', 'Positiva'],
                    'Cambio vs período anterior': ['+1.2%', '-$3.45', '+28%', '↑']
                })
                
                st.table(metrics_data)
                
                # Opciones para continuar
                st.subheader("¿Qué deseas hacer ahora?")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.button("Descargar resultados")
                
                with col2:
                    st.button("Generar informe")
                
                with col3:
                    st.button("Nuevo análisis")
    
    def mostrar_seccion_reportes(self):
        """
        Muestra la interfaz de reportes.
        """
        st.title("Reportes - Motor de Decisión")
        
        # Selector de tipo de reporte
        tipo_reporte = st.selectbox(
            "Tipo de reporte a generar:",
            ["Reporte ejecutivo", "Reporte de marketing", "Reporte de conversión", 
             "Reporte de ROI", "Reporte de tendencias", "Reporte personalizado"]
        )
        
        # Parámetros comunes
        st.subheader("Parámetros del reporte")
        col1, col2 = st.columns(2)
        
        with col1:
            fecha_inicio = st.date_input("Fecha de inicio")
            st.selectbox("Programa", ["Todos", "Programa 1", "Programa 2", "Programa 3"])
            formato_reporte = st.selectbox("Formato", ["PDF", "Excel", "PowerPoint", "Google Data Studio"])
        
        with col2:
            fecha_fin = st.date_input("Fecha de fin")
            st.selectbox("Marca", ["Todas", "Marca 1", "Marca 2", "Marca 3"])
            st.checkbox("Incluir gráficos", value=True)
        
        # Parámetros específicos según tipo de reporte
        if tipo_reporte == "Reporte ejecutivo":
            st.subheader("Configuración de reporte ejecutivo")
            
            metricas_incluir = st.multiselect(
                "Métricas a incluir",
                ["Resumen general", "KPIs principales", "Comparativa con período anterior", 
                 "Proyecciones", "Recomendaciones"],
                default=["Resumen general", "KPIs principales", "Comparativa con período anterior"]
            )
            
            nivel_detalle = st.slider("Nivel de detalle", 1, 5, 3)
            
            st.checkbox("Incluir resumen ejecutivo", value=True)
            st.checkbox("Incluir recomendaciones automáticas", value=True)
        
        elif tipo_reporte == "Reporte de marketing":
            st.subheader("Configuración de reporte de marketing")
            
            metricas_incluir = st.multiselect(
                "Métricas a incluir",
                ["Rendimiento por canal", "Costo por adquisición", "Tasa de conversión", 
                 "Eficiencia de campañas", "Segmentación de audiencia"],
                default=["Rendimiento por canal", "Costo por adquisición", "Tasa de conversión"]
            )
            
            desglosar_por = st.multiselect(
                "Desglosar por",
                ["Canal", "Campaña", "Programa", "Ubicación geográfica", "Dispositivo"],
                default=["Canal", "Campaña"]
            )
            
            st.checkbox("Incluir comparativa con competidores", value=False)
        
        elif tipo_reporte == "Reporte personalizado":
            st.subheader("Configuración de reporte personalizado")
            
            # Columnas personalizadas
            st.multiselect(
                "Selecciona las columnas para tu reporte",
                ["Fecha", "Canal", "Campaña", "Leads", "Matrículas", "Costo", "ROI", 
                 "Tasa de conversión", "Costo por lead", "Costo por matrícula"],
                default=["Fecha", "Canal", "Leads", "Matrículas", "Costo", "ROI"]
            )
            
            # Visualizaciones
            st.multiselect(
                "Visualizaciones a incluir",
                ["Gráfico de líneas", "Gráfico de barras", "Gráfico circular", "Mapa de calor", 
                 "Tabla pivote", "KPIs", "Comparativas"],
                default=["Gráfico de líneas", "Gráfico de barras", "KPIs"]
            )
            
            # Estilo
            st.selectbox("Estilo de reporte", ["Corporativo", "Minimalista", "Detallado", "Personalizado"])
        
        # Información adicional
        st.subheader("Información adicional")
        destinatarios = st.text_input("Destinatarios de correo (separados por coma)")
        programar = st.checkbox("Programar envío recurrente", value=False)
        
        if programar:
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("Frecuencia", ["Diaria", "Semanal", "Mensual"])
            with col2:
                st.selectbox("Hora de envío", [f"{i:02d}:00" for i in range(24)])
        
        # Botón para generar el reporte
        if st.button("Generar reporte", type="primary", use_container_width=True):
            with st.spinner("Generando reporte..."):
                # Simulación de procesamiento
                progress_bar = st.progress(0)
                for i in range(101):
                    progress_bar.progress(i)
                    time.sleep(0.02)
                
                # Éxito simulado
                st.success(f"Reporte {tipo_reporte} generado correctamente en formato {formato_reporte}")
                
                # Opciones post-generación
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label=f"Descargar reporte ({formato_reporte})",
                        data=b"contenido_simulado",
                        file_name=f"reporte_{tipo_reporte.lower().replace(' ', '_')}_{fecha_inicio.strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                
                with col2:
                    if destinatarios:
                        st.button("Enviar por correo")
                    else:
                        st.button("Configurar envío por correo")
    
    def mostrar_seccion_reportes_avanzados(self):
        """
        Muestra la interfaz de reportes avanzados.
        """
        st.title("Reportes Avanzados - Motor de Decisión")
        
        # Selector de tipo de reporte avanzado
        tipo_reporte = st.selectbox(
            "Tipo de reporte avanzado:",
            ["Análisis multivariable", "Segmentación avanzada", "Predicción por cohortes", 
             "Análisis de atribución", "Modelado predictivo", "Reporte personalizado avanzado"]
        )
        
        # Parámetros comunes
        st.subheader("Configuración avanzada")
        col1, col2 = st.columns(2)
        
        with col1:
            fecha_inicio = st.date_input("Fecha de inicio", key="adv_fecha_inicio")
            st.selectbox("Nivel de agregación", ["Diario", "Semanal", "Mensual", "Trimestral", "Personalizado"])
            formato_reporte = st.selectbox("Formato de salida", ["Dashboard interactivo", "PDF avanzado", "Excel con macros", "Power BI", "API JSON"])
        
        with col2:
            fecha_fin = st.date_input("Fecha de fin", key="adv_fecha_fin")
            st.selectbox("Motor de análisis", ["Estándar", "Avanzado (ML)", "Estadístico", "Big Data"])
            st.checkbox("Incluir métricas avanzadas", value=True)
        
        # Parámetros específicos según tipo de reporte
        if tipo_reporte == "Análisis multivariable":
            st.subheader("Configuración de análisis multivariable")
            
            variables = st.multiselect(
                "Variables a correlacionar",
                ["Inversión por canal", "Tasa de conversión", "Costo por lead", "Tiempo de conversión", 
                 "Valor de matrícula", "Afinidad de programa", "Comportamiento en sitio", "Retención", "LTV"],
                default=["Inversión por canal", "Tasa de conversión", "Costo por lead"]
            )
            
            st.selectbox(
                "Método de correlación",
                ["Pearson", "Spearman", "Kendall", "Regresión múltiple", "PCA"]
            )
            
            st.slider("Umbral de significancia", 0.01, 0.10, 0.05, 0.01)
            st.checkbox("Incluir gráficos de correlación", value=True)
            st.checkbox("Normalizar variables", value=True)
        
        elif tipo_reporte == "Análisis de atribución":
            st.subheader("Configuración de análisis de atribución")
            
            st.selectbox(
                "Modelo de atribución",
                ["First Touch", "Last Touch", "Linear", "Time Decay", "U-Shaped", "Markov Chains", "Shapley", "Personalizado"]
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.number_input("Ventana de atribución (días)", min_value=1, max_value=90, value=30)
                st.checkbox("Incluir medios offline", value=False)
            
            with col2:
                st.multiselect(
                    "Canales a incluir",
                    ["Facebook Ads", "Google Ads", "Email Marketing", "Instagram", "TikTok", "Organic", "Referral", "Direct"],
                    default=["Facebook Ads", "Google Ads", "Email Marketing", "Organic"]
                )
                st.checkbox("Comparar modelos de atribución", value=True)
            
            st.checkbox("Análisis de rutas de conversión", value=True)
            
        elif tipo_reporte == "Modelado predictivo":
            st.subheader("Configuración de modelado predictivo")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.selectbox(
                    "Objetivo de predicción",
                    ["Matrículas futuras", "ROI por canal", "Asignación óptima de presupuesto", 
                     "Tasa de conversión", "Demanda por programa", "Abandono"]
                )
                
                st.selectbox(
                    "Algoritmo de predicción",
                    ["Regresión lineal", "Random Forest", "Gradient Boosting", "XGBoost", 
                     "Prophet", "ARIMA", "LSTM", "Ensemble"]
                )
                
                st.number_input("Horizonte de predicción (días)", min_value=1, max_value=365, value=90)
            
            with col2:
                st.multiselect(
                    "Variables predictoras",
                    ["Histórico de conversión", "Estacionalidad", "Tendencias de mercado", 
                     "Presupuesto de marketing", "Competencia", "Factores macroeconómicos"],
                    default=["Histórico de conversión", "Estacionalidad"]
                )
                
                st.slider("División train/test", 0.5, 0.9, 0.8, 0.05)
                st.checkbox("Incluir intervalos de confianza", value=True)
            
            st.checkbox("Validación cruzada", value=True)
            st.checkbox("Optimización de hiperparámetros", value=True)
            st.text_area("Variables externas (una por línea)")
        
        # Configuración de visualización
        st.subheader("Opciones de visualización avanzadas")
        
        visualizaciones = st.multiselect(
            "Visualizaciones a incluir",
            ["Mapas de calor", "Gráficos de dispersión 3D", "Análisis de redes", "Series temporales", 
             "Árboles de decisión", "Clustering", "Gráficos de área", "KPIs dinámicos"],
            default=["Mapas de calor", "Series temporales", "KPIs dinámicos"]
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.selectbox("Esquema de color", ["Corporate", "Analytical", "Divergent", "Sequential", "Personalizado"])
        
        with col2:
            st.selectbox("Nivel de interactividad", ["Estático", "Interactivo básico", "Completamente interactivo"])
        
        with col3:
            st.selectbox("Formato de exportación", ["HTML", "PDF", "PNG", "Interactive Dashboard"])
        
        # Programación y distribución
        st.subheader("Programación y distribución")
        
        col1, col2 = st.columns(2)
        
        with col1:
            programar = st.checkbox("Programar generación periódica", value=False)
            if programar:
                st.selectbox("Frecuencia", ["Diaria", "Semanal", "Mensual", "Trimestral"])
                st.selectbox("Día de envío", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"])
        
        with col2:
            distribuir = st.checkbox("Distribuir automáticamente", value=False)
            if distribuir:
                st.text_input("Destinatarios (emails separados por comas)")
                st.text_area("Mensaje personalizado")
        
        # Botón para generar el reporte
        if st.button("Generar reporte avanzado", type="primary", use_container_width=True):
            with st.spinner("Generando reporte avanzado..."):
                # Simulación de procesamiento
                progress_bar = st.progress(0)
                for i in range(101):
                    progress_bar.progress(i)
                    time.sleep(0.02)
                
                # Resultados simulados
                st.success(f"Reporte avanzado '{tipo_reporte}' generado correctamente")
                
                # Vista previa
                st.subheader("Vista previa")
                
                # Gráfico de ejemplo (simulado)
                import numpy as np
                
                # Datos de ejemplo para la visualización
                dates = pd.date_range(start='2023-01-01', periods=100)
                np.random.seed(42)
                values = np.cumsum(np.random.randn(100)) + 100
                values2 = np.cumsum(np.random.randn(100)) + 120
                
                chart_data = pd.DataFrame({
                    'Fecha': dates,
                    'Métrica 1': values,
                    'Métrica 2': values2
                })
                
                # Mostrar visualización
                st.line_chart(chart_data.set_index('Fecha'))
                
                # Insights generados
                st.subheader("Insights principales")
                
                st.info("Se detectó una correlación significativa (r=0.78) entre la inversión en Facebook Ads y las matrículas efectivas con un retraso de 15 días.")
                st.info("El modelo predictivo estima un aumento del 22% en conversiones para el próximo trimestre, con un intervalo de confianza del 95%.")
                st.info("El análisis de atribución muestra que Google Ads está subvalorado en un 15% en el modelo actual de seguimiento.")
                
                # Acciones
                st.subheader("Acciones recomendadas")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        label="Descargar reporte completo",
                        data=b"contenido_simulado",
                        file_name=f"reporte_avanzado_{tipo_reporte.lower().replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
                
                with col2:
                    st.button("Programar seguimiento")
                
                with col3:
                    st.button("Compartir dashboard")
    
    def mostrar_seccion_configuracion(self):
        """
        Muestra la interfaz de configuración del sistema.
        """
        st.title("Configuración - Motor de Decisión")
        
        # Crear pestañas para diferentes configuraciones
        tab1, tab2, tab3, tab4 = st.tabs([
            "General", "Conexiones", "Usuarios", "Avanzado"
        ])
        
        with tab1:
            st.subheader("Configuración general")
            
            # Configuración básica
            st.selectbox(
                "Idioma de la interfaz",
                ["Español", "English", "Português"],
                index=0
            )
            
            st.selectbox(
                "Zona horaria",
                ["(GMT-03:00) Buenos Aires", "(GMT-05:00) Bogotá", "(GMT-04:00) Santiago", 
                 "(GMT+01:00) Madrid", "(GMT-06:00) Ciudad de México"],
                index=0
            )
            
            # Configuración de datos
            st.subheader("Configuración de datos")
            
            # Rutas de directorios
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("Directorio de datos", value=str(self.dir_datos))
                st.text_input("Directorio de reportes", value=self.config['paths']['output']['reportes'])
            
            with col2:
                st.text_input("Directorio de logs", value=self.config['paths']['logs'])
                st.text_input("Directorio de backups", value="backups/")
            
            # Configuración de análisis
            st.subheader("Configuración de análisis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.selectbox(
                    "Frecuencia predeterminada",
                    ["Diaria", "Semanal", "Mensual", "Trimestral"],
                    index=1
                )
                
                st.number_input(
                    "Períodos mínimos para análisis",
                    min_value=4,
                    max_value=52,
                    value=12
                )
            
            with col2:
                st.slider(
                    "Nivel de confianza",
                    min_value=0.8,
                    max_value=0.99,
                    value=0.95,
                    step=0.01,
                    format="%.2f"
                )
                
                st.select_slider(
                    "Detalle de logs",
                    options=["ERROR", "WARNING", "INFO", "DEBUG"],
                    value="INFO"
                )
        
        with tab2:
            st.subheader("Conexiones")
            
            # Google Sheets
            st.subheader("Google Sheets")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("Ruta de credenciales", value=self.config['google_sheets']['credenciales'])
                st.text_input("ID hoja de leads", value=self.config['google_sheets']['hojas']['leads'])
            
            with col2:
                st.text_input("Ruta de token", value=self.config['google_sheets']['token'])
                st.text_input("ID hoja de matrículas", value=self.config['google_sheets']['hojas']['matriculas'])
            
            st.checkbox(
                "Sincronización automática", 
                value=self.config['google_sheets']['sincronizacion_automatica']
            )
            
            if self.config['google_sheets']['sincronizacion_automatica']:
                st.number_input(
                    "Intervalo de sincronización (segundos)",
                    min_value=300,
                    max_value=86400,
                    value=self.config['google_sheets']['intervalo_sincronizacion'],
                    step=300
                )
            
            st.button("Probar conexión a Google Sheets")
            
            # Power BI
            st.subheader("Power BI")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.selectbox(
                    "Formato de exportación",
                    ["CSV", "Excel", "JSON"],
                    index=["csv", "xlsx", "json"].index(self.config['power_bi']['exportar_formato'].lower())
                )
            
            with col2:
                st.checkbox("Incluir gráficos", value=self.config['power_bi']['incluir_graficos'])
                st.checkbox("Incluir predicciones", value=self.config['power_bi']['incluir_predicciones'])
            
            # Bases de datos
            st.subheader("Base de datos")
            
            st.selectbox(
                "Tipo de base de datos",
                ["SQLite (local)", "MySQL", "PostgreSQL"],
                index=0
            )
            
            if st.checkbox("Configurar conexión a base de datos externa", value=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text_input("Host", value="localhost")
                    st.text_input("Usuario", value="")
                
                with col2:
                    st.text_input("Puerto", value="3306")
                    st.text_input("Contraseña", type="password", value="")
                
                st.text_input("Nombre de base de datos", value="digitalteam")
                st.button("Probar conexión")
        
        with tab3:
            st.subheader("Gestión de usuarios")
            
            # Usuarios actuales (simulados)
            usuarios = [
                {"nombre": "Administrador", "email": "admin@digitalteam.com", "rol": "Administrador", "ultimo_acceso": "Hoy, 10:45"},
                {"nombre": "Marketing", "email": "marketing@digitalteam.com", "rol": "Editor", "ultimo_acceso": "Ayer, 15:30"},
                {"nombre": "Analista", "email": "analista@digitalteam.com", "rol": "Visualizador", "ultimo_acceso": "Hace 3 días"}
            ]
            
            # Mostrar usuarios
            for usuario in usuarios:
                with st.expander(f"{usuario['nombre']} ({usuario['email']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Rol:** {usuario['rol']}")
                        st.write(f"**Último acceso:** {usuario['ultimo_acceso']}")
                    
                    with col2:
                        st.button("Editar", key=f"edit_{usuario['email']}")
                        st.button("Eliminar", key=f"delete_{usuario['email']}")
            
            # Agregar nuevo usuario
            with st.expander("Agregar nuevo usuario", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text_input("Nombre", key="new_user_name")
                    st.text_input("Correo electrónico", key="new_user_email")
                
                with col2:
                    st.selectbox("Rol", ["Administrador", "Editor", "Visualizador"], key="new_user_role")
                    st.text_input("Contraseña", type="password", key="new_user_password")
                
                st.button("Agregar usuario")
            
            # Configuración de autenticación
            st.subheader("Configuración de autenticación")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.selectbox(
                    "Método de autenticación",
                    ["Básico (usuario/contraseña)", "Google OAuth", "LDAP", "Personalizado"],
                    index=0
                )
                
                st.number_input(
                    "Tiempo de sesión (minutos)",
                    min_value=5,
                    max_value=1440,
                    value=60,
                    step=5
                )
            
            with col2:
                st.checkbox("Requerir contraseñas seguras", value=True)
                st.checkbox("Bloquear después de 3 intentos fallidos", value=True)
                st.checkbox("Registro de eventos de autenticación", value=True)
        
        with tab4:
            st.subheader("Configuración avanzada")
            
            # Configuración de modelos
            st.subheader("Configuración de modelos")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.multiselect(
                    "Modelos disponibles",
                    ["Linear", "Ridge", "Lasso", "Random Forest", "Gradient Boosting", "XGBoost", "ARIMA", "Prophet"],
                    default=["Linear", "Random Forest", "Gradient Boosting"]
                )
                
                st.selectbox(
                    "Modelo predeterminado",
                    ["Random Forest", "Linear", "Gradient Boosting"],
                    index=0
                )
            
            with col2:
                st.number_input(
                    "Seed para reproducibilidad",
                    min_value=1,
                    max_value=9999,
                    value=42
                )
                
                st.checkbox("Paralelización de entrenamientos", value=True)
                st.checkbox("Guardar modelos entrenados", value=True)
            
            # Configuración de simulaciones
            st.subheader("Configuración de simulaciones")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.number_input(
                    "Simulaciones Monte Carlo",
                    min_value=100,
                    max_value=10000,
                    value=1000,
                    step=100
                )
            
            with col2:
                st.slider(
                    "Precisión de predicciones",
                    min_value=1,
                    max_value=10,
                    value=5
                )
            
            # Configuración de visualización
            st.subheader("Configuración de visualización")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.selectbox(
                    "Estilo de gráficos",
                    ["Seaborn", "Matplotlib", "Plotly", "Personalizado"],
                    index=0
                )
                
                st.multiselect(
                    "Colores de marca",
                    ["#FF6F00", "#2196F3", "#4CAF50", "#9C27B0", "#F44336"],
                    default=["#FF6F00", "#2196F3"]
                )
            
            with col2:
                st.number_input(
                    "DPI de imágenes",
                    min_value=72,
                    max_value=600,
                    value=300,
                    step=10
                )
                
                st.text_input(
                    "Formato de fecha predeterminado",
                    value="%d/%m/%Y"
                )
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Guardar configuración", type="primary"):
                st.success("Configuración guardada correctamente")
        
        with col2:
            if st.button("Restaurar valores predeterminados"):
                st.info("Configuración restaurada a valores predeterminados")
        
        with col3:
            if st.button("Exportar configuración"):
                st.download_button(
                    label="Descargar archivo de configuración",
                    data=b"contenido_simulado",
                    file_name="config_export.yaml",
                    mime="application/x-yaml"
                )

def main():
    """Función principal para ejecutar la interfaz de carga de datos."""
    if check_password():
        interfaz = InterfazCargaDatos()
        interfaz.mostrar_interfaz_carga()

if __name__ == "__main__":
    main() 