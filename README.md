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

## Preguntas Frecuentes Profesionales

### 🎯 1. Sobre el propósito general

**¿Cómo describirías en una frase la misión de este sistema para marketing digital?**  
El Motor de Decisión es un sistema integral que automatiza la toma de decisiones basada en datos para campañas de captación de matrículas educativas, combinando análisis predictivo, simulación de escenarios y visualización avanzada para optimizar la inversión en marketing.

**¿Cuál es la principal ventaja competitiva que nos da respecto a otros sistemas tradicionales de reporting?**  
A diferencia de los sistemas tradicionales que solo reportan datos históricos, nuestro Motor de Decisión integra predicciones con intervalos de confianza, análisis de elasticidad y simulaciones Monte Carlo, permitiendo decisiones proactivas basadas en escenarios futuros probables, no solo en datos pasados.

### 🎯 2. Sobre análisis y métricas que calcula

**¿Qué métricas principales calcula automáticamente el sistema (CPL, CPA, conversión)?**  
El sistema calcula automáticamente:
- CPL (Costo por Lead)
- CPA (Costo por Adquisición)
- Tasa de conversión (leads a matrículas)
- ROI por canal y programa
- Elasticidad de demanda
- Intervalos de confianza para predicciones
- Desviaciones respecto a objetivos y patrones históricos

**¿Cómo se calcula la predicción del cierre de convocatoria?**  
La predicción del cierre se calcula mediante modelos de machine learning que consideran:
- Patrones históricos de estacionalidad
- Tasa de conversión actual vs. histórica
- Velocidad de captación de leads
- Factores de elasticidad por canal
- Simulaciones Monte Carlo para generar intervalos de confianza

**¿Qué tipo de alertas genera el sistema cuando detecta desvíos críticos?**  
El sistema genera alertas para:
- Desviaciones mayores al 20% de los objetivos de captación
- Caídas significativas en tasas de conversión
- Incrementos anormales en CPL o CPA
- Patrones que se desvían significativamente de la estacionalidad histórica
- Escenarios con alta probabilidad de no alcanzar objetivos

**¿Se incluyen cálculos de proyección de matrículas bajo escenarios de mejora o empeoramiento?**  
Sí, el sistema incluye simulaciones de escenarios optimistas, pesimistas y neutrales, permitiendo visualizar el impacto de mejoras o deterioros en tasas de conversión, CPL y otros factores clave.

### 🎯 3. Sobre predicción y forecast

**¿Cómo funciona el forecast dinámico hasta el cierre de convocatoria?**  
El forecast dinámico:
- Se actualiza automáticamente con cada nueva carga de datos
- Ajusta las predicciones según el rendimiento actual vs. histórico
- Incorpora factores de estacionalidad y tendencias recientes
- Genera intervalos de confianza que se estrechan a medida que se acerca el cierre
- Permite visualizar la probabilidad de alcanzar diferentes niveles de objetivos

**¿Qué variables principales afectan la predicción de cierre?**  
Las variables clave incluyen:
- Velocidad actual de captación de leads
- Tasa de conversión histórica y actual
- Patrones de estacionalidad
- Elasticidad de demanda por canal
- Factores externos (competencia, economía, etc.)
- Calidad de leads por origen

**¿Qué pasa si la tasa de conversión mejora o empeora 5%? ¿El sistema puede simularlo?**  
Sí, el sistema permite simular escenarios con diferentes tasas de conversión mediante el módulo de simulación de escenarios, mostrando el impacto en matrículas finales y ajustando las recomendaciones de inversión según la elasticidad de cada canal.

### 🎯 4. Sobre modelado histórico y estacionalidad

**¿Cómo compara el avance actual con el patrón de estacionalidad de campañas anteriores?**  
El sistema:
- Analiza patrones históricos de captación y conversión
- Identifica períodos de alta/baja estacionalidad
- Compara el rendimiento actual con el esperado según la estacionalidad
- Ajusta las predicciones considerando si estamos en un período típicamente fuerte o débil
- Visualiza la desviación respecto al patrón histórico esperado

**¿El sistema puede detectar automáticamente si estamos por debajo o por encima del patrón histórico esperado?**  
Sí, el sistema detecta automáticamente desviaciones significativas del patrón histórico y las clasifica en tres categorías:
- POR DEBAJO: Rendimiento inferior al esperado según estacionalidad
- DENTRO DEL RANGO: Rendimiento acorde a lo esperado
- POR ENCIMA: Rendimiento superior al esperado

### 🎯 5. Sobre elasticidad y simulación de escenarios

**¿Qué impacto predice el sistema si subimos o bajamos el presupuesto un 10% o 20%?**  
El sistema calcula la elasticidad de demanda por canal y programa, permitiendo simular el impacto de cambios en el presupuesto:
- Para canales con elasticidad >1.0: Incrementos proporcionalmente mayores en leads
- Para canales con elasticidad ~1.0: Cambios proporcionales
- Para canales con elasticidad <1.0: Incrementos proporcionalmente menores
- Recomendaciones específicas de reasignación basadas en elasticidades

**¿La simulación de escenarios de elasticidad mantiene el CPL actual o permite variarlo manualmente?**  
El sistema permite ambas opciones:
- Simulación con CPL constante (para evaluar solo el impacto del volumen)
- Simulación con CPL variable (para evaluar el impacto de cambios en eficiencia)
- Personalización manual de parámetros para escenarios específicos

### 🎯 6. Sobre gobernanza de datos y reporting

**¿Cómo se organiza el flujo de carga de datos para proteger la calidad de la información?**  
El sistema implementa un flujo de datos con múltiples capas de validación:
- Verificación automática de columnas requeridas
- Validación de tipos de datos y rangos
- Detección de valores atípicos y anomalías
- Registro detallado de errores y advertencias
- Proceso de carga en etapas con puntos de control

**¿Qué roles y accesos tiene cada equipo sobre los reportes y métricas?**  
El sistema implementa tres niveles de acceso:
- **Nivel Comercial**: Dashboard diario con KPIs esenciales y alertas
- **Nivel Táctico**: Análisis detallado por canal, programa y marca
- **Nivel Estratégico**: Visualización completa con todos los datos y análisis avanzados

**¿Se puede exportar visualmente todo en formato consolidado para no compartir datos crudos?**  
Sí, el sistema permite exportar resultados en múltiples formatos:
- Dashboards interactivos en Power BI
- Reportes PDF consolidados
- Visualizaciones PNG/JPG para presentaciones
- Exportaciones a Excel con datos agregados (no crudos)
- Integración con Google Sheets para colaboración

### 🎯 7. Sobre evolución futura

**¿Qué funcionalidades están preparadas para agregar en una futura versión?**  
El sistema está diseñado para incorporar:
- Scoring de leads basado en comportamiento y características
- Análisis de lifetime value por programa y marca
- Automatización completa de carga de datos desde múltiples fuentes
- Integración con sistemas de CRM y marketing automation
- Análisis de sentimiento en interacciones con leads
- Recomendaciones de optimización automáticas

**¿Qué tan escalable es el sistema para incorporar nuevos análisis o nuevas marcas si crece la universidad?**  
El sistema está diseñado con alta escalabilidad:
- Arquitectura modular que permite añadir nuevos análisis sin modificar el núcleo
- Configuración centralizada que facilita la incorporación de nuevas marcas
- Procesamiento paralelo para manejar volúmenes crecientes de datos
- Separación clara entre lógica de negocio y visualización
- Capacidad de personalizar modelos por marca o programa
