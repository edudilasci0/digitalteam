# Especificación Técnica: Motor de Decisión Educativo y Predictivo

Este documento proporciona información técnica detallada sobre los componentes internos, algoritmos y arquitectura del sistema, orientado a desarrolladores y personal técnico.

## 1. Arquitectura de Generación de Reportes

### 1.1 Pipeline de Procesamiento de Datos
El sistema utiliza un pipeline secuencial para transformar los datos brutos en reportes estructurados:

```
Datos Brutos → Preprocesamiento → Agregación → Modelado → Visualización → Exportación Excel
```

### 1.2 Estructura Interna del Motor de Reportes
```python
# Componentes técnicos principales
- Capa de Acceso a Datos (load_dataframe, get_brand_path)
- Capa de Procesamiento (agregación, normalización)
- Capa de Análisis (métricas, proyecciones)
- Capa de Visualización (Excel con XlsxWriter)
```

El flujo de datos sigue un patrón MVC modificado:
1. **Modelo**: Gestión y manipulación de DataFrames de pandas
2. **Vista**: Generación de visualizaciones y exportación Excel
3. **Controlador**: Funciones de app_motor.py que coordinan el proceso

## 2. Algoritmos de Estimación de Leads

### 2.1 Proyección Lineal Proporcional con Intervalos de Confianza
```python
def proyeccion_lineal_con_intervalos(leads_actuales, ratio_tiempo, historico_leads=None):
    """Proyección simple basada en el tiempo transcurrido con intervalos de confianza"""
    if ratio_tiempo > 0:
        # Predicción central
        proyeccion_central = leads_actuales / ratio_tiempo
        
        # Intervalos de confianza basados en variabilidad histórica
        if historico_leads is not None and len(historico_leads) > 5:
            # Calcular coeficiente de variación histórico
            cv = historico_leads.std() / historico_leads.mean()
            
            # Ajustar variabilidad según tiempo restante
            factor_tiempo = np.sqrt(1 - ratio_tiempo)  # Mayor incertidumbre al inicio
            
            # Calcular intervalos
            margen = proyeccion_central * cv * factor_tiempo
            
            # Intervalos con 95% de confianza (aproximado)
            limite_inferior = max(0, proyeccion_central - 1.96 * margen)
            limite_superior = proyeccion_central + 1.96 * margen
            
            return proyeccion_central, (limite_inferior, limite_superior)
        else:
            # Intervalos simplificados por defecto (±15%)
            return proyeccion_central, (proyeccion_central * 0.85, proyeccion_central * 1.15)
    return 0, (0, 0)
```

Esta implementación mejorada incluye obligatoriamente intervalos de confianza para la proyección de leads, que se calculan utilizando:
- El coeficiente de variación histórico cuando hay suficientes datos disponibles
- Un factor de tiempo que amplía los intervalos al inicio de la campaña (mayor incertidumbre)
- Un valor z=1.96 para un nivel de confianza del 95%

### 2.2 Modelo de Series Temporales con Intervalos
El sistema implementa un análisis de tendencia utilizando:
- Descomposición de series temporales (tendencia, estacionalidad, residuo)
- Análisis de patrones semanales con corrección según día de la semana
- Ponderación de datos recientes (mayor influencia de datos recientes)
- **Intervalos de confianza bootstrap** aplicando remuestreo de los residuos

```python
def proyeccion_series_temporales(df_historico, periodos_futuros=4):
    """
    Proyección basada en descomposición de series temporales
    con intervalos de confianza
    """
    # Crear y ajustar modelo de series temporales
    modelo = ExponentialSmoothing(
        df_historico['leads'],
        trend='add',
        seasonal='add',
        seasonal_periods=7  # Patrón semanal
    ).fit()
    
    # Predicción central
    prediccion = modelo.forecast(periodos_futuros)
    
    # Generar intervalos de confianza
    intervalos = modelo.get_prediction(
        start=len(df_historico), 
        end=len(df_historico)+periodos_futuros-1
    ).conf_int(alpha=0.05)  # 95% de confianza
    
    return prediccion, (intervalos.iloc[:, 0], intervalos.iloc[:, 1])
```

El modelo detecta patrones como:
- Estacionalidad semanal (días de mayor rendimiento)
- Tendencias a corto plazo (últimas 2-4 semanas)
- Patrones de conversión según canal

