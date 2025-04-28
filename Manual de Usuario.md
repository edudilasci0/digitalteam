# Manual de Usuario - Motor de Decisión

## Índice

1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Estructura del Sistema](#estructura-del-sistema)
4. [Flujo de Trabajo Básico](#flujo-de-trabajo-básico)
5. [Módulos Principales](#módulos-principales)
   - [Procesador de Datos](#procesador-de-datos)
   - [Gestor de Modelos](#gestor-de-modelos)
   - [Evaluador de Modelos](#evaluador-de-modelos)
   - [Visualizador](#visualizador)
6. [Línea de Comandos](#línea-de-comandos)
7. [Visualizaciones y Reportes](#visualizaciones-y-reportes)
8. [Análisis de Resultados](#análisis-de-resultados)
9. [Preguntas Frecuentes](#preguntas-frecuentes)
10. [Solución de Problemas](#solución-de-problemas)

## Introducción

El Motor de Decisión es una herramienta para equipos de marketing educativo diseñada para:

- Analizar datos históricos y actuales de leads y matrículas
- Construir modelos predictivos para estimar conversiones futuras
- Generar visualizaciones que faciliten la toma de decisiones
- Evaluar el rendimiento de diferentes modelos predictivos
- Optimizar la asignación de recursos en campañas

Este manual explica cómo utilizar el sistema desde su instalación hasta la interpretación de resultados.

## Instalación

### Requisitos previos

- Python 3.6 o superior
- Pip (gestor de paquetes de Python)
- Espacio en disco para almacenar datos y modelos

### Pasos de instalación

1. Clone el repositorio:
```bash
git clone https://github.com/tu-usuario/sistema-predictor-matriculas.git
cd sistema-predictor-matriculas
```

2. Instale las dependencias:
```bash
pip install -r requirements.txt
```

3. Cree las carpetas necesarias:
```bash
mkdir -p datos/actual datos/historico output/reportes output/modelos output/graficos logs
```

4. Verifique la instalación ejecutando:
```bash
python src/main.py --solo-carga
```

## Estructura del Sistema

El sistema está organizado en módulos específicos, cada uno con una responsabilidad definida:

- **Procesador de Datos** (`src/data/procesador_datos.py`): Carga, limpia y transforma datos
- **Gestor de Modelos** (`src/models/model_manager.py`): Entrena y gestiona modelos predictivos
- **Evaluador de Modelos** (`src/models/evaluador_modelos.py`): Evalúa y compara rendimiento de modelos
- **Visualizador** (`src/visualizacion/visualizador.py`): Genera gráficos y visualizaciones
- **Configuración** (`src/utils/config.py`): Gestiona parámetros de configuración
- **Logging** (`src/utils/logging.py`): Maneja registros de actividad y errores

Además, la estructura de directorios está organizada de la siguiente manera:

- `datos/`: Contiene archivos de datos de entrada
- `output/`: Almacena resultados, modelos y visualizaciones
- `logs/`: Guarda registros de ejecución y errores
- `config/`: Archivos de configuración
- `src/`: Código fuente del sistema

## Flujo de Trabajo Básico

El flujo de trabajo típico para utilizar el sistema es:

1. **Preparación de datos**: Coloque sus archivos de leads y matrículas en formato CSV en la carpeta `datos/actual/`
2. **Procesamiento inicial**: Ejecute el sistema para cargar y preprocesar los datos
3. **Entrenamiento de modelos**: Entrene diferentes modelos predictivos
4. **Evaluación de modelos**: Compare el rendimiento de los modelos
5. **Visualización de resultados**: Genere gráficos y reportes
6. **Análisis y decisiones**: Utilice los resultados para tomar decisiones informadas

### Ejemplo de flujo completo

```bash
# 1. Preparar datos (archivos CSV en datos/actual/)

# 2. Procesar datos y entrenar modelo
python src/main.py --datos-leads datos/actual/leads.csv --datos-matriculas datos/actual/matriculas.csv --tipo-modelo random_forest --guardar-resultados

# 3. Evaluar modelo guardado
python src/main.py --ruta-modelo output/modelos/modelo_principal_random_forest_20230615_120000.pkl --solo-evaluar

# 4. Analizar resultados en la carpeta output/
```

## Módulos Principales

### Procesador de Datos

El módulo `procesador_datos.py` permite trabajar con archivos de leads y matrículas.

#### Funcionalidades principales:

- **Cargar datos**: Importar archivos CSV o Excel
- **Validar datos**: Verificar columnas requeridas y estructura
- **Limpiar datos**: Eliminar duplicados y manejar valores nulos
- **Unir datos**: Combinar información de leads y matrículas
- **Crear características**: Generar nuevas variables para modelado

#### Columnas requeridas:

Para **leads**:
- `id_lead`: Identificador único
- `fecha_creacion`: Fecha de creación del lead
- `origen`: Canal de captación
- `programa`: Programa académico
- `marca`: Marca educativa
- `costo`: Costo de adquisición
- `estado`: Estado del lead

Para **matrículas**:
- `id_matricula`: Identificador de matrícula
- `id_lead`: Identificador del lead asociado
- `fecha_matricula`: Fecha de matrícula
- `programa`: Programa académico
- `marca`: Marca educativa
- `valor_matricula`: Valor de la matrícula

#### Ejemplo de uso avanzado:

```python
from src.data.procesador_datos import ProcesadorDatos

# Inicializar procesador
procesador = ProcesadorDatos()

# Cargar datos
datos_leads = procesador.cargar_datos("datos/actual/leads.csv")
datos_matriculas = procesador.cargar_datos("datos/actual/matriculas.csv")

# Validar estructura
leads_valido, columnas_faltantes = procesador.validar_datos(datos_leads, 'leads')
if not leads_valido:
    print(f"Columnas faltantes: {columnas_faltantes}")

# Limpiar y convertir tipos
datos_leads = procesador.limpiar_datos(datos_leads)
datos_leads = procesador.convertir_tipos_datos(datos_leads, 'leads')
datos_matriculas = procesador.limpiar_datos(datos_matriculas)
datos_matriculas = procesador.convertir_tipos_datos(datos_matriculas, 'matriculas')

# Filtrar datos por origen
datos_leads_filtrados = procesador.filtrar_datos(
    datos_leads, 
    filtros={'origen': ['Facebook', 'Google']}
)

# Unir datos de leads y matrículas
datos_unidos = procesador.unir_leads_matriculas(datos_leads, datos_matriculas)

# Generar características para modelado
datos_procesados = procesador.crear_caracteristicas(datos_unidos)

# Dividir para entrenamiento y prueba
X_train, X_test, y_train, y_test = procesador.dividir_datos_entrenamiento(
    datos_procesados,
    columna_objetivo='convertido',
    test_size=0.25
)
```

### Gestor de Modelos

El módulo `model_manager.py` se encarga de entrenar, evaluar y gestionar modelos predictivos.

#### Modelos soportados:

- **Lineales**: 
  - `linear`: Regresión Lineal
  - `ridge`: Regresión Ridge
  - `lasso`: Regresión Lasso
- **Ensemble**:
  - `random_forest`: Random Forest
  - `gradient_boosting`: Gradient Boosting

#### Funcionalidades principales:

- **Entrenamiento**: Entrenar modelos con diferentes algoritmos
- **Evaluación**: Calcular métricas de rendimiento
- **Guardado/Carga**: Persistir modelos entrenados
- **Predicción**: Generar predicciones con modelos guardados
- **Análisis**: Evaluar importancia de características

#### Ejemplo de uso avanzado:

```python
from src.models.model_manager import ModelManager

# Inicializar gestor de modelos
model_manager = ModelManager(model_name="prediccion_conversion")

# Entrenar modelo con parámetros personalizados
metricas = model_manager.train(
    datos=datos_procesados,
    target_column="convertido",
    features=["origen_Facebook", "origen_Google", "costo", "programa_MBA"],
    categorical_features=["programa", "marca"],
    model_type="random_forest",
    model_params={"n_estimators": 200, "max_depth": 10},
    test_size=0.25,
    cv_folds=5
)

# Guardar modelo entrenado
ruta_modelo = model_manager.save(filename="modelo_conversion_v1.pkl")

# Cargar modelo existente
model_manager.load("output/modelos/modelo_conversion_v1.pkl")

# Realizar predicciones
nuevos_datos = procesador.cargar_datos("datos/actual/nuevos_leads.csv")
nuevos_datos_proc = procesador.crear_caracteristicas(nuevos_datos)
predicciones = model_manager.predict(nuevos_datos_proc)

# Analizar importancia de características
importancias = model_manager.feature_importance()
print(importancias.head(10))  # Top 10 características más importantes
```

### Evaluador de Modelos

El módulo `evaluador_modelos.py` proporciona herramientas para evaluar el rendimiento de modelos predictivos.

#### Funcionalidades principales:

- **Evaluación de regresión**: Calcular MAE, MSE, RMSE, R²
- **Evaluación de clasificación**: Calcular precision, recall, F1, matriz confusión
- **Comparación de modelos**: Contrastar rendimiento de diferentes modelos
- **Visualización**: Generar gráficos de rendimiento
- **Almacenamiento**: Guardar métricas para análisis posterior

#### Ejemplo de uso avanzado:

```python
from src.models.evaluador_modelos import EvaluadorModelos

# Inicializar evaluador
evaluador = EvaluadorModelos()

# Evaluar modelo de regresión
metricas_regresion = evaluador.evaluar_regresion(
    y_true=y_test,
    y_pred=predicciones,
    nombre_modelo="random_forest_v1"
)

# Evaluar modelo de clasificación 
metricas_clasificacion = evaluador.evaluar_clasificacion(
    y_true=y_test_binario,
    y_pred=predicciones_binarias,
    y_prob=probabilidades,  # Probabilidades para curva ROC
    nombre_modelo="rf_clasificacion"
)

# Comparar varios modelos
comparacion = evaluador.comparar_modelos(
    modelos=["linear_v1", "ridge_v1", "random_forest_v1"],
    metricas_clave=["rmse", "r2", "mae"]
)

# Visualizar predicciones vs. valores reales
evaluador.graficar_predicciones_vs_reales(
    y_true=y_test,
    y_pred=predicciones,
    nombre_modelo="random_forest_v1"
)

# Visualizar residuos
evaluador.graficar_residuos(
    y_true=y_test,
    y_pred=predicciones,
    nombre_modelo="random_forest_v1"
)

# Guardar métricas para análisis posterior
ruta_metricas = evaluador.guardar_metricas()
```

### Visualizador

El módulo `visualizador.py` genera gráficos y visualizaciones para analizar datos y resultados.

#### Tipos de visualizaciones:

- **Series temporales**: Evolución de métricas en el tiempo
- **Distribuciones**: Histogramas y densidades de variables
- **Gráficos de barras**: Comparaciones por categorías
- **Gráficos de dispersión**: Relaciones entre variables
- **Matrices de correlación**: Interrelaciones entre variables
- **Gráficos multilinea**: Comparación de series temporales

#### Ejemplo de uso avanzado:

```python
from src.visualizacion.visualizador import Visualizador

# Inicializar visualizador
visualizador = Visualizador()

# Gráfico de serie temporal (leads por semana)
datos_temporales = datos_unidos.groupby(pd.Grouper(key='fecha_creacion', freq='W')).size().reset_index()
datos_temporales.columns = ['fecha_creacion', 'conteo']

visualizador.graficar_serie_temporal(
    datos=datos_temporales,
    columna_fecha='fecha_creacion',
    columna_valor='conteo',
    titulo='Evolución semanal de leads',
    nombre_archivo='evolucion_leads_semanal.png'
)

# Distribución de costos por lead
visualizador.graficar_distribucion(
    datos=datos_leads,
    columna='costo',
    titulo='Distribución de costo por lead',
    kde=True
)

# Leads por origen (barras)
visualizador.graficar_barras(
    datos=datos_leads,
    columna_categoria='origen',
    columna_valor=None,  # Cuenta frecuencias
    titulo='Leads por canal de origen',
    orientacion='horizontal',
    limite_categorias=10
)

# Relación entre costo y conversión
visualizador.graficar_dispersion(
    datos=datos_procesados,
    columna_x='costo',
    columna_y='tasa_conversion',
    columna_color='origen',
    titulo='Relación entre costo y conversión por origen',
    mostrar_regresion=True
)

# Matriz de correlación
columnas_numericas = ['costo', 'dias_hasta_contacto', 'tasa_conversion', 'valor_matricula']
visualizador.graficar_matriz_correlacion(
    datos=datos_procesados,
    columnas=columnas_numericas,
    titulo='Correlaciones entre variables principales'
)

# Comparación multilinea
visualizador.graficar_multilinea(
    datos=datos_tendencia,
    columna_x='fecha',
    columnas_y=['leads', 'matriculas', 'proyeccion'],
    titulo='Comparación de tendencias',
    etiqueta_y='Cantidad'
)
```

## Línea de Comandos

El sistema puede ejecutarse desde la línea de comandos con diferentes opciones y parámetros.

### Comando principal

```bash
python src/main.py [opciones]
```

### Opciones disponibles

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--datos-leads` | Ruta al archivo CSV de leads | `--datos-leads datos/actual/leads.csv` |
| `--datos-matriculas` | Ruta al archivo CSV de matrículas | `--datos-matriculas datos/actual/matriculas.csv` |
| `--config` | Ruta al archivo de configuración | `--config mi_config.yaml` |
| `--guardar-resultados` | Guarda resultados en disco | `--guardar-resultados` |
| `--dir-salida` | Directorio para guardar resultados | `--dir-salida resultados_personalizados/` |
| `--tipo-modelo` | Tipo de modelo a entrenar | `--tipo-modelo random_forest` |
| `--target` | Columna objetivo para el modelo | `--target convertido` |
| `--solo-carga` | Solo cargar datos sin entrenar modelo | `--solo-carga` |
| `--solo-evaluar` | Evaluar modelo sin entrenarlo | `--solo-evaluar` |
| `--ruta-modelo` | Ruta a un modelo guardado | `--ruta-modelo output/modelos/modelo.pkl` |

### Ejemplos de comandos comunes

```bash
# Cargar datos, entrenar modelo y guardar resultados
python src/main.py --datos-leads datos/actual/leads.csv --datos-matriculas datos/actual/matriculas.csv --tipo-modelo gradient_boosting --guardar-resultados

# Solo cargar y procesar datos
python src/main.py --datos-leads datos/actual/leads.csv --datos-matriculas datos/actual/matriculas.csv --solo-carga

# Evaluar un modelo guardado previamente
python src/main.py --ruta-modelo output/modelos/modelo_principal_random_forest_20230615_120000.pkl --solo-evaluar --datos-leads datos/actual/leads.csv --datos-matriculas datos/actual/matriculas.csv
```

## Visualizaciones y Reportes

El sistema genera diferentes tipos de visualizaciones y reportes:

### Tipos de visualizaciones

1. **Visualizaciones de datos**:
   - Distribución de leads por origen
   - Evolución temporal de leads
   - Comparaciones por programa/marca
   - Matrices de correlación entre variables

2. **Visualizaciones de modelos**:
   - Predicciones vs. valores reales
   - Análisis de residuos
   - Importancia de características
   - Comparación de rendimiento entre modelos

### Ubicación de los resultados

Todos los resultados generados se guardan en la carpeta `output/` con la siguiente estructura:

- `output/graficos/`: Visualizaciones de datos y análisis exploratorio
- `output/reportes/`: Reportes de evaluación de modelos y resultados
- `output/modelos/`: Modelos entrenados guardados en formato PKL

### Interpretación de visualizaciones

- **Gráficos de series temporales**: Muestran tendencias y patrones estacionales en leads o conversiones.
- **Gráficos de barras**: Comparan rendimiento entre diferentes categorías (origen, programa, etc.).
- **Gráficos de dispersión**: Revelan relaciones entre variables (ej. costo vs. conversión).
- **Predicciones vs. reales**: La cercanía a la línea diagonal indica precisión del modelo.
- **Análisis de residuos**: Distribución simétrica alrededor de cero indica buen ajuste del modelo.
- **Importancia de características**: Identifica qué variables tienen mayor influencia en las predicciones.

## Análisis de Resultados

### Métricas de evaluación

#### Para modelos de regresión:

- **MAE (Error Absoluto Medio)**: Error promedio en términos absolutos
- **RMSE (Raíz del Error Cuadrático Medio)**: Error promedio ponderando más los errores grandes
- **R² (Coeficiente de determinación)**: Proporción de varianza explicada por el modelo (0-1)
- **Error Porcentual Medio**: Error promedio expresado como porcentaje

#### Para modelos de clasificación:

- **Accuracy**: Proporción de predicciones correctas
- **Precision**: Proporción de positivos predichos que son realmente positivos
- **Recall**: Proporción de positivos reales que fueron identificados correctamente
- **F1-Score**: Media armónica de precision y recall
- **AUC**: Área bajo la curva ROC (0.5-1.0)

### Cómo interpretar las métricas

| Métrica | Bueno | Moderado | Deficiente |
|---------|-------|----------|------------|
| R² | >0.7 | 0.4-0.7 | <0.4 |
| RMSE | Depende del rango de datos, menor es mejor |
| MAE | Depende del rango de datos, menor es mejor |
| Accuracy | >0.8 | 0.6-0.8 | <0.6 |
| F1-Score | >0.8 | 0.6-0.8 | <0.6 |
| AUC | >0.8 | 0.7-0.8 | <0.7 |

### Comparación de modelos

Para comparar el rendimiento de diferentes modelos, examine:

1. **Métricas clave**: Compare R², RMSE, MAE para modelos de regresión; Accuracy, F1, AUC para clasificación
2. **Visualizaciones**: Compare gráficos de predicciones vs. reales y distribución de residuos
3. **Complejidad**: Modelos más simples son preferibles si tienen rendimiento similar a los complejos
4. **Tiempo de entrenamiento/predicción**: Modelos más rápidos son ventajosos para actualizaciones frecuentes
5. **Interpretabilidad**: Modelos lineales son más fáciles de interpretar que Random Forest o Gradient Boosting

## Preguntas Frecuentes

### Datos y Preparación

**P: ¿Qué formato deben tener mis archivos de datos?**  
R: Los archivos deben estar en formato CSV, preferiblemente con delimitador coma (,) y con las columnas requeridas mencionadas en la sección de Procesador de Datos.

**P: ¿Cómo manejo valores faltantes en mis datos?**  
R: El sistema detecta valores faltantes durante la validación. Para columnas críticas, considere imputar valores o filtrar filas antes de procesar los datos.

**P: ¿Puedo usar otras fuentes de datos además de CSV?**  
R: Actualmente el sistema soporta CSV y Excel. Para otros formatos, conviértalos primero a uno de estos formatos.

### Modelos y Entrenamiento

**P: ¿Qué modelo debo usar para mi caso?**  
R: Depende de sus datos y objetivo:
- Para predicciones numéricas precisas: Gradient Boosting o Random Forest
- Para modelos interpretables: Linear, Ridge o Lasso
- Para datasets pequeños: Ridge o Lasso para evitar sobreajuste

**P: ¿Cómo evito el sobreajuste?**  
R: Utilice validación cruzada (ya implementada), reduzca la complejidad del modelo o aumente el tamaño del conjunto de datos.

**P: ¿Con qué frecuencia debo reentrenar mis modelos?**  
R: Depende de cómo cambian sus datos. Para campañas educativas, se recomienda reentrenar mensualmente o cuando haya cambios significativos en estrategias de marketing.

### Resultados e Interpretación

**P: ¿Cómo interpreto la importancia de características?**  
R: Las características con mayor valor tienen más impacto en las predicciones. Use esta información para identificar qué variables influyen más en las conversiones.

**P: ¿Qué hago si mi modelo tiene un rendimiento pobre?**  
R: Considere:
1. Añadir más datos de entrenamiento
2. Crear características adicionales
3. Probar diferentes tipos de modelos
4. Ajustar hiperparámetros
5. Verificar la calidad de los datos

**P: ¿Cómo utilizo las predicciones para optimizar campañas?**  
R: Identifique segmentos con alta probabilidad de conversión y enfoque recursos en ellos. Use la importancia de características para ajustar estrategias de marketing.

## Solución de Problemas

### Errores comunes y soluciones

#### Error: "No se encuentra el módulo X"

**Causa**: Estructura de directorios incorrecta o error en el Python PATH.  
**Solución**: 
- Verifique que está ejecutando desde la raíz del proyecto
- Confirme que todas las dependencias están instaladas
- Ejecute `python -m src.main` en lugar de `python src/main.py`

#### Error: "No se pueden cargar los datos"

**Causa**: Archivo no encontrado o formato incorrecto.  
**Solución**:
- Verifique las rutas a los archivos
- Confirme que los archivos existen y tienen permisos de lectura
- Verifique el formato del CSV (delimitadores, encabezados)

#### Error: "Error al entrenar el modelo"

**Causa**: Problemas con los datos o configuración del modelo.  
**Solución**:
- Verifique la calidad de los datos (valores nulos, outliers)
- Revise los parámetros del modelo
- Consulte los logs detallados en la carpeta `logs/`

#### Advertencia: "Características con varianza cero"

**Causa**: Algunas columnas tienen el mismo valor para todas las filas.  
**Solución**: 
- Elimine estas columnas de los datos de entrada
- Verifique la calidad y diversidad de sus datos

### Registro de errores

Para diagnósticos detallados, revise los archivos de log generados en la carpeta `logs/`. Estos archivos contienen información detallada sobre la ejecución del sistema, incluidos errores, advertencias y detalles del procesamiento.

### Contacto y soporte

Para soporte adicional:
- Consulte la documentación detallada en `docs/`
- Revise el repositorio del proyecto para actualizaciones y soluciones conocidas
- Contacte al equipo de desarrollo para problemas no resueltos 