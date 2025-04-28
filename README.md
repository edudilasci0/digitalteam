# Sistema Predictor y Optimizador de Matrículas basado en CPA

![Versión](https://img.shields.io/badge/versión-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.6+-green)
![Licencia](https://img.shields.io/badge/licencia-MIT-yellow)

## 📋 Índice
1. [Introducción](#introducción)
2. [Características](#características)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Requisitos](#requisitos)
5. [Instalación](#instalación)
6. [Uso](#uso)
7. [Archivos de Entrada](#archivos-de-entrada)
8. [Reportes Generados](#reportes-generados)
9. [Variables Configurables](#variables-configurables)
10. [Solución de Problemas](#solución-de-problemas)
11. [Contribuir](#contribuir)

## 🚀 Introducción

El Sistema Predictor y Optimizador de Matrículas es una herramienta creada para ayudar a equipos de marketing y comercial a predecir y optimizar el rendimiento de sus campañas de captación de matrículas educativas basándose en el CPA (Costo Por Adquisición).

> "Pasar de decisiones reactivas a decisiones proactivas basadas en ciencia de datos, para optimizar las matrículas logradas en convocatorias educativas controlando el CPA y maximizando la eficiencia de la inversión publicitaria."

## ✨ Características

El sistema permite:
- Cargar datos de leads y matrículas desde archivos CSV/Excel
- Calcular métricas clave como CPL, CPA y Tasa de Conversión
- Predecir el número final de matrículas basado en el avance de la convocatoria
- Visualizar el rendimiento actual y proyectado de cada campaña
- Controlar campañas con diferentes duraciones (6, 12 semanas, etc.)
- Generar reportes visuales en formato PNG

## 📁 Estructura del Proyecto

```
/
├── data/                       # Carpeta para archivos de datos
│   ├── leads_matriculas_reales.csv        # Datos de leads y matrículas
│   └── planificacion_quincenal.csv        # Planificación de medios con duraciones
├── scripts/                    # Scripts Python del sistema
│   ├── load_data.py            # Carga de datos CSV/Excel
│   ├── validate_data.py        # Validación de estructura de datos
│   ├── calculate_metrics.py    # Cálculo de métricas (CPL, CPA, etc.)
│   ├── rule_based_predictor.py # Predictor basado en reglas
│   ├── generate_report.py      # Generación de reportes visuales
│   └── main.py                 # Script principal integrador
├── outputs/                    # Carpeta donde se guardan los reportes generados
├── docs/                       # Documentación
│   └── manual_usuario.md       # Manual de usuario detallado
├── .gitignore                  # Archivos a ignorar en control de versiones
└── requirements.txt            # Dependencias del proyecto
```

## 📋 Requisitos

- Python 3.6 o superior
- Librerías Python (instalables mediante `pip`):
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - scikit-learn
  - openpyxl

## 💻 Instalación

1. Clone este repositorio:
```bash
git clone https://github.com/edudilasci0/digitalteam.git
cd digitalteam
```

2. Instale las dependencias necesarias:
```bash
pip install -r requirements.txt
```

## 🔧 Uso

Para ejecutar el programa, navegue a la carpeta principal del proyecto y ejecute:

```bash
python scripts/main.py
```

El sistema ejecutará el siguiente flujo de trabajo:
1. Carga de datos de leads y matrículas desde archivos CSV
2. Validación de estructura de datos
3. Cálculo de métricas: CPL, CPA y Tasa de Conversión
4. Predicción basada en duración de convocatorias
5. Generación de reportes visuales en la carpeta `outputs/`

## 📊 Archivos de Entrada

El sistema requiere dos archivos de entrada principales:

### 1. leads_matriculas_reales.csv

Contiene los datos de leads y matrículas extraídos del CRM, con la siguiente estructura:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| Fecha | Fecha del registro | 2023-01-01 |
| Marca | Nombre de la institución educativa | Universidad A |
| Canal | Canal de captación | Facebook |
| Tipo | Lead o Matrícula | Lead |
| Estado | Estado del registro | Contactado, Interesado, etc. |
| ID Lead | Identificador único del lead (opcional) | 1001 |

### 2. planificacion_quincenal.csv

Contiene los datos de planificación de medios con la siguiente estructura:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| Quincena | Periodo de la planificación | 2023-01-01/2023-01-15 |
| Marca | Nombre de la institución educativa | Universidad A |
| Canal | Canal de captación | Facebook |
| Presupuesto Asignado (USD) | Presupuesto para el periodo | 1000 |
| CPL Objetivo (USD) | Costo por Lead objetivo | 10 |
| Leads Estimados | Cantidad de leads estimados | 100 |
| ID Convocatoria | Identificador de la convocatoria | CONV-A-2023-01 |
| Fecha Inicio | Fecha de inicio de la convocatoria | 2023-01-01 |
| Fecha Fin | Fecha de fin de la convocatoria | 2023-02-12 |
| Duracion Semanas | Duración en semanas de la convocatoria | 6 |

## 📈 Reportes Generados

El sistema genera cinco tipos de reportes visuales:

1. **CPL Report** (cpl_report_[fecha].png):
   - Muestra el CPL Real vs Objetivo por Marca y Canal
   - Compara el costo por lead actual con el objetivo planificado

2. **CPA Report** (cpa_report_[fecha].png):
   - Muestra el CPA Real por Marca y Canal
   - Visualiza el costo por matrícula actual

3. **Conversion Report** (conversion_report_[fecha].png):
   - Muestra la Tasa de Conversión por Marca y Canal
   - Porcentaje de leads que se convierten en matrículas

4. **Prediction Report** (prediction_report_[fecha].png):
   - Compara Matrículas Actuales vs Esperadas por Marca y Canal
   - Proyección de matrículas al final de la convocatoria

5. **Convocation Progress Report** (conv_progress_report_[fecha].png):
   - Muestra el progreso de cada convocatoria
   - Incluye barras de progreso, porcentaje de avance y estado
   - Permite visualizar el avance de convocatorias con diferentes duraciones

## ⚙️ Variables Configurables

El sistema permite modificar varias configuraciones para adaptarse a sus necesidades específicas:

### En scripts/main.py:
- **Rutas de archivos**: Puede modificar las rutas a los archivos de entrada y salida.
```python
ruta_archivo_crm = "data/leads_matriculas_reales.csv"
ruta_archivo_planificacion = "data/planificacion_quincenal.csv"
dir_salida = "outputs"
```

### En scripts/validate_data.py:
- **Columnas requeridas**: Puede modificar las columnas que se validan en los archivos de entrada.
```python
columnas_requeridas = ['Fecha', 'Marca', 'Canal', 'Tipo', 'Estado']
```

### En scripts/rule_based_predictor.py:
- **Lógica de predicción**: Puede ajustar la lógica para predecir matrículas.
```python
# Predicción actual basada en el porcentaje de avance de la convocatoria
datos_prediccion['Leads Esperados Total'] = datos_prediccion['Leads Actuales'] / datos_prediccion['Porcentaje Avance Decimal']
```

### En scripts/generate_report.py:
- **Estilo de gráficos**: Puede modificar colores, tamaños y estilos de los reportes visuales.
```python
def configurar_estilo_grafico():
    sns.set(style="whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12
```

## ❓ Solución de Problemas

### Errores comunes:

1. **Error al cargar archivo**: Verifique que los archivos existan en la ruta especificada y tengan el formato correcto.

2. **Columnas faltantes**: Asegúrese de que los archivos de entrada contengan todas las columnas requeridas.

3. **Error en formato de fechas**: Las fechas deben estar en formato YYYY-MM-DD.

4. **División por cero**: Puede ocurrir si no hay leads o si el porcentaje de avance es cero. El sistema intenta manejar estos casos pero verifique sus datos de entrada.

5. **Convocatorias inconsistentes**: Asegúrese de que las fechas de inicio y fin de cada convocatoria son coherentes y la duración en semanas es correcta.

## 🤝 Contribuir

Si deseas contribuir a este proyecto:

1. Haz un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/nueva-funcionalidad`)
3. Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva funcionalidad'`)
4. Sube los cambios a tu fork (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

Desarrollado por [Digital Team](https://github.com/edudilasci0/digitalteam)
