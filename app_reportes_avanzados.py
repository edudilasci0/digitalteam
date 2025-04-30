import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Asegurar que src sea accesible
sys.path.append('.')

# Importar módulos necesarios
try:
    from src.ui.reportes_avanzados import mostrar_ui_reportes_avanzados
except ImportError as e:
    st.error(f"Error al importar módulos: {str(e)}")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Motor de Decisión - Reportes Avanzados",
    page_icon="📊",
    layout="wide"
)

# Iniciar la interfaz de usuario
if __name__ == "__main__":
    mostrar_ui_reportes_avanzados() 