import os
import json
from pathlib import Path
from typing import Dict, Tuple
import datetime

import pandas as pd
import numpy as np
import streamlit as st
import joblib
from sklearn.ensemble import RandomForestRegressor

try:
    from fpdf import FPDF  # generación rápida de PDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# PowerPoint export
try:
    from pptx import Presentation
    from pptx.util import Inches
    PPT_AVAILABLE = True
except ImportError:
    PPT_AVAILABLE = False

# Estilos CSS para mejorar la interfaz
CUSTOM_CSS = """
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stMetric {
        background-color: #f0f5ff;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #1E3A8A;
    }
    .stAlert {
        border-radius: 4px;
    }
    /* Mejora de barras de progreso en textos */
    pre {
        font-size: 1.2em !important;
    }
    .css-1kyxreq {
        justify-content: center;
    }
</style>
"""

# ============================================================
# Configuración global de Streamlit
# ============================================================

st.set_page_config(
    page_title="Motor de Decisión Educativo",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# Utilidades de gestión de marcas y datos
# ============================================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

REPORTE_DIR_NAME = "reportes"
PLAN_FILE = "plan_actual.csv"
HIST_FILE = "historico.csv"
MODEL_FILE = "modelo_rf.joblib"

# Versión del sistema
VERSION = "1.0.0"

# Tooltip ayudas contextuales
TOOLTIPS = {
    "cpa": "CPA (Costo Por Adquisición) es el costo promedio de obtener una matrícula.",
    "cpl": "CPL (Costo Por Lead) es el costo promedio de obtener un lead potencial.",
    "leads": "Prospecto interesado en un programa educativo.",
    "prediccion_ml": "Predicción basada en Machine Learning (RandomForest) con intervalos de confianza.",
    "anomalia": "Valor que se desvía significativamente del resto (> 3 desviaciones estándar)."
}

def get_brand_path(brand: str) -> Path:
    """Devuelve la ruta del directorio de la marca y lo crea si no existe."""
    brand_path = DATA_DIR / brand
    brand_path.mkdir(exist_ok=True)
    (brand_path / REPORTE_DIR_NAME).mkdir(exist_ok=True)
    return brand_path


def save_dataframe(df: pd.DataFrame, path: Path):
    """Guarda un DataFrame en CSV."""
    df.to_csv(path, index=False)


def load_dataframe(path: Path) -> pd.DataFrame:
    """Carga un CSV a DataFrame, si existe."""
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


# ============================================================
# Funciones de Machine Learning
# ============================================================

def train_or_load_model(df_hist: pd.DataFrame, brand_path: Path):
    """Entrena un modelo RandomForest o carga uno existente."""
    model_path = brand_path / MODEL_FILE
    
    # Si no hay suficientes datos, no se puede entrenar un modelo
    if len(df_hist) < 10 or "leads" not in df_hist.columns or "matriculas" not in df_hist.columns:
        return None
    
    # Si ya existe un modelo, cargarlo
    if model_path.exists():
        try:
            return joblib.load(model_path)
        except Exception as e:
            st.warning(f"Error al cargar modelo existente: {str(e)}")
    
    # Entrenar un nuevo modelo
    try:
        X = df_hist[["leads", "inversion"]]
        y = df_hist["matriculas"]
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Guardar el modelo
        joblib.dump(model, model_path)
        return model
    except Exception as e:
        st.warning(f"Error al entrenar modelo: {str(e)}")
        return None


def predict_matriculas_interval(model, df_future: pd.DataFrame, 
                              confidence_level: float = 0.95) -> Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """
    Realiza predicciones y genera intervalos de confianza.
    
    Args:
        model: Modelo RandomForest entrenado
        df_future: DataFrame con columnas 'leads' e 'inversion'
        confidence_level: Nivel de confianza para el intervalo (0-1)
        
    Returns:
        Tupla con (predicciones, (límite_inferior, límite_superior))
    """
    if model is None:
        return np.zeros(len(df_future)), (np.zeros(len(df_future)), np.zeros(len(df_future)))
    
    X_future = df_future[["leads", "inversion"]]
    
    # Predicción central
    preds = model.predict(X_future)
    
    # Calcular intervalos usando los árboles individuales del RandomForest
    tree_preds = np.array([tree.predict(X_future) for tree in model.estimators_])
    
    # Desviación estándar basada en predicciones de árboles individuales
    std_dev = np.std(tree_preds, axis=0)
    
    # Factor z para el nivel de confianza (aproximación)
    z = 1.96  # para 95% de confianza
    
    lower_bound = preds - z * std_dev
    upper_bound = preds + z * std_dev
    
    # Asegurar que los límites no sean negativos
    lower_bound = np.maximum(lower_bound, 0)
    
    return preds, (lower_bound, upper_bound)

# ============================================================
# UI auxiliar
# ============================================================


def sidebar_brand_selector() -> str:
    """Permite seleccionar o crear una marca desde la barra lateral."""
    st.sidebar.header("🎯 Selección de marca")
    existing_brands = [d.name for d in DATA_DIR.iterdir() if d.is_dir()]

    if "current_brand" not in st.session_state:
        st.session_state.current_brand = existing_brands[0] if existing_brands else ""

    brand_option = st.sidebar.selectbox(
        "Marca", options=["<Nueva marca>"] + existing_brands, index=0 if not existing_brands else existing_brands.index(st.session_state.current_brand) + 1
    )

    if brand_option == "<Nueva marca>":
        new_brand = st.sidebar.text_input("Nombre de la nueva marca")
        if new_brand:
            st.session_state.current_brand = new_brand.strip()
    else:
        st.session_state.current_brand = brand_option

    return st.session_state.current_brand


# ============================================================
# Lógica de carga de datos
# ============================================================


def load_data_ui(brand: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Interfaz para cargar datos históricos y de la convocatoria actual."""
    st.subheader("📥 Carga de datos")

    # Permitir seleccionar marcas predefinidas
    marcas_predefinidas = ["GR", "PR", "WZ", "ADV", "UNISUD", "AJA"]
    if brand not in marcas_predefinidas and st.checkbox("Usar una marca predefinida"):
        brand = st.selectbox("Seleccionar marca:", marcas_predefinidas)
        st.session_state.current_brand = brand

    brand_path = get_brand_path(brand)

    # Configurar camino de archivos
    plan_path = brand_path / PLAN_FILE
    hist_path = brand_path / HIST_FILE
    leads_path = brand_path / "leads_actual.csv"
    matriculas_path = brand_path / "matriculas_actual.csv"
    inversion_path = brand_path / "inversion_actual.csv"

    # Configuración de la convocatoria
    st.subheader("⚙️ Configuración de convocatoria")
    col1, col2, col3 = st.columns(3)
    with col1:
        semana_actual = st.number_input("Semana actual del año:", min_value=1, max_value=52, value=datetime.datetime.now().isocalendar()[1])
    with col2:
        duracion_convocatoria = st.number_input("Duración total (semanas):", min_value=1, max_value=26, value=13)
    with col3:
        semanas_restantes = st.number_input("Semanas restantes:", min_value=0, max_value=26, value=max(0, duracion_convocatoria - (datetime.datetime.now().isocalendar()[1] % duracion_convocatoria)))
    
    # Guardar configuración en session_state
    if "config_convocatoria" not in st.session_state:
        st.session_state.config_convocatoria = {}
    
    st.session_state.config_convocatoria = {
        "semana_actual": semana_actual,
        "duracion_convocatoria": duracion_convocatoria,
        "semanas_restantes": semanas_restantes,
        "progreso": (duracion_convocatoria - semanas_restantes) / duracion_convocatoria
    }

    # Sección de carga de archivos - 3 pestañas para diferentes tipos de datos
    tabs = st.tabs(["Datos Históricos", "Convocatoria Actual", "Planificación"])
    
    # Tab 1: Datos Históricos
    with tabs[0]:
        st.markdown("### Datos Históricos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Leads Históricos**")
            if (brand_path / "leads_historico.csv").exists():
                df_leads_hist = load_dataframe(brand_path / "leads_historico.csv")
                st.success(f"Leads históricos cargados: {len(df_leads_hist)} registros")
                st.dataframe(df_leads_hist.head(3))
            else:
                st.info("No hay leads históricos cargados")
            
            leads_hist_file = st.file_uploader("Subir archivo de leads históricos", type=["csv"], key="leads_hist")
            if leads_hist_file is not None:
                df_leads_hist = pd.read_csv(leads_hist_file)
                save_dataframe(df_leads_hist, brand_path / "leads_historico.csv")
                st.success(f"Leads históricos guardados: {len(df_leads_hist)} registros")
            
            # Ejemplo de leads
            ejemplo_leads = Path("datos/plantillas/ejemplo_leads.csv")
            if ejemplo_leads.exists():
                with open(ejemplo_leads, "r") as f:
                    st.download_button(
                        label="Ejemplo de leads",
                        data=f,
                        file_name="ejemplo_leads.csv",
                        mime="text/csv",
                        help="Descarga un archivo CSV de ejemplo de leads",
                        key="leads_hist_ejemplo"
                    )
        
        with col2:
            st.markdown("**Matrículas Históricas**")
            if (brand_path / "matriculas_historico.csv").exists():
                df_mats_hist = load_dataframe(brand_path / "matriculas_historico.csv")
                st.success(f"Matrículas históricas cargadas: {len(df_mats_hist)} registros")
                st.dataframe(df_mats_hist.head(3))
            else:
                st.info("No hay matrículas históricas cargadas")
            
            mats_hist_file = st.file_uploader("Subir archivo de matrículas históricas", type=["csv"], key="mats_hist")
            if mats_hist_file is not None:
                df_mats_hist = pd.read_csv(mats_hist_file)
                save_dataframe(df_mats_hist, brand_path / "matriculas_historico.csv")
                st.success(f"Matrículas históricas guardadas: {len(df_mats_hist)} registros")
            
            # Ejemplo de matrículas
            ejemplo_mats = Path("datos/plantillas/ejemplo_matriculas.csv")
            if ejemplo_mats.exists():
                with open(ejemplo_mats, "r") as f:
                    st.download_button(
                        label="Ejemplo de matrículas",
                        data=f,
                        file_name="ejemplo_matriculas.csv",
                        mime="text/csv",
                        help="Descarga un archivo CSV de ejemplo de matrículas",
                        key="mats_hist_ejemplo"
                    )
        
        st.markdown("**Inversión Histórica**")
        if (brand_path / "inversion_historico.csv").exists():
            df_inv_hist = load_dataframe(brand_path / "inversion_historico.csv")
            st.success(f"Inversión histórica cargada: {len(df_inv_hist)} registros")
            st.dataframe(df_inv_hist.head(3))
        else:
            st.info("No hay datos de inversión histórica cargados")
        
        inv_hist_file = st.file_uploader("Subir archivo de inversión histórica", type=["csv"], key="inv_hist")
        if inv_hist_file is not None:
            df_inv_hist = pd.read_csv(inv_hist_file)
            save_dataframe(df_inv_hist, brand_path / "inversion_historico.csv")
            st.success(f"Inversión histórica guardada: {len(df_inv_hist)} registros")
        
        # Ejemplo de inversión
        ejemplo_inv = Path("datos/plantillas/ejemplo_inversion.csv")
        if ejemplo_inv.exists():
            with open(ejemplo_inv, "r") as f:
                st.download_button(
                    label="Ejemplo de inversión",
                    data=f,
                    file_name="ejemplo_inversion.csv",
                    mime="text/csv",
                    help="Descarga un archivo CSV de ejemplo de inversión",
                    key="inv_hist_ejemplo"
                )
    
    # Tab 2: Convocatoria Actual
    with tabs[1]:
        st.markdown("### Datos de Convocatoria Actual")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Leads Actuales**")
            if leads_path.exists():
                df_leads_act = load_dataframe(leads_path)
                st.success(f"Leads actuales cargados: {len(df_leads_act)} registros")
                st.dataframe(df_leads_act.head(3))
            else:
                df_leads_act = pd.DataFrame()
                st.info("No hay leads actuales cargados")
            
            leads_file = st.file_uploader("Subir archivo de leads actuales", type=["csv"], key="leads_act")
            if leads_file is not None:
                df_leads_act = pd.read_csv(leads_file)
                save_dataframe(df_leads_act, leads_path)
                st.success(f"Leads actuales guardados: {len(df_leads_act)} registros")
        
        with col2:
            st.markdown("**Matrículas Actuales**")
            if matriculas_path.exists():
                df_mats_act = load_dataframe(matriculas_path)
                st.success(f"Matrículas actuales cargadas: {len(df_mats_act)} registros")
                st.dataframe(df_mats_act.head(3))
            else:
                df_mats_act = pd.DataFrame()
                st.info("No hay matrículas actuales cargadas")
            
            mats_file = st.file_uploader("Subir archivo de matrículas actuales", type=["csv"], key="mats_act")
            if mats_file is not None:
                df_mats_act = pd.read_csv(mats_file)
                save_dataframe(df_mats_act, matriculas_path)
                st.success(f"Matrículas actuales guardadas: {len(df_mats_act)} registros")
        
        st.markdown("**Inversión Actual**")
        if inversion_path.exists():
            df_inv_act = load_dataframe(inversion_path)
            st.success(f"Inversión actual cargada: {len(df_inv_act)} registros")
            st.dataframe(df_inv_act.head(3))
        else:
            df_inv_act = pd.DataFrame()
            st.info("No hay datos de inversión actual cargados")
        
        inv_file = st.file_uploader("Subir archivo de inversión actual", type=["csv"], key="inv_act")
        if inv_file is not None:
            df_inv_act = pd.read_csv(inv_file)
            save_dataframe(df_inv_act, inversion_path)
            st.success(f"Inversión actual guardada: {len(df_inv_act)} registros")
            
        # Ejemplo de inversión
        ejemplo_inv = Path("datos/plantillas/ejemplo_inversion.csv")
        if ejemplo_inv.exists():
            with open(ejemplo_inv, "r") as f:
                st.download_button(
                    label="Ejemplo de inversión",
                    data=f,
                    file_name="ejemplo_inversion.csv",
                    mime="text/csv",
                    help="Descarga un archivo CSV de ejemplo de inversión",
                    key="inv_act_ejemplo"
                )
    
    # Tab 3: Planificación
    with tabs[2]:
        st.markdown("### Planificación")
        
        if plan_path.exists():
            df_plan = load_dataframe(plan_path)
            st.success("Planificación cargada")
            st.dataframe(df_plan.head())
        else:
            df_plan = pd.DataFrame()
            st.info("No hay planificación cargada")

        plan_file = st.file_uploader("Subir planificación CSV", type=["csv"], key="plan")
        
        # Añadir ejemplo descargable para planificación
        ejemplo_plan = Path("datos/plantillas/ejemplo_planificacion.csv")
        if ejemplo_plan.exists():
            with open(ejemplo_plan, "r") as f:
                st.download_button(
                    label="Descargar ejemplo de planificación",
                    data=f,
                    file_name="ejemplo_planificacion.csv",
                    mime="text/csv",
                    help="Descarga un archivo CSV de ejemplo para subir como planificación",
                    key="plan_ejemplo"
                )
        
        if plan_file is not None:
            df_plan = pd.read_csv(plan_file)
            save_dataframe(df_plan, plan_path)
            st.success("Planificación guardada correctamente")
    
    # Generar DataFrame histórico combinado para compatibilidad con funciones existentes
    df_hist = pd.DataFrame()
    
    # Si tenemos datos actuales, combinarlos
    if 'df_leads_act' in locals() and not df_leads_act.empty and 'df_mats_act' in locals() and not df_mats_act.empty:
        # Número de leads
        if 'fecha_creacion' in df_leads_act.columns:
            leads_por_fecha = df_leads_act.groupby('fecha_creacion').size().reset_index(name='leads')
            leads_por_fecha.rename(columns={'fecha_creacion': 'fecha'}, inplace=True)
            
            # Número de matrículas
            if 'fecha_matricula' in df_mats_act.columns:
                mats_por_fecha = df_mats_act.groupby('fecha_matricula').size().reset_index(name='matriculas')
                mats_por_fecha.rename(columns={'fecha_matricula': 'fecha'}, inplace=True)
                
                # Combinar
                df_hist = pd.merge(leads_por_fecha, mats_por_fecha, on='fecha', how='outer').fillna(0)
                
                # Agregar inversión si existe
                if 'df_inv_act' in locals() and not df_inv_act.empty and 'fecha' in df_inv_act.columns and 'monto' in df_inv_act.columns:
                    df_hist = pd.merge(df_hist, df_inv_act[['fecha', 'monto']], on='fecha', how='left')
                    df_hist.rename(columns={'monto': 'inversion'}, inplace=True)
                    df_hist['inversion'].fillna(0, inplace=True)
    
    # Si no tenemos datos actuales pero sí históricos, usar esos
    elif hist_path.exists():
        df_hist = load_dataframe(hist_path)
    
    # Guardar el DataFrame combinado para compatibilidad
    if not df_hist.empty:
        save_dataframe(df_hist, hist_path)

    return df_plan, df_hist


# ============================================================
# Reportes
# ============================================================


def calcular_metricas_estrategicas(df_plan: pd.DataFrame, df_hist: pd.DataFrame) -> Dict:
    """Calcula métricas clave para el reporte estratégico."""
    if df_plan.empty or df_hist.empty:
        return {}

    total_inv = df_hist["inversion"].sum()
    total_leads = df_hist["leads"].sum()
    total_mats = df_hist["matriculas"].sum()

    cpa = total_inv / total_mats if total_mats else np.nan
    cpl = total_inv / total_leads if total_leads else np.nan

    progreso_leads = total_leads / df_plan["leads_estimados"].iloc[0] if "leads_estimados" in df_plan.columns else np.nan
    progreso_mats = total_mats / df_plan["objetivo_matriculas"].iloc[0] if "objetivo_matriculas" in df_plan.columns else np.nan

    return {
        "CPA": cpa,
        "CPL": cpl,
        "Progreso Leads": progreso_leads,
        "Progreso Matriculas": progreso_mats,
    }


def show_help(key):
    """Muestra un tooltip de ayuda contextual."""
    st.info(TOOLTIPS.get(key, "Información no disponible"))


def reporte_estrategico_ui(df_plan: pd.DataFrame, df_hist: pd.DataFrame):
    st.header("📊 Reporte Estratégico de Marketing")

    if df_plan.empty or df_hist.empty:
        st.warning("Cargue planificación e histórico para generar el reporte.")
        return

    # Obtener configuración de la convocatoria
    config = st.session_state.get("config_convocatoria", {
        "semana_actual": datetime.datetime.now().isocalendar()[1],
        "duracion_convocatoria": 13,
        "semanas_restantes": 7,
        "progreso": 0.5
    })
    
    # Calcular métricas estratégicas
    metricas = calcular_metricas_estrategicas(df_plan, df_hist)

    # Mostrar información de la convocatoria
    st.subheader("Información de la convocatoria")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Semana actual", f"{config['semana_actual']} de {config['duracion_convocatoria']}")
    col2.metric("Semanas restantes", f"{config['semanas_restantes']}")
    col3.metric("Progreso", f"{config['progreso']*100:.1f}%")
    
    # Calcular días transcurridos para reportes
    dias_transcurridos = int(config['progreso'] * config['duracion_convocatoria'] * 7)  # Aproximado en días
    tiempo_total = config['duracion_convocatoria'] * 7  # Total en días
    col4.metric("Días", f"{dias_transcurridos} de {tiempo_total}")

    # Métricas principales
    st.subheader("Métricas principales")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CPA", f"${metricas['CPA']:.2f}")
    col2.metric("CPL", f"${metricas['CPL']:.2f}")
    col3.metric("Progreso Leads", f"{metricas['Progreso Leads']*100:.1f}%")
    col4.metric("Progreso Matrículas", f"{metricas['Progreso Matriculas']*100:.1f}%")

    # ======================================================
    # 1. Comparativa de plataformas (CPA y Conversión)
    # ======================================================
    st.subheader("Comparativa de plataformas")

    if "canal" in df_hist.columns and "matriculas" in df_hist.columns and "inversion" in df_hist.columns:
        # Calcular CPA por canal
        df_canales = df_hist.groupby("canal").agg({
            "matriculas": "sum",
            "inversion": "sum",
            "leads": "sum"
        }).reset_index()
        
        # Evitar división por cero
        df_canales["cpa"] = df_canales.apply(
            lambda row: row["inversion"] / row["matriculas"] if row["matriculas"] > 0 else 0, 
            axis=1
        )
        
        df_canales["conversion"] = df_canales.apply(
            lambda row: row["matriculas"] / row["leads"] if row["leads"] > 0 else 0, 
            axis=1
        )
        
        cpa_canal = df_canales.set_index("canal")["cpa"].sort_values()
        conv_canal = df_canales.set_index("canal")["conversion"].sort_values(ascending=False)
        
        st.subheader("CPA por canal")
        st.bar_chart(cpa_canal, use_container_width=True)

        st.subheader("Conversión por canal")
        st.bar_chart(conv_canal, use_container_width=True)
    
    elif "canal" in df_hist.columns and "cpa" in df_hist.columns:
        cpa_canal = df_hist.groupby("canal")["cpa"].mean().sort_values()
        st.bar_chart(cpa_canal, use_container_width=True)

    if "canal" in df_hist.columns and "conversion" in df_hist.columns:
        conv_canal = df_hist.groupby("canal")["conversion"].mean().sort_values()
        st.bar_chart(conv_canal, use_container_width=True)

    # ======================================================
    # 2. Curva de avance: Leads, Matrículas, Inversión
    # ======================================================
    st.subheader("Curva de avance")
    if "fecha" in df_hist.columns:
        df_hist["fecha"] = pd.to_datetime(df_hist["fecha"])
        df_curve = df_hist.sort_values("fecha").set_index("fecha")[[c for c in ["leads", "matriculas", "inversion"] if c in df_hist.columns]]
        st.line_chart(df_curve)
    else:
        st.info("No se encontró la columna 'fecha' para generar curvas.")

    # ======================================================
    # 3. Escenarios simulados basados en tiempo restante
    # ======================================================
    st.subheader("Escenarios simulados")

    # Calcular valores base usando tiempo y configuración
    ratio_tiempo = config['progreso']  # Progreso de tiempo
    
    # Leads y matrículas actuales
    leads_actuales = df_hist["leads"].sum() if "leads" in df_hist.columns else 0
    mats_actuales = df_hist["matriculas"].sum() if "matriculas" in df_hist.columns else 0
    
    # Proyecciones finales (proporcionales al tiempo restante)
    base_leads = leads_actuales / ratio_tiempo if ratio_tiempo > 0 else 0
    base_mats = mats_actuales / ratio_tiempo if ratio_tiempo > 0 else 0
    
    # Objetivos
    leads_obj = df_plan["leads_estimados"].iloc[0] if "leads_estimados" in df_plan.columns else 0
    mats_obj = df_plan["objetivo_matriculas"].iloc[0] if "objetivo_matriculas" in df_plan.columns else 0
    
    # Ratio de conversión actual
    ratio_conversion = mats_actuales / leads_actuales if leads_actuales > 0 else 0
    
    # Proyecciones de escenarios
    escenarios = pd.DataFrame({
        "Escenario": ["Actual", "Mejora 5% conversión", "Aumento +20% inversión"],
        "Leads estimados": [base_leads, base_leads, base_leads*1.2],
        "Matrículas estimadas": [base_mats, base_mats*1.05, base_mats*1.2],
        "% Objetivo": [
            f"{(base_mats/mats_obj)*100:.1f}%" if mats_obj > 0 else "N/A", 
            f"{(base_mats*1.05/mats_obj)*100:.1f}%" if mats_obj > 0 else "N/A", 
            f"{(base_mats*1.2/mats_obj)*100:.1f}%" if mats_obj > 0 else "N/A"
        ],
        "Descripción": [
            "Mantener ritmo actual", 
            "Incremento de conversión en 5% con misma inversión", 
            "Aumentar inversión total 20% manteniendo conversión"
        ]
    })
    st.table(escenarios)

    # ======================================================
    # 4. Predicción ML considerando semanas restantes
    # ======================================================
    cols = st.columns([3, 1])
    cols[0].subheader("Predicción ML de matrículas para próximas semanas")
    if cols[1].button("❓ Ayuda ML", key="help_ml"):
        show_help("prediccion_ml")

    # Usar el número real de semanas restantes para la predicción
    semanas_restantes = config["semanas_restantes"]
    
    brand_path = get_brand_path(st.session_state.current_brand)
    model = train_or_load_model(df_hist, brand_path)
    if model is not None and "leads" in df_hist.columns and "inversion" in df_hist.columns:
        # Crear df_future con promedio de leads e inversión de últimas 4 semanas o todos los disponibles
        avg_leads = df_hist["leads"].tail(min(4, len(df_hist))).mean()
        avg_inv = df_hist["inversion"].tail(min(4, len(df_hist))).mean()
        
        # Usar el número de semanas restantes para la predicción (máx 6 semanas)
        num_semanas_pred = min(6, semanas_restantes)
        
        if num_semanas_pred > 0:
            semanas = pd.DataFrame({
                "leads": [avg_leads] * num_semanas_pred,
                "inversion": [avg_inv] * num_semanas_pred,
                "semana": list(range(1, num_semanas_pred + 1))
            })
            preds, (low, up) = predict_matriculas_interval(model, semanas)
            df_pred = pd.DataFrame({
                "Semana +": list(range(1, num_semanas_pred + 1)),
                "Predicción": preds.astype(int),
                "IC Inferior": low.astype(int),
                "IC Superior": up.astype(int)
            })
            st.dataframe(df_pred)
        else:
            st.info("No quedan semanas restantes para predecir.")
    else:
        st.info("Modelo predictivo no disponible: cargue columnas leads, inversion y matriculas suficientes.")

    # ======================================================
    # 5. Alertas automáticas basadas en tiempo restante
    # ======================================================
    st.subheader("Alertas destacadas")
    
    # Verificar CPA alto
    if metricas["CPA"] > 50:
        st.error("CPA alto: revise campañas menos eficientes.")
    
    # Verificar progreso considerando tiempo restante
    progreso_leads = metricas["Progreso Leads"]
    tiempo_usado = config["progreso"]
    
    # Verificar si el progreso de leads está por debajo del progreso de tiempo
    if progreso_leads < tiempo_usado * 0.8:
        st.warning(f"Ritmo bajo de generación de leads ({progreso_leads*100:.1f}% completado vs {tiempo_usado*100:.1f}% de tiempo usado).")
    
    # Verificar canales ineficientes
    if "cpa_canal" in locals():
        inefficient = cpa_canal[cpa_canal > metricas["CPA"] * 1.2]
        for canal, val in inefficient.items():
            st.warning(f"Canal ineficiente: {canal} (CPA ${val:.2f})")
    
    # Alerta por tiempo restante limitado
    if semanas_restantes <= 4 and metricas["Progreso Matriculas"] < 0.6:
        st.error(f"¡URGENTE! Quedan solo {semanas_restantes} semanas y se ha alcanzado solo el {metricas['Progreso Matriculas']*100:.1f}% del objetivo de matrículas.")

    # ======================================================
    # 6. Exportación a PDF
    # ======================================================
    if PDF_AVAILABLE:
        if st.button("Descargar PDF resumen", key="pdf_estrategico"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Reporte Estratégico", ln=True, align="C")
            pdf.ln(5)
            pdf.cell(0, 10, txt=f"Marca: {st.session_state.current_brand}", ln=True)
            pdf.cell(0, 10, txt=f"Semana: {config['semana_actual']} de {config['duracion_convocatoria']} (Restantes: {config['semanas_restantes']})", ln=True)
            for k, v in metricas.items():
                pdf.cell(0, 10, txt=f"{k}: {v}", ln=True)
            pdf_output = pdf.output(dest="S").encode("latin-1")
            st.download_button("PDF", data=pdf_output, file_name="reporte_estrategico.pdf", mime="application/pdf", key="pdf_estrategico")
    else:
        st.info("Instale 'fpdf' para exportar PDF.")

    # 7. Exportación a PowerPoint
    if PPT_AVAILABLE:
        if st.button("Descargar PowerPoint resumen", key="pptx_estrategico"):
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[0])
            title = slide.shapes.title
            subtitle = slide.placeholders[1]
            title.text = "Reporte Estratégico"
            subtitle.text = f"Marca: {st.session_state.current_brand} - Semana {config['semana_actual']} de {config['duracion_convocatoria']}"

            # Segunda diapositiva métricas
            slide2 = prs.slides.add_slide(prs.slide_layouts[1])
            slide2.shapes.title.text = "Métricas clave"
            body = slide2.shapes.placeholders[1].text_frame
            for k, v in metricas.items():
                body.add_paragraph().text = f"{k}: {v:.2f}"

            from io import BytesIO
            ppt_buffer = BytesIO()
            prs.save(ppt_buffer)
            ppt_buffer.seek(0)
            st.download_button("PPTX", data=ppt_buffer, file_name="reporte_estrategico.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation", key="pptx_estrategico")
    else:
        st.info("Instale 'python-pptx' para exportar PowerPoint.")


def reporte_comercial_ui(df_plan: pd.DataFrame, df_hist: pd.DataFrame):
    st.header("📊 Reporte Comercial (Status Semanal)")

    if df_plan.empty or df_hist.empty:
        st.warning("Cargue planificación e histórico para generar el reporte.")
        return

    # Obtener configuración de la convocatoria
    config = st.session_state.get("config_convocatoria", {
        "semana_actual": datetime.datetime.now().isocalendar()[1],
        "duracion_convocatoria": 13,
        "semanas_restantes": 7,
        "progreso": 0.5
    })
    
    semana_actual = config["semana_actual"]
    duracion_total = config["duracion_convocatoria"]
    semanas_restantes = config["semanas_restantes"]
    progreso = config["progreso"]

    # Fechas
    if "fecha" in df_hist.columns:
        df_hist["fecha"] = pd.to_datetime(df_hist["fecha"])
        fecha_min, fecha_max = df_hist["fecha"].min(), df_hist["fecha"].max()
        dias_transcurridos = (fecha_max - fecha_min).days + 1
    else:
        dias_transcurridos = int(progreso * duracion_total * 7)  # Aproximado en días

    # Objetivos
    tiempo_total = duracion_total * 7  # Días totales de la convocatoria
    leads_obj = df_plan["leads_estimados"].iloc[0] if "leads_estimados" in df_plan.columns else 0
    mats_obj = df_plan["objetivo_matriculas"].iloc[0] if "objetivo_matriculas" in df_plan.columns else 0

    # Valores actuales
    leads_actuales = df_hist["leads"].sum() if "leads" in df_hist.columns else 0
    mats_actuales = df_hist["matriculas"].sum() if "matriculas" in df_hist.columns else 0

    # Información de la convocatoria
    st.subheader("Información de la convocatoria")
    col1, col2, col3 = st.columns(3)
    col1.metric("Semana actual", f"{semana_actual} de {duracion_total}")
    col2.metric("Semanas restantes", f"{semanas_restantes}")
    col3.metric("Progreso", f"{progreso*100:.1f}%")

    # Barras de progreso
    st.subheader("Progreso de la convocatoria")
    def barra(texto, valor, total):
        pct = int(100 * valor / total) if total else 0
        bar = "▓" * (pct // 10) + "░" * (10 - pct // 10)
        st.write(f"{texto:<25} {bar} {pct}%")

    barra("Tiempo transcurrido", dias_transcurridos, tiempo_total)
    barra("Leads entregados", leads_actuales, leads_obj)
    barra("Matrículas confirmadas", mats_actuales, mats_obj)

    # Proyección simple lineal basada en el tiempo transcurrido
    ratio_tiempo = progreso  # Progreso de tiempo
    ratio_conversión = mats_actuales / leads_actuales if leads_actuales > 0 else 0
    
    # Proyección de leads
    proy_leads_final = leads_actuales / ratio_tiempo if ratio_tiempo > 0 else 0
    
    # Proyección de matrículas basada en proyección de leads y ratio de conversión
    proy_mats_por_leads = proy_leads_final * ratio_conversión
    
    # Proyección de matrículas basada en ritmo actual
    proy_mats_por_tiempo = mats_actuales / ratio_tiempo if ratio_tiempo > 0 else 0
    
    # Proyección final (promedio de ambos métodos)
    proy_final = (proy_mats_por_leads + proy_mats_por_tiempo) / 2
    
    # Intervalo de confianza usando tiempo restante
    margen_error = proy_final * (semanas_restantes / duracion_total) * 0.2  # Margen de error proporcional al tiempo restante
    ic_lower = max(0, proy_final - margen_error)
    ic_upper = proy_final + margen_error
    
    col1, col2 = st.columns([3, 1])
    col1.metric("Proyección matrículas finales", f"{int(proy_final)}", delta=f"±{int(margen_error)} (IC 95%)")
    
    # Métricas adicionales
    st.subheader("Métricas de rendimiento")
    col1, col2, col3 = st.columns(3)
    
    # Cálculo de CPA y CPL si hay datos de inversión
    inversion_total = df_hist["inversion"].sum() if "inversion" in df_hist.columns else 0
    cpa = inversion_total / mats_actuales if mats_actuales > 0 else 0
    cpl = inversion_total / leads_actuales if leads_actuales > 0 else 0
    
    col1.metric("CPA (Costo por matrícula)", f"${cpa:.2f}")
    col2.metric("CPL (Costo por lead)", f"${cpl:.2f}")
    col3.metric("Ratio conversión", f"{ratio_conversión*100:.2f}%")

    st.subheader("Observación ejecutiva")
    if proy_final >= mats_obj:
        st.success("✅ Si se mantiene el ritmo, se alcanzará el objetivo de matrículas.")
    else:
        deficit = mats_obj - proy_final
        st.warning(f"⚠️ Ritmo insuficiente. Déficit estimado: {int(deficit)} matrículas. RECOMENDACIONES:")
        st.markdown("""
        * Incrementar presupuesto publicitario (especialmente en canales más eficientes).
        * Reforzar seguimiento del equipo comercial.
        * Revisar mensajes creativos de campañas existentes.
        """)

    st.subheader("Exportar análisis")
    col1, col2 = st.columns(2)
    # Excel export
    if col1.button("Generar Excel"):
        from io import BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_hist.to_excel(writer, sheet_name="Histórico", index=False)
            
            # Crea sheet con resumen
            resumen = pd.DataFrame({
                "Métrica": ["Tiempo transcurrido", "Leads", "Matrículas", "Proyección final", "IC inferior", "IC superior"],
                "Valor": [dias_transcurridos, leads_actuales, mats_actuales, proy_final, ic_lower, ic_upper],
                "Objetivo": [tiempo_total, leads_obj, mats_obj, mats_obj, "-", "-"]
            })
            resumen.to_excel(writer, sheet_name="Resumen", index=False)
        
        buffer.seek(0)
        st.download_button(
            label="Descargar Excel",
            data=buffer,
            file_name="reporte_comercial.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="excel_comercial"
        )
    
    # PDF export
    if PDF_AVAILABLE and col2.button("Generar PDF", key="pdf_comercial"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=15)
        pdf.cell(200, 10, txt="Reporte Comercial", ln=True, align="C")
        pdf.set_font("Arial", size=10)
        pdf.ln(5)
        pdf.cell(0, 10, txt=f"Marca: {st.session_state.current_brand}", ln=True)
        pdf.cell(0, 10, txt=f"Semana: {semana_actual} de {duracion_total}", ln=True)
        pdf.cell(0, 10, txt=f"Tiempo transcurrido: {dias_transcurridos}/{tiempo_total} días", ln=True)
        pdf.cell(0, 10, txt=f"Leads: {leads_actuales}/{leads_obj}", ln=True)
        pdf.cell(0, 10, txt=f"Matrículas: {mats_actuales}/{mats_obj}", ln=True)
        pdf.cell(0, 10, txt=f"Proyección: {int(proy_final)} ± {int(margen_error)}", ln=True)
        
        pdf_output = pdf.output(dest="S").encode("latin-1")
        st.download_button("Descargar PDF", data=pdf_output, file_name="reporte_comercial.pdf", mime="application/pdf", key="pdf_comercial")


def reporte_exploratorio_ui(df_plan: pd.DataFrame, df_hist: pd.DataFrame):
    st.header("📊 Reporte Exploratorio / Diagnóstico")

    if df_hist.empty:
        st.warning("Cargue un histórico para explorar los datos.")
        return

    # Obtener configuración de la convocatoria
    config = st.session_state.get("config_convocatoria", {
        "semana_actual": datetime.datetime.now().isocalendar()[1],
        "duracion_convocatoria": 13,
        "semanas_restantes": 7,
        "progreso": 0.5
    })
    
    # Mostrar información de la convocatoria
    col1, col2, col3 = st.columns(3)
    col1.metric("Semana actual", f"{config['semana_actual']} de {config['duracion_convocatoria']}")
    col2.metric("Semanas restantes", f"{config['semanas_restantes']}")
    col3.metric("Progreso", f"{config['progreso']*100:.1f}%")

    st.subheader("Distribución de leads por canal")
    if "canal" in df_hist.columns and "leads" in df_hist.columns:
        dist = df_hist.groupby("canal")["leads"].sum().sort_values(ascending=False)
        st.bar_chart(dist)

    st.subheader("Matriz de correlación (lead, inversión, CPA, conversión)")
    cols_corr = [c for c in ["leads", "inversion", "cpa", "conversion"] if c in df_hist.columns]
    if len(cols_corr) >= 2:
        corr = df_hist[cols_corr].corr()
        st.dataframe(corr)

    # Detección de anomalías simple: z-score en leads
    col1, col2 = st.columns([3, 1])
    col1.subheader("Detección de anomalías (z-score)")
    if col2.button("❓ Ayuda anomalías", key="help_anomalias"):
        show_help("anomalia")

    if "leads" in df_hist.columns:
        df_hist["z"] = (df_hist["leads"] - df_hist["leads"].mean()) / df_hist["leads"].std()
        anomalies = df_hist[np.abs(df_hist["z"]) > 3]
        if not anomalies.empty:
            st.warning("Se detectaron valores atípicos en leads:")
            st.dataframe(anomalies[[c for c in df_hist.columns if c != "z"]])
        else:
            st.success("No se detectaron anomalías significativas en leads.")

    # Análisis temporal
    st.subheader("Análisis temporal")
    if "fecha" in df_hist.columns and "leads" in df_hist.columns:
        df_hist["fecha"] = pd.to_datetime(df_hist["fecha"])
        df_hist["dia_semana"] = df_hist["fecha"].dt.day_name()
        df_hist["mes"] = df_hist["fecha"].dt.month_name()
        
        # Análisis por día de semana
        leads_dia = df_hist.groupby("dia_semana")["leads"].mean().sort_values(ascending=False)
        st.subheader("Días con mayor captación de leads")
        st.bar_chart(leads_dia)
        
        # Mejor día
        mejor_dia = leads_dia.idxmax()
        st.info(f"El día con mayor captación promedio de leads es {mejor_dia}")
        
        # Análisis de tendencia actual vs histórico
        st.subheader("Análisis de tendencia en convocatoria actual")
        
        # Obtener fechas de inicio y fin basadas en la configuración
        duracion_dias = config['duracion_convocatoria'] * 7
        dias_transcurridos = int(config['progreso'] * duracion_dias)
        
        if dias_transcurridos > 0:
            fechas_actuales = pd.date_range(end=pd.Timestamp.now(), periods=min(dias_transcurridos, len(df_hist)))
            
            # Filtrar datos solo para la convocatoria actual
            df_hist_actual = df_hist[df_hist["fecha"] >= fechas_actuales[0]]
            if not df_hist_actual.empty:
                st.line_chart(df_hist_actual.set_index("fecha")["leads"])
                
                # Comparar con tendencia histórica
                media_leads_dia_actual = df_hist_actual["leads"].mean()
                media_leads_dia_historica = df_hist["leads"].mean()
                
                tendencia = media_leads_dia_actual / media_leads_dia_historica
                if tendencia > 1.1:
                    st.success(f"Tendencia positiva: +{(tendencia-1)*100:.1f}% leads/día vs histórico")
                elif tendencia < 0.9:
                    st.warning(f"Tendencia negativa: {(tendencia-1)*100:.1f}% leads/día vs histórico")
                else:
                    st.info(f"Tendencia estable: {tendencia*100:.1f}% vs histórico")
    else:
        st.info("Se requiere columna 'fecha' para realizar análisis temporal.")

    # Exportar
    st.subheader("Exportar análisis")
    col1, col2 = st.columns(2)
    if col1.button("Descargar Excel diagnóstico", key="excel_diagnostico"):
        from io import BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_hist.to_excel(writer, sheet_name="Histórico", index=False)
            if len(cols_corr) >= 2:
                corr.to_excel(writer, sheet_name="Correlación")
        buffer.seek(0)
        st.download_button("Excel", data=buffer, file_name="diagnostico.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="excel_diagnostico")
    
    if PDF_AVAILABLE and col2.button("Generar PDF resumen", key="pdf_diagnostico"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=15)
        pdf.cell(200, 10, txt="Diagnóstico Exploratorio", ln=True, align="C")
        pdf.set_font("Arial", size=10)
        pdf.ln(5)
        pdf.cell(0, 10, txt=f"Marca: {st.session_state.current_brand}", ln=True)
        pdf.cell(0, 10, txt=f"Semana: {config['semana_actual']} de {config['duracion_convocatoria']}", ln=True)
        if "leads" in df_hist.columns:
            pdf.cell(0, 10, txt=f"Total leads: {df_hist['leads'].sum()}", ln=True)
        if "dia_semana" in locals() and "mejor_dia" in locals():
            pdf.cell(0, 10, txt=f"Mejor día captación: {mejor_dia}", ln=True)
        if "anomalies" in locals() and not anomalies.empty:
            pdf.cell(0, 10, txt=f"Anomalías detectadas: {len(anomalies)}", ln=True)
        
        pdf_output = pdf.output(dest="S").encode("latin-1")
        st.download_button("Descargar PDF", data=pdf_output, file_name="diagnostico.pdf", mime="application/pdf", key="pdf_diagnostico")


# ============================================================
# Main App
# ============================================================


def main():
    st.title("📘 Motor de Decisión Educativo y Predictivo")
    
    # Aplicar estilos CSS personalizados
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Agregar ayuda general del sistema
    if st.sidebar.button("📋 Manual de usuario"):
        st.sidebar.info("""
        **Motor de Decisión Educativo v{}**

        Este sistema permite analizar datos de marketing educativo por marcas,
        generar informes estratégicos y comerciales, y exportar datos
        para toma de decisiones.

        **Uso básico:**
        1. Seleccione una marca o cree una nueva
        2. Cargue datos de planificación e histórico
        3. Explore los reportes disponibles
        4. Utilice los botones de ayuda (❓) para información contextual

        **Requerimientos:**
        - fpdf (para exportación PDF)
        - python-pptx (para exportación PowerPoint)
        - scikit-learn, joblib (para predicciones ML)
        """.format(VERSION))

    brand = sidebar_brand_selector()
    st.sidebar.write(f"Marca seleccionada: **{brand}**")

    menu = st.sidebar.radio(
        "Menú", ["Carga de Datos", "Reporte Estratégico", "Reporte Comercial", "Reporte Exploratorio"], index=0
    )

    df_plan, df_hist = load_data_ui(brand)

    if menu == "Reporte Estratégico":
        reporte_estrategico_ui(df_plan, df_hist)
    elif menu == "Reporte Comercial":
        reporte_comercial_ui(df_plan, df_hist)
    elif menu == "Reporte Exploratorio":
        reporte_exploratorio_ui(df_plan, df_hist)


if __name__ == "__main__":
    main() 