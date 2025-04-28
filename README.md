# Sistema Predictor y Optimizador de Matrículas

## Introducción

Sistema integral para la predicción y optimización de campañas de captación de matrículas educativas. Esta herramienta permite analizar datos históricos, predecir resultados futuros, y optimizar la inversión para maximizar el retorno. Está diseñado específicamente para equipos de marketing educativo y media planners.

## Características Principales

- **Procesamiento de datos**: Carga, limpieza y transformación de datos de leads y matrículas
- **Análisis predictivo**: Modelos de machine learning para predecir conversiones y matrículas
- **Evaluación de modelos**: Comparación y selección del mejor modelo predictivo
- **Visualización avanzada**: Gráficos interactivos para interpretación de resultados
- **Análisis de estacionalidad**: Identificación de patrones temporales en datos históricos
- **Simulación Monte Carlo**: Evaluación de escenarios con intervalos de confianza
- **Generación de reportes**: Dashboards y reportes automatizados para toma de decisiones
- **Integración con Google Sheets**: Sincronización automática de datos con hojas de cálculo

## Estructura del Proyecto

```
├── config/                # Archivos de configuración
│   ├── config.yaml        # Configuración centralizada del sistema
│   └── README.md          # Instrucciones de configuración
├── datos/                 # Datos del sistema
│   ├── actual/            # Datos de la campaña actual
│   ├── historico/         # Datos de campañas anteriores
│   ├── leads_matriculas_reales.csv  # Datos de ejemplo
│   └── planificacion_quincenal.csv  # Datos de ejemplo
├── docs/                  # Documentación
│   ├── manual_usuario.md  # Manual detallado de uso
│   └── implementacion_dashboard.md  # Guía de implementación
├── logs/                  # Registros de ejecución del sistema
├── output/                # Salidas generadas
│   ├── graficos/          # Visualizaciones generadas
│   ├── modelos/           # Modelos guardados
│   └── reportes/          # Reportes en diferentes formatos
├── scripts/               # Scripts de ejecución
│   ├── analisis_estacionalidad.py  # Análisis de patrones temporales
│   ├── analizar_elasticidad.py     # Análisis de elasticidad de demanda
│   ├── analizar_rendimiento.py     # Análisis de rendimiento de campañas
│   ├── calcular_metricas.py        # Cálculo de métricas clave
│   ├── cargar_datos.py             # Cargador de datos en español
│   ├── data_loader.py              # Cargador de datos en inglés
│   ├── dashboard_comercial.py      # Generación de dashboard comercial
│   ├── ejecutar_analisis_completo.py  # Análisis completo del sistema
│   ├── ejecutar_sincronizacion.py  # Sincronización con Google Sheets
│   ├── export_powerbi.py           # Exportación a Power BI
│   ├── generar_reportes.py         # Generación de reportes
│   ├── matriz_decision.py          # Matriz de decisión para optimización
│   ├── modelo_estacionalidad.py    # Modelo de estacionalidad
│   ├── optimizar_campañas.py       # Optimización de campañas
│   ├── optimizar_presupuesto.py    # Optimización de presupuesto
│   ├── planificar_campaña.py       # Planificación de campañas
│   ├── predecir_matriculas.py      # Predicción de matrículas
│   ├── proyectar_convocatoria.py   # Proyección de convocatorias
│   ├── simular_mejora_conversion.py  # Simulación de mejoras
│   ├── simulacion_montecarlo.py    # Simulación Monte Carlo
│   ├── sincronizar_sheets.py       # Integración con Google Sheets
│   ├── sistema_ajuste_automatico.py  # Ajuste automático de campañas
│   └── validar_datos.py            # Validación de datos
├── src/                   # Código fuente principal
│   ├── analysis/          # Módulos de análisis
│   ├── data/              # Módulos de procesamiento de datos
│   ├── models/            # Módulos de modelado predictivo
│   ├── utils/             # Utilidades generales
│   ├── visualization/     # Módulos de visualización
│   └── main.py            # Script principal del sistema
├── Manual de Usuario.md   # Guía completa de uso
├── Modelo decisiones.md   # Guía para interpretación y decisiones
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
  - google-api-python-client
  - google-auth-httplib2
  - google-auth-oauthlib
  - openpyxl
  - pyyaml

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/sistema-predictor-matriculas.git
cd sistema-predictor-matriculas
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar el sistema:
```bash
mkdir -p datos/actual datos/historico output/reportes output/modelos output/graficos logs
```

4. Configurar la integración con Google Sheets (opcional):
   - Sigue las instrucciones en `config/README.md`

## Uso Básico

### Ejecución del sistema completo

```bash
python src/main.py --datos-leads datos/actual/leads.csv --datos-matriculas datos/actual/matriculas.csv --guardar-resultados
```

### Sincronización con Google Sheets

```bash
python scripts/ejecutar_sincronizacion.py
```

### Opciones de línea de comandos

```
--datos-leads          Ruta al archivo CSV de leads
--datos-matriculas     Ruta al archivo CSV de matrículas
--config               Ruta al archivo de configuración personalizado
--guardar-resultados   Guarda los resultados en disco
--dir-salida           Directorio para guardar resultados
--tipo-modelo          Tipo de modelo a entrenar (linear, ridge, lasso, random_forest, gradient_boosting)
--target               Columna objetivo para el modelo (por defecto: convertido)
--solo-carga           Solo cargar y preprocesar datos, sin entrenar modelo
--solo-evaluar         Evaluar modelo ya entrenado sin volver a entrenar
--ruta-modelo          Ruta a un modelo guardado para evaluar
```

## Módulos Principales

### Procesador de Datos

El sistema proporciona dos versiones del cargador de datos:
- `scripts/cargar_datos.py`: Versión en español
- `scripts/data_loader.py`: Versión en inglés

Ambas versiones ofrecen las mismas funcionalidades:
- Cargar datos desde archivos CSV
- Validar la estructura y contenido de los datos
- Convertir tipos de datos
- Manejar errores de formato o archivos no encontrados

```python
# Ejemplo con la versión en español
from scripts.cargar_datos import cargar_datos_crm, cargar_datos_planificacion

