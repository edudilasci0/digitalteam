# Instrucciones de Uso del Motor de Decisión

## Mejoras Implementadas

En esta versión del Motor de Decisión se han implementado las siguientes mejoras:

### 1. Carga de datos separada por tipo

- Ahora es posible cargar leads, matrículas e inversión de forma individual
- Se organizaron los campos en tres pestañas para mejor organización:
  - **Datos Históricos**: Para cargar información de leads, matrículas e inversión histórica
  - **Convocatoria Actual**: Para cargar información de la convocatoria vigente
  - **Planificación**: Para cargar el plan de la campaña

### 2. Configuración de convocatoria

- Se añadieron controles para configurar:
  - **Semana actual del año**: Indica en qué semana del año nos encontramos
  - **Duración total de la convocatoria**: Total de semanas que dura la campaña
  - **Semanas restantes**: Cuántas semanas faltan para finalizar
- Esta información se utiliza en todos los reportes para calcular progreso y proyecciones

### 3. Soporte para marcas predefinidas

- Se implementó un selector para las marcas específicas:
  - GR, PR, WZ, ADV, UNISUD, AJA
- Permite cambiar fácilmente entre marcas para realizar análisis comparativos

### 4. Archivos de ejemplo

- Se crearon plantillas para todos los tipos de datos:
  - Leads
  - Matrículas
  - Planificación
  - Inversión
- Se añadieron botones para descargar estos ejemplos en las secciones correspondientes

### 5. Mejoras en reportes

- Los reportes ahora utilizan la configuración de convocatoria para cálculos más precisos
- Se mejoró la proyección de matrículas basándose en el tiempo transcurrido
- Se agregaron análisis de tendencia comparando la convocatoria actual con datos históricos

## Instructivo de Uso

### Configuración inicial

1. Seleccione una marca existente o cree una nueva
2. Configure los parámetros de la convocatoria:
   - Semana actual
   - Duración total
   - Semanas restantes

### Carga de datos

#### Datos Históricos
1. Navegue a la pestaña "Datos Históricos"
2. Suba los archivos separados de leads históricos, matrículas históricas e inversión histórica
3. Puede descargar ejemplos de formato haciendo clic en los botones de ejemplo

#### Convocatoria Actual
1. Navegue a la pestaña "Convocatoria Actual"
2. Suba los archivos de leads, matrículas e inversión de la convocatoria actual
3. Los datos se combinarán automáticamente para los reportes

#### Planificación
1. Navegue a la pestaña "Planificación"
2. Suba el archivo con los objetivos y planificación de la campaña

### Generación de reportes

#### Reporte Estratégico
- Muestra métricas de rendimiento general
- Incluye análisis por canal y proyecciones
- Utiliza el modelo de ML para predecir resultados de las semanas restantes

#### Reporte Comercial
- Muestra el estado actual de la convocatoria
- Calcula la proyección final y recomendaciones
- Incluye barras de progreso y métricas de rendimiento

#### Reporte Exploratorio
- Análisis detallado de los datos
- Detección de anomalías y patrones
- Comparación de tendencias actuales vs históricas

## Estructura de archivos

### Leads
Debe contener como mínimo las columnas:
- `fecha_creacion`: Fecha de creación del lead
- `canal`: Canal por el que llegó el lead
- Otros campos informactivos como email, nombre, etc.

### Matrículas
Debe contener como mínimo las columnas:
- `fecha_matricula`: Fecha de la matrícula
- `id_lead`: Identificador del lead que se convirtió
- `monto`: Valor de la matrícula

### Inversión
Debe contener como mínimo las columnas:
- `fecha`: Fecha de la inversión
- `canal`: Canal donde se realizó la inversión
- `monto`: Monto invertido

### Planificación
Debe contener como mínimo las columnas:
- `leads_estimados`: Objetivo de leads para la campaña
- `objetivo_matriculas`: Objetivo de matrículas
- Puede incluir otros objetivos por canal 