# 📘 Motor de Decisión Educativo y Predictivo

Sistema local de análisis y reportes para marketing educativo, que permite cargar planificación de campañas, analizar datos y generar reportes diferenciados para áreas de marketing, comercial y diagnóstico.

## 🚀 Características principales

- **Gestión por marcas**: Organiza datos por marcas de forma independiente
- **Carga de datos flexible**: Planificación e históricos en CSV/Excel 
- **Reportes diferenciados**:
  - **Estratégico (Marketing)**: CPA, ROI, proyecciones, simulaciones
  - **Comercial (Status)**: Barras de progreso, proyecciones con IC
  - **Exploratorio (Diagnóstico)**: Distribuciones, anomalías, correlaciones
- **Machine Learning integrado**: Predicciones automatizadas 
- **Exportación multiformato**: Excel, PDF, PowerPoint

## 📋 Requisitos

```bash
pip install -r requirements.txt
```

## 🚀 Inicio rápido

```bash
streamlit run app_motor.py
```

## 📂 Estructura de datos

```
data/
├── MARCA1/
│   ├── historico.csv
│   ├── plan_actual.csv
│   └── reportes/
├── MARCA2/
│   └── ...
```

## 🔍 Formato de archivos

**plan_actual.csv (mínimo requerido)**
- leads_estimados
- objetivo_matriculas

**historico.csv (mínimo requerido)**
- fecha 
- leads
- matriculas
- inversion
- canal

## 👥 Uso típico

1. Seleccionar o crear marca 
2. Cargar datos de planificación e histórico
3. Navegar a reportes para análisis
4. Exportar resultados en formato deseado

## 📊 Ejemplo

![imagen](https://via.placeholder.com/800x400.png?text=Motor+de+Decision+Educativo)

## 🛠️ Tecnologías

- Streamlit (interfaz)
- Pandas/NumPy (procesamiento)
- Scikit-learn (modelos predictivos)
- Matplotlib (visualización)
- FPDF/python-pptx (exportación)

## 📄 Licencia

Uso interno - Team Digital
