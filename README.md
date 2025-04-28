# Motor de Decisión

## Introducción

Sistema integral para la toma de decisiones basada en datos para campañas de captación de matrículas educativas. Esta herramienta permite analizar datos históricos, predecir resultados futuros, y optimizar la inversión para maximizar el retorno. Está diseñado específicamente para equipos de marketing educativo y media planners.

## Características Principales

- **Procesamiento de datos**: Carga, limpieza y transformación de datos de leads y matrículas
- **Análisis predictivo**: Modelos de machine learning para predecir conversiones y matrículas
- **Evaluación de modelos**: Comparación y selección del mejor modelo predictivo
- **Visualización avanzada**: Gráficos interactivos para interpretación de resultados
- **Análisis de estacionalidad**: Identificación de patrones temporales en datos históricos
- **Simulación Monte Carlo**: Evaluación de escenarios con intervalos de confianza
- **Generación de reportes**: Dashboards y reportes automatizados para toma de decisiones
- **Integración con Google Sheets**: Importación/exportación de datos desde/hacia hojas de cálculo

## Estructura del Proyecto

```
├── config/                # Archivos de configuración
│   ├── config.yaml        # Configuración centralizada del sistema
│   └── README.md          # Instrucciones de configuración
├── datos/                 # Datos del sistema
│   ├── actual/            # Datos de la campaña actual (leads y matrículas)
│   ├── historico/         # Datos de campañas anteriores
│   ├── planificacion/     # Archivos CSV de planificación de campañas
│   └── plantillas/        # Plantillas CSV para Google Sheets
├── docs/                  # Documentación
│   ├── Modelo_de_decisiones.md    # Documento principal del modelo
│   ├── estructura_datos.md        # Estructura de los datos
│   ├── manual_planificacion_sheets.md # Manual para Google Sheets
│   └── manual_usuario.md          # Manual detallado de uso
├── logs/                  # Registros de ejecución del sistema
├── output/                # Salidas generadas
│   ├── graficos/          # Visualizaciones generadas
│   ├── modelos/           # Modelos guardados
│   └── reportes/          # Reportes en diferentes formatos
├── resultados/            # Resultados procesados listos para importar
├── scripts/               # Scripts de ejecución
│   ├── cargar_datos.py             # Adaptador para formatos anteriores
│   ├── cargar_datos_individuales.py # Carga de leads y matrículas individuales
│   ├── estimador_valores.py        # Distribuye costos y calcula métricas
│   └── [otros scripts]             # Otros scripts del sistema
├── src/                   # Código fuente principal
│   ├── analysis/          # Módulos de análisis
│   ├── data/              # Módulos de procesamiento de datos
│   ├── models/            # Módulos de modelado predictivo
│   ├── utils/             # Utilidades generales
│   ├── visualization/     # Módulos de visualización
│   └── main.py            # Script principal del sistema
└── requirements.txt       # Dependencias del proyecto
```

## Requisitos

- Python 3.6 o superior
- Bibliotecas principales:
  - pandas
  - numpy
  - scikit-learn
  - matplotlib
  - seaborn
  - joblib
  - openpyxl
  - pyyaml

## Instalación

1. Clonar el repositorio:
```bash
git clone [URL del repositorio]
cd motor-decision
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar el sistema:
```bash
mkdir -p datos/actual datos/historico datos/planificacion datos/plantillas resultados output/reportes output/modelos output/graficos logs
```

## Uso Básico

### Planificación de Campañas

1. Utilice Google Sheets para definir la planificación de campañas:
   - Use la plantilla proporcionada en `datos/plantillas/planificacion_campaña.csv`
   - Defina los parámetros de la campaña (objetivos, presupuesto, canales, etc.)

2. Exporte el archivo desde Google Sheets:
   - Archivo > Descargar > Valores separados por comas (.csv)
   - Nombre el archivo con formato: `YYYYMMDD_planificacion_campaña.csv`
   - Guárdelo en la carpeta `datos/planificacion/`

### Procesamiento y Análisis

```bash
python src/main.py --datos-leads datos/actual/leads.csv --datos-matriculas datos/actual/matriculas.csv --planificacion datos/planificacion/20230701_planificacion_campaña.csv --guardar-resultados
```

### Importar Resultados a Google Sheets

1. Los resultados se generan en la carpeta `resultados/`
2. Estos archivos pueden importarse directamente a Google Sheets para su visualización y compartición

## Modelo de Presupuestación

El Motor de Decisión trabaja con un modelo donde:

- **El presupuesto se asigna a nivel de campaña completa**, no por programa individual
- Cada campaña incluye múltiples programas que comparten el presupuesto común
- Los objetivos se establecen para el total de matrículas de la campaña
- La demanda natural determina qué programas generan más leads dentro de una campaña
- El análisis de rendimiento por programa se realiza para optimización táctica, no para planificación presupuestaria inicial

## Documentación

Para instrucciones detalladas, consulte:

- [Modelo de Decisiones](docs/Modelo_de_decisiones.md): Guía completa del motor, su funcionamiento y outputs
- [Estructura de Datos](docs/estructura_datos.md): Formato de los archivos CSV de leads y matrículas
- [Manual de Planificación con Google Sheets](docs/manual_planificacion_sheets.md): Guía para planificar campañas con Google Sheets

## Solución de Problemas

### Errores comunes

1. **"No se encuentra el archivo CSV de planificación"**:
   - Verifique que el archivo está en la carpeta correcta (`datos/planificacion/`)
   - Asegúrese de que el nombre sigue el formato recomendado

2. **"Error al cargar los datos"**:
   - Verifique que los archivos existen en las rutas especificadas
   - Asegúrese de que los archivos tienen el formato correcto (CSV)
   - Revise que contienen las columnas requeridas

3. **"Error al distribuir el presupuesto"**:
   - Compruebe que el presupuesto total es un valor numérico positivo
   - Verifique que los canales están correctamente especificados y separados por el carácter `|`

## Preguntas Frecuentes

### ¿Puedo modificar la plantilla de planificación?

Sí, pero debe mantener las columnas principales requeridas por el sistema. Si necesita añadir columnas adicionales para uso interno, puede hacerlo sin afectar el funcionamiento.

### ¿Es necesario usar Google Sheets?

No, aunque es recomendado para facilitar la colaboración, puede crear los archivos CSV directamente o usar otra herramienta, siempre que mantenga el formato esperado.

### ¿Cómo se distribuye el presupuesto entre canales?

El motor analiza el rendimiento histórico de cada canal (conversión, CPA, etc.) y calcula la distribución óptima considerando tanto la eficiencia pasada como las tendencias actuales.
