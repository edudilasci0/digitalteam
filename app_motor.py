import os
import json
from pathlib import Path
from typing import Dict, Tuple

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
    """Interfaz para cargar planificación y datos históricos."""
    st.subheader("📥 Carga de datos")

    brand_path = get_brand_path(brand)

    # Mostrar estado actual
    plan_path = brand_path / PLAN_FILE
    hist_path = brand_path / HIST_FILE

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Planificación actual**")
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
                    help="Descarga un archivo CSV de ejemplo para subir como planificación"
                )
        
        if plan_file is not None:
            df_plan = pd.read_csv(plan_file)
            save_dataframe(df_plan, plan_path)
            st.success("Planificación guardada correctamente")

    with col2:
        st.markdown("**Histórico**")
        if hist_path.exists():
            df_hist = load_dataframe(hist_path)
            st.success("Histórico cargado")
            st.dataframe(df_hist.head())
        else:
            df_hist = pd.DataFrame()
            st.info("No hay histórico cargado")

        hist_file = st.file_uploader("Subir histórico CSV", type=["csv"], key="hist")
        
        # Añadir ejemplos descargables para leads y matrículas
        col_leads, col_mats = st.columns(2)
        
        with col_leads:
            ejemplo_leads = Path("datos/plantillas/ejemplo_leads.csv")
            if ejemplo_leads.exists():
                with open(ejemplo_leads, "r") as f:
                    st.download_button(
                        label="Ejemplo de leads",
                        data=f,
                        file_name="ejemplo_leads.csv",
                        mime="text/csv",
                        help="Descarga un archivo CSV de ejemplo de leads"
                    )
        
        with col_mats:
            ejemplo_mats = Path("datos/plantillas/ejemplo_matriculas.csv")
            if ejemplo_mats.exists():
                with open(ejemplo_mats, "r") as f:
                    st.download_button(
                        label="Ejemplo de matrículas",
                        data=f,
                        file_name="ejemplo_matriculas.csv",
                        mime="text/csv",
                        help="Descarga un archivo CSV de ejemplo de matrículas"
                    )
        
        if hist_file is not None:
            df_hist = pd.read_csv(hist_file)
            save_dataframe(df_hist, hist_path)
            st.success("Histórico guardado correctamente")

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

    metricas = calcular_metricas_estrategicas(df_plan, df_hist)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CPA", f"${metricas['CPA']:.2f}")
    col2.metric("CPL", f"${metricas['CPL']:.2f}")
    col3.metric("Progreso Leads", f"{metricas['Progreso Leads']*100:.1f}%")
    col4.metric("Progreso Matrículas", f"{metricas['Progreso Matriculas']*100:.1f}%")

    # ======================================================
    # 1. Comparativa de plataformas (CPA y Conversión)
    # ======================================================
    st.subheader("Comparativa de plataformas")

    if "canal" in df_hist.columns and "cpa" in df_hist.columns:
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
    # 3. Escenarios simulados
    # ======================================================
    st.subheader("Escenarios simulados")

    base_leads = metricas["Progreso Leads"] * df_plan["leads_estimados"].iloc[0] if "leads_estimados" in df_plan.columns else 0
    base_mats = metricas["Progreso Matriculas"] * df_plan["objetivo_matriculas"].iloc[0] if "objetivo_matriculas" in df_plan.columns else 0

    escenarios = pd.DataFrame({
        "Escenario": ["Actual", "Mejora 5% conversión", "Aumento +20% inversión"],
        "Leads estimados": [base_leads, base_leads*1.05, base_leads*1.05],
        "Matrículas estimadas": [base_mats, base_mats*1.05, base_mats*1.1],
        "Descripción": [
            "Mantener ritmo actual", 
            "Incremento de conversión en 5% con misma inversión", 
            "Aumentar inversión total 20% manteniendo conversión"
        ]
    })
    st.table(escenarios)

    # ======================================================
    # 4bis. Predicción ML
    # ======================================================
    cols = st.columns([3, 1])
    cols[0].subheader("Predicción ML de matrículas para próximas 4 semanas")
    if cols[1].button("❓ Ayuda ML", key="help_ml"):
        show_help("prediccion_ml")

    brand_path = get_brand_path(st.session_state.current_brand)
    model = train_or_load_model(df_hist, brand_path)
    if model is not None and "leads" in df_hist.columns and "inversion" in df_hist.columns:
        st.subheader("Predicción ML de matrículas para próximas 4 semanas")

        # Crear df_future con promedio de leads e inversión de últimas 4 semanas
        avg_leads = df_hist["leads"].tail(4).mean()
        avg_inv = df_hist["inversion"].tail(4).mean()
        semanas = pd.DataFrame({
            "leads": [avg_leads]*4,
            "inversion": [avg_inv]*4,
            "semana": list(range(1,5))
        })
        preds, (low, up) = predict_matriculas_interval(model, semanas)
        df_pred = pd.DataFrame({
            "Semana +": [1,2,3,4],
            "Predicción": preds.astype(int),
            "IC Inferior": low.astype(int),
            "IC Superior": up.astype(int)
        })
        st.dataframe(df_pred)
    else:
        st.info("Modelo predictivo no disponible: cargue columnas leads, inversion y matriculas suficientes.")

    # ======================================================
    # 5. Alertas automáticas
    # ======================================================
    st.subheader("Alertas destacadas")
    if metricas["CPA"] > 50:
        st.error("CPA alto: revise campañas menos eficientes.")
    if metricas["Progreso Leads"] < 0.5:
        st.warning("Ritmo bajo de generación de leads (<50% meta).")
    inefficient = cpa_canal[cpa_canal > metricas["CPA"] * 1.2] if "cpa_canal" in locals() else []
    for canal, val in inefficient.items():
        st.warning(f"Canal ineficiente: {canal} (CPA ${val:.2f})")

    # ======================================================
    # 6. Exportación a PDF
    # ======================================================
    if PDF_AVAILABLE:
        if st.button("Descargar PDF resumen"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Reporte Estratégico", ln=True, align="C")
            pdf.ln(5)
            for k, v in metricas.items():
                pdf.cell(0, 10, txt=f"{k}: {v}", ln=True)
            pdf_output = pdf.output(dest="S").encode("latin-1")
            st.download_button("PDF", data=pdf_output, file_name="reporte_estrategico.pdf", mime="application/pdf")
    else:
        st.info("Instale 'fpdf' para exportar PDF.")

    # 7. Exportación a PowerPoint
    if PPT_AVAILABLE:
        if st.button("Descargar PowerPoint resumen"):
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[0])
            title = slide.shapes.title
            subtitle = slide.placeholders[1]
            title.text = "Reporte Estratégico"
            subtitle.text = f"Marca: {st.session_state.current_brand}"

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
            st.download_button("PPTX", data=ppt_buffer, file_name="reporte_estrategico.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
    else:
        st.info("Instale 'python-pptx' para exportar PowerPoint.")


def reporte_comercial_ui(df_plan: pd.DataFrame, df_hist: pd.DataFrame):
    st.header("📊 Reporte Comercial (Status Semanal)")

    if df_plan.empty or df_hist.empty:
        st.warning("Cargue planificación e histórico para generar el reporte.")
        return

    # Supongamos que df_hist tiene columna 'fecha' en formato YYYY-MM-DD
    if "fecha" in df_hist.columns:
        df_hist["fecha"] = pd.to_datetime(df_hist["fecha"])
        fecha_min, fecha_max = df_hist["fecha"].min(), df_hist["fecha"].max()
        dias_transcurridos = (fecha_max - fecha_min).days + 1
    else:
        dias_transcurridos = 0

    tiempo_total = 90  # Placeholder
    leads_obj = df_plan["leads_estimados"].iloc[0] if "leads_estimados" in df_plan.columns else 0
    mats_obj = df_plan["objetivo_matriculas"].iloc[0] if "objetivo_matriculas" in df_plan.columns else 0

    leads_actuales = df_hist["leads"].sum() if "leads" in df_hist.columns else 0
    mats_actuales = df_hist["matriculas"].sum() if "matriculas" in df_hist.columns else 0

    # Barras de progreso
    st.subheader("Progreso de la convocatoria")
    def barra(texto, valor, total):
        pct = int(100 * valor / total) if total else 0
        bar = "▓" * (pct // 10) + "░" * (10 - pct // 10)
        st.write(f"{texto:<25} {bar} {pct}%")

    barra("Tiempo transcurrido", dias_transcurridos, tiempo_total)
    barra("Leads entregados", leads_actuales, leads_obj)
    barra("Matrículas confirmadas", mats_actuales, mats_obj)

    # Proyección simple lineal
    ratio = (mats_actuales / dias_transcurridos) if dias_transcurridos else 0
    proy_final = ratio * tiempo_total
    # Intervalo de confianza simple usando Poisson approximation
    ic_lower = proy_final - 1.96 * np.sqrt(proy_final) if proy_final > 0 else 0
    ic_upper = proy_final + 1.96 * np.sqrt(proy_final)
    col1, col2 = st.columns([3, 1])
    col1.metric("Proyección matrículas finales", f"{int(proy_final)}", delta=f"±{int(ic_upper-ic_lower)} (95% IC)")
    if col2.button("❓ Ayuda", key="help_proy"):
        st.info("Proyección lineal basada en ritmo actual, con intervalo de confianza estadístico del 95%.")

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
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # PDF export
    if PDF_AVAILABLE and col2.button("Generar PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=15)
        pdf.cell(200, 10, txt="Reporte Comercial", ln=True, align="C")
        pdf.set_font("Arial", size=10)
        pdf.ln(5)
        pdf.cell(0, 10, txt=f"Marca: {st.session_state.current_brand}", ln=True)
        pdf.cell(0, 10, txt=f"Tiempo transcurrido: {dias_transcurridos}/{tiempo_total} días", ln=True)
        pdf.cell(0, 10, txt=f"Leads: {leads_actuales}/{leads_obj}", ln=True)
        pdf.cell(0, 10, txt=f"Matrículas: {mats_actuales}/{mats_obj}", ln=True)
        pdf.cell(0, 10, txt=f"Proyección: {int(proy_final)} ± {int(ic_upper-ic_lower)}", ln=True)
        
        pdf_output = pdf.output(dest="S").encode("latin-1")
        st.download_button("Descargar PDF", data=pdf_output, file_name="reporte_comercial.pdf", mime="application/pdf")


def reporte_exploratorio_ui(df_plan: pd.DataFrame, df_hist: pd.DataFrame):
    st.header("📊 Reporte Exploratorio / Diagnóstico")

    if df_hist.empty:
        st.warning("Cargue un histórico para explorar los datos.")
        return

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

    # Añadir análisis temporal
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
    else:
        st.info("Se requiere columna 'fecha' para realizar análisis temporal.")

    st.subheader("Exportar análisis")
    col1, col2 = st.columns(2)
    if col1.button("Descargar Excel diagnóstico"):
        from io import BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_hist.to_excel(writer, sheet_name="Histórico", index=False)
            if not corr.empty:
                corr.to_excel(writer, sheet_name="Correlación")
        buffer.seek(0)
        st.download_button("Excel", data=buffer, file_name="diagnostico.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    if PDF_AVAILABLE and col2.button("Generar PDF resumen"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=15)
        pdf.cell(200, 10, txt="Diagnóstico Exploratorio", ln=True, align="C")
        pdf.set_font("Arial", size=10)
        pdf.ln(5)
        pdf.cell(0, 10, txt=f"Marca: {st.session_state.current_brand}", ln=True)
        if "leads" in df_hist.columns:
            pdf.cell(0, 10, txt=f"Total leads: {df_hist['leads'].sum()}", ln=True)
        if "dia_semana" in locals() and "mejor_dia" in locals():
            pdf.cell(0, 10, txt=f"Mejor día captación: {mejor_dia}", ln=True)
        if "anomalies" in locals() and not anomalies.empty:
            pdf.cell(0, 10, txt=f"Anomalías detectadas: {len(anomalies)}", ln=True)
        
        pdf_output = pdf.output(dest="S").encode("latin-1")
        st.download_button("Descargar PDF", data=pdf_output, file_name="diagnostico.pdf", mime="application/pdf")


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