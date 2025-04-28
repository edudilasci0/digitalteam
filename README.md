# digitalteam
# README.md - Proyecto: Predictor y Optimizador de Matrículas basadas en CPA

---

# 🌟 Objetivo General

Construir un sistema modular en Python que permita:
- Cargar archivos CSV o Excel de leads y matrículas reales extraídos del CRM.
- Calcular CPL (Costo por Lead), CPA (Costo por Matrícula) y Tasa de Conversión real.
- Predecir si se alcanzará el objetivo de matrículas:
  - Vía reglas deterministas (cálculo clásico).
  - Vía modelo de Machine Learning (regresión).
- Simular escenarios alternativos de optimización (por ejemplo, mejora de conversión o CPL).
- Generar reportes visuales (.PNG) para el equipo de marketing y comercial.


---

# 📅 Entregables

- Estructura de carpetas del proyecto.
- Scripts Python modulares.
- Dataset de ejemplo.
- Reportes automáticos en PNG.
- README.md explicativo.
- requirements.txt con librerías necesarias.


---

# 🔄 Estructura de carpetas esperada

```
/data
  - leads_matriculas_reales.csv
  - planificacion_quincenal.csv
/scripts
  - load_data.py
  - validate_data.py
  - calculate_metrics.py
  - rule_based_predictor.py
  - ml_predictor.py
  - generate_report.py
  - simulation.py
/outputs
/models
/docs
/notebooks
/config
.gitignore
requirements.txt
README.md
```


---

# 🔄 Flujo General del Sistema

```
1. El equipo descarga leads y matrículas del CRM.
2. El equipo actualiza presupuesto y CPL objetivo en planificacion_quincenal.csv.
3. Se cargan ambos archivos al sistema.
4. Se validan las estructuras de datos.
5. Se calculan CPL, CPA, Tasa de Conversión.
6. Se realiza predicción determinista y predicción ML.
7. Se generan reportes visuales en formato PNG.
8. Se simulan escenarios de optimización (opcional).
```


---

# 🛠️ Scripts a construir

| Script | Descripción |
|:---|:---|
| load_data.py | Cargar datos CSV/Excel del CRM y de planificación. |
| validate_data.py | Validar que los datos contengan las columnas necesarias. |
| calculate_metrics.py | Calcular CPL, CPA y Tasa de Conversión reales. |
| rule_based_predictor.py | Predicción lógica basada en avance de tiempo y leads. |
| ml_predictor.py | Modelo de regresión para predecir matrículas futuras. |
| generate_report.py | Crear reportes visuales con barras de progreso y estado. |
| simulation.py | Simular cambios de CPL o tasa de conversión. |


---

# 🔹 Datos requeridos en /data

**Leads y matrículas reales:** leads_matriculas_reales.csv
- Fecha
- Marca
- Canal
- Tipo (Lead/Matrícula)
- Estado
- ID Lead (opcional)

**Planificación de medios:** planificacion_quincenal.csv
- Quincena
- Marca
- Canal
- Presupuesto Asignado (USD)
- CPL Objetivo (USD)
- Leads Estimados (opcional, si no se calcula automático)


---

# 🌐 Librerías necesarias (requirements.txt)

```
pandas
numpy
matplotlib
seaborn
scikit-learn
openpyxl
```


---

# 🌟 Reglas de funcionamiento clave

- El **CPA real** es la métrica principal a optimizar.
- CPL real es solo un indicador auxiliar.
- Todas las simulaciones y predicciones deben enfocarse en maximizar matrículas con el mejor CPA posible.
- Actualizar datos cada 2 semanas.
- Dejar registros de cambios en /docs/changes.md.


---

# 🔹 Roadmap Inicial

| Semana | Actividades |
|:---|:---|
| Semana 1 | Setup de proyecto, carga de datos, validación, cálculo de métricas |
| Semana 2 | Predicción determinista + generación de reportes PNG |
| Semana 3 | Dataset histórico + primer modelo de Machine Learning |
| Semana 4 | Integración predicción ML + simulaciones de escenarios |
| Semana 5 | Documentación final, optimizaciones, extensiones |


---

# 🔄 Misión del sistema

> "Pasar de decisiones reactivas a decisiones proactivas basadas en ciencia de datos, para optimizar las matrículas logradas en convocatorias educativas controlando el CPA y maximizando la eficiencia de la inversión publicitaria."


---

# 🚀 Ready to Build.
