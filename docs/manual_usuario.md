# Manual de Usuario - Sistema Predictor y Optimizador de Matrículas

## Índice
1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Estructura de Archivos](#estructura-de-archivos)
4. [Instalación](#instalación)
5. [Ejecución del Programa](#ejecución-del-programa)
6. [Archivos de Entrada](#archivos-de-entrada)
7. [Reportes Generados](#reportes-generados)
8. [Variables Configurables](#variables-configurables)
9. [Solución de Problemas](#solución-de-problemas)

## Introducción

El Sistema Predictor y Optimizador de Matrículas es una herramienta diseñada para ayudar a equipos de marketing y comercial a predecir y optimizar el rendimiento de sus campañas de captación de matrículas educativas.

El sistema permite:
- Cargar datos de leads y matrículas desde archivos CSV/Excel
- Calcular métricas clave como CPL, CPA y Tasa de Conversión
- Predecir el número final de matrículas basado en el avance de la convocatoria
- Visualizar el rendimiento actual y proyectado de cada campaña
- Controlar campañas con diferentes duraciones (6, 12 semanas, etc.)

## Requisitos del Sistema

- Python 3.6 o superior
- Librerías Python (instalables mediante `pip`):
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - scikit-learn
  - openpyxl

## Estructura de Archivos

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
│   └── manual_usuario.md       # Este manual
├── .gitignore                  # Archivos a ignorar en control de versiones
└── requirements.txt            # Dependencias del proyecto
```

## Instalación

1. Asegúrese de tener Python 3.6 o superior instalado
2. Clone o descargue este repositorio
3. Instale las dependencias necesarias:

```bash
pip install -r requirements.txt
```

## Ejecución del Programa

Para ejecutar el programa, navegue a la carpeta principal del proyecto y ejecute:

```bash
python scripts/main.py
```

El programa leerá los archivos de datos de la carpeta `data/`, procesará la información y generará los reportes visuales en la carpeta `outputs/`.

## Archivos de Entrada

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

## Reportes Generados

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

## Variables Configurables

El sistema permite modificar varias configuraciones para adaptarse a sus necesidades específicas:

### En scripts/main.py:
- **Rutas de archivos**: Puede modificar las rutas a los archivos de entrada y salida.
```python
crm_file_path = "data/leads_matriculas_reales.csv"
planning_file_path = "data/planificacion_quincenal.csv"
output_dir = "outputs"
```

### En scripts/validate_data.py:
- **Columnas requeridas**: Puede modificar las columnas que se validan en los archivos de entrada.
```python
required_columns = ['Fecha', 'Marca', 'Canal', 'Tipo', 'Estado']
```

### En scripts/rule_based_predictor.py:
- **Lógica de predicción**: Puede ajustar la lógica para predecir matrículas.
```python
# Predicción actual basada en el porcentaje de avance de la convocatoria
prediction_data['Leads Esperados Total'] = prediction_data['Leads Actuales'] / prediction_data['Porcentaje Avance Decimal']
```

### En scripts/generate_report.py:
- **Estilo de gráficos**: Puede modificar colores, tamaños y estilos de los reportes visuales.
```python
def setup_plot_style():
    sns.set(style="whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12
```

## Solución de Problemas

### Errores comunes:

1. **Error al cargar archivo**: Verifique que los archivos existan en la ruta especificada y tengan el formato correcto.

2. **Columnas faltantes**: Asegúrese de que los archivos de entrada contengan todas las columnas requeridas.

3. **Error en formato de fechas**: Las fechas deben estar en formato YYYY-MM-DD.

4. **División por cero**: Puede ocurrir si no hay leads o si el porcentaje de avance es cero. El sistema intenta manejar estos casos pero verifique sus datos de entrada.

5. **Convocatorias inconsistentes**: Asegúrese de que las fechas de inicio y fin de cada convocatoria son coherentes y la duración en semanas es correcta.

---

**Nota**: Se recomienda traducir el código fuente al español para facilitar su mantenimiento por el equipo local. Esto incluiría nombres de funciones, variables y comentarios. 