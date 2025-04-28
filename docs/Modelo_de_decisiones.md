# Motor de Decisión: Funcionamiento, Análisis y Outcomes

## 1. Estructura y Funcionamiento del Motor

### 1.1 Componentes Principales

El Motor de Decisión está compuesto por tres módulos fundamentales:

1. **Módulo de Carga de Datos** (`cargar_datos_individuales.py`): 
   - Carga y valida datos de leads y matrículas desde archivos CSV
   - Asegura la integridad de los datos y las relaciones entre tablas
   - Convierte los formatos de fecha y asegura la consistencia de tipos de datos

2. **Módulo de Métricas y Distribución** (`estimador_valores.py`):
   - Distribuye los costos totales de marketing entre los leads generados
   - Calcula métricas clave de rendimiento para diferentes segmentos
   - Proporciona la base cuantitativa para la toma de decisiones

3. **Módulo de Predicción y Recomendación**:
   - Utiliza los datos históricos para generar modelos predictivos
   - Estima resultados futuros basados en diferentes escenarios
   - Recomienda acciones específicas para optimizar el rendimiento

### 1.2 Flujo de Datos y Procesamiento

```
[CSVs de Leads y Matrículas] → [Carga y Validación] → [Cálculo de Métricas Base] 
                              → [Modelado Predictivo] → [Generación de Recomendaciones]
```

El flujo de datos comienza con la información cruda de leads y matrículas, pasa por procesos de transformación y análisis, y culmina con recomendaciones accionables para las campañas de marketing.

## 2. Análisis y Métricas

### 2.1 Métricas Fundamentales

El motor calcula y analiza sistemáticamente las siguientes métricas clave:

#### Métricas de Costo
- **CPL (Costo por Lead)**: `costo_total / total_leads`
- **CPA (Costo por Adquisición)**: `costo_total / total_matriculas`

#### Métricas de Conversión
- **Tasa de Conversión General**: `(total_matriculas / total_leads) * 100`
- **Tasas de Conversión Segmentadas**: Por marca, programa académico y origen

#### Métricas de Eficiencia
- **Eficiencia de Canales**: Relación entre inversión y resultados por canal
- **Rendimiento de Programas**: Comparativa de conversión entre programas

### 2.2 Segmentación y Análisis Multidimensional

El motor realiza análisis segmentado en múltiples dimensiones:

```
Por Marca → Por Programa → Por Canal → Por Período → Por Estado del Lead
```

Esta segmentación permite identificar:
- Qué marcas tienen mejor rendimiento
- Qué programas generan mayor interés
- Qué canales de captación son más efectivos
- Cómo fluctúa el rendimiento en diferentes períodos
- Dónde ocurren los principales abandonos en el funnel

## 3. Modelos Predictivos

### 3.1 Tipos de Modelos Implementados

El motor utiliza varios modelos predictivos para anticipar resultados:

1. **Modelo de Conversión de Leads**:
   - Predice la probabilidad de que un lead se convierta en matrícula
   - Utiliza variables como: origen, programa, marca, tiempo de respuesta, interacciones
   - Técnica: Regresión logística y árboles de decisión

2. **Modelo de Proyección de Volumen**:
   - Estima el número de leads y matrículas por período
   - Considera estacionalidad, tendencias y eventos especiales
   - Técnica: Series temporales (ARIMA) y modelos de regresión

3. **Modelo de Optimización de Presupuesto**:
   - Determina la distribución óptima del presupuesto entre canales
   - Maximiza el número de matrículas con restricciones presupuestarias
   - Técnica: Algoritmos de optimización y programación lineal

### 3.2 Entrenamiento y Validación

Los modelos se entrenan con datos históricos y se validan utilizando:
- Validación cruzada (k-fold)
- Conjuntos de prueba independientes
- Monitoreo de rendimiento en tiempo real

Las métricas de validación incluyen:
- Precisión y recall para modelos de clasificación
- MAE y RMSE para modelos de regresión
- Lift y ganancia para modelos de propensión

## 4. Outcomes y Recomendaciones

### 4.1 Tipos de Recomendaciones Generadas

El motor genera automáticamente recomendaciones como:

1. **Recomendaciones de Asignación Presupuestaria**:
   ```
   "Incrementar presupuesto en canal Facebook para programa MBA en 25%"
   "Reducir inversión en LinkedIn para Licenciatura en Derecho en 15%"
   ```

2. **Recomendaciones de Calendario**:
   ```
   "Intensificar campañas para Maestrías en Educación durante Mayo-Junio"
   "Evitar grandes inversiones en período vacacional para programas de Doctorado"
   ```

3. **Recomendaciones de Optimización del Funnel**:
   ```
   "Revisar proceso de seguimiento en fase de calificación para Licenciatura en Psicología"
   "Mejorar material informativo para programa de Maestría en Finanzas"
   ```

### 4.2 Formato de Presentación

Las recomendaciones se presentan en:
- Tableros interactivos con métricas clave
- Informes automáticos periódicos
- Alertas en tiempo real cuando se detectan anomalías
- Proyecciones de escenarios "what-if" para evaluar diferentes estrategias

## 5. Aplicación para Planificación de Campañas

### 5.1 Proceso de Planificación Basado en Datos

1. **Definición de Objetivos**:
   - Establecer metas de matrículas por programa y marca
   - Definir restricciones presupuestarias

2. **Generación de Escenarios**:
   - El modelo proyecta resultados basados en datos históricos
   - Se simulan diferentes distribuciones presupuestarias

3. **Optimización y Calendarización**:
   - Se selecciona el escenario óptimo según objetivos
   - Se genera un calendario de inversión por canal

4. **Monitoreo y Ajuste**:
   - Seguimiento continuo del rendimiento vs. proyecciones
   - Ajustes en tiempo real basados en el rendimiento actual

### 5.2 Ejemplo de Planificación

**Caso**: Campaña para nueva Maestría en Marketing Digital

**Input al motor**:
- Objetivo: 50 matrículas
- Presupuesto máximo: $30,000
- Período: 3 meses

**Output del motor**:
```
Distribución recomendada:
- Facebook: $12,000 (40%)
- Google Ads: $9,000 (30%)
- LinkedIn: $6,000 (20%)
- Email Marketing: $3,000 (10%)

Proyección esperada:
- Leads totales: 800
- Tasa de conversión estimada: 6.5%
- Matrículas esperadas: 52
- CPA proyectado: $577

Calendarización:
- Mes 1: 50% del presupuesto
- Mes 2: 30% del presupuesto
- Mes 3: 20% del presupuesto
```

## 6. Integración en el Flujo de Trabajo

El Motor de Decisión se integra en el flujo de trabajo de marketing a través de:

1. **Ciclo de Planificación**:
   - Análisis histórico
   - Proyección y presupuestación
   - Implementación y seguimiento
   - Evaluación y retroalimentación

2. **Dashboard en Tiempo Real**:
   - Métricas actualizadas diariamente
   - Comparación vs. proyecciones
   - Alertas sobre desviaciones significativas

3. **Retroalimentación al Modelo**:
   - Los resultados reales alimentan el modelo
   - Mejora continua de la precisión predictiva
   - Adaptación a cambios en el mercado o comportamiento de los leads

---

## Apéndice: Fórmulas Clave

### Distribución de Presupuesto
```
Presupuesto_Canal = Presupuesto_Total * (Peso_Canal / Suma_Pesos)
```
Donde `Peso_Canal` se calcula considerando el rendimiento histórico y el potencial predicho.

### Estimación de Leads Necesarios
```
Leads_Necesarios = Objetivo_Matriculas / Tasa_Conversion_Estimada
```

### Presupuesto Requerido
```
Presupuesto_Requerido = Leads_Necesarios * CPL_Promedio_Ponderado
```

### Score de Propensión de Lead
```
Score_Propensión = f(Origen, Programa, Marca, Tiempo_Respuesta, Interacciones)
```
Donde `f()` es la función predictiva entrenada con datos históricos. 