# Cargar datos
datos_crm = cargar_datos_crm("datos/actual/leads_matriculas_reales.csv")
datos_planificacion = cargar_datos_planificacion("datos/actual/planificacion_quincenal.csv")

# Ejemplo con la versión en inglés
from scripts.data_loader import load_crm_data, load_planning_data

# Load data
crm_data = load_crm_data("datos/actual/leads_matriculas_reales.csv")
planning_data = load_planning_data("datos/actual/planificacion_quincenal.csv")
```

### Gestor de Modelos

El módulo `model_manager.py` permite:
- Entrenar diferentes tipos de modelos predictivos
- Evaluar el rendimiento de los modelos
- Guardar y cargar modelos entrenados
- Realizar predicciones con modelos entrenados
- Analizar la importancia de características

```python
from src.models.model_manager import ModelManager

# Inicializar gestor de modelos
model_manager = ModelManager(model_name="modelo_conversion")

# Entrenar modelo
metricas = model_manager.train(
    datos_procesados, 
    target_column="convertido",
    model_type="random_forest", 
    categorical_features=["origen", "programa", "marca"]
)

# Guardar modelo
ruta_modelo = model_manager.save()

# Cargar modelo previamente guardado
model_manager.load("output/modelos/modelo_conversion.pkl")

# Realizar predicciones
predicciones = model_manager.predict(nuevos_datos)
```

### Evaluador de Modelos

El módulo `evaluador_modelos.py` proporciona:
- Evaluación de modelos de regresión y clasificación
- Comparación de diferentes modelos
- Visualización de resultados (predicciones vs. reales, residuos)
- Almacenamiento y carga de métricas de evaluación

```python
from src.models.evaluador_modelos import EvaluadorModelos

# Inicializar evaluador
evaluador = EvaluadorModelos()

# Evaluar modelo de regresión
metricas_regresion = evaluador.evaluar_regresion(
    y_true=y_test, 
    y_pred=predicciones,
    nombre_modelo="random_forest"
)

# Visualizar resultados
evaluador.graficar_predicciones_vs_reales(
    y_true=y_test, 
    y_pred=predicciones,
    nombre_modelo="random_forest"
)

# Comparar modelos
comparacion = evaluador.comparar_modelos(
    modelos=["linear", "ridge", "random_forest"],
    metricas_clave=["rmse", "r2"]
)
```

### Visualizador

El módulo `visualizador.py` permite:
- Generar gráficos de series temporales
- Visualizar distribuciones de variables
- Crear gráficos de barras para categorías
- Generar gráficos de dispersión
- Visualizar matrices de correlación
- Crear gráficos multilinea para comparaciones

```python
from src.visualizacion.visualizador import Visualizador

# Inicializar visualizador
visualizador = Visualizador()

# Gráfico de serie temporal
visualizador.graficar_serie_temporal(
    datos=datos_temporales,
    columna_fecha="fecha_creacion",
    columna_valor="conteo",
    titulo="Evolución de leads por semana"
)

# Gráfico de barras por categoría
visualizador.graficar_barras(
    datos=datos_procesados,
    columna_categoria="origen",
    columna_valor="costo",
    titulo="Costo por origen"
)
```

## Configuración

El sistema utiliza un archivo de configuración centralizado (`config/config.yaml`) que permite ajustar:

- Rutas de directorios de datos, salida y logs
- Parámetros de análisis (frecuencia, periodos mínimos)
- Configuraciones de modelos y simulaciones
- Opciones de integración con Google Sheets y Power BI

Para cargar una configuración personalizada:

```bash
python src/main.py --config mi_configuracion.yaml
```

## Integración con Google Sheets

El sistema incluye integración con Google Sheets para:

- Sincronizar datos de leads y matrículas
- Actualizar planificación de campañas
- Exportar resultados y predicciones

Para configurar la integración:

1. Sigue las instrucciones en `config/README.md`
2. Ejecuta el script de sincronización:
```bash
python scripts/ejecutar_sincronizacion.py
```

## Documentación Adicional

Para instrucciones detalladas sobre el uso del sistema, consulte:

- [Manual de Usuario](Manual%20de%20Usuario.md): Guía completa para usuarios del sistema
- [Modelo de Decisiones](Modelo%20decisiones.md): Guía para interpretar resultados y tomar decisiones basadas en datos
- [Implementación de Dashboard](docs/implementacion_dashboard.md): Guía para implementar dashboards interactivos

## Solución de Problemas

### Errores comunes

1. **"No se encuentra el módulo X"**:
   - Asegúrese de estar ejecutando desde la raíz del proyecto
   - Verifique que ha instalado todas las dependencias

2. **"Error al cargar los datos"**:
   - Verifique que los archivos existen en las rutas especificadas
   - Asegúrese de que los archivos tienen el formato correcto (CSV)
   - Revise que contienen las columnas requeridas

3. **"Error al entrenar el modelo"**:
   - Verifique que los datos contienen suficientes observaciones
   - Asegúrese de que no hay valores faltantes en características importantes
   - Revise los logs para mensajes de error específicos

4. **"Error de autenticación con Google Sheets"**:
   - Verifique que ha configurado correctamente las credenciales
   - Asegúrese de que las hojas de cálculo están compartidas con la cuenta de servicio
   - Revise los permisos de la API de Google Sheets

## Contribución

Si desea contribuir a este proyecto:

1. Haga un fork del repositorio
2. Cree una rama para su funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Realice sus cambios y haga commit (`git commit -m 'Añadir nueva funcionalidad'`)
4. Suba los cambios a su fork (`git push origin feature/nueva-funcionalidad`)
5. Abra un Pull Request
