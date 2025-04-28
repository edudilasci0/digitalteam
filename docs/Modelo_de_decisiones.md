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
[CSVs de Leads, Matrículas y Planificación] → [Carga y Validación] → [Cálculo de Métricas Base] 
                                            → [Modelado Predictivo] → [Generación de Recomendaciones]
```

El flujo de datos comienza con la información cruda de leads, matrículas y planificación de campañas (exportada desde Google Sheets), pasa por procesos de transformación y análisis, y culmina con recomendaciones accionables para las campañas de marketing.

### 1.3 Integración con Google Sheets

El motor se integra con Google Sheets mediante un flujo de trabajo simplificado:

1. El equipo planifica campañas en Google Sheets utilizando una plantilla establecida
2. La planificación se exporta como CSV y se coloca en la carpeta adecuada
3. El motor procesa estos datos para generar recomendaciones
4. Los resultados pueden visualizarse o importarse de vuelta a Google Sheets

Esta integración permite una colaboración fluida sin necesidad de programación de APIs.

## 2. Análisis y Métricas

### 2.1 Métricas Fundamentales

El motor calcula y analiza sistemáticamente las siguientes métricas clave:

#### Métricas de Costo
- **CPL (Costo por Lead)**: `costo_total_campaña / total_leads`
- **CPA (Costo por Adquisición)**: `costo_total_campaña / total_matriculas`

#### Métricas de Conversión
- **Tasa de Conversión General**: `(total_matriculas / total_leads) * 100`
- **Tasas de Conversión Segmentadas**: Por marca, programa académico y origen

#### Métricas de Eficiencia
- **Eficiencia de Canales**: Relación entre inversión y resultados por canal
- **Rendimiento de Programas**: Comparativa de conversión entre programas

### 2.2 Modelo de Presupuestación y Análisis

El motor trabaja con un modelo donde:

- **El presupuesto se asigna a nivel de campaña completa**, no por programa individual
- Cada campaña incluye múltiples programas que comparten el presupuesto común
- Los objetivos se establecen para el total de matrículas de la campaña
- La demanda natural determina qué programas generan más leads dentro de una campaña
- El análisis de rendimiento por programa se realiza para optimización táctica, no para planificación presupuestaria inicial

### 2.3 Segmentación y Análisis Multidimensional

El motor realiza análisis segmentado en múltiples dimensiones:

```
Por Campaña → Por Marca → Por Canal → Por Programa → Por Período → Por Estado del Lead
```

Esta segmentación permite identificar:
- Qué campañas tienen mejor rendimiento
- Qué marcas tienen mejor respuesta
- Qué canales de captación son más efectivos
- Qué programas generan mayor interés natural
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
   - Determina la distribución óptima del presupuesto entre canales a nivel de campaña
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
   "Incrementar inversión en canal Facebook para la campaña Q3 en 25%"
   "Reducir inversión en LinkedIn para la campaña actual en 15%"
   ```

2. **Recomendaciones de Calendario**:
   ```
   "Intensificar inversión durante las semanas 3-4 para la campaña actual"
   "Evitar grandes inversiones en período vacacional para las campañas de Doctorado"
   ```

3. **Recomendaciones de Optimización del Funnel**:
   ```
   "Revisar proceso de seguimiento para leads de Licenciatura en Psicología"
   "Mejorar material informativo para programa de Maestría en Finanzas"
   ```

### 4.2 Formato de Presentación

Las recomendaciones se presentan en:
- Archivos CSV fácilmente importables a Google Sheets
- Informes automáticos periódicos
- Archivos de visualización para presentaciones
- Proyecciones de escenarios "what-if" para evaluar diferentes estrategias

## 5. Aplicación para Planificación de Campañas

### 5.1 Proceso de Planificación Basado en Datos

1. **Definición de Objetivos**:
   - Establecer metas de matrículas totales por campaña
   - Definir restricciones presupuestarias por campaña
   - Identificar los programas incluidos en cada campaña

2. **Ingreso de Datos de Planificación en Google Sheets**:
   - Utilizar la plantilla estandarizada
   - Exportar a CSV y colocar en la carpeta de datos

3. **Generación de Escenarios**:
   - El modelo proyecta resultados basados en datos históricos
   - Se simulan diferentes distribuciones presupuestarias por canal

4. **Optimización y Calendarización**:
   - Se selecciona el escenario óptimo según objetivos
   - Se genera un calendario de inversión por canal

5. **Monitoreo y Ajuste**:
   - Seguimiento continuo del rendimiento vs. proyecciones
   - Ajustes en tiempo real basados en el rendimiento actual

### 5.2 Ejemplo de Planificación

**Caso**: Campaña Q3 2023 para UTEL

**Input al motor** (desde archivo CSV exportado de Google Sheets):
- Campaña: Q3 2023
- Marca: UTEL
- Programas incluidos: Maestría en Educación, Maestría en Administración, Licenciatura en Derecho
- Objetivo total: 120 matrículas
- Presupuesto total: $75,000
- Período: 2 meses (8 semanas)
- Canales activos: Facebook, Google, LinkedIn, Instagram, Email

**Output del motor**:
```
Distribución recomendada por canal:
- Facebook: 35% - $26,250
- Google: 30% - $22,500
- LinkedIn: 20% - $15,000
- Instagram: 10% - $7,500
- Email: 5% - $3,750

Proyección esperada:
- Leads totales: 1,500
- Tasa de conversión estimada: 8.0%
- Matrículas esperadas: 120
- CPA proyectado: $625

Calendarización recomendada:
- Semanas 1-2: 30% - $22,500
- Semanas 3-4: 25% - $18,750
- Semanas 5-6: 25% - $18,750
- Semanas 7-8: 20% - $15,000

Distribución natural proyectada por programa:
- Maestría en Educación: 45% (~54 matrículas)
- Maestría en Administración: 35% (~42 matrículas)
- Licenciatura en Derecho: 20% (~24 matrículas)
```

## 6. Integración en el Flujo de Trabajo

El Motor de Decisión se integra en el flujo de trabajo de marketing a través de:

1. **Ciclo de Planificación**:
   - Análisis histórico
   - Planificación en Google Sheets
   - Exportación de planificación
   - Generación de recomendaciones
   - Implementación y seguimiento

2. **Gestión de Archivos**:
   - Plantillas en `datos/plantillas/`
   - Archivos de planificación en `datos/planificacion/`
   - Datos de leads y matrículas en `datos/actual/`
   - Resultados generados en `resultados/`

3. **Retroalimentación al Modelo**:
   - Los resultados reales alimentan el modelo
   - Mejora continua de la precisión predictiva
   - Adaptación a cambios en el mercado o comportamiento de los leads

---

## Apéndice: Fórmulas Clave

### Distribución de Presupuesto por Canal
```
Presupuesto_Canal = Presupuesto_Total_Campaña * (Peso_Canal / Suma_Pesos)
```
Donde `Peso_Canal` se calcula considerando el rendimiento histórico y el potencial predicho.

### Estimación de Leads Necesarios
```
Leads_Necesarios = Objetivo_Matriculas_Total / Tasa_Conversion_Estimada
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