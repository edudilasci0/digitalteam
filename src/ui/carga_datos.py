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
            'matriculas': self.procesador.columnas_requeridas['matriculas'],
            'planificacion_campanas': [
                'fecha_inicio_campana', 'fecha_fin_campana', 'canal', 
                'presupuesto_estimado', 'presupuesto_ejecutado', 'objetivo_leads'
            ]
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
            str: Tipo de datos detectado ('leads', 'matriculas', 'planificacion_campanas' o 'desconocido')
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
        
        elif tipo_datos == 'planificacion_campanas':
            # Verificar fechas
            for campo_fecha in ['fecha_inicio_campana', 'fecha_fin_campana']:
                if campo_fecha in df.columns:
                    try:
                        pd.to_datetime(df[campo_fecha], errors='raise')
                    except:
                        problemas.append({
                            'tipo': 'tipo_datos_incorrecto',
                            'descripcion': f"La columna '{campo_fecha}' contiene valores que no son fechas válidas",
                            'gravedad': 'alta'
                        })
            
            # Verificar numéricos
            for campo_num in ['presupuesto_estimado', 'presupuesto_ejecutado', 'objetivo_leads']:
                if campo_num in df.columns:
                    if not pd.api.types.is_numeric_dtype(df[campo_num]) and not all(pd.to_numeric(df[campo_num], errors='coerce').notna()):
                        problemas.append({
                            'tipo': 'tipo_datos_incorrecto',
                            'descripcion': f"La columna '{campo_num}' contiene valores que no son numéricos",
                            'gravedad': 'alta'
                        })
            
            # Verificar coherencia de fechas
            if 'fecha_inicio_campana' in df.columns and 'fecha_fin_campana' in df.columns:
                try:
                    fechas_inicio = pd.to_datetime(df['fecha_inicio_campana'])
                    fechas_fin = pd.to_datetime(df['fecha_fin_campana'])
                    fechas_invalidas = fechas_inicio > fechas_fin
                    
                    if fechas_invalidas.any():
                        filas_invalidas = fechas_invalidas.sum()
                        problemas.append({
                            'tipo': 'coherencia_fechas',
                            'descripcion': f"Se detectaron {filas_invalidas} campañas donde la fecha de inicio es posterior a la fecha de fin",
                            'gravedad': 'alta'
                        })
                except:
                    # Error ya reportado en la validación de fechas
                    pass
        
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
            ["Leads", "Matrículas", "Planificación de campañas", "Auto-detectar"],
            horizontal=True
        )
        tipo_datos = tipo_datos.lower().replace('ó', 'o').replace(' ', '_') if tipo_datos != "Auto-detectar" else None
        
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
            ["Reporte General Estratégico (Marketing)", "Reporte de Status Comercial", 
             "Análisis multivariable", "Segmentación avanzada", "Predicción por cohortes", 
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
        if tipo_reporte == "Reporte General Estratégico (Marketing)":
            st.subheader("Configuración de Reporte General Estratégico")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.multiselect(
                    "Métricas a incluir",
                    ["Leads", "Matrículas", "CPA", "Elasticidad", "Proyección de cierre",
                     "Conversión por canal", "ROI por campaña", "Efectividad de mensajes"],
                    default=["Leads", "Matrículas", "CPA", "Elasticidad", "Proyección de cierre"]
                )
                
                st.selectbox(
                    "Nivel de detalle por canal",
                    ["Agregado", "Por canal", "Por campaña", "Por anuncio"]
                )
                
                st.number_input("Intervalo de confianza (%)", min_value=80, max_value=99, value=95, step=1)
            
            with col2:
                st.multiselect(
                    "Simulaciones de escenarios",
                    ["Conversión optimista", "Conversión pesimista", "Aumento de inversión", 
                     "Reducción de inversión", "Cambio mix de canales", "Estacionalidad"],
                    default=["Conversión optimista", "Conversión pesimista", "Aumento de inversión"]
                )
                
                st.selectbox(
                    "Formato de exportación",
                    ["Excel compatible Power BI", "CSV compatible Power BI", "Excel estándar", "PDF"]
                )
        
                st.checkbox("Incluir recomendaciones automatizadas", value=True)
            
            # Sección de proyecciones
            st.subheader("Configuración de proyecciones")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.selectbox(
                    "Método de proyección",
                    ["Regresión lineal", "Media móvil", "Tendencia histórica", "Machine Learning"]
                )
                
                st.number_input("Horizonte de proyección (días)", min_value=7, max_value=180, value=30)
            
            with col2:
                st.checkbox("Ajustar por estacionalidad", value=True)
                st.checkbox("Incluir indicadores de calidad de predicción", value=True)
        
        elif tipo_reporte == "Reporte de Status Comercial":
            st.subheader("Configuración de Reporte de Status Comercial")
            
            # Selector de convocatoria
            convocatoria = st.selectbox(
                "Seleccionar convocatoria",
                ["Marzo 2023", "Agosto 2023", "Octubre 2023", "Marzo 2024"]
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.checkbox("Incluir notas y observaciones", value=True)
                st.checkbox("Mostrar histórico de convocatorias anteriores", value=False)
            
            with col2:
                st.selectbox("Frecuencia de actualización", ["Diaria", "Semanal", "Quincenal"])
                st.selectbox("Formato de exportación", ["PDF", "Excel", "Power BI"])
            
            # Previsualización de las barras de progreso
            st.subheader("Vista previa de barras de progreso")
            
            # Simulación de datos de progreso
            tiempo_total = 90  # días
            tiempo_transcurrido = 45
            meta_leads = 1000
            leads_actuales = 660
            meta_matriculas = 150
            matriculas_actuales = 70
            
            # Mostrar barras de progreso
            st.markdown(self._crear_barra_progreso(tiempo_transcurrido, tiempo_total, "Tiempo transcurrido"))
            st.markdown(self._crear_barra_progreso(leads_actuales, meta_leads, "Leads generados"))
            st.markdown(self._crear_barra_progreso(matriculas_actuales, meta_matriculas, "Matrículas"))
            
            # Predicción
            st.subheader("Predicción de resultados finales")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Proyección de matrículas", "145", "96% de la meta")
                st.metric("Intervalo de confianza", "±15", "90% de confianza")
            
            with col2:
                st.metric("Leads faltantes", "340", "34% restante")
                st.metric("Días restantes", "45", "50% del tiempo")
            
            # Acciones recomendadas
            st.subheader("Acciones recomendadas")
            st.info("Incrementar presupuesto en Google Ads para compensar el déficit actual de matrículas")
            st.info("Revisar el mensaje creativo de las campañas de Facebook que están teniendo menor conversión de lo esperado")
        
        elif tipo_reporte == "Análisis multivariable":
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
                
                # Vista previa personalizada según el tipo de reporte
                if tipo_reporte == "Reporte General Estratégico (Marketing)":
                    self._mostrar_vista_previa_reporte_estrategico()
                elif tipo_reporte == "Reporte de Status Comercial":
                    self._mostrar_vista_previa_reporte_status()
                else:
                    # Vista previa genérica para otros tipos
                    self._mostrar_vista_previa_generica()
                    
                # Acciones comunes para todos los reportes
                st.subheader("Acciones")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        label=f"Descargar reporte",
                        data=b"contenido_simulado",
                        file_name=f"reporte_{tipo_reporte.lower().replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )
                
                with col2:
                    st.button("Programar envío periódico")
                
                with col3:
                    st.button("Compartir reporte")
    
    def _crear_barra_progreso(self, valor, max_valor, etiqueta, ancho=100):
        """
        Crea una barra de progreso HTML personalizada.
        
        Args:
            valor: Valor actual
            max_valor: Valor máximo (meta)
            etiqueta: Etiqueta de la barra
            ancho: Ancho en porcentaje
            
        Returns:
            str: HTML de la barra de progreso
        """
        porcentaje = min(100, int((valor / max_valor) * 100))
        barra_llena = "▓" * int(porcentaje / 10)
        barra_vacia = "░" * (10 - int(porcentaje / 10))
        
        barra_html = f"""
        <div style="margin-bottom:15px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                <span style="font-weight:bold;">{etiqueta}</span>
                <span>{porcentaje}%</span>
            </div>
            <div style="font-family:monospace; font-size:24px; line-height:1; color:#FF6F00;">
                {barra_llena}{barra_vacia} {porcentaje}%
            </div>
        </div>
        """
        return barra_html
    
    def _mostrar_vista_previa_reporte_estrategico(self):
        """Muestra una vista previa del reporte estratégico de marketing."""
        st.subheader("Vista previa del Reporte Estratégico")
        
        # Datos de ejemplo para visualización
        fechas = pd.date_range(start='2023-01-01', periods=90)
        np.random.seed(42)
        valores_leads = np.cumsum(np.random.randn(90) * 5 + 20)  # Tendencia creciente con ruido
        valores_matriculas = np.cumsum(np.random.randn(90) * 2 + 6)  # Tendencia creciente con ruido
        
        # Crear proyección
        fechas_futuras = pd.date_range(start=fechas[-1] + pd.Timedelta(days=1), periods=30)
        proyeccion_leads = np.linspace(valores_leads[-1], valores_leads[-1] * 1.3, 30)
        proyeccion_matriculas = np.linspace(valores_matriculas[-1], valores_matriculas[-1] * 1.2, 30)
        
        # Intervalos de confianza (95%)
        ic_superior_leads = proyeccion_leads + np.linspace(10, 25, 30)
        ic_inferior_leads = proyeccion_leads - np.linspace(10, 25, 30)
        ic_superior_matriculas = proyeccion_matriculas + np.linspace(3, 8, 30)
        ic_inferior_matriculas = proyeccion_matriculas - np.linspace(3, 8, 30)
            
        # Preparar datos para gráfico
        df_historico = pd.DataFrame({
            'Fecha': fechas,
            'Leads': valores_leads,
            'Matrículas': valores_matriculas
        })
        
        df_proyeccion = pd.DataFrame({
            'Fecha': fechas_futuras,
            'Leads (proyección)': proyeccion_leads,
            'Leads (IC superior)': ic_superior_leads,
            'Leads (IC inferior)': ic_inferior_leads,
            'Matrículas (proyección)': proyeccion_matriculas,
            'Matrículas (IC superior)': ic_superior_matriculas,
            'Matrículas (IC inferior)': ic_inferior_matriculas
        })
        
        # Mostrar gráficos
        st.subheader("Tendencia y proyección de Leads")
        fig_leads = self._crear_grafico_proyeccion(df_historico, df_proyeccion, 'Leads')
        st.pyplot(fig_leads)
                
        st.subheader("Tendencia y proyección de Matrículas")
        fig_matriculas = self._crear_grafico_proyeccion(df_historico, df_proyeccion, 'Matrículas')
        st.pyplot(fig_matriculas)
        
        # Métricas clave
        st.subheader("Métricas clave")
        col1, col2, col3 = st.columns(3)
            
            with col1:
            st.metric("CPA Actual", "$45.32", "-12% vs mes anterior")
            st.metric("Elasticidad", "1.32", "+0.08 vs mes anterior")
            
            with col2:
            st.metric("Proyección matrículas", "210", "+15% vs meta")
            st.metric("Margen de error", "±22", "95% confianza")
        
        with col3:
            st.metric("ROI estimado", "324%", "+28% vs mes anterior")
            st.metric("Conversión Lead-Matrícula", "8.2%", "+1.5% vs mes anterior")
        
        # Escenarios
        st.subheader("Simulación de escenarios")
        escenarios = pd.DataFrame({
            'Escenario': ['Actual', 'Optimista', 'Pesimista', 'Aumento 20% inversión'],
            'Leads estimados': [2500, 2800, 2300, 3000],
            'Matrículas estimadas': [210, 250, 180, 240],
            'CPA esperado': ['$45.32', '$40.50', '$50.20', '$48.10'],
            'ROI proyectado': ['324%', '380%', '270%', '315%']
        })
        
        st.table(escenarios)
        
        # Recomendaciones
        st.subheader("Recomendaciones")
        st.info("Aumentar inversión en Google Ads (Canal con mayor elasticidad actual)")
        st.info("Optimizar mensajes de Facebook Ads para mejorar tasa de conversión")
        st.info("Revisar segmentación en campañas de Instagram para reducir CPA")
        
    def _mostrar_vista_previa_reporte_status(self):
        """Muestra una vista previa del reporte de status comercial."""
        st.subheader("Vista previa del Reporte de Status Comercial")
        
        # Encabezado del reporte
        st.markdown("""
        <div style="background-color:#f0f0f0; padding:15px; border-radius:5px; margin-bottom:20px;">
            <h3 style="margin:0; color:#FF6F00; text-align:center;">Estado de Convocatoria - Marzo 2024</h3>
            <p style="text-align:center; margin:5px 0 0 0;">Periodo: 01/03/2024 al 15/03/2024</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Datos de ejemplo para el reporte
        tiempo_total = 90  # días
        tiempo_transcurrido = 45
        meta_leads = 1000
        leads_actuales = 660
        meta_matriculas = 150
        matriculas_actuales = 70
        
        # Barras de progreso
        st.markdown("<h4>Progreso actual</h4>", unsafe_allow_html=True)
        st.markdown(self._crear_barra_progreso(tiempo_transcurrido, tiempo_total, "Tiempo transcurrido"))
        st.markdown(self._crear_barra_progreso(leads_actuales, meta_leads, "Leads generados"))
        st.markdown(self._crear_barra_progreso(matriculas_actuales, meta_matriculas, "Matrículas"))
        
        # Estado quincenal
        st.markdown("<h4>Estado quincenal</h4>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
            st.metric("Leads última quincena", "250", "+15% vs quincena anterior")
            st.metric("Matrículas última quincena", "32", "+8% vs quincena anterior")
            
            with col2:
            st.metric("Conversión última quincena", "12.8%", "+0.5% vs quincena anterior")
            st.metric("CPA última quincena", "$42.50", "-$3.75 vs quincena anterior")
            
        # Observaciones
        st.markdown("<h4>Observaciones clave</h4>", unsafe_allow_html=True)
        st.info("La campaña de remarketing está teniendo mejores resultados que lo esperado")
        st.warning("Se detectó una disminución en la eficiencia de las campañas de Facebook durante fines de semana")
        
        # Predicción final
        st.markdown("<h4>Predicción de matrícula final</h4>", unsafe_allow_html=True)
        
        # Datos de ejemplo para gráfico de predicción
        dias = list(range(1, tiempo_total + 1))
        matriculas_reales = [0] + [int(1.2 * i + np.random.randint(-3, 3)) for i in range(1, tiempo_transcurrido)]
        
        # Predicción para el resto del período
        prediccion = [None] * (tiempo_transcurrido - 1)
        for i in range(tiempo_transcurrido, tiempo_total + 1):
            prediccion.append(matriculas_actuales + int((i - tiempo_transcurrido) * (150 - matriculas_actuales) / (tiempo_total - tiempo_transcurrido) + np.random.randint(-5, 5)))
        
        # Límites del intervalo de confianza
        ic_superior = [None] * (tiempo_transcurrido - 1)
        ic_inferior = [None] * (tiempo_transcurrido - 1)
        for i in range(tiempo_transcurrido, tiempo_total + 1):
            distancia = int((i - tiempo_transcurrido) * 0.5)
            ic_superior.append(prediccion[i-1] + distancia)
            ic_inferior.append(max(prediccion[i-1] - distancia, matriculas_actuales))
        
        # Crear DataFrame para el gráfico
        df_prediccion = pd.DataFrame({
            'Día': dias,
            'Matrículas reales': matriculas_reales + [None] * (tiempo_total - tiempo_transcurrido + 1),
            'Predicción': prediccion,
            'IC Superior': ic_superior,
            'IC Inferior': ic_inferior
        })
        
        # Mostrar gráfico de predicción
        fig = self._crear_grafico_prediccion(df_prediccion)
        st.pyplot(fig)
        
        # Resumen de predicción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Predicción final", "142 matrículas", "95% de la meta")
        
        with col2:
            st.metric("Intervalo de confianza", "±15", "90% de confianza")
        
        with col3:
            st.metric("Días restantes", "45", "50% del tiempo")
        
        # Acciones recomendadas
        st.markdown("<h4>Acciones recomendadas</h4>", unsafe_allow_html=True)
        st.warning("Incrementar presupuesto en Google Ads para compensar el déficit actual")
        st.warning("Revisar el mensaje creativo de las campañas de Facebook")
        st.info("Mantener la estrategia actual de remarketing que está funcionando bien")
    
    def _mostrar_vista_previa_generica(self):
        """Muestra una vista previa genérica para otros tipos de reportes."""
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
    
    def _crear_grafico_proyeccion(self, df_historico, df_proyeccion, metrica):
        """
        Crea un gráfico de proyección con intervalos de confianza.
        """
        import matplotlib.pyplot as plt
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Graficar datos históricos
        ax.plot(df_historico['Fecha'], df_historico[metrica], 
                color='#FF6F00', linewidth=2, label=f'{metrica} históricos')
        
        # Graficar proyección
        ax.plot(df_proyeccion['Fecha'], df_proyeccion[f'{metrica} (proyección)'],
                color='#2196F3', linewidth=2, linestyle='--', label=f'{metrica} proyectados')
        
        # Graficar intervalo de confianza
        ax.fill_between(df_proyeccion['Fecha'],
                        df_proyeccion[f'{metrica} (IC inferior)'],
                        df_proyeccion[f'{metrica} (IC superior)'],
                        color='#2196F3', alpha=0.2, label='Intervalo 95% conf.')
        
        # Configurar gráfico
        ax.set_title(f'Tendencia y proyección de {metrica}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Fecha', fontsize=12)
        ax.set_ylabel(f'Cantidad de {metrica}', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        # Añadir línea vertical en el presente
        ax.axvline(x=df_historico['Fecha'].iloc[-1], color='black', linestyle='-', alpha=0.5)
        ax.text(df_historico['Fecha'].iloc[-1], ax.get_ylim()[1]*0.9, 'Hoy', 
                rotation=90, verticalalignment='top')
        
        # Ajustar layout
        plt.tight_layout()
        
        return fig
    
    def _crear_grafico_prediccion(self, df):
        """
        Crea un gráfico de predicción con intervalos de confianza para el reporte de status.
        """
        import matplotlib.pyplot as plt
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Graficar datos reales
        ax.plot(df['Día'], df['Matrículas reales'], 
                color='#FF6F00', linewidth=2, marker='o', label='Matrículas reales')
        
        # Graficar predicción
        ax.plot(df['Día'], df['Predicción'],
                color='#2196F3', linewidth=2, linestyle='--', label='Predicción')
        
        # Graficar intervalo de confianza
        ax.fill_between(df['Día'],
                        df['IC Inferior'],
                        df['IC Superior'],
                        color='#2196F3', alpha=0.2, label='Intervalo 90% conf.')
        
        # Configurar gráfico
        ax.set_title('Predicción de matrículas', fontsize=14, fontweight='bold')
        ax.set_xlabel('Día de campaña', fontsize=12)
        ax.set_ylabel('Cantidad de matrículas', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        # Añadir línea vertical en el día actual
        dia_actual = df[df['Matrículas reales'].notna()].iloc[-1]['Día']
        ax.axvline(x=dia_actual, color='black', linestyle='-', alpha=0.5)
        ax.text(dia_actual, ax.get_ylim()[1]*0.9, 'Hoy', 
                rotation=90, verticalalignment='top')
        
        # Ajustar layout
        plt.tight_layout()
        
        return fig

def main():
    """Función principal para ejecutar la interfaz de carga de datos."""
    if check_password():
    interfaz = InterfazCargaDatos()
    interfaz.mostrar_interfaz_carga()

if __name__ == "__main__":
    main() 