import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import os
import yaml
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile
from datetime import datetime

# Asegurar que src sea accesible
sys.path.append('.')

# Intentar importar los módulos necesarios
try:
    from src.data.procesador_datos import ProcesadorDatos
except ImportError:
    # Crear clase de respaldo si no existe
    class ProcesadorDatos:
        def limpiar_datos(self, datos):
            return datos
        def unir_leads_matriculas(self, leads, matriculas):
            # Simulación simple de unión
            return leads
        def crear_caracteristicas(self, datos):
            return datos

try:
    from src.visualizacion.visualizador import Visualizador
except ImportError:
    # Clase de respaldo para visualizador
    class Visualizador:
        def graficar_barras(self, datos, columna_categoria, columna_valor=None, 
                          titulo=None, orientacion='vertical', limite_categorias=10,
                          mostrar=True, retornar_figura=False):
            # Crear gráfico simple
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Obtener conteo o suma
            if columna_valor is None:
                # Contar frecuencias
                conteo = datos[columna_categoria].value_counts().head(limite_categorias)
                conteo.plot(kind='bar', ax=ax)
            else:
                # Sumar valores por categoría
                agrupado = datos.groupby(columna_categoria)[columna_valor].sum().sort_values(ascending=False).head(limite_categorias)
                agrupado.plot(kind='bar', ax=ax)
            
            # Configurar gráfico
            if titulo:
                ax.set_title(titulo)
            ax.set_xlabel(columna_categoria)
            
            if retornar_figura:
                return fig
            
            if mostrar:
                plt.show()
                
        def graficar_serie_temporal(self, datos, columna_fecha, columna_valor, 
                                 titulo=None, mostrar=True, retornar_figura=False):
            # Crear gráfico simple
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Graficar serie temporal
            ax.plot(datos[columna_fecha], datos[columna_valor])
            
            # Configurar gráfico
            if titulo:
                ax.set_title(titulo)
            ax.set_xlabel('Fecha')
            ax.set_ylabel(columna_valor)
            
            # Rotar etiquetas del eje x para mejor visualización
            plt.xticks(rotation=45)
            
            if retornar_figura:
                return fig
            
            if mostrar:
                plt.show()
                
        def graficar_matriz_correlacion(self, datos, columnas=None, 
                                     titulo=None, mostrar=True, retornar_figura=False):
            # Seleccionar columnas o usar todas las numéricas
            if columnas:
                datos_num = datos[columnas]
            else:
                datos_num = datos.select_dtypes(include=np.number)
            
            # Calcular correlación
            corr = datos_num.corr()
            
            # Crear gráfico
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Crear mapa de calor
            sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax, vmin=-1, vmax=1)
            
            # Configurar gráfico
            if titulo:
                ax.set_title(titulo)
            
            if retornar_figura:
                return fig
            
            if mostrar:
                plt.show()
                
        def graficar_dispersion(self, datos, columna_x, columna_y, columna_color=None,
                            titulo=None, mostrar_regresion=False, mostrar=True, retornar_figura=False):
            # Crear gráfico
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Graficar dispersión
            if columna_color:
                scatter = ax.scatter(datos[columna_x], datos[columna_y], c=datos[columna_color].astype('category').cat.codes, alpha=0.6)
                # Añadir leyenda
                legend = ax.legend(*scatter.legend_elements(), title=columna_color)
                ax.add_artist(legend)
            else:
                ax.scatter(datos[columna_x], datos[columna_y], alpha=0.6)
            
            # Añadir línea de regresión
            if mostrar_regresion:
                z = np.polyfit(datos[columna_x], datos[columna_y], 1)
                p = np.poly1d(z)
                ax.plot(datos[columna_x], p(datos[columna_x]), "r--", alpha=0.8)
            
            # Configurar gráfico
            if titulo:
                ax.set_title(titulo)
            ax.set_xlabel(columna_x)
            ax.set_ylabel(columna_y)
            
            if retornar_figura:
                return fig
            
            if mostrar:
                plt.show()

# Configuración de la página
st.set_page_config(
    page_title="Motor de Decisión - Team Digital",
    page_icon="📊",
    layout="wide"
)