## 3. Generación de Escenarios

### 3.1 Implementación Matemática con Intervalos de Confianza
```python
def calcular_escenarios_con_intervalos(base_proyeccion, intervalos_base, tasa_conversion):
    """Genera tres escenarios de proyección con intervalos de confianza"""
    # Desempaquetar intervalos base
    limite_inferior_base, limite_superior_base = intervalos_base
    
    # Calcular margen de variación proporcional
    margen_proporcional = (limite_superior_base - limite_inferior_base) / (2 * base_proyeccion) if base_proyeccion > 0 else 0.15
    
    # Generar escenarios con sus respectivos intervalos
    escenarios = {
        "actual": {
            "central": base_proyeccion,
            "intervalos": (limite_inferior_base, limite_superior_base)
        },
        "optimista": {
            "central": base_proyeccion * 1.05,  # Mejora del 5% en conversión
            "intervalos": (
                base_proyeccion * 1.05 * (1 - margen_proporcional),
                base_proyeccion * 1.05 * (1 + margen_proporcional)
            )
        },
        "agresivo": {
            "central": base_proyeccion * 1.2,     # Aumento del 20% en inversión
            "intervalos": (
                base_proyeccion * 1.2 * (1 - margen_proporcional * 1.2),  # Mayor incertidumbre en escenario agresivo
                base_proyeccion * 1.2 * (1 + margen_proporcional * 1.2)
            )
        }
    }
    return escenarios
```

### 3.2 Variables de Control
- **Elasticidad del canal**: Sensibilidad de generación de leads ante cambios de inversión
- **Factor estacional**: Ajuste según comportamiento histórico del periodo
- **Factor de saturación**: Modelo logarítmico que captura rendimientos decrecientes

La elasticidad se calcula mediante regresión de datos históricos:
```python
def calcular_elasticidad(df_hist):
    # Datos normalizados para comparabilidad
    X = df_hist["inversion_normalizada"].values.reshape(-1, 1)
    y = df_hist["leads_normalizados"].values
    
    # Regresión log-lineal para capturar elasticidad
    modelo = LinearRegression()
    modelo.fit(np.log(X), np.log(y))
    
    # El coeficiente representa la elasticidad
    return modelo.coef_[0]
```

## 4. Cálculo de Intervalos de Confianza

### 4.1 Intervalos de Confianza con Random Forest
```python
def predict_matriculas_interval(model, df_future, confidence_level=0.95):
    """
    Predicciones con intervalos de confianza usando RandomForest
    """
    if model is None:
        return np.zeros(len(df_future)), (np.zeros(len(df_future)), np.zeros(len(df_future)))
    
    X_future = df_future[["leads", "inversion"]]
    
    # Predicción central
    preds = model.predict(X_future)
    
    # Calcular intervalos usando los árboles individuales del RandomForest
    tree_preds = np.array([tree.predict(X_future) for tree in model.estimators_])
    
    # Desviación estándar basada en predicciones de árboles individuales
    std_dev = np.std(tree_preds, axis=0)
    
    # Factor z para el nivel de confianza (aproximación)
    z = 1.96  # para 95% de confianza
    
    lower_bound = preds - z * std_dev
    upper_bound = preds + z * std_dev
    
    # Asegurar que los límites no sean negativos
    lower_bound = np.maximum(lower_bound, 0)
    
    return preds, (lower_bound, upper_bound)
```

Este enfoque aprovecha la naturaleza de Random Forest como ensamble: cada árbol del bosque genera una predicción, y la distribución de estas predicciones se utiliza para calcular intervalos de confianza. Esto es una aproximación de la incertidumbre del modelo.

### 4.2 Corrección Basada en Tiempo Restante
El sistema ajusta los intervalos según las semanas restantes:
- **Ajuste proporcional**: Intervalos más amplios cuando queda más tiempo
- **Factor de incertidumbre**: 
  ```python
  margen_error = proyeccion_final * (semanas_restantes / duracion_total) * 0.2
  ```

Este enfoque reconoce que la incertidumbre aumenta con el horizonte de predicción, ampliando los intervalos cuando queda más tiempo para el final de la campaña.

### 4.3 Validación y Calibración de Intervalos
El sistema evalúa y ajusta periódicamente la calidad de los intervalos de confianza:

```python
def validar_intervalos_confianza(predicciones_historicas, intervalos_historicos, resultados_reales):
    """
    Evalúa qué porcentaje de resultados reales cayeron dentro de los intervalos predichos
    y calibra los intervalos futuros
    """
    # Contar cuántos resultados reales cayeron dentro del intervalo
    dentro_intervalo = 0
    
    for i, real in enumerate(resultados_reales):
        limite_inf, limite_sup = intervalos_historicos[i]
        if limite_inf <= real <= limite_sup:
            dentro_intervalo += 1
    
    # Calcular porcentaje de acierto
    porcentaje_acierto = dentro_intervalo / len(resultados_reales) * 100
    
    # Factor de calibración para ajustar futuros intervalos
    # Si el porcentaje es muy bajo, ampliamos los intervalos
    # Si es muy alto, los reducimos
    factor_calibracion = 1.0
    
    if porcentaje_acierto < 90:  # Menos del 90% dentro del intervalo
        factor_calibracion = 1 + (90 - porcentaje_acierto) / 100
    elif porcentaje_acierto > 98:  # Más del 98% dentro del intervalo
        factor_calibracion = 0.95  # Reducción ligera
    
    return porcentaje_acierto, factor_calibracion
```

Esta función permite que el sistema aprenda de sus propias predicciones y mejore continuamente la precisión de sus intervalos de confianza.

## 5. Implementación de Visualizaciones Avanzadas en Excel

### 5.1 Generación de Gráficos en Excel
```python
# Ejemplo de código para gráfico de proyecciones
chart = workbook.add_chart({'type': 'line'})

# Predicción central
chart.add_series({
    'name': 'Predicción',
    'categories': ['Predicciones ML', 2, 0, 1 + len(df_pred), 0],
    'values': ['Predicciones ML', 2, 1, 1 + len(df_pred), 1],
    'line': {'color': 'blue', 'width': 2.5},
    'marker': {'type': 'circle', 'size': 5, 'fill': {'color': 'blue'}}
})

# Límites inferior y superior
chart.add_series({
    'name': 'Límite Inferior',
    'categories': ['Predicciones ML', 2, 0, 1 + len(df_pred), 0],
    'values': ['Predicciones ML', 2, 2, 1 + len(df_pred), 2],
    'line': {'color': 'orange', 'width': 1, 'dash_type': 'dash'},
})

chart.add_series({
    'name': 'Límite Superior',
    'categories': ['Predicciones ML', 2, 0, 1 + len(df_pred), 0],
    'values': ['Predicciones ML', 2, 3, 1 + len(df_pred), 3],
    'line': {'color': 'green', 'width': 1, 'dash_type': 'dash'},
})

# Configurar gráfico
chart.set_title({'name': 'Proyección de Matrículas'})
chart.set_x_axis({'name': 'Semana +'})
chart.set_y_axis({'name': 'Matrículas Proyectadas'})
chart.set_style(42)
worksheet.insert_chart('F2', chart, {'x_offset': 25, 'y_offset': 10, 'x_scale': 1.5, 'y_scale': 1.5})
```

### 5.2 Estructura de Reportes Excel
El sistema genera reportes Excel con varias hojas estructuradas:

| Hoja Excel | Descripción | Visualizaciones |
|------------|-------------|-----------------|
| Resumen Ejecutivo | KPIs y métricas clave | - |
| Datos Históricos | Dataset completo con formato | Filtros automáticos |
| Métricas por Canal | Análisis comparativo por canal | Gráfico de barras |
| Proyecciones | Estimaciones y escenarios | Gráfico de líneas |
| Atribución | Análisis de atribución multicanal | Gráfico de sectores |
| Predicciones ML | Resultados del modelo ML | Gráfico de líneas con intervalos |

## 6. Calibración del Modelo

### 6.1 Validación Cruzada
El sistema implementa validación para evaluar precisión:
- Hold-out validation: 70% entrenamiento, 30% validación
- Error cuadrático medio (MSE) como métrica de evaluación
- Ajuste regularizado para evitar sobreajuste

### 6.2 Matriz de Confusión para Escenarios
```
           | Real BAJO | Real MEDIO | Real ALTO
Pred BAJO  |    TP     |     FP     |    FP
Pred MEDIO |    FN     |     TP     |    FP
Pred ALTO  |    FN     |     FN     |    TP
```

Esta matriz ayuda a evaluar la precisión del modelo en la clasificación de escenarios (bajo/medio/alto rendimiento).

### 6.3 Actualización Dinámica
- **Frecuencia**: Recalibración semanal del modelo
- **Factores de peso**: Mayor influencia de datos recientes (decay factor)
- **Detección de anomalías**: Z-score > 3 para identificar outliers

El factor de decaimiento temporal se implementa como:
```python
def aplicar_ponderacion_temporal(df, col_fecha, half_life=30):
    """Aplica factor de decaimiento exponencial basado en fecha"""
    fechas = pd.to_datetime(df[col_fecha])
    fecha_max = fechas.max()
    
    # Calcular días desde la fecha más reciente
    dias_desde_max = (fecha_max - fechas).dt.days
    
    # Calcular pesos usando decaimiento exponencial
    pesos = np.exp(-(np.log(2)/half_life) * dias_desde_max)
    
    return pesos
```

## 7. Optimizaciones de Rendimiento

### 7.1 Vectorización y Paralelización
```python
# Entrenamiento paralelo de Random Forest
model = RandomForestRegressor(
    n_estimators=100, 
    random_state=42,
    n_jobs=-1  # Utiliza todos los núcleos disponibles
)
model.fit(X, y)
```

### 7.2 Caching y Memoización
```python
# Guardar y cargar modelo entrenado
import joblib

# Guardar modelo
joblib.dump(model, modelo_path)

# Cargar modelo previamente entrenado
try:
    model = joblib.load(modelo_path)
except:
    # Entrenar nuevo modelo si el anterior no existe o está corrupto
    model = train_new_model(data)
```

### 7.3 Organización de datos y precálculo
El sistema gestiona datos de alta frecuencia con una estrategia de agregación multinivel:
- Datos diarios → Agregación semanal → Análisis mensual
- Precálculo de métricas costosas (CPA, CPL por canal)
- Uso de índices para búsquedas rápidas en DataFrames grandes

## 8. Módulo de Atribución Multicanal

### 8.1 Implementación de Modelos de Atribución
```python
def calcular_atribucion(df_leads, df_matriculas, modelo="ultimo_clic"):
    """Calcula la atribución según diferentes modelos"""
    # Obtener IDs de leads que se convirtieron en matrículas
    leads_convertidos = df_leads[df_leads["ID"].isin(df_matriculas["ID"])]
    resultados = {}
    
    if modelo == "ultimo_clic":
        # Agrupa por ID y toma el último canal de cada grupo
        for id_lead, grupo in leads_convertidos.groupby("ID"):
            ultimo_canal = grupo.iloc[-1]["canal"]
            if ultimo_canal in resultados:
                resultados[ultimo_canal] += 1
            else:
                resultados[ultimo_canal] = 1
    
    elif modelo == "primer_clic":
        # Similar al anterior pero con el primer canal
        for id_lead, grupo in leads_convertidos.groupby("ID"):
            primer_canal = grupo.iloc[0]["canal"]
            if primer_canal in resultados:
                resultados[primer_canal] += 1
            else:
                resultados[primer_canal] = 1
    
    # ... otras implementaciones de modelos ...
    
    # Convertir a DataFrame para visualización
    df_atribucion = pd.DataFrame({
        "canal": list(resultados.keys()),
        "atribucion": list(resultados.values())
    })
    
    # Calcular porcentajes
    total = df_atribucion["atribucion"].sum()
    df_atribucion["porcentaje"] = df_atribucion["atribucion"] / total * 100
    
    return df_atribucion
```

Esta implementación permite comparar diferentes modelos de atribución para identificar la contribución real de cada canal en el proceso de conversión.

## 9. Detalles de Implementación por Componente

### 9.1 Procesamiento de Datos
- Normalización de fechas con pandas (formato ISO)
- Detección y manejo de valores nulos (relleno estratégico)
- Transformación de tipos para optimizar memoria

### 9.2 Modelo Predictivo (Random Forest)
- Hiperparámetros óptimos: `max_depth=8, min_samples_leaf=5`
- Variables predictoras: leads, inversión, histórico de conversión
- Regularización: valores limitados para evitar sobreajuste

### 9.3 Exportación Excel
- Motor XlsxWriter para optimizar rendimiento
- Estructura de memoria para archivos grandes: escritura por lotes
- Optimización de tamaño del archivo resultante 