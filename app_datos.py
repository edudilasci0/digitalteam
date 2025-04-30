import streamlit as st
import pandas as pd
from pathlib import Path
import os
import yaml

# Cargar configuración
def get_config():
    config_path = Path("config/config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

# Configurar la página
st.set_page_config(
    page_title="Motor de Decisión - Team Digital",
    page_icon="📊",
    layout="wide"
)

st.title("Aplicación Motor de Decisión - Team Digital")

# Mostrar mensaje de bienvenida
st.write("Bienvenido al Motor de Decisión. Esta es una versión simplificada para probar.")

# Cargar configuración
config = get_config()

# Usar correctamente la configuración
st.subheader("Configuración actual")

# Mostrar información de rutas
st.write("Rutas configuradas:")
st.json({
    "Datos actuales": config["paths"]["data"]["actual"],
    "Datos históricos": config["paths"]["data"]["historico"],
    "Reportes": config["paths"]["output"]["reportes"]
})

# Formulario de carga de archivo
st.subheader("Cargar archivo de datos")
tipo_datos = st.radio(
    "Tipo de datos a cargar:",
    ["Leads", "Matrículas"],
    horizontal=True
)

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
        
        # Mostrar estadísticas básicas
        st.subheader("Estadísticas básicas")
        st.write(f"Número de filas: {len(df)}")
        st.write(f"Número de columnas: {len(df.columns)}")
        
    except Exception as e:
        st.error(f"Error al leer el archivo: {str(e)}")

# Botón de acción
if st.button("Procesar datos"):
    st.balloons()
    st.success("¡Datos procesados correctamente!")
    
# Información adicional
st.sidebar.title("Información")
st.sidebar.info(
    """
    Esta es una versión simplificada del Motor de Decisión.
    Para acceder a todas las funcionalidades, use la versión completa.
    """
) 