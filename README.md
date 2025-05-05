# 📘 Motor de Decisión Educativo y Predictivo v2.0

Sistema local de análisis y reportes para marketing educativo, que permite cargar planificación de campañas, analizar datos y generar reportes diferenciados para áreas de marketing, comercial y diagnóstico.

## 🚀 Características principales (v2.0)

- **Gestión completa por marca**: Organiza datos de forma independiente para GR, PG, ADV, GMBA, WZ, AJA
- **Carga flexible**: Modo acumulativo o archivos semanales en CSV/Excel
- **Validación de datos**: Verificación de estructura y detección de duplicados
- **Reportes mejorados**:
  - **Estratégico (Marketing)**: CPA, ROI, proyecciones, simulaciones, **atribución multicanal**
  - **Comercial (Status)**: Barras de progreso con indicadores visuales, proyecciones con IC
  - **Exploratorio (Diagnóstico)**: Distribuciones, anomalías, correlaciones, análisis por cohortes
- **Machine Learning integrado**: Predicciones con intervalos de confianza
- **Análisis individual de leads**: Seguimiento detallado de la conversión 
- **Atribución multicanal**: 6 modelos de atribución (último clic, primer clic, lineal, tiempo, posicional, Shapley)
- **Exportación Excel avanzada**: Diseño optimizado con gráficos interactivos, múltiples hojas y formato profesional

## 📋 Requisitos

```bash
pip install -r requirements.txt
```

## 🚀 Inicio rápido

```bash
streamlit run app_motor.py
```

## 📂 Nueva estructura de datos

```
data/
├── GR/                          # Marca 1
│   ├── actual/                  # Datos actuales
│   │   ├── leads_actual.csv
│   │   └── matriculas_actual.csv
│   ├── historico/               # Datos históricos
│   │   ├── leads/               # Organizado por año
│   │   │   └── 2024/
│   │   └── matriculas/          # Organizado por año
│   │       └── 2024/
│   ├── reportes/                # Reportes generados
│   ├── historico.csv            # Datos agregados
│   └── plan_actual.csv          # Planificación
├── PG/                          # Marca 2
│   └── ...
├── ADV/                         # Marca 3
│   └── ...
```

## 🔍 Formato de archivos actualizados

**plan_actual.csv**
- fecha
- marca
- canal
- presupuesto
- leads_estimados
- objetivo_matriculas

**historico.csv**
- fecha 
- marca
- canal
- leads
- matriculas
- inversion

**leads_actual.csv**
- ID
- fecha_generacion
- canal
- programa
- marca
- estado
- secuencia_canales (opcional, para atribución)
- timestamp_interacciones (opcional, para atribución)

**matriculas_actual.csv**
- ID
- fecha_matricula
- canal
- marca
- programa
- fecha_contacto_inicial
- nivel_interes
- tipo_matricula

## 👥 Flujo de trabajo 2.0

1. Seleccionar marca predefinida o crear una nueva
2. Configurar modo de carga (acumulativo o semanal)
3. Cargar datos de planificación, históricos e individuales
4. Explorar reportes: estratégico, comercial o exploratorio
5. Analizar atribución multicanal con diferentes modelos
6. Exportar resultados en formato Excel optimizado con gráficos interactivos

## 🔄 Módulo de Atribución Multicanal

El nuevo sistema incluye 6 modelos de atribución para leads convertidos:

- **Último clic**: Atribuye 100% del mérito al último canal de contacto
- **Primer clic**: Atribuye 100% del mérito al primer canal de contacto
- **Lineal**: Distribuye equitativamente entre todos los canales
- **Decaimiento temporal**: Asigna más peso a los canales más recientes
- **Posicional**: 40% primer contacto, 40% último contacto, 20% resto
- **Shapley value**: Basado en la contribución marginal de cada canal

## 📊 Exportación Excel Mejorada

Los reportes Excel incluyen ahora:
- **Formato profesional**: Diseño visual mejorado con colores corporativos
- **Múltiples hojas temáticas**: Resumen ejecutivo, datos históricos, proyecciones, etc.
- **Gráficos interactivos**: Visualizaciones integradas que pueden manipularse en Excel
- **Barras de progreso visuales**: Indicadores de cumplimiento con códigos de color
- **Filtros automáticos**: Para facilitar el análisis de datos
- **Formatos condicionales**: Resaltan automáticamente datos importantes

## 🛠️ Tecnologías

- Streamlit (interfaz)
- Pandas/NumPy (procesamiento)
- Scikit-learn (modelos predictivos)
- Matplotlib (visualización)
- XlsxWriter (exportación Excel avanzada)

## 📄 Licencia

Uso interno - Team Digital