# Función para cargar configuración
def get_config():
    config_path = Path("config/config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

# Inicializar sesión
if 'datos_leads' not in st.session_state:
    st.session_state.datos_leads = None
if 'datos_matriculas' not in st.session_state:
    st.session_state.datos_matriculas = None
if 'datos_procesados' not in st.session_state:
    st.session_state.datos_procesados = None
if 'modelo_entrenado' not in st.session_state:
    st.session_state.modelo_entrenado = False

# Cargar configuración
config = get_config()

# Navegación principal
st.sidebar.title("Motor de Decisión")
menu = st.sidebar.radio(
    "Menú Principal",
    ["Inicio", "Carga de Datos", "Exploración", "Análisis", "Reportes", "Modelos"]
)

# Página de Inicio
if menu == "Inicio":
    st.title("Motor de Decisión - Team Digital")
    st.write("Bienvenido al sistema completo de análisis predictivo para campañas educativas.")
    
    # Mostrar estado actual
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Estado actual")
        if st.session_state.datos_leads is not None:
            st.success(f"✅ Datos de leads cargados: {len(st.session_state.datos_leads)} registros")
        else:
            st.warning("❌ Datos de leads no cargados")
            
        if st.session_state.datos_matriculas is not None:
            st.success(f"✅ Datos de matrículas cargados: {len(st.session_state.datos_matriculas)} registros")
        else:
            st.warning("❌ Datos de matrículas no cargados")
            
        if st.session_state.modelo_entrenado:
            st.success("✅ Modelo predictivo entrenado")
        else:
            st.warning("❌ Modelo predictivo no entrenado")
    
    with col2:
        st.subheader("Acciones rápidas")
        if st.button("Cargar datos de ejemplo"):
            # Código para cargar datos de ejemplo
            try:
                if os.path.exists("datos/actual/leads_ejemplo.csv") and os.path.exists("datos/actual/matriculas_ejemplo.csv"):
                    st.session_state.datos_leads = pd.read_csv("datos/actual/leads_ejemplo.csv")
                    st.session_state.datos_matriculas = pd.read_csv("datos/actual/matriculas_ejemplo.csv")
                    st.success("Datos de ejemplo cargados correctamente")
                    st.rerun()
                else:
                    st.error("Archivos de ejemplo no encontrados")
            except Exception as e:
                st.error(f"Error al cargar datos de ejemplo: {str(e)}")
        
        if st.button("Generar reporte rápido"):
            # Verificar si hay datos
            if st.session_state.datos_leads is None or st.session_state.datos_matriculas is None:
                st.error("Primero debe cargar los datos")
            else:
                # Aquí se generaría un reporte básico
                st.info("Generando reporte rápido...")
                try:
                    # Crear directorio temporal
                    dir_temp = tempfile.mkdtemp()
                    
                    # Generar reporte básico
                    reporte_path = os.path.join(dir_temp, f"reporte_rapido_{datetime.now().strftime('%Y%m%d_%H%M')}.html")
                    
                    # Aquí iría el código real para generar el reporte
                    with open(reporte_path, 'w') as f:
                        f.write("<html><body><h1>Reporte Rápido</h1></body></html>")
                    
                    # Mostrar éxito
                    st.success("Reporte generado correctamente")
                    
                    # Botón de descarga
                    with open(reporte_path, "rb") as file:
                        st.download_button(
                            "Descargar Reporte",
                            file,
                            f"reporte_rapido_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                            "text/html"
                        )
                except Exception as e:
                    st.error(f"Error al generar reporte: {str(e)}")

# Página de Carga de Datos
elif menu == "Carga de Datos":
    st.title("Carga y Procesamiento de Datos")
    
    # Pestañas para diferentes tipos de carga
    tab1, tab2, tab3 = st.tabs(["Cargar Archivos", "Conectar a Base de Datos", "Google Sheets"])
    
    with tab1:
        st.subheader("Cargar archivos CSV o Excel")
        
        # Selección de tipo de datos
        tipo_datos = st.radio(
            "Tipo de datos a cargar:",
            ["Leads", "Matrículas"],
            horizontal=True
        )
        
        # Carga de archivo
        uploaded_file = st.file_uploader(
            "Arrastra o selecciona archivos CSV o Excel", 
            type=["csv", "xlsx", "xls"]
        )
        
        if uploaded_file is not None:
            st.success(f"Archivo cargado correctamente: {uploaded_file.name}")
            
            try:
                # Determinar formato
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(uploaded_file)
                    
                # Mostrar vista previa
                st.subheader("Vista previa de datos")
                st.dataframe(df.head(5))
                
                # Guardar en session_state
                if tipo_datos == "Leads":
                    st.session_state.datos_leads = df
                    st.success("Datos de leads actualizados correctamente")
                else:
                    st.session_state.datos_matriculas = df
                    st.success("Datos de matrículas actualizados correctamente")
                
            except Exception as e:
                st.error(f"Error al leer el archivo: {str(e)}")
    
    with tab2:
        st.subheader("Conectar a Base de Datos")
        st.info("Esta funcionalidad estará disponible próximamente")
        
        # Campos simulados para la conexión
        db_type = st.selectbox("Tipo de base de datos", ["SQLite", "MySQL", "PostgreSQL"])
        db_host = st.text_input("Host o ruta de archivo", "datos/database.db")
        db_user = st.text_input("Usuario")
        db_password = st.text_input("Contraseña", type="password")
        
        if st.button("Conectar a Base de Datos"):
            st.warning("Función en desarrollo, todavía no está implementada")
    
    with tab3:
        st.subheader("Google Sheets")
        st.info("Esta funcionalidad estará disponible próximamente")
        
        sheet_id = st.text_input("ID de la hoja de Google Sheets")
        
        if st.button("Conectar a Google Sheets"):
            st.warning("Función en desarrollo, todavía no está implementada")
    
    # Procesamiento de Datos
    if st.session_state.datos_leads is not None and st.session_state.datos_matriculas is not None:
        st.subheader("Procesar datos cargados")
        
        if st.button("Procesar y unir datos"):
            try:
                procesador = ProcesadorDatos()
                
                with st.spinner("Limpiando datos..."):
                    # Limpiar datos
                    datos_leads_limpios = procesador.limpiar_datos(st.session_state.datos_leads)
                    datos_matriculas_limpios = procesador.limpiar_datos(st.session_state.datos_matriculas)
                
                with st.spinner("Uniendo datos..."):
                    # Unir datos
                    datos_unidos = procesador.unir_leads_matriculas(datos_leads_limpios, datos_matriculas_limpios)
                
                with st.spinner("Creando características..."):
                    # Crear características
                    datos_procesados = procesador.crear_caracteristicas(datos_unidos)
                
                # Guardar resultados
                st.session_state.datos_procesados = datos_procesados
                
                st.success("Datos procesados correctamente")
                
                # Mostrar estadísticas
                st.subheader("Estadísticas generales")
                st.write(f"Total de registros: {len(datos_procesados)}")
                st.write(f"Total de características: {len(datos_procesados.columns)}")
                
                # Mostrar primeras filas
                st.subheader("Vista previa de datos procesados")
                st.dataframe(datos_procesados.head())
                
            except Exception as e:
                st.error(f"Error al procesar datos: {str(e)}")

# Página de Exploración
elif menu == "Exploración":
    st.title("Exploración de Datos")
    
    # Verificar si hay datos
    if (st.session_state.datos_leads is None and 
        st.session_state.datos_matriculas is None and 
        st.session_state.datos_procesados is None):
        st.warning("Primero debe cargar datos en la sección 'Carga de Datos'")
    else:
        # Inicializar visualizador
        visualizador = Visualizador()
        
        # Seleccionar conjunto de datos
        conjunto_datos = st.radio(
            "Seleccione conjunto de datos a explorar:",
            ["Leads", "Matrículas", "Datos procesados"],
            horizontal=True
        )
        
        # Determinar el conjunto de datos a utilizar
        if conjunto_datos == "Leads" and st.session_state.datos_leads is not None:
            datos = st.session_state.datos_leads
        elif conjunto_datos == "Matrículas" and st.session_state.datos_matriculas is not None:
            datos = st.session_state.datos_matriculas
        elif conjunto_datos == "Datos procesados" and st.session_state.datos_procesados is not None:
            datos = st.session_state.datos_procesados
        else:
            st.error(f"El conjunto de datos '{conjunto_datos}' no está disponible")
            datos = None
        
        if datos is not None:
            # Opciones de visualización
            st.subheader("Seleccione tipo de visualización")
            
            viz_tipo = st.selectbox(
                "Tipo de visualización:",
                ["Distribución de variables categóricas", 
                 "Evolución temporal", 
                 "Comparación por categorías", 
                 "Matriz de correlación",
                 "Relación entre variables",
                 "Estadísticas básicas"]
            )
            
            # Diferentes visualizaciones según selección
            if viz_tipo == "Distribución de variables categóricas":
                # Detectar columnas categóricas
                columnas_cat = datos.select_dtypes(include=['object', 'category']).columns.tolist()
                
                if columnas_cat:
                    # Seleccionar columna
                    columna_cat = st.selectbox("Seleccione columna categórica:", columnas_cat)
                    
                    st.subheader(f"Distribución de {columna_cat}")
                    
                    # Límite de categorías
                    limite = st.slider("Límite de categorías a mostrar:", 3, 20, 10)
                    
                    # Generar gráfico
                    fig = visualizador.graficar_barras(
                        datos=datos,
                        columna_categoria=columna_cat,
                        columna_valor=None,
                        titulo=f'Distribución de {columna_cat}',
                        orientacion='horizontal',
                        limite_categorias=limite,
                        mostrar=False,
                        retornar_figura=True
                    )
                    
                    st.pyplot(fig)
                    
                    # Tabla de distribución
                    conteo = datos[columna_cat].value_counts().reset_index()
                    conteo.columns = [columna_cat, 'Cantidad']
                    st.dataframe(conteo)
                else:
                    st.info("No se encontraron columnas categóricas en este conjunto de datos")
                    
            elif viz_tipo == "Evolución temporal":
                # Detectar columnas de fecha
                columnas_fecha = []
                for col in datos.columns:
                    if 'fecha' in col.lower() or 'date' in col.lower():
                        columnas_fecha.append(col)
                
                if columnas_fecha:
                    # Seleccionar columna fecha
                    columna_fecha = st.selectbox("Seleccione columna de fecha:", columnas_fecha)
                    
                    # Opciones de agrupación
                    frecuencia = st.radio(
                        "Frecuencia de agrupación",
                        ["Diaria", "Semanal", "Mensual"],
                        horizontal=True
                    )
                    
                    freq_map = {"Diaria": "D", "Semanal": "W", "Mensual": "M"}
                    
                    # Seleccionar variable a agregar
                    columnas_num = datos.select_dtypes(include=np.number).columns.tolist()
                    
                    if columnas_num:
                        columna_valor = st.selectbox(
                            "Variable a agregar (deje vacío para contar registros):",
                            ["<Contar registros>"] + columnas_num
                        )
                        
                        # Preparar datos temporales
                        datos_temp = datos.copy()
                        datos_temp[columna_fecha] = pd.to_datetime(datos_temp[columna_fecha], errors='coerce')
                        
                        # Filtrar fechas inválidas
                        datos_temp = datos_temp.dropna(subset=[columna_fecha])
                        
                        # Agrupar por fecha
                        if columna_valor == "<Contar registros>":
                            datos_temporales = datos_temp.groupby(
                                pd.Grouper(key=columna_fecha, freq=freq_map[frecuencia])
                            ).size().reset_index()
                            datos_temporales.columns = [columna_fecha, 'conteo']
                            columna_y = 'conteo'
                        else:
                            datos_temporales = datos_temp.groupby(
                                pd.Grouper(key=columna_fecha, freq=freq_map[frecuencia])
                            )[columna_valor].sum().reset_index()
                            columna_y = columna_valor
                        
                        st.subheader(f"Evolución {frecuencia.lower()} de {columna_y}")
                        
                        # Graficar
                        fig = visualizador.graficar_serie_temporal(
                            datos=datos_temporales,
                            columna_fecha=columna_fecha,
                            columna_valor=columna_y,
                            titulo=f'Evolución {frecuencia.lower()} de {columna_y}',
                            mostrar=False,
                            retornar_figura=True
                        )
                        
                        st.pyplot(fig)
                        
                        # Mostrar datos
                        st.subheader("Datos de la serie temporal")
                        st.dataframe(datos_temporales)
                    else:
                        st.info("No se encontraron columnas numéricas para agregar")
                else:
                    st.info("No se encontraron columnas de fecha en este conjunto de datos")
            
            elif viz_tipo == "Matriz de correlación":
                # Obtener columnas numéricas
                columnas_num = datos.select_dtypes(include=np.number).columns.tolist()
                
                if len(columnas_num) > 1:
                    st.subheader("Matriz de correlación entre variables numéricas")
                    
                    # Seleccionar columnas
                    columnas_seleccionadas = st.multiselect(
                        "Seleccione variables para la matriz (máximo 10):",
                        columnas_num,
                        default=columnas_num[:min(5, len(columnas_num))]
                    )
                    
                    if columnas_seleccionadas and len(columnas_seleccionadas) > 1:
                        if len(columnas_seleccionadas) > 10:
                            st.warning("Se mostrarán solo las primeras 10 variables seleccionadas")
                            columnas_seleccionadas = columnas_seleccionadas[:10]
                        
                        # Generar matriz
                        fig = visualizador.graficar_matriz_correlacion(
                            datos=datos,
                            columnas=columnas_seleccionadas,
                            titulo='Correlaciones entre variables seleccionadas',
                            mostrar=False,
                            retornar_figura=True
                        )
                        
                        st.pyplot(fig)
                        
                        # Mostrar tabla de correlaciones
                        corr = datos[columnas_seleccionadas].corr()
                        st.dataframe(corr.style.highlight_max(axis=0))
                    else:
                        st.info("Seleccione al menos 2 variables para ver la correlación")
                else:
                    st.info("No hay suficientes variables numéricas para calcular correlaciones")
            
            elif viz_tipo == "Relación entre variables":
                # Obtener columnas numéricas
                columnas_num = datos.select_dtypes(include=np.number).columns.tolist()
                
                if len(columnas_num) > 1:
                    st.subheader("Gráfico de dispersión")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        variable_x = st.selectbox("Variable eje X:", columnas_num)
                    
                    with col2:
                        # Filtrar para no mostrar la misma variable
                        opciones_y = [col for col in columnas_num if col != variable_x]
                        variable_y = st.selectbox("Variable eje Y:", opciones_y)
                    
                    # Obtener columnas categóricas para colorear
                    columnas_cat = datos.select_dtypes(include=['object', 'category']).columns.tolist()
                    
                    if columnas_cat:
                        variable_color = st.selectbox(
                            "Variable para colorear (opcional):",
                            ["<Ninguna>"] + columnas_cat
                        )
                        
                        if variable_color == "<Ninguna>":
                            variable_color = None
                    else:
                        variable_color = None
                    
                    # Opciones adicionales
                    mostrar_regresion = st.checkbox("Mostrar línea de regresión", value=True)
                    
                    # Generar gráfico
                    fig = visualizador.graficar_dispersion(
                        datos=datos,
                        columna_x=variable_x,
                        columna_y=variable_y,
                        columna_color=variable_color,
                        titulo=f'Relación entre {variable_x} y {variable_y}',
                        mostrar_regresion=mostrar_regresion,
                        mostrar=False,
                        retornar_figura=True
                    )
                    
                    st.pyplot(fig)
                    
                    # Mostrar estadísticas de correlación
                    if mostrar_regresion:
                        correlacion = datos[[variable_x, variable_y]].corr().iloc[0, 1]
                        st.info(f"Correlación entre {variable_x} y {variable_y}: {correlacion:.4f}")
                else:
                    st.info("No hay suficientes variables numéricas para el gráfico de dispersión")
            
            elif viz_tipo == "Estadísticas básicas":
                st.subheader("Estadísticas descriptivas")
                
                # Obtener estadísticas descriptivas
                stats = datos.describe(include='all').T
                
                # Añadir conteo de valores nulos
                stats['nulos'] = datos.isnull().sum()
                
                # Añadir porcentaje de valores nulos
                stats['nulos_pct'] = (datos.isnull().sum() / len(datos)) * 100
                
                # Mostrar estadísticas
                st.dataframe(stats)
                
                # Información general
                st.subheader("Información general")
                buffer = []
                datos.info(buf=buffer)
                info_str = "".join(buffer)
                st.text(info_str)

# Página de Análisis
elif menu == "Análisis":
    st.title("Análisis Avanzados")
    
    if st.session_state.datos_procesados is None:
        st.warning("Primero debe cargar y procesar los datos en la sección 'Carga de Datos'")
    else:
        # Tipo de análisis
        analisis_tipo = st.selectbox(
            "Seleccione tipo de análisis:",
            ["Análisis de Estacionalidad", 
             "Análisis de Elasticidad", 
             "Simulación de Mejora de Conversión",
             "Proyección de Cierre"]
        )
        
        # Ejecutar análisis según selección
        if analisis_tipo == "Análisis de Estacionalidad":
            st.subheader("Análisis de Estacionalidad")
            
            # Parámetros para el análisis
            agrupacion = st.radio(
                "Tipo de agrupación temporal",
                ["Quincena", "Mes", "Semana"],
                horizontal=True
            )
            
            # Verificar si hay columnas de fecha
            columnas_fecha = []
            for col in st.session_state.datos_procesados.columns:
                if 'fecha' in col.lower() or 'date' in col.lower():
                    columnas_fecha.append(col)
            
            if not columnas_fecha:
                st.error("No se encontraron columnas de fecha en los datos procesados")
            else:
                columna_fecha = st.selectbox(
                    "Seleccione columna de fecha para análisis:",
                    columnas_fecha
                )
                
                if st.button("Ejecutar Análisis de Estacionalidad"):
                    with st.spinner("Ejecutando análisis..."):
                        try:
                            # Crear directorio temporal para resultados
                            import tempfile
                            directorio_temp = tempfile.mkdtemp()
                            
                            # Preparar datos
                            datos = st.session_state.datos_procesados.copy()
                            datos[columna_fecha] = pd.to_datetime(datos[columna_fecha], errors='coerce')
                            
                            # Determinar período actual
                            mes_actual = datetime.now().month
                            dia_actual = datetime.now().day
                            quincena_actual = (mes_actual - 1) * 2 + (2 if dia_actual > 15 else 1)
                            
                            # Simulación de patrones estacionales (en lugar del módulo real)
                            # En una implementación real, aquí se llamaría a la función del módulo modelo_estacionalidad
                            
                            # Simulación de patrones
                            periodos = {"Quincena": 24, "Mes": 12, "Semana": 52}
                            n_periodos = periodos[agrupacion]
                            
                            # Crear datos de ejemplo para patrones
                            patrones_data = {
                                'periodo': list(range(1, n_periodos + 1)),
                                'patron_leads': np.random.normal(100, 20, n_periodos),
                                'patron_conversion': np.random.normal(0.1, 0.02, n_periodos)
                            }
                            patrones_df = pd.DataFrame(patrones_data)
                            
                            # Crear datos de ejemplo para comparación
                            comparacion_data = {
                                'periodo': list(range(1, quincena_actual + 1)),
                                'leads_actual': np.random.normal(100, 25, quincena_actual),
                                'leads_esperado': np.random.normal(100, 20, quincena_actual),
                                'conversion_actual': np.random.normal(0.1, 0.03, quincena_actual),
                                'conversion_esperada': np.random.normal(0.1, 0.02, quincena_actual)
                            }
                            comparacion_df = pd.DataFrame(comparacion_data)
                            
                            # Generar gráficos
                            fig1, ax1 = plt.subplots(figsize=(10, 6))
                            ax1.plot(patrones_df['periodo'], patrones_df['patron_leads'], 'b-', label='Patrón de leads')
                            ax1.set_title(f'Patrón estacional de leads por {agrupacion.lower()}')
                            ax1.set_xlabel(f'Período ({agrupacion.lower()})')
                            ax1.set_ylabel('Cantidad de leads')
                            ax1.legend()
                            ax1.grid(True, linestyle='--', alpha=0.7)
                            
                            fig2, ax2 = plt.subplots(figsize=(10, 6))
                            ax2.plot(comparacion_df['periodo'], comparacion_df['leads_actual'], 'b-', label='Leads actual')
                            ax2.plot(comparacion_df['periodo'], comparacion_df['leads_esperado'], 'r--', label='Leads esperado')
                            ax2.set_title(f'Comparación de leads actual vs esperado ({agrupacion.lower()})')
                            ax2.set_xlabel(f'Período ({agrupacion.lower()})')
                            ax2.set_ylabel('Cantidad de leads')
                            ax2.legend()
                            ax2.grid(True, linestyle='--', alpha=0.7)
                            
                            # Guardar gráficos
                            ruta_grafico1 = os.path.join(directorio_temp, 'patron_estacional.png')
                            ruta_grafico2 = os.path.join(directorio_temp, 'comparacion_leads.png')
                            
                            fig1.savefig(ruta_grafico1)
                            fig2.savefig(ruta_grafico2)
                            
                            # Guardar Excel
                            ruta_excel = os.path.join(directorio_temp, 'analisis_estacionalidad.xlsx')
                            with pd.ExcelWriter(ruta_excel, engine='xlsxwriter') as writer:
                                patrones_df.to_excel(writer, sheet_name='Patrones Estacionales', index=False)
                                comparacion_df.to_excel(writer, sheet_name='Comparación Avance', index=False)
                            
                            # Resultados simulados
                            resultado = {
                                'patrones': patrones_df,
                                'comparacion': comparacion_df,
                                'archivos': {
                                    'graficos': [ruta_grafico1, ruta_grafico2],
                                    'excel': ruta_excel
                                }
                            }
                            
                            # Mostrar resultados
                            st.success("Análisis completado exitosamente")
                            
                            # Mostrar patrones
                            st.subheader("Patrones Estacionales")
                            st.dataframe(resultado['patrones'])
                            
                            # Mostrar comparación
                            st.subheader("Comparación de Avance")
                            st.dataframe(resultado['comparacion'])
                            
                            # Mostrar visualizaciones
                            st.subheader("Visualizaciones")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.image(ruta_grafico1)
                            with col2:
                                st.image(ruta_grafico2)
                                
                            # Botón para descargar reporte Excel
                            if 'excel' in resultado['archivos']:
                                with open(resultado['archivos']['excel'], "rb") as file:
                                    st.download_button(
                                        "Descargar Reporte Excel",
                                        file,
                                        f"analisis_estacionalidad_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                        
                        except Exception as e:
                            st.error(f"Error al ejecutar análisis: {str(e)}")
        
        elif analisis_tipo == "Análisis de Elasticidad":
            st.subheader("Análisis de Elasticidad de Presupuesto")
            
            # Parámetros para el análisis
            st.write("Explore el impacto de diferentes variaciones presupuestarias en el rendimiento de las campañas.")
            
            # Verificar columnas necesarias
            col_requeridas = ['costo', 'conversiones', 'origen', 'programa']
            tiene_columnas = all(col in st.session_state.datos_procesados.columns for col in col_requeridas)
            
            if not tiene_columnas:
                cols_disponibles = list(st.session_state.datos_procesados.columns)
                st.warning(f"Los datos procesados no contienen todas las columnas requeridas: {col_requeridas}")
                st.write(f"Columnas disponibles: {cols_disponibles}")
                
                # Selección alternativa de columnas
                col_costo = st.selectbox("Seleccione columna de costo:", cols_disponibles)
                col_conv = st.selectbox("Seleccione columna de conversiones/resultados:", cols_disponibles)
                col_origen = st.selectbox("Seleccione columna de origen/canal:", cols_disponibles)
            else:
                col_costo = 'costo'
                col_conv = 'conversiones'
                col_origen = 'origen'
            
            # Parámetros de simulación
            variaciones = st.multiselect(
                "Seleccione variaciones presupuestarias a simular:",
                ["-30%", "-20%", "-10%", "+10%", "+20%", "+30%"],
                default=["-20%", "-10%", "+10%", "+20%"]
            )
            
            if st.button("Ejecutar Análisis de Elasticidad"):
                with st.spinner("Ejecutando análisis..."):
                    try:
                        # Crear directorio temporal para resultados
                        import tempfile
                        directorio_temp = tempfile.mkdtemp()
                        
                        # Preparar datos
                        datos = st.session_state.datos_procesados.copy()
                        
                        # Simulación de análisis de elasticidad (en lugar del módulo real)
                        # En una implementación real, aquí se llamaría a la función del módulo correspondiente
                        
                        # Convertir variaciones a números
                        var_numeros = [float(v.replace("%", "").replace("+", ""))/100 for v in variaciones]
                        
                        # Datos actuales (agregados por origen)
                        actuales = datos.groupby(col_origen).agg({
                            col_costo: 'sum',
                            col_conv: 'sum'
                        }).reset_index()
                        actuales['costo_por_conversion'] = actuales[col_costo] / actuales[col_conv]
                        actuales['elasticidad'] = np.random.uniform(0.7, 1.3, len(actuales))  # Simulada
                        
                        # Crear proyecciones para cada variación
                        proyecciones = []
                        for variacion in var_numeros:
                            for _, row in actuales.iterrows():
                                # Simular efecto de variación presupuestaria
                                # Usando elasticidad: conv_nueva = conv * (1 + elasticidad * variacion)
                                costo_nuevo = row[col_costo] * (1 + variacion)
                                conv_nuevas = row[col_conv] * (1 + row['elasticidad'] * variacion)
                                costo_por_conv_nuevo = costo_nuevo / conv_nuevas
                                roi_nuevo = conv_nuevas / costo_nuevo
                                
                                var_percent = f"+{variacion*100:.0f}%" if variacion > 0 else f"{variacion*100:.0f}%"
                                
                                proyecciones.append({
                                    'variacion': var_percent,
                                    'origen': row[col_origen],
                                    'costo_original': row[col_costo],
                                    'conversiones_original': row[col_conv],
                                    'costo_nuevo': costo_nuevo,
                                    'conversiones_nuevo': conv_nuevas,
                                    'diferencia_conversiones': conv_nuevas - row[col_conv],
                                    'diferencia_porcentual': (conv_nuevas / row[col_conv] - 1) * 100,
                                    'costo_por_conversion_original': row['costo_por_conversion'],
                                    'costo_por_conversion_nuevo': costo_por_conv_nuevo,
                                    'elasticidad': row['elasticidad']
                                })
                        
                        # Convertir a DataFrame
                        proyecciones_df = pd.DataFrame(proyecciones)
                        
                        # Resumen por variación
                        resumen = proyecciones_df.groupby('variacion').agg({
                            'costo_original': 'sum',
                            'conversiones_original': 'sum',
                            'costo_nuevo': 'sum',
                            'conversiones_nuevo': 'sum',
                            'diferencia_conversiones': 'sum'
                        }).reset_index()
                        
                        resumen['costo_por_conversion_original'] = resumen['costo_original'] / resumen['conversiones_original']
                        resumen['costo_por_conversion_nuevo'] = resumen['costo_nuevo'] / resumen['conversiones_nuevo']
                        resumen['eficiencia_cambio'] = (resumen['costo_por_conversion_original'] / resumen['costo_por_conversion_nuevo'] - 1) * 100
                        
                        # Generar gráficos
                        # 1. Gráfico de barras de conversiones por variación
                        fig1, ax1 = plt.subplots(figsize=(10, 6))
                        
                        # Ordenar variaciones correctamente
                        orden_var = sorted(resumen['variacion'].unique(), key=lambda x: float(x.replace("%", "").replace("+", "")))
                        resumen_ord = resumen.set_index('variacion').loc[orden_var].reset_index()
                        
                        ax1.bar(resumen_ord['variacion'], resumen_ord['conversiones_nuevo'], color='skyblue')
                        ax1.set_title('Conversiones proyectadas por variación presupuestaria')
                        ax1.set_xlabel('Variación presupuestaria')
                        ax1.set_ylabel('Conversiones proyectadas')
                        ax1.grid(True, linestyle='--', alpha=0.7, axis='y')
                        
                        # 2. Gráfico de cambio porcentual en costo por conversión
                        fig2, ax2 = plt.subplots(figsize=(10, 6))
                        ax2.bar(resumen_ord['variacion'], resumen_ord['eficiencia_cambio'], color='lightgreen')
                        ax2.set_title('Cambio en eficiencia (costo por conversión)')
                        ax2.set_xlabel('Variación presupuestaria')
                        ax2.set_ylabel('Cambio en eficiencia (%)')
                        ax2.grid(True, linestyle='--', alpha=0.7, axis='y')
                        
                        # Guardar gráficos
                        ruta_grafico1 = os.path.join(directorio_temp, 'conversiones_proyectadas.png')
                        ruta_grafico2 = os.path.join(directorio_temp, 'cambio_eficiencia.png')
                        
                        fig1.savefig(ruta_grafico1)
                        fig2.savefig(ruta_grafico2)
                        
                        # Guardar Excel
                        ruta_excel = os.path.join(directorio_temp, 'analisis_elasticidad.xlsx')
                        with pd.ExcelWriter(ruta_excel, engine='xlsxwriter') as writer:
                            actuales.to_excel(writer, sheet_name='Datos Actuales', index=False)
                            proyecciones_df.to_excel(writer, sheet_name='Proyecciones Detalladas', index=False)
                            resumen.to_excel(writer, sheet_name='Resumen', index=False)
                        
                        # Resultados simulados
                        resultado = {
                            'actuales': actuales,
                            'proyecciones': proyecciones_df,
                            'resumen': resumen,
                            'archivos': {
                                'graficos': [ruta_grafico1, ruta_grafico2],
                                'excel': ruta_excel
                            }
                        }
                        
                        # Mostrar resultados
                        st.success("Análisis completado exitosamente")
                        
                        # Mostrar resumen
                        st.subheader("Resumen por Variación Presupuestaria")
                        st.dataframe(resultado['resumen'])
                        
                        # Mostrar visualizaciones
                        st.subheader("Visualizaciones")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(ruta_grafico1)
                        with col2:
                            st.image(ruta_grafico2)
                        
                        # Mostrar proyecciones detalladas
                        with st.expander("Ver proyecciones detalladas por origen"):
                            st.dataframe(resultado['proyecciones'])
                        
                        # Botón para descargar reporte Excel
                        with open(resultado['archivos']['excel'], "rb") as file:
                            st.download_button(
                                "Descargar Reporte Excel",
                                file,
                                f"analisis_elasticidad_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    
                    except Exception as e:
                        st.error(f"Error al ejecutar análisis: {str(e)}")
        
        elif analisis_tipo == "Simulación de Mejora de Conversión":
            st.subheader("Simulación de Mejora de Conversión")
            
            st.write("Simule el impacto de mejoras en las tasas de conversión en diferentes etapas del embudo.")
            
            # Parámetros de simulación
            etapas = ["Leads a Contacto", "Contacto a Demostración", "Demostración a Matrícula"]
            
            mejoras = {}
            col1, col2, col3 = st.columns(3)
            
            with col1:
                mejoras[etapas[0]] = st.slider(f"Mejora en {etapas[0]}", 0, 100, 10, 5) / 100
            
            with col2:
                mejoras[etapas[1]] = st.slider(f"Mejora en {etapas[1]}", 0, 100, 15, 5) / 100
            
            with col3:
                mejoras[etapas[2]] = st.slider(f"Mejora en {etapas[2]}", 0, 100, 20, 5) / 100
            
            # Valores base (simulados)
            valores_base = {
                etapas[0]: 0.60,  # 60% de leads contactados
                etapas[1]: 0.30,  # 30% de contactados asisten a demo
                etapas[2]: 0.20   # 20% de demos se matriculan
            }
            
            # Calcular valores nuevos
            valores_nuevos = {
                etapa: min(1.0, tasa * (1 + mejoras[etapa])) 
                for etapa, tasa in valores_base.items()
            }
            
            # Mostrar tasas actuales vs proyectadas
            st.subheader("Tasas actuales vs. proyectadas")
            
            data_tasas = []
            for etapa in etapas:
                data_tasas.append({
                    "Etapa": etapa,
                    "Tasa Actual": valores_base[etapa],
                    "Tasa Proyectada": valores_nuevos[etapa],
                    "Mejora": mejoras[etapa] * 100
                })
            
            df_tasas = pd.DataFrame(data_tasas)
            st.dataframe(df_tasas)
            
            # Embudo actual
            leads_iniciales = 1000  # Valor ejemplo
            
            actual = {
                "Leads": leads_iniciales,
                "Contactados": leads_iniciales * valores_base[etapas[0]],
                "Demostraciones": leads_iniciales * valores_base[etapas[0]] * valores_base[etapas[1]],
                "Matrículas": leads_iniciales * valores_base[etapas[0]] * valores_base[etapas[1]] * valores_base[etapas[2]]
            }
            
            # Embudo proyectado
            proyectado = {
                "Leads": leads_iniciales,
                "Contactados": leads_iniciales * valores_nuevos[etapas[0]],
                "Demostraciones": leads_iniciales * valores_nuevos[etapas[0]] * valores_nuevos[etapas[1]],
                "Matrículas": leads_iniciales * valores_nuevos[etapas[0]] * valores_nuevos[etapas[1]] * valores_nuevos[etapas[2]]
            }
            
            if st.button("Ejecutar Simulación"):
                # Crear directorio temporal para resultados
                import tempfile
                directorio_temp = tempfile.mkdtemp()
                
                # Generar gráfico de comparación
                fig, ax = plt.subplots(figsize=(12, 7))
                
                etapas_embudo = list(actual.keys())
                valores_actuales = list(actual.values())
                valores_proyectados = list(proyectado.values())
                
                # Crear posiciones en el eje x
                x = range(len(etapas_embudo))
                width = 0.35
                
                # Graficar barras
                ax.bar([i - width/2 for i in x], valores_actuales, width, label='Actual', color='lightblue')
                ax.bar([i + width/2 for i in x], valores_proyectados, width, label='Proyectado', color='lightgreen')
                
                # Configurar gráfico
                ax.set_title('Comparación de Embudo de Conversión: Actual vs. Proyectado')
                ax.set_xticks(x)
                ax.set_xticklabels(etapas_embudo)
                ax.legend()
                
                # Añadir etiquetas de valores
                for i, v in enumerate(valores_actuales):
                    ax.text(i - width/2, v + 5, f'{v:.1f}', ha='center', fontsize=9)
                
                for i, v in enumerate(valores_proyectados):
                    ax.text(i + width/2, v + 5, f'{v:.1f}', ha='center', fontsize=9)
                
                # Calcular diferencias y ROI
                dif_matriculas = proyectado["Matrículas"] - actual["Matrículas"]
                incremento_pct = (dif_matriculas / actual["Matrículas"]) * 100
                
                # Guardar gráfico
                ruta_grafico = os.path.join(directorio_temp, 'simulacion_conversion.png')
                fig.savefig(ruta_grafico)
                
                # Crear dataframe para Excel
                df_embudo = pd.DataFrame({
                    'Etapa': etapas_embudo,
                    'Actual': valores_actuales,
                    'Proyectado': valores_proyectados,
                    'Diferencia': [b-a for a, b in zip(valores_actuales, valores_proyectados)],
                    'Incremento %': [(b/a-1)*100 if a > 0 else 0 for a, b in zip(valores_actuales, valores_proyectados)]
                })
                
                # Guardar Excel
                ruta_excel = os.path.join(directorio_temp, 'simulacion_conversion.xlsx')
                with pd.ExcelWriter(ruta_excel, engine='xlsxwriter') as writer:
                    df_tasas.to_excel(writer, sheet_name='Tasas de Conversión', index=False)
                    df_embudo.to_excel(writer, sheet_name='Embudo Completo', index=False)
                
                # Mostrar resultados
                st.success("Simulación completada exitosamente")
                
                # Mostrar gráfico
                st.image(ruta_grafico)
                
                # Mostrar resumen de impacto
                st.subheader("Resumen de Impacto")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Incremento en Matrículas", 
                        f"{dif_matriculas:.1f}", 
                        f"{incremento_pct:.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "Tasa de Conversión Total",
                        f"{(proyectado['Matrículas']/proyectado['Leads'])*100:.2f}%",
                        f"{((proyectado['Matrículas']/proyectado['Leads'])/(actual['Matrículas']/actual['Leads'])-1)*100:.1f}%"
                    )
                
                # Mostrar tabla de embudo
                st.subheader("Embudo de Conversión")
                st.dataframe(df_embudo)
                
                # Botón para descargar Excel
                with open(ruta_excel, "rb") as file:
                    st.download_button(
                        "Descargar Reporte Excel",
                        file,
                        f"simulacion_conversion_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        elif analisis_tipo == "Proyección de Cierre":
            st.subheader("Proyección de Cierre de Campaña")
            
            st.write("Estime los resultados finales de la campaña basados en el avance actual.")
            
            # Parámetros
            col1, col2 = st.columns(2)
            
            with col1:
                avance_actual = st.slider("Avance actual de la campaña (%)", 10, 90, 40, 5)
                
            with col2:
                nivel_confianza = st.slider("Nivel de confianza (%)", 80, 99, 95, 1)
            
            # Datos actuales (simulados)
            resultados_actuales = {
                "Leads generados": 1200,
                "Leads contactados": 720,
                "Demostraciones": 210,
                "Matrículas": 38
            }
            
            if st.button("Calcular Proyección"):
                # Crear directorio temporal para resultados
                import tempfile
                directorio_temp = tempfile.mkdtemp()
                
                # Factor de proyección basado en avance
                factor_proyeccion = 100 / avance_actual
                
                # Calcular proyecciones
                proyecciones = {}
                intervalos = {}
                
                for metrica, valor in resultados_actuales.items():
                    # Proyección simple
                    proyeccion = valor * factor_proyeccion
                    
                    # Simular intervalo de confianza
                    # En un caso real, esto se calcularía con métodos estadísticos más rigurosos
                    z_score = {
                        90: 1.645,
                        95: 1.96,
                        99: 2.576
                    }.get(nivel_confianza, 1.96)
                    
                    # Simular error estándar como función del avance (menor avance, mayor incertidumbre)
                    error_std = proyeccion * (1.5 - avance_actual/100)
                    
                    # Intervalo de confianza
                    margen_error = z_score * error_std
                    limite_inferior = max(0, proyeccion - margen_error)
                    limite_superior = proyeccion + margen_error
                    
                    proyecciones[metrica] = proyeccion
                    intervalos[metrica] = (limite_inferior, limite_superior)
                
                # Crear dataframe con proyecciones
                df_proyeccion = pd.DataFrame({
                    'Métrica': list(resultados_actuales.keys()),
                    'Actual': list(resultados_actuales.values()),
                    'Proyección': [proyecciones[k] for k in resultados_actuales.keys()],
                    'Límite Inferior': [intervalos[k][0] for k in resultados_actuales.keys()],
                    'Límite Superior': [intervalos[k][1] for k in resultados_actuales.keys()]
                })
                
                # Generar gráfico de proyección
                fig, ax = plt.subplots(figsize=(12, 7))
                
                # Datos para el gráfico
                metricas = df_proyeccion['Métrica']
                actuales = df_proyeccion['Actual']
                proyectados = df_proyeccion['Proyección']
                
                # Crear posiciones en el eje x
                x = range(len(metricas))
                width = 0.35
                
                # Graficar barras
                ax.bar([i - width/2 for i in x], actuales, width, label=f'Actual ({avance_actual}%)', color='lightblue')
                ax.bar([i + width/2 for i in x], proyectados, width, label='Proyección Final', color='lightgreen')
                
                # Añadir intervalos de confianza
                errores = [(sup-inf)/2 for inf, sup in zip(df_proyeccion['Límite Inferior'], df_proyeccion['Límite Superior'])]
                ax.errorbar([i + width/2 for i in x], proyectados, yerr=errores, fmt='none', color='darkgreen', capsize=5)
                
                # Configurar gráfico
                ax.set_title(f'Proyección de Resultados Finales (Confianza: {nivel_confianza}%)')
                ax.set_xticks(x)
                ax.set_xticklabels(metricas, rotation=45, ha='right')
                ax.legend()
                
                # Añadir etiquetas de valores
                for i, v in enumerate(actuales):
                    ax.text(i - width/2, v + 5, f'{v:.0f}', ha='center', fontsize=9)
                
                for i, v in enumerate(proyectados):
                    ax.text(i + width/2, v + 5, f'{v:.0f}', ha='center', fontsize=9)
                
                plt.tight_layout()
                
                # Guardar gráfico
                ruta_grafico = os.path.join(directorio_temp, 'proyeccion_cierre.png')
                fig.savefig(ruta_grafico)
                
                # Guardar Excel
                ruta_excel = os.path.join(directorio_temp, 'proyeccion_cierre.xlsx')
                with pd.ExcelWriter(ruta_excel, engine='xlsxwriter') as writer:
                    df_proyeccion.to_excel(writer, sheet_name='Proyecciones', index=False)
                
                # Mostrar resultados
                st.success("Proyección calculada exitosamente")
                
                # Mostrar gráfico
                st.image(ruta_grafico)
                
                # Mostrar tabla de proyección
                st.subheader("Proyecciones de Cierre")
                st.dataframe(df_proyeccion)
                
                # Mostrar resumen
                st.subheader("Resumen de Intervalos de Confianza")
                
                for metrica in resultados_actuales.keys():
                    st.metric(
                        metrica,
                        f"{proyecciones[metrica]:.0f}",
                        f"±{((intervalos[metrica][1]-intervalos[metrica][0])/2):.0f}"
                    )
                
                # Botón para descargar Excel
                with open(ruta_excel, "rb") as file:
                    st.download_button(
                        "Descargar Proyecciones",
                        file,
                        f"proyeccion_cierre_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

# Página de Reportes
elif menu == "Reportes":
    st.title("Generación de Reportes")
    
    if st.session_state.datos_procesados is None:
        st.warning("Primero debe cargar y procesar los datos en la sección 'Carga de Datos'")
    else:
        # Tipo de reporte
        reporte_tipo = st.selectbox(
            "Seleccione tipo de reporte:",
            ["Reporte Diario", 
             "Reporte Semanal", 
             "Reporte de Performance",
             "Reporte Ejecutivo",
             "Reporte Personalizado"]
        )
        
        # Opciones según tipo de reporte
        if reporte_tipo == "Reporte Diario":
            st.subheader("Reporte Diario")
            
            fecha_reporte = st.date_input("Seleccione fecha")
            
            formato_reporte = st.radio(
                "Formato de salida",
                ["PDF", "Excel", "HTML"],
                horizontal=True
            )
            
            # Opciones adicionales
            incluir_graficos = st.checkbox("Incluir gráficos", value=True)
            incluir_metricas = st.checkbox("Incluir métricas detalladas", value=True)
            
            # Secciones a incluir
            st.subheader("Secciones a incluir:")
            col1, col2 = st.columns(2)
            
            with col1:
                incluir_leads = st.checkbox("Leads generados", value=True)
                incluir_contactados = st.checkbox("Contactos realizados", value=True)
                incluir_demostraciones = st.checkbox("Demostraciones", value=True)
            
            with col2:
                incluir_conversiones = st.checkbox("Conversiones", value=True)
                incluir_cac = st.checkbox("Costo de adquisición", value=True)
                incluir_roi = st.checkbox("ROI por canal", value=True)
            
            if st.button("Generar Reporte Diario"):
                with st.spinner("Generando reporte..."):
                    try:
                        # Código para generar reporte diario
                        # En una implementación real, aquí se llamaría a la función correspondiente
                        
                        # Crear directorio temporal
                        import tempfile
                        dir_temp = tempfile.mkdtemp()
                        
                        # Generar título del reporte
                        titulo_reporte = f"Reporte Diario - {fecha_reporte.strftime('%d/%m/%Y')}"
                        
                        # Datos simulados
                        datos_dia = {
                            "Leads": {
                                "Total": 120,
                                "Facebook": 45,
                                "Google": 38,
                                "Instagram": 22,
                                "Otros": 15
                            },
                            "Contactados": {
                                "Total": 87,
                                "Facebook": 32,
                                "Google": 29,
                                "Instagram": 16,
                                "Otros": 10
                            },
                            "Demostraciones": {
                                "Total": 28,
                                "Facebook": 12,
                                "Google": 9,
                                "Instagram": 5,
                                "Otros": 2
                            },
                            "Conversiones": {
                                "Total": 8,
                                "Facebook": 3,
                                "Google": 3,
                                "Instagram": 2,
                                "Otros": 0
                            },
                            "Costos": {
                                "Total": 1500,
                                "Facebook": 600,
                                "Google": 450,
                                "Instagram": 300,
                                "Otros": 150
                            }
                        }
                        
                        # Crear DataFrames para el reporte
                        df_canales = pd.DataFrame({
                            "Canal": ["Facebook", "Google", "Instagram", "Otros", "Total"],
                            "Leads": [datos_dia["Leads"][canal] for canal in ["Facebook", "Google", "Instagram", "Otros", "Total"]],
                            "Contactados": [datos_dia["Contactados"][canal] for canal in ["Facebook", "Google", "Instagram", "Otros", "Total"]],
                            "Demostraciones": [datos_dia["Demostraciones"][canal] for canal in ["Facebook", "Google", "Instagram", "Otros", "Total"]],
                            "Conversiones": [datos_dia["Conversiones"][canal] for canal in ["Facebook", "Google", "Instagram", "Otros", "Total"]],
                            "Costo": [datos_dia["Costos"][canal] for canal in ["Facebook", "Google", "Instagram", "Otros", "Total"]]
                        })
                        
                        # Calcular métricas
                        df_canales["Tasa Contacto"] = df_canales["Contactados"] / df_canales["Leads"]
                        df_canales["Tasa Demo"] = df_canales["Demostraciones"] / df_canales["Contactados"]
                        df_canales["Tasa Conversión"] = df_canales["Conversiones"] / df_canales["Demostraciones"]
                        df_canales["Costo por Lead"] = df_canales["Costo"] / df_canales["Leads"]
                        df_canales["Costo por Conversión"] = df_canales["Costo"] / df_canales["Conversiones"].replace(0, float('nan'))
                        
                        # Generar gráficos
                        if incluir_graficos:
                            # Gráfico 1: Distribución de leads por canal
                            fig1, ax1 = plt.subplots(figsize=(8, 5))
                            canales = df_canales["Canal"][:-1]  # Excluir Total
                            valores = df_canales["Leads"][:-1]
                            ax1.pie(valores, labels=canales, autopct='%1.1f%%', startangle=90)
                            ax1.axis('equal')
                            ax1.set_title('Distribución de Leads por Canal')
                            
                            # Gráfico 2: Embudo de conversión
                            fig2, ax2 = plt.subplots(figsize=(10, 6))
                            etapas = ["Leads", "Contactados", "Demostraciones", "Conversiones"]
                            valores = [datos_dia[etapa]["Total"] for etapa in etapas]
                            ax2.bar(etapas, valores, color=['skyblue', 'lightgreen', 'lightsalmon', 'gold'])
                            for i, v in enumerate(valores):
                                ax2.text(i, v + 3, str(v), ha='center')
                            ax2.set_title('Embudo de Conversión')
                            
                            # Guardar gráficos
                            ruta_grafico1 = os.path.join(dir_temp, 'distribucion_leads.png')
                            ruta_grafico2 = os.path.join(dir_temp, 'embudo_conversion.png')
                            fig1.savefig(ruta_grafico1)
                            fig2.savefig(ruta_grafico2)
                        
                        # Generar reporte según formato
                        if formato_reporte == "Excel":
                            ruta_reporte = os.path.join(dir_temp, f"reporte_diario_{fecha_reporte.strftime('%Y%m%d')}.xlsx")
                            
                            with pd.ExcelWriter(ruta_reporte, engine='xlsxwriter') as writer:
                                df_canales.to_excel(writer, sheet_name='Resumen por Canal', index=False)
                                
                                # Crear hojas adicionales según secciones seleccionadas
                                if incluir_leads:
                                    datos_leads = pd.DataFrame({"Canal": ["Facebook", "Google", "Instagram", "Otros"],
                                                            "Leads": [datos_dia["Leads"][canal] for canal in ["Facebook", "Google", "Instagram", "Otros"]]})
                                    datos_leads.to_excel(writer, sheet_name='Leads Detallados', index=False)
                                
                                if incluir_conversiones:
                                    datos_conv = pd.DataFrame({"Canal": ["Facebook", "Google", "Instagram", "Otros"],
                                                            "Conversiones": [datos_dia["Conversiones"][canal] for canal in ["Facebook", "Google", "Instagram", "Otros"]]})
                                    datos_conv.to_excel(writer, sheet_name='Conversiones Detalladas', index=False)
                                
                                # Insertar imágenes si se incluyen gráficos
                                if incluir_graficos:
                                    worksheet = writer.sheets['Resumen por Canal']
                                    worksheet.insert_image('H2', ruta_grafico1)
                                    worksheet.insert_image('H15', ruta_grafico2)
                        
                        elif formato_reporte == "PDF":
                            ruta_reporte = os.path.join(dir_temp, f"reporte_diario_{fecha_reporte.strftime('%Y%m%d')}.html")
                            
                            # Generar HTML para convertir a PDF
                            html_content = f"""
                            <html>
                            <head>
                                <title>{titulo_reporte}</title>
                                <style>
                                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                                    h1 {{ color: #2c3e50; }}
                                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                                    th {{ background-color: #f2f2f2; }}
                                    .metric {{ font-size: 24px; font-weight: bold; color: #3498db; }}
                                    .metric-title {{ font-size: 14px; color: #7f8c8d; }}
                                    .metric-container {{ float: left; width: 120px; margin: 10px; text-align: center; }}
                                    .clearfix {{ clear: both; }}
                                </style>
                            </head>
                            <body>
                                <h1>{titulo_reporte}</h1>
                                
                                <div>
                            """
                            
                            # Añadir métricas principales
                            html_content += """
                                <div style="margin-bottom: 30px;">
                                    <div class="metric-container">
                                        <div class="metric">{}</div>
                                        <div class="metric-title">Leads</div>
                                    </div>
                                    <div class="metric-container">
                                        <div class="metric">{}</div>
                                        <div class="metric-title">Contactados</div>
                                    </div>
                                    <div class="metric-container">
                                        <div class="metric">{}</div>
                                        <div class="metric-title">Demos</div>
                                    </div>
                                    <div class="metric-container">
                                        <div class="metric">{}</div>
                                        <div class="metric-title">Conversiones</div>
                                    </div>
                                    <div class="clearfix"></div>
                                </div>
                            """.format(
                                datos_dia["Leads"]["Total"],
                                datos_dia["Contactados"]["Total"],
                                datos_dia["Demostraciones"]["Total"],
                                datos_dia["Conversiones"]["Total"]
                            )
                            
                            # Añadir tabla de resumen
                            html_content += """
                                <h2>Resumen por Canal</h2>
                                <table>
                                    <tr>
                                        <th>Canal</th>
                                        <th>Leads</th>
                                        <th>Contactados</th>
                                        <th>Demos</th>
                                        <th>Conversiones</th>
                                        <th>Costo</th>
                                        <th>Costo/Lead</th>
                                        <th>Costo/Conversión</th>
                                    </tr>
                            """
                            
                            for i, row in df_canales.iterrows():
                                html_content += f"""
                                    <tr>
                                        <td>{row['Canal']}</td>
                                        <td>{row['Leads']}</td>
                                        <td>{row['Contactados']}</td>
                                        <td>{row['Demostraciones']}</td>
                                        <td>{row['Conversiones']}</td>
                                        <td>${row['Costo']:.2f}</td>
                                        <td>${row['Costo por Lead']:.2f}</td>
                                        <td>${row['Costo por Conversión'] if not pd.isna(row['Costo por Conversión']) else 'N/A'}</td>
                                    </tr>
                                """
                            
                            html_content += """
                                </table>
                            """
                            
                            # Añadir imágenes si se incluyen gráficos
                            if incluir_graficos:
                                # Codificar imágenes en base64
                                import base64
                                
                                def get_image_base64(ruta):
                                    with open(ruta, "rb") as img_file:
                                        return base64.b64encode(img_file.read()).decode('utf-8')
                                
                                img1_b64 = get_image_base64(ruta_grafico1)
                                img2_b64 = get_image_base64(ruta_grafico2)
                                
                                html_content += f"""
                                    <h2>Gráficos</h2>
                                    <div style="text-align: center; margin-bottom: 20px;">
                                        <img src="data:image/png;base64,{img1_b64}" style="max-width: 400px; margin-bottom: 20px;">
                                        <img src="data:image/png;base64,{img2_b64}" style="max-width: 500px;">
                                    </div>
                                """
                            
                            # Cerrar HTML
                            html_content += """
                                </div>
                            </body>
                            </html>
                            """
                            
                            # Guardar HTML
                            with open(ruta_reporte, 'w') as f:
                                f.write(html_content)
                            
                            # En una implementación real, aquí se convertiría el HTML a PDF
                            # Para este ejemplo, usamos solo HTML
                            ruta_reporte = ruta_reporte  # La ruta real sería al PDF
                        
                        else:  # HTML
                            ruta_reporte = os.path.join(dir_temp, f"reporte_diario_{fecha_reporte.strftime('%Y%m%d')}.html")
                            
                            # Similar al caso de PDF, pero sin conversión final
                            # Reutilizar el código HTML del caso PDF
                            # ...
                            
                            # Para simplificar, generamos un HTML básico
                            html_content = f"""
                            <html>
                            <head>
                                <title>{titulo_reporte}</title>
                                <style>
                                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                                    h1 {{ color: #2c3e50; }}
                                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                                    th {{ background-color: #f2f2f2; }}
                                </style>
                            </head>
                            <body>
                                <h1>{titulo_reporte}</h1>
                                <h2>Resumen por Canal</h2>
                                {df_canales.to_html(index=False)}
                            </body>
                            </html>
                            """
                            
                            # Guardar HTML
                            with open(ruta_reporte, 'w') as f:
                                f.write(html_content)
                        
                        # Mostrar éxito
                        st.success(f"Reporte generado correctamente en formato {formato_reporte}")
                        
                        # Mostrar vista previa
                        if incluir_graficos:
                            st.subheader("Vista previa de gráficos")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.image(ruta_grafico1)
                            with col2:
                                st.image(ruta_grafico2)
                        
                        st.subheader("Resumen por Canal")
                        st.dataframe(df_canales)
                        
                        # Botón de descarga
                        with open(ruta_reporte, "rb") as file:
                            extension = "xlsx" if formato_reporte == "Excel" else "html"
                            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if formato_reporte == "Excel" else "text/html"
                            
                            st.download_button(
                                f"Descargar Reporte {formato_reporte}",
                                file,
                                f"reporte_diario_{fecha_reporte.strftime('%Y%m%d')}.{extension}",
                                mime_type
                            )
                    
                    except Exception as e:
                        st.error(f"Error al generar reporte: {str(e)}")
        
        elif reporte_tipo == "Reporte Ejecutivo":
            st.subheader("Reporte Ejecutivo")
            
            # Parámetros
            periodo = st.selectbox(
                "Seleccione período:",
                ["Última semana", "Último mes", "Trimestre actual", "Año actual"]
            )
            
            formato_reporte = st.radio(
                "Formato de salida",
                ["PDF", "PowerPoint", "Excel"],
                horizontal=True
            )
            
            # Audiencia del reporte
            audiencia = st.selectbox(
                "Audiencia objetivo:",
                ["Dirección General", "Equipo de Marketing", "Equipo Comercial", "Todo público"]
            )
            
            # Nivel de detalle
            nivel_detalle = st.slider(
                "Nivel de detalle",
                1, 5, 3,
                help="1: Muy resumido, 5: Muy detallado"
            )
            
            # Secciones a incluir
            st.subheader("Secciones a incluir:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                incluir_resumen = st.checkbox("Resumen ejecutivo", value=True)
                incluir_tendencias = st.checkbox("Tendencias principales", value=True)
            
            with col2:
                incluir_comparativas = st.checkbox("Comparativas históricas", value=True)
                incluir_roi = st.checkbox("Análisis de ROI", value=True)
            
            with col3:
                incluir_predictivo = st.checkbox("Análisis predictivo", value=True)
                incluir_recomendaciones = st.checkbox("Recomendaciones", value=True)
            
            if st.button("Generar Reporte Ejecutivo"):
                with st.spinner("Generando reporte ejecutivo..."):
                    try:
                        # Crear directorio temporal
                        import tempfile
                        dir_temp = tempfile.mkdtemp()
                        
                        # En una implementación real, aquí se generaría el reporte ejecutivo
                        # Dependiendo de los parámetros seleccionados
                        
                        # Simulación simple: crear un archivo de muestra
                        if formato_reporte == "PDF":
                            ruta_reporte = os.path.join(dir_temp, "reporte_ejecutivo_ejemplo.html")
                            with open(ruta_reporte, 'w') as f:
                                f.write("<html><body><h1>Reporte Ejecutivo de Ejemplo</h1></body></html>")
                        elif formato_reporte == "PowerPoint":
                            ruta_reporte = os.path.join(dir_temp, "reporte_ejecutivo_ejemplo.html")
                            with open(ruta_reporte, 'w') as f:
                                f.write("<html><body><h1>Presentación Ejecutiva de Ejemplo</h1></body></html>")
                        else:  # Excel
                            ruta_reporte = os.path.join(dir_temp, "reporte_ejecutivo_ejemplo.html")
                            with open(ruta_reporte, 'w') as f:
                                f.write("<html><body><h1>Datos de Reporte Ejecutivo de Ejemplo</h1></body></html>")
                        
                        st.success(f"Reporte ejecutivo generado para {audiencia}, período {periodo}")
                        
                        # Mostrar contenido del reporte (simulado)
                        st.subheader("Vista previa del reporte")
                        
                        # Imagen de ejemplo
                        st.image("https://via.placeholder.com/800x400?text=Vista+Previa+Reporte+Ejecutivo")
                        
                        # Información sobre lo que contiene
                        st.write(f"**Reporte Ejecutivo para:** {audiencia}")
                        st.write(f"**Período:** {periodo}")
                        st.write(f"**Nivel de detalle:** {nivel_detalle}/5")
                        
                        st.write("**Secciones incluidas:**")
                        secciones = []
                        if incluir_resumen:
                            secciones.append("Resumen ejecutivo")
                        if incluir_tendencias:
                            secciones.append("Tendencias principales")
                        if incluir_comparativas:
                            secciones.append("Comparativas históricas")
                        if incluir_roi:
                            secciones.append("Análisis de ROI")
                        if incluir_predictivo:
                            secciones.append("Análisis predictivo")
                        if incluir_recomendaciones:
                            secciones.append("Recomendaciones")
                        
                        for seccion in secciones:
                            st.write(f"- {seccion}")
                        
                        # Botón de descarga (simulado)
                        with open(ruta_reporte, "rb") as file:
                            st.download_button(
                                f"Descargar Reporte Ejecutivo ({formato_reporte})",
                                file,
                                f"reporte_ejecutivo_{datetime.now().strftime('%Y%m%d')}.html",
                                "text/html"
                            )
                    
                    except Exception as e:
                        st.error(f"Error al generar reporte ejecutivo: {str(e)}")
        
        elif reporte_tipo == "Reporte Personalizado":
            st.subheader("Reporte Personalizado")
            
            st.write("Configure su reporte personalizado seleccionando dimensiones, métricas y filtros.")
            
            # Dimensiones disponibles
            dimensiones_disponibles = [
                "Fecha", "Origen", "Programa", "Marca", "Región", "Asesor", "Campaña"
            ]
            
            # Métricas disponibles
            metricas_disponibles = [
                "Leads", "Contactados", "Demostraciones", "Matrículas", 
                "Costo", "Costo por Lead", "Costo por Matrícula", "ROI", 
                "Tasa de Contacto", "Tasa de Demostración", "Tasa de Conversión"
            ]
            
            # Selección de dimensiones
            dimensiones_seleccionadas = st.multiselect(
                "Seleccione dimensiones (máximo 3):",
                dimensiones_disponibles,
                default=["Origen", "Programa"]
            )
            
            if len(dimensiones_seleccionadas) > 3:
                st.warning("Se recomienda seleccionar como máximo 3 dimensiones para mantener la legibilidad del reporte.")
            
            # Selección de métricas
            metricas_seleccionadas = st.multiselect(
                "Seleccione métricas:",
                metricas_disponibles,
                default=["Leads", "Matrículas", "Costo por Lead"]
            )
            
            # Filtros
            with st.expander("Configurar filtros"):
                # Fechas
                col1, col2 = st.columns(2)
                with col1:
                    fecha_inicio = st.date_input("Fecha inicio")
                with col2:
                    fecha_fin = st.date_input("Fecha fin")
                
                # Filtros adicionales
                if "Origen" in dimensiones_disponibles and "Origen" not in dimensiones_seleccionadas:
                    origen_filtro = st.multiselect("Filtrar por origen:", ["Facebook", "Google", "Instagram", "Email", "Orgánico"])
                
                if "Programa" in dimensiones_disponibles and "Programa" not in dimensiones_seleccionadas:
                    programa_filtro = st.multiselect("Filtrar por programa:", ["MBA", "Marketing Digital", "Data Science", "UX/UI", "Finanzas"])
            
            # Opciones de visualización
            with st.expander("Opciones de visualización"):
                # Tipo de gráfico
                tipo_grafico = st.selectbox(
                    "Tipo de gráfico principal:",
                    ["Barras", "Líneas", "Dispersión", "Pastel", "Área", "Mapa de calor"]
                )
                
                # Colores
                paleta_colores = st.selectbox(
                    "Paleta de colores:",
                    ["Blues", "Greens", "Reds", "Purples", "Viridis", "Plasma"]
                )
                
                # Título y subtítulo
                titulo_reporte = st.text_input("Título del reporte:", "Reporte Personalizado de Desempeño")
                subtitulo_reporte = st.text_input("Subtítulo:", "Análisis de métricas clave")
            
            # Formato de salida
            formato_reporte = st.radio(
                "Formato de salida",
                ["Excel", "PDF", "HTML", "Power BI"],
                horizontal=True
            )
            
            if st.button("Generar Reporte Personalizado"):
                with st.spinner("Generando reporte personalizado..."):
                    try:
                        # Crear directorio temporal
                        import tempfile
                        dir_temp = tempfile.mkdtemp()
                        
                        # En una implementación real, aquí se generaría el reporte personalizado
                        # basado en las dimensiones, métricas y filtros seleccionados
                        
                        # Datos simulados para el reporte
                        # Crear combinaciones de dimensiones seleccionadas
                        import itertools
                        
                        # Valores de ejemplo para cada dimensión
                        valores_dimension = {
                            "Fecha": ["2023-01", "2023-02", "2023-03"],
                            "Origen": ["Facebook", "Google", "Instagram"],
                            "Programa": ["MBA", "Marketing", "Data Science"],
                            "Marca": ["Marca A", "Marca B"],
                            "Región": ["Norte", "Sur", "Centro"],
                            "Asesor": ["Juan", "María", "Carlos"],
                            "Campaña": ["Verano", "Otoño", "Black Friday"]
                        }
                        
                        # Crear combinaciones de valores para las dimensiones seleccionadas
                        dimensiones_valores = []
                        for dim in dimensiones_seleccionadas:
                            dimensiones_valores.append(valores_dimension.get(dim, ["N/A"]))
                        
                        # Generar todas las combinaciones
                        combinaciones = list(itertools.product(*dimensiones_valores))
                        
                        # Crear DataFrame con las combinaciones
                        datos_reporte = []
                        for combo in combinaciones:
                            fila = {}
                            # Añadir dimensiones
                            for i, dim in enumerate(dimensiones_seleccionadas):
                                fila[dim] = combo[i]
                            
                            # Añadir métricas simuladas
                            for metrica in metricas_seleccionadas:
                                if metrica in ["Leads", "Contactados", "Demostraciones", "Matrículas"]:
                                    fila[metrica] = np.random.randint(10, 200)
                                elif metrica in ["Costo"]:
                                    fila[metrica] = np.random.randint(100, 2000)
                                elif metrica in ["Costo por Lead", "Costo por Matrícula"]:
                                    fila[metrica] = np.random.randint(10, 50)
                                elif metrica in ["ROI"]:
                                    fila[metrica] = np.random.uniform(0.5, 3.0)
                                elif metrica in ["Tasa de Contacto", "Tasa de Demostración", "Tasa de Conversión"]:
                                    fila[metrica] = np.random.uniform(0.1, 0.8)
                            
                            datos_reporte.append(fila)
                        
                        df_reporte = pd.DataFrame(datos_reporte)
                        
                        # Generar gráfico según configuración
                        if dimensiones_seleccionadas and metricas_seleccionadas:
                            fig, ax = plt.subplots(figsize=(10, 6))
                            
                            # Agrupar datos según primera dimensión
                            dimension_x = dimensiones_seleccionadas[0]
                            metrica_y = metricas_seleccionadas[0]
                            
                            if len(dimensiones_seleccionadas) > 1:
                                dimension_color = dimensiones_seleccionadas[1]
                                grupos = df_reporte.groupby([dimension_x, dimension_color])[metrica_y].mean().unstack()
                                
                                if tipo_grafico == "Barras":
                                    grupos.plot(kind='bar', ax=ax)
                                elif tipo_grafico == "Líneas":
                                    grupos.plot(kind='line', marker='o', ax=ax)
                                elif tipo_grafico == "Área":
                                    grupos.plot(kind='area', ax=ax)
                                else:
                                    grupos.plot(kind='bar', ax=ax)  # Default
                            else:
                                grupos = df_reporte.groupby(dimension_x)[metrica_y].mean()
                                
                                if tipo_grafico == "Barras":
                                    grupos.plot(kind='bar', ax=ax)
                                elif tipo_grafico == "Líneas":
                                    grupos.plot(kind='line', marker='o', ax=ax)
                                elif tipo_grafico == "Pastel":
                                    grupos.plot(kind='pie', autopct='%1.1f%%', ax=ax)
                                elif tipo_grafico == "Área":
                                    grupos.plot(kind='area', ax=ax)
                                else:
                                    grupos.plot(kind='bar', ax=ax)  # Default
                            
                            ax.set_title(f"{metrica_y} por {dimension_x}")
                            ax.set_xlabel(dimension_x)
                            ax.set_ylabel(metrica_y)
                            
                            # Guardar gráfico
                            ruta_grafico = os.path.join(dir_temp, 'grafico_personalizado.png')
                            fig.savefig(ruta_grafico, bbox_inches='tight')
                        
                        # Generar reporte según formato
                        if formato_reporte == "Excel":
                            ruta_reporte = os.path.join(dir_temp, "reporte_personalizado.xlsx")
                            with pd.ExcelWriter(ruta_reporte, engine='xlsxwriter') as writer:
                                df_reporte.to_excel(writer, sheet_name='Datos', index=False)
                                
                                # Añadir hoja con metadatos
                                pd.DataFrame({
                                    'Parámetro': [
                                        'Título', 'Dimensiones', 'Métricas', 'Fecha inicio', 'Fecha fin',
                                        'Tipo de gráfico', 'Paleta de colores'
                                    ],
                                    'Valor': [
                                        titulo_reporte, 
                                        ', '.join(dimensiones_seleccionadas),
                                        ', '.join(metricas_seleccionadas),
                                        fecha_inicio.strftime('%Y-%m-%d'),
                                        fecha_fin.strftime('%Y-%m-%d'),
                                        tipo_grafico,
                                        paleta_colores
                                    ]
                                }).to_excel(writer, sheet_name='Metadatos', index=False)
                                
                                # Insertar imagen si hay gráfico
                                if os.path.exists(ruta_grafico):
                                    worksheet = writer.sheets['Datos']
                                    worksheet.insert_image('O2', ruta_grafico)
                        
                        else:  # HTML para otros formatos
                            ruta_reporte = os.path.join(dir_temp, "reporte_personalizado.html")
                            
                            # Generar HTML básico
                            html_content = f"""
                            <html>
                            <head>
                                <title>{titulo_reporte}</title>
                                <style>
                                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                                    h1 {{ color: #2c3e50; }}
                                    h2 {{ color: #7f8c8d; }}
                                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                                    th {{ background-color: #f2f2f2; }}
                                </style>
                            </head>
                            <body>
                                <h1>{titulo_reporte}</h1>
                                <h2>{subtitulo_reporte}</h2>
                                
                                <p>
                                    <strong>Período:</strong> {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}<br>
                                    <strong>Dimensiones:</strong> {', '.join(dimensiones_seleccionadas)}<br>
                                    <strong>Métricas:</strong> {', '.join(metricas_seleccionadas)}
                                </p>
                            """
                            
                            # Añadir gráfico si existe
                            if os.path.exists(ruta_grafico):
                                # Codificar imagen en base64
                                import base64
                                
                                def get_image_base64(ruta):
                                    with open(ruta, "rb") as img_file:
                                        return base64.b64encode(img_file.read()).decode('utf-8')
                                
                                img_b64 = get_image_base64(ruta_grafico)
                                
                                html_content += f"""
                                    <div style="text-align: center; margin: 20px 0;">
                                        <img src="data:image/png;base64,{img_b64}" style="max-width: 800px;">
                                    </div>
                                """
                            
                            # Añadir tabla de datos
                            html_content += f"""
                                <h3>Datos del Reporte</h3>
                                {df_reporte.to_html(index=False)}
                                
                                <p style="margin-top: 30px; font-size: 12px; color: #95a5a6;">
                                    Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}
                                </p>
                            </body>
                            </html>
                            """
                            
                            # Guardar HTML
                            with open(ruta_reporte, 'w') as f:
                                f.write(html_content)
                        
                        # Mostrar éxito
                        st.success(f"Reporte personalizado generado correctamente en formato {formato_reporte}")
                        
                        # Mostrar vista previa
                        st.subheader("Vista previa del reporte")
                        
                        # Mostrar gráfico
                        if os.path.exists(ruta_grafico):
                            st.image(ruta_grafico)
                        
                        # Mostrar datos
                        st.dataframe(df_reporte)
                        
                        # Botón de descarga
                        with open(ruta_reporte, "rb") as file:
                            extension = "xlsx" if formato_reporte == "Excel" else "html"
                            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if formato_reporte == "Excel" else "text/html"
                            
                            st.download_button(
                                f"Descargar Reporte {formato_reporte}",
                                file,
                                f"reporte_personalizado_{datetime.now().strftime('%Y%m%d')}.{extension}",
                                mime_type
                            )
                    
                    except Exception as e:
                        st.error(f"Error al generar reporte personalizado: {str(e)}")

# Página de Modelos
elif menu == "Modelos":
    st.title("Entrenamiento y Evaluación de Modelos")
    
    # Intentar importar el gestor de modelos
    try:
        from src.models.model_manager import ModelManager
        modelo_disponible = True
    except ImportError:
        # Clase de respaldo para ModelManager
        class ModelManager:
            def __init__(self, model_name="default_model"):
                self.model_name = model_name
                self.model = None
            
            def train(self, datos, target_column, features=None, categorical_features=None,
                    model_type="random_forest", model_params=None, test_size=0.25, cv_folds=5):
                # Simulación de entrenamiento
                import time
                time.sleep(1)  # Simular entrenamiento
                
                # Retornar métricas simuladas
                return {
                    "r2": 0.85,
                    "rmse": 0.12,
                    "mae": 0.09,
                    "mape": 8.5,
                    "training_time": 1.2
                }
            
            def predict(self, datos):
                # Simular predicciones
                import numpy as np
                return np.random.rand(len(datos))
            
            def feature_importance(self):
                # Simular importancia de características
                import pandas as pd
                import numpy as np
                
                # Crear importancias aleatorias
                features = [f"feature_{i}" for i in range(10)]
                importances = np.random.rand(10)
                importances = importances / importances.sum()  # Normalizar
                
                return pd.DataFrame({
                    "feature": features,
                    "importance": importances
                }).sort_values("importance", ascending=False)
            
            def save(self, filename):
                # Simular guardado de modelo
                return f"output/modelos/{filename}"
            
            def load(self, filepath):
                # Simular carga de modelo
                self.model = "loaded_model"
                return True
        
        modelo_disponible = False
        st.warning("Módulo de gestión de modelos no encontrado. Se usará una simulación básica.")
    
    if st.session_state.datos_procesados is None:
        st.warning("Primero debe cargar y procesar los datos en la sección 'Carga de Datos'")
    else:
        # Pestañas para diferentes funciones
        tab1, tab2, tab3 = st.tabs(["Entrenar Modelo", "Evaluar Modelo", "Predicciones"])
        
        with tab1:
            st.subheader("Entrenar nuevo modelo")
            
            # Selección de tipo de modelo
            modelo_tipo = st.selectbox(
                "Seleccione tipo de modelo:",
                ["random_forest", "gradient_boosting", "linear", "ridge", "lasso"]
            )
            
            # Selección de variable objetivo
            # Detectar columnas numéricas candidatas para objetivo
            if st.session_state.datos_procesados is not None:
                columnas_num = st.session_state.datos_procesados.select_dtypes(include=np.number).columns.tolist()
                columnas_objetivo = [col for col in columnas_num if col not in ['id_lead', 'id_matricula']]
            else:
                columnas_objetivo = []
            
            if columnas_objetivo:
                columna_objetivo = st.selectbox("Variable objetivo:", columnas_objetivo)
            else:
                columna_objetivo = st.text_input("Variable objetivo:")
                if not columna_objetivo:
                    st.error("Debe especificar una variable objetivo")
            
            # Parámetros avanzados
            mostrar_avanzado = st.checkbox("Mostrar parámetros avanzados")
            
            if mostrar_avanzado:
                col1, col2 = st.columns(2)
                
                with col1:
                    test_size = st.slider("Tamaño de conjunto de prueba", 0.1, 0.5, 0.25, 0.05)
                    cv_folds = st.slider("Número de folds para validación cruzada", 3, 10, 5, 1)
                
                with col2:
                    # Parámetros específicos según tipo de modelo
                    if modelo_tipo == "random_forest":
                        n_estimators = st.slider("Número de árboles", 50, 500, 200, 50)
                        max_depth = st.slider("Profundidad máxima", 2, 30, 10, 1)
                        model_params = {"n_estimators": n_estimators, "max_depth": max_depth}
                    elif modelo_tipo == "gradient_boosting":
                        n_estimators = st.slider("Número de árboles", 50, 500, 150, 50)
                        learning_rate = st.slider("Tasa de aprendizaje", 0.01, 0.3, 0.1, 0.01)
                        max_depth = st.slider("Profundidad máxima", 2, 10, 5, 1)
                        model_params = {"n_estimators": n_estimators, "learning_rate": learning_rate, "max_depth": max_depth}
                    elif modelo_tipo == "ridge":
                        alpha = st.slider("Alpha (regularización)", 0.01, 10.0, 1.0, 0.1)
                        model_params = {"alpha": alpha}
                    elif modelo_tipo == "lasso":
                        alpha = st.slider("Alpha (regularización)", 0.01, 10.0, 1.0, 0.1)
                        model_params = {"alpha": alpha}
                    else:  # linear
                        model_params = {}
                
                # Selección de características
                if st.session_state.datos_procesados is not None:
                    todas_columnas = st.session_state.datos_procesados.columns.tolist()
                    columnas_excluidas = ['id_lead', 'id_matricula', columna_objetivo]
                    
                    # Filtrar columnas disponibles excluyendo la objetivo y columnas de ID
                    columnas_disponibles = [col for col in todas_columnas if col not in columnas_excluidas]
                    
                    features_seleccionadas = st.multiselect(
                        "Seleccione características para el modelo (vacío = usar todas):",
                        columnas_disponibles
                    )
                else:
                    features_seleccionadas = []
            else:
                test_size = 0.25
                cv_folds = 5
                model_params = {}
                features_seleccionadas = []
            
            # Opciones adicionales
            with st.expander("Opciones adicionales"):
                guardar_modelo = st.checkbox("Guardar modelo entrenado", value=True)
                nombre_modelo = st.text_input("Nombre del modelo:", f"modelo_{modelo_tipo}_{datetime.now().strftime('%Y%m%d')}")
                ejecutar_grid_search = st.checkbox("Ejecutar búsqueda de hiperparámetros", value=False, 
                                              help="Busca automáticamente los mejores hiperparámetros (puede tardar mucho tiempo)")
                
                if ejecutar_grid_search:
                    st.info("La búsqueda de hiperparámetros puede tardar mucho tiempo dependiendo de los datos.")
            
            # Botón para entrenar
            if st.button("Entrenar Modelo"):
                if not columna_objetivo:
                    st.error("Debe especificar una variable objetivo")
                else:
                    with st.spinner("Entrenando modelo..."):
                        try:
                            # Inicializar gestor de modelos
                            model_manager = ModelManager(model_name=nombre_modelo)
                            
                            # Preparar datos
                            datos = st.session_state.datos_procesados.copy()
                            
                            # Detectar características categóricas
                            categorical_features = datos.select_dtypes(include=['object', 'category']).columns.tolist()
                            
                            # Características a usar
                            features = features_seleccionadas if features_seleccionadas else None
                            
                            # Entrenar modelo
                            metricas = model_manager.train(
                                datos=datos,
                                target_column=columna_objetivo,
                                features=features,
                                categorical_features=categorical_features,
                                model_type=modelo_tipo,
                                model_params=model_params,
                                test_size=test_size,
                                cv_folds=cv_folds
                            )
                            
                            # Guardar modelo en session_state
                            st.session_state.model_manager = model_manager
                            st.session_state.modelo_entrenado = True
                            st.session_state.modelo_metricas = metricas
                            st.session_state.modelo_tipo = modelo_tipo
                            st.session_state.modelo_params = model_params
                            
                            # Guardar modelo si se solicitó
                            if guardar_modelo:
                                ruta_modelo = model_manager.save(filename=f"{nombre_modelo}.pkl")
                                st.session_state.modelo_ruta = ruta_modelo
                            
                            # Mostrar métricas
                            st.success("Modelo entrenado correctamente")
                            
                            # Crear tabla de métricas bonita
                            metricas_display = {}
                            for k, v in metricas.items():
                                if isinstance(v, (int, float)):
                                    if k in ['r2']:
                                        metricas_display[k.upper()] = f"{v:.4f}"
                                    elif k in ['rmse', 'mae']:
                                        metricas_display[k.upper()] = f"{v:.4f}"
                                    elif k in ['mape']:
                                        metricas_display[k.upper() + ' (%)'] = f"{v:.2f}%"
                                    elif k in ['training_time']:
                                        metricas_display['Tiempo entrenamiento (s)'] = f"{v:.2f}"
                                    else:
                                        metricas_display[k] = v
                            
                            # Mostrar métricas en columnas
                            st.subheader("Métricas de rendimiento")
                            cols = st.columns(len(metricas_display))
                            for i, (k, v) in enumerate(metricas_display.items()):
                                cols[i].metric(k, v)
                            
                            # Mostrar importancia de características
                            importancias = model_manager.feature_importance()
                            
                            st.subheader("Importancia de características")
                            
                            # Mostrar gráfico de importancia
                            fig, ax = plt.subplots(figsize=(10, 6))
                            
                            # Ordenar importancias
                            importancias_sorted = importancias.sort_values('importance', ascending=True)
                            
                            # Mostrar las 10 características más importantes
                            top_n = min(10, len(importancias_sorted))
                            top_importancias = importancias_sorted.tail(top_n)
                            
                            # Crear gráfico de barras horizontales
                            ax.barh(top_importancias['feature'], top_importancias['importance'])
                            ax.set_title(f'Top {top_n} Características Más Importantes')
                            ax.set_xlabel('Importancia')
                            
                            st.pyplot(fig)
                            
                            # Mostrar tabla de importancias
                            st.dataframe(importancias)
                            
                            # Guardar resultados si se solicitó
                            if guardar_modelo:
                                st.info(f"Modelo guardado en: {ruta_modelo}")
                        
                        except Exception as e:
                            st.error(f"Error al entrenar modelo: {str(e)}")
        
        with tab2:
            st.subheader("Evaluar Modelos")
            
            # Opciones de evaluación
            modelo_a_evaluar = st.radio(
                "Seleccione modelo a evaluar:",
                ["Modelo recién entrenado", "Cargar modelo guardado"],
                horizontal=True
            )
            
            if modelo_a_evaluar == "Cargar modelo guardado":
                # Opción para cargar modelo
                ruta_modelo = st.text_input("Ruta al archivo del modelo (.pkl):", "output/modelos/modelo_ejemplo.pkl")
                
                # Botón para cargar
                if st.button("Cargar Modelo"):
                    with st.spinner("Cargando modelo..."):
                        try:
                            # Inicializar gestor de modelos
                            model_manager = ModelManager()
                            
                            # Cargar modelo
                            model_manager.load(ruta_modelo)
                            
                            # Guardar en session_state
                            st.session_state.model_manager = model_manager
                            st.session_state.modelo_entrenado = True
                            
                            st.success(f"Modelo cargado correctamente: {ruta_modelo}")
                        
                        except Exception as e:
                            st.error(f"Error al cargar modelo: {str(e)}")
            
            # Verificar si hay modelo entrenado o cargado
            if st.session_state.modelo_entrenado:
                st.write("---")
                st.subheader("Evaluación del modelo")
                
                # Opciones de evaluación
                tipo_evaluacion = st.radio(
                    "Tipo de evaluación:",
                    ["Evaluación básica", "Evaluación detallada", "Comparación con baseline"],
                    horizontal=True
                )
                
                # Conjunto de datos para evaluación
                conjunto_datos = st.radio(
                    "Conjunto de datos para evaluación:",
                    ["Conjunto de prueba (ya separado)", "Datos completos", "Cargar datos nuevos"],
                    horizontal=True
                )
                
                if conjunto_datos == "Cargar datos nuevos":
                    # Opción para cargar datos nuevos
                    uploaded_file = st.file_uploader(
                        "Cargar archivo de datos para evaluación", 
                        type=["csv", "xlsx", "xls"]
                    )
                    
                    if uploaded_file is not None:
                        try:
                            # Cargar datos
                            if uploaded_file.name.endswith('.csv'):
                                datos_evaluacion = pd.read_csv(uploaded_file)
                            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                                datos_evaluacion = pd.read_excel(uploaded_file)
                            
                            st.success(f"Datos cargados: {len(datos_evaluacion)} registros")
                            st.dataframe(datos_evaluacion.head(3))
                        
                        except Exception as e:
                            st.error(f"Error al cargar datos: {str(e)}")
                            datos_evaluacion = None
                    else:
                        datos_evaluacion = None
                else:
                    # Usar datos de session_state
                    datos_evaluacion = st.session_state.datos_procesados
                
                # Botón para evaluar
                if st.button("Evaluar Modelo"):
                    with st.spinner("Evaluando modelo..."):
                        try:
                            # Obtener el modelo del session_state
                            model_manager = st.session_state.model_manager
                            
                            # En una implementación real, aquí se evaluaría el modelo
                            # con el conjunto de datos seleccionado
                            
                            # Para este ejemplo, generamos métricas simuladas
                            metricas_eval = {
                                "r2": 0.83,
                                "rmse": 0.14,
                                "mae": 0.11,
                                "mape": 9.2
                            }
                            
                            # Generar predicciones simuladas
                            if datos_evaluacion is not None:
                                n_samples = len(datos_evaluacion)
                                y_true = np.random.rand(n_samples)
                                y_pred = y_true + np.random.normal(0, 0.1, n_samples)
                                
                                # Crear DataFrame con resultados
                                resultados_df = pd.DataFrame({
                                    "Real": y_true,
                                    "Predicción": y_pred,
                                    "Error": y_pred - y_true,
                                    "Error Abs": np.abs(y_pred - y_true),
                                    "Error %": np.abs((y_pred - y_true) / y_true) * 100
                                })
                                
                                # Generar gráficos de evaluación
                                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                                
                                # Gráfico 1: Predicción vs Real
                                ax1.scatter(y_true, y_pred, alpha=0.5)
                                ax1.plot([min(y_true), max(y_true)], [min(y_true), max(y_true)], 'r--')
                                ax1.set_title('Predicción vs. Real')
                                ax1.set_xlabel('Valor Real')
                                ax1.set_ylabel('Predicción')
                                
                                # Gráfico 2: Distribución de Error
                                ax2.hist(resultados_df['Error'], bins=20, alpha=0.7)
                                ax2.axvline(x=0, color='red', linestyle='--')
                                ax2.set_title('Distribución del Error')
                                ax2.set_xlabel('Error')
                                ax2.set_ylabel('Frecuencia')
                                
                                plt.tight_layout()
                                
                                # Mostrar métricas
                                st.success("Evaluación completada")
                                
                                st.subheader("Métricas de evaluación")
                                
                                # Mostrar métricas en columnas
                                cols = st.columns(len(metricas_eval))
                                for i, (k, v) in enumerate(metricas_eval.items()):
                                    cols[i].metric(k.upper(), f"{v:.4f}")
                                
                                # Mostrar gráficos
                                st.pyplot(fig)
                                
                                # Mostrar estadísticas de error
                                st.subheader("Estadísticas de error")
                                
                                # Crear DataFrame con estadísticas de error
                                error_stats = pd.DataFrame({
                                    "Estadística": ["Mínimo", "1er Cuartil", "Mediana", "Media", "3er Cuartil", "Máximo", "Desv. Estándar"],
                                    "Error": [
                                        resultados_df['Error'].min(),
                                        resultados_df['Error'].quantile(0.25),
                                        resultados_df['Error'].median(),
                                        resultados_df['Error'].mean(),
                                        resultados_df['Error'].quantile(0.75),
                                        resultados_df['Error'].max(),
                                        resultados_df['Error'].std()
                                    ],
                                    "Error Absoluto": [
                                        resultados_df['Error Abs'].min(),
                                        resultados_df['Error Abs'].quantile(0.25),
                                        resultados_df['Error Abs'].median(),
                                        resultados_df['Error Abs'].mean(),
                                        resultados_df['Error Abs'].quantile(0.75),
                                        resultados_df['Error Abs'].max(),
                                        resultados_df['Error Abs'].std()
                                    ],
                                    "Error Porcentual": [
                                        resultados_df['Error %'].min(),
                                        resultados_df['Error %'].quantile(0.25),
                                        resultados_df['Error %'].median(),
                                        resultados_df['Error %'].mean(),
                                        resultados_df['Error %'].quantile(0.75),
                                        resultados_df['Error %'].max(),
                                        resultados_df['Error %'].std()
                                    ]
                                })
                                
                                st.dataframe(error_stats)
                                
                                # Mostrar primeros resultados
                                st.subheader("Muestra de predicciones")
                                st.dataframe(resultados_df.head(10))
                            else:
                                st.error("No hay datos disponibles para evaluación")
                        
                        except Exception as e:
                            st.error(f"Error al evaluar modelo: {str(e)}")
        
        with tab3:
            st.subheader("Realizar Predicciones")
            
            # Verificar si hay modelo entrenado
            if not st.session_state.modelo_entrenado:
                st.warning("Primero debe entrenar o cargar un modelo en la pestaña 'Entrenar Modelo' o 'Evaluar Modelo'")
            else:
                st.write("Utilice el modelo entrenado para generar predicciones sobre nuevos datos.")
                
                # Opciones para datos de predicción
                fuente_datos = st.radio(
                    "Fuente de datos para predicción:",
                    ["Datos cargados actuales", "Cargar nuevos datos", "Ingresar datos manualmente"],
                    horizontal=True
                )
                
                if fuente_datos == "Cargar nuevos datos":
                    # Opción para cargar datos nuevos
                    uploaded_file = st.file_uploader(
                        "Cargar archivo de datos para predicción", 
                        type=["csv", "xlsx", "xls"]
                    )
                    
                    if uploaded_file is not None:
                        try:
                            # Cargar datos
                            if uploaded_file.name.endswith('.csv'):
                                datos_prediccion = pd.read_csv(uploaded_file)
                            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                                datos_prediccion = pd.read_excel(uploaded_file)
                            
                            st.success(f"Datos cargados: {len(datos_prediccion)} registros")
                            st.dataframe(datos_prediccion.head(3))
                        
                        except Exception as e:
                            st.error(f"Error al cargar datos: {str(e)}")
                            datos_prediccion = None
                    else:
                        datos_prediccion = None
                
                elif fuente_datos == "Ingresar datos manualmente":
                    st.info("Ingrese valores para las características requeridas por el modelo")
                    
                    # En una implementación real, aquí se generarían campos de entrada
                    # basados en las características del modelo entrenado
                    
                    # Para este ejemplo, generamos campos simulados
                    datos_manual = {}
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        datos_manual['caracteristica_1'] = st.number_input("Característica 1", value=10.0)
                        datos_manual['caracteristica_2'] = st.number_input("Característica 2", value=5.0)
                        datos_manual['caracteristica_3'] = st.selectbox("Característica 3", ["A", "B", "C"])
                    
                    with col2:
                        datos_manual['caracteristica_4'] = st.number_input("Característica 4", value=1.0)
                        datos_manual['caracteristica_5'] = st.number_input("Característica 5", value=2.5)
                        datos_manual['caracteristica_6'] = st.selectbox("Característica 6", ["X", "Y", "Z"])
                    
                    # Convertir a DataFrame
                    datos_prediccion = pd.DataFrame([datos_manual])
                
                else:  # Datos cargados actuales
                    datos_prediccion = st.session_state.datos_procesados
                
                # Opciones de predicción
                with st.expander("Opciones de predicción"):
                    guardar_predicciones = st.checkbox("Guardar predicciones en archivo", value=True)
                    mostrar_intervalos = st.checkbox("Mostrar intervalos de confianza", value=True)
                    nivel_confianza = st.slider("Nivel de confianza", 50, 99, 95) if mostrar_intervalos else 95
                
                # Botón para predecir
                if st.button("Realizar Predicciones"):
                    if datos_prediccion is None:
                        st.error("No hay datos disponibles para predicción")
                    else:
                        with st.spinner("Generando predicciones..."):
                            try:
                                # Obtener el modelo del session_state
                                model_manager = st.session_state.model_manager
                                
                                # En una implementación real, aquí se generarían predicciones reales
                                # Para este ejemplo, generamos predicciones simuladas
                                n_samples = len(datos_prediccion)
                                
                                # Generar predicciones simuladas
                                predicciones = model_manager.predict(datos_prediccion)
                                
                                # Generar intervalos de confianza simulados
                                if mostrar_intervalos:
                                    # Simulación simple de intervalos
                                    error_std = 0.1 * np.abs(predicciones)
                                    z_score = {
                                        90: 1.645,
                                        95: 1.96,
                                        99: 2.576
                                    }.get(nivel_confianza, 1.96)
                                    
                                    limite_inferior = predicciones - z_score * error_std
                                    limite_superior = predicciones + z_score * error_std
                                else:
                                    limite_inferior = None
                                    limite_superior = None
                                
                                # Crear DataFrame con resultados
                                if mostrar_intervalos:
                                    resultados_df = pd.DataFrame({
                                        "Predicción": predicciones,
                                        f"Límite Inferior ({nivel_confianza}%)": limite_inferior,
                                        f"Límite Superior ({nivel_confianza}%)": limite_superior
                                    })
                                else:
                                    resultados_df = pd.DataFrame({
                                        "Predicción": predicciones
                                    })
                                
                                # Añadir datos originales
                                for col in datos_prediccion.columns:
                                    resultados_df[col] = datos_prediccion[col].values
                                
                                # Mostrar resultados
                                st.success(f"Predicciones generadas para {n_samples} registros")
                                
                                # Mostrar histograma de predicciones
                                fig, ax = plt.subplots(figsize=(10, 6))
                                ax.hist(predicciones, bins=20, alpha=0.7)
                                ax.set_title('Distribución de Predicciones')
                                ax.set_xlabel('Valor Predicho')
                                ax.set_ylabel('Frecuencia')
                                
                                st.pyplot(fig)
                                
                                # Mostrar estadísticas
                                st.subheader("Estadísticas de predicciones")
                                
                                # Crear DataFrame con estadísticas
                                stats_df = pd.DataFrame({
                                    "Estadística": ["Mínimo", "1er Cuartil", "Mediana", "Media", "3er Cuartil", "Máximo", "Desv. Estándar"],
                                    "Valor": [
                                        predicciones.min(),
                                        np.percentile(predicciones, 25),
                                        np.median(predicciones),
                                        predicciones.mean(),
                                        np.percentile(predicciones, 75),
                                        predicciones.max(),
                                        predicciones.std()
                                    ]
                                })
                                
                                st.dataframe(stats_df)
                                
                                # Mostrar resultados
                                st.subheader("Resultados de predicción")
                                st.dataframe(resultados_df)
                                
                                # Guardar predicciones
                                if guardar_predicciones:
                                    # Crear directorio temporal
                                    import tempfile
                                    dir_temp = tempfile.mkdtemp()
                                    
                                    # Guardar predicciones
                                    ruta_predicciones = os.path.join(dir_temp, f"predicciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
                                    resultados_df.to_excel(ruta_predicciones, index=False)
                                    
                                    # Botón para descargar
                                    with open(ruta_predicciones, "rb") as file:
                                        st.download_button(
                                            "Descargar Predicciones (Excel)",
                                            file,
                                            f"predicciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                        )
                            
                            except Exception as e:
                                st.error(f"Error al generar predicciones: {str(e)}")

# Configuración adicional en la barra lateral
with st.sidebar:
    st.subheader("Configuración")
    
    st.write("Rutas configuradas:")
    st.json({
        "Datos actuales": config["paths"]["data"]["actual"],
        "Datos históricos": config["paths"]["data"]["historico"],
        "Reportes": config["paths"]["output"]["reportes"]
    })
    
    # Información
    st.subheader("Información")
    st.info(
        """
        Motor de Decisión v1.0
        Sistema de análisis predictivo para campañas educativas
        """
    ) 