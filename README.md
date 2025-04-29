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
- **Interfaz en español**: Sistema completamente en español para fácil uso
- **Sistema de autenticación**: Protección con contraseña para acceso seguro

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
├── .streamlit/            # Configuración de Streamlit
│   └── config.toml        # Configuración para desactivar solicitud de correo
└── requirements.txt       # Dependencias del proyecto
```

## Requisitos

- Python 3.6 o superior
- Bibliotecas principales (todas instalables via pip):
  - pandas
  - numpy
  - streamlit
  - scikit-learn
  - matplotlib
  - seaborn
  - python-dotenv
  - sqlite3 (incluido con Python)
  - openpyxl (para Excel)
  - pyyaml (para archivos de configuración)

## Guía de Instalación y Configuración

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/motor-decision.git
cd motor-decision
```

### Paso 2: Configurar entorno virtual (recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar directorios

```bash
# Crear directorios necesarios
mkdir -p datos/actual datos/historico datos/planificacion datos/plantillas
mkdir -p output/reportes output/modelos output/graficos
mkdir -p logs resultados
```

### Paso 5: Configurar Streamlit

Para evitar la solicitud de correo electrónico de Streamlit y otros ajustes:

```bash
# Crear directorio de configuración
mkdir -p .streamlit

# Crear archivo de configuración
echo "[browser]
gatherUsageStats = false

[server]
headless = true
enableCORS = false
enableXsrfProtection = false" > .streamlit/config.toml
```

## Ejecución del Sistema

### Iniciar la aplicación

```bash
streamlit run src/ui/carga_datos.py
```

La aplicación se abrirá automáticamente en tu navegador web (http://localhost:8501).

### Autenticación

Al iniciar la aplicación, verás una pantalla de inicio de sesión:

1. Ingresa la contraseña: `teamdigital`
2. Haz clic en "Iniciar Sesión"

## Uso Básico del Sistema

### 1. Carga de Datos

Después de iniciar sesión, puedes cargar datos de leads y matrículas:

1. Selecciona el tipo de datos (Leads, Matrículas o Auto-detectar)
2. Arrastra y suelta archivos CSV o Excel en la zona de carga
3. El sistema analizará y validará los datos automáticamente
4. Confirma la carga para procesar los datos

### 2. Análisis de Datos

Una vez cargados los datos:

1. Navega a la sección "Análisis" en el menú lateral
2. Selecciona el tipo de análisis a realizar
3. Configura los parámetros según tus necesidades
4. Explora los resultados y visualizaciones generadas

### 3. Generación de Reportes

Para crear informes de resultados:

1. Ve a la sección "Reportes" en el menú lateral
2. Selecciona el tipo de reporte deseado
3. Configura el período y otros parámetros
4. Genera y descarga el reporte en formato PowerPoint o PDF

## Guía para Analistas de Datos

### Preparación de Datos

- Utiliza las plantillas disponibles en `datos/plantillas/` para preparar tus archivos
- Asegúrate de que las fechas estén en formato YYYY-MM-DD
- Incluye todas las columnas requeridas según la documentación

### Interpretación de Resultados

- Para cada análisis, el sistema proporciona:
  - Estadísticas descriptivas de los datos
  - Visualizaciones interactivas
  - Predicciones con intervalos de confianza
  - Recomendaciones basadas en los hallazgos

## Solución de Problemas

### Errores comunes

1. **"No se encuentra el archivo CSV de planificación"**:
   - Verifica que el archivo está en la carpeta correcta (`datos/planificacion/`)
   - Asegúrate de que el nombre sigue el formato recomendado

2. **"Error al cargar los datos"**:
   - Verifica que los archivos existen en las rutas especificadas
   - Asegúrate de que los archivos tienen el formato correcto (CSV, Excel)
   - Revisa que contienen las columnas requeridas

3. **"Error de autenticación"**:
   - Asegúrate de usar la contraseña correcta: `teamdigital`
   - Si persiste, reinicia la aplicación

4. **"Streamlit no inicia"**:
   - Verifica que todas las dependencias están instaladas
   - Comprueba la configuración en `.streamlit/config.toml`

## Preguntas Frecuentes

### ¿Cómo cambiar la contraseña de acceso?

Para cambiar la contraseña, edita el archivo `src/ui/carga_datos.py` y busca la línea:
```python
if password == "teamdigital":
```
Cambia "teamdigital" por tu contraseña preferida.

### ¿Puedo modificar la plantilla de planificación?

Sí, pero debes mantener las columnas principales requeridas por el sistema. Si necesitas añadir columnas adicionales para uso interno, puedes hacerlo sin afectar el funcionamiento.

### ¿Es necesario usar Google Sheets?

No, aunque es recomendado para facilitar la colaboración, puedes crear los archivos CSV directamente o usar otra herramienta, siempre que mantenga el formato esperado.

### ¿Cómo se distribuye el presupuesto entre canales?

El motor analiza el rendimiento histórico de cada canal (conversión, CPA, etc.) y calcula la distribución óptima considerando tanto la eficiencia pasada como las tendencias actuales.

## Mejoras Técnicas

### Dockerización
El proyecto incluye soporte para Docker, lo que facilita la instalación y ejecución en cualquier entorno.

```bash
# Construir imagen Docker
docker-compose build

# Ejecutar en contenedor
docker-compose up
```

### Base de Datos SQLite
Se ha implementado un sistema de base de datos SQLite para reemplazar el almacenamiento basado en archivos CSV, mejorando la eficiencia, integridad y consulta de datos.

```bash
# Acceder a la base de datos directamente
sqlite3 datos/motor_decision.db

# Consultar datos
SELECT * FROM leads LIMIT 10;
```

### Sistema de Logging Mejorado
Nuevo sistema de logging con rotación de archivos y niveles configurables.

```python
from src.utils.logging import get_module_logger

# Obtener logger para el módulo
logger = get_module_logger(__name__)

# Registrar mensajes
logger.info("Mensaje informativo")
logger.warning("Advertencia")
logger.error("Error en la operación")
```

### Gestión de Secretos
Sistema de gestión de credenciales y configuraciones sensibles mediante archivos `.env`.

1. Copia el archivo `.env.template` a `.env`
2. Completa los valores de tus credenciales
3. Las credenciales serán accesibles de forma segura desde el código

```python
from src.utils.secrets import get_secret

# Obtener credenciales
api_key = get_secret("API_KEY")
```

### Sistema de Backup
Script de respaldo automático para datos, modelos y configuraciones.

```bash
# Ejecutar backup manual
bash scripts/backup.sh

# Programar backup automático (ejemplo: cada día a las 2 AM)
# Añadir al crontab:
# 0 2 * * * cd /ruta/a/motor-decision && bash scripts/backup.sh
```

### Pruebas Unitarias
Sistema completo de pruebas unitarias con pytest y reportes de cobertura.

```bash
# Ejecutar todas las pruebas
python run_tests.py

# Ejecutar pruebas con reporte de cobertura
python run_tests.py --coverage

# Ejecutar pruebas para un módulo específico
python run_tests.py --module data
```

## Contribuciones y Soporte

Para reportar problemas, solicitar funcionalidades o contribuir al proyecto, por favor contacta al equipo de Digital Team.

## Licencia

Este proyecto es propiedad de Digital Team y está protegido por derechos de autor.
