# Motor de Decisión Educativo y Predictivo - Documentación Completa

## Índice
1. [Introducción y Visión Estratégica](#introducción-y-visión-estratégica)
2. [Instalación y Requisitos](#instalación-y-requisitos)
3. [Estructura del Sistema](#estructura-del-sistema)
4. [Funcionalidades Principales](#funcionalidades-principales)
5. [Instrucciones de Uso](#instrucciones-de-uso)
   - [Configuración Inicial](#configuración-inicial)
   - [Carga de Datos](#carga-de-datos)
   - [Uso de Reportes](#uso-de-reportes)
6. [Modelo de Decisiones](#modelo-de-decisiones)
7. [Estado Actual del Proyecto](#estado-actual-del-proyecto)
8. [Solución de Problemas](#solución-de-problemas)

## Introducción y Visión Estratégica

El Motor de Decisión Educativo y Predictivo es un sistema inteligente diseñado para equipos de marketing educativo que permite:

- **Anticipar problemas** antes de que ocurran
- **Optimizar el presupuesto** en campañas digitales
- **Mejorar el cierre de matrículas** basado en datos y no intuiciones
- **Automatizar la toma de decisiones** tácticas y estratégicas

El sistema analiza:
- CPL (Costo por Lead) diario y acumulado
- CPA (Costo por Adquisición de matrícula)
- Tasa de conversión leads → matrículas
- Modelado de estacionalidad (patrones históricos)
- Simulación de escenarios
- Forecast dinámico de cierre de convocatoria
- Análisis de elasticidad y simulaciones Monte Carlo

## Instalación y Requisitos

### Requisitos previos
- Python 3.7 o superior
- Pip (gestor de paquetes de Python)
- Navegador web moderno

### Instalación

1. Clone el repositorio:
```bash
git clone https://github.com/su-usuario/motor-decision-educativo.git
cd motor-decision-educativo
```

2. Instale las dependencias:
```bash
pip install -r requirements.txt
```

3. Inicie la aplicación:
```bash
streamlit run app_motor.py
```

## Estructura del Sistema

El sistema está organizado en una arquitectura por marcas educativas:

```
data/
├── MARCA1/
│   ├── historico.csv
│   ├── plan_actual.csv
│   ├── leads_actual.csv
│   ├── matriculas_actual.csv
│   ├── inversion_actual.csv
│   ├── leads_historico.csv
│   ├── matriculas_historico.csv
│   ├── inversion_historico.csv
│   ├── modelo_rf.joblib
│   └── reportes/
├── MARCA2/
│   └── ...
```

- Cada **marca** representa una unidad educativa independiente
- El sistema soporta marcas predefinidas: GR, PR, WZ, ADV, UNISUD, AJA
- Para cada marca se pueden cargar datos históricos y de convocatoria actual
- Los reportes se generan específicamente para cada marca
- Los modelos predictivos se entrenan por separado para cada marca

## Funcionalidades Principales

### Mejoras Implementadas Recientemente

1. **Carga de datos separada por tipo**
   - Ahora es posible cargar leads, matrículas e inversión de forma individual
   - Se organizaron los campos en tres pestañas: Datos Históricos, Convocatoria Actual y Planificación

2. **Configuración de convocatoria**
   - Semana actual del año
   - Duración total de la convocatoria (semanas)
   - Semanas restantes

3. **Soporte para marcas predefinidas**
   - Implementación de selector para marcas específicas
   - GR, PR, WZ, ADV, UNISUD, AJA

4. **Archivos de ejemplo**
   - Plantillas para leads, matrículas, planificación e inversión

5. **Mejoras en reportes**
   - Uso de configuración de convocatoria para cálculos precisos
   - Proyección de matrículas basada en tiempo transcurrido
   - Análisis de tendencia comparando convocatoria actual vs histórico

### Reportes Disponibles

1. **Reporte Estratégico (Marketing)**
   - Métricas clave: CPA, CPL, progreso de leads y matrículas
   - Comparativa de plataformas: CPA y tasas de conversión por canal
   - Curva de avance: Evolución temporal de leads, matrículas e inversión
   - Escenarios simulados: Proyecciones con diferentes escenarios de inversión
   - Predicciones ML: Estimaciones de matrículas basadas en machine learning
   - Alertas automáticas: Identificación de problemas o ineficiencias

2. **Reporte Comercial (Status)**
   - Barras de progreso: Visualización de avance hacia los objetivos
   - Proyección lineal: Estimación de resultados finales con intervalos de confianza
   - Observaciones ejecutivas: Conclusiones y recomendaciones automatizadas
   - Exportación a Excel avanzada: Descarga de reportes optimizados con gráficos interactivos

3. **Reporte Exploratorio (Diagnóstico)**
   - Distribución por canal: Análisis de la distribución de leads por origen
   - Matriz de correlación: Relaciones entre variables principales
   - Detección de anomalías: Identificación de valores atípicos mediante Z-score
   - Análisis temporal: Patrones por día de la semana y tendencias

### Exportación Excel Mejorada

Todos los reportes incluyen exportación a Excel con características avanzadas:

- **Formato profesional**: Diseño visual con colores corporativos y estilo coherente
- **Múltiples hojas organizadas**: Datos separados por categorías y análisis
- **Gráficos interactivos**: Visualizaciones que pueden manipularse directamente en Excel
- **Barras de progreso visuales**: Representación gráfica con códigos de color según avance
- **Formatos condicionales**: Destacan automáticamente valores importantes o fuera de rango
- **Filtros automáticos**: Facilitan el análisis y exploración de los datos
- **Ancho de columna optimizado**: Ajuste automático según el contenido
- **Formato numérico inteligente**: Moneda, porcentaje o número según el tipo de dato

## Instrucciones de Uso

### Configuración Inicial

1. **Seleccionar marca**
   - Elija una marca existente o cree una nueva desde la barra lateral
   - Si desea usar una marca predefinida, active la opción correspondiente

2. **Configurar convocatoria**
   - Establezca la semana actual del año
   - Configure la duración total (en semanas)
   - Indique las semanas restantes

### Carga de Datos

#### Estructura de archivos requerida

1. **Leads**
   - `fecha_creacion`: Fecha de creación del lead
   - `canal`: Canal por el que llegó el lead
   - Otros campos informativos como email, nombre, etc.

2. **Matrículas**
   - `fecha_matricula`: Fecha de la matrícula
   - `id_lead`: Identificador del lead que se convirtió
   - `monto`: Valor de la matrícula

3. **Inversión**
   - `fecha`: Fecha de la inversión
   - `canal`: Canal donde se realizó la inversión
   - `monto`: Monto invertido

4. **Planificación**
   - `leads_estimados`: Objetivo de leads para la campaña
   - `objetivo_matriculas`: Objetivo de matrículas
   - Puede incluir otros objetivos por canal

#### Pestañas de Carga

1. **Datos Históricos**
   - Navegue a la pestaña "Datos Históricos"
   - Suba los archivos separados de leads históricos, matrículas históricas e inversión histórica
   - Puede descargar ejemplos de formato haciendo clic en los botones de ejemplo

2. **Convocatoria Actual**
   - Navegue a la pestaña "Convocatoria Actual"
   - Suba los archivos de leads, matrículas e inversión de la convocatoria actual
   - Los datos se combinarán automáticamente para los reportes

3. **Planificación**
   - Navegue a la pestaña "Planificación"
   - Suba el archivo con los objetivos y planificación de la campaña

### Uso de Reportes

Una vez cargados los datos, navegue entre los diferentes reportes usando el menú lateral:

1. **Reporte Estratégico**
   - Utilice este reporte para decisiones de marketing y planificación
   - Los gráficos muestran tendencias y proyecciones
   - Las métricas clave se muestran en la parte superior
   - Exporte a Excel con el botón "Descargar Excel Avanzado"

2. **Reporte Comercial**
   - Utilice este reporte para seguimiento semanal
   - Las barras de progreso muestran el avance actual
   - Las proyecciones incluyen intervalos de confianza
   - Las recomendaciones automáticas sugieren acciones

3. **Reporte Exploratorio**
   - Utilice este reporte para análisis detallado
   - Puede detectar anomalías en los datos
   - Analice correlaciones entre variables
   - Explore patrones temporales

## Modelo de Decisiones

### Frecuencia Recomendada de Análisis

- **Revisión quincenal**: Análisis completo de rendimiento y ajustes principales
- **Monitoreo semanal**: Seguimiento rápido de KPIs críticos y ajustes menores
- **Análisis mensual**: Evaluación estratégica completa con revisión de estacionalidad

### Proceso de Toma de Decisiones

1. **Revisión de estado actual**
   - Identifique si está POR DEBAJO, DENTRO DEL RANGO o POR ENCIMA de objetivos
   - Utilice barras de progreso y proyecciones del Reporte Comercial

2. **Interpretación de métricas**
   - Evalúe CPA, CPL y tasa de conversión
   - Compare con objetivos y tendencias históricas
   - Utilice los intervalos de confianza para evaluar riesgos

3. **Decisiones tácticas**
   - Asigne presupuesto basándose en rendimiento de canales
   - Optimice campañas según elasticidad y estacionalidad
   - Implemente acciones correctivas cuando sea necesario

4. **Seguimiento**
   - Monitoree los efectos de las decisiones
   - Ajuste según retroalimentación
   - Actualice datos regularmente para mantener predicciones precisas

### Matriz de Decisiones

| Estado | Estacionalidad | Decisiones recomendadas |
|--------|----------------|-------------------------|
| **POR DEBAJO** | Alta | • Aumentar inversión significativamente en canales de alta elasticidad<br>• Implementar promociones especiales inmediatas |
| **POR DEBAJO** | Baja | • Aumentar inversión en canales específicos según elasticidad<br>• Optimizar proceso de conversión |
| **DENTRO DEL RANGO** | Alta | • Mantener estrategia actual<br>• Optimizar asignación entre canales según elasticidad |
| **DENTRO DEL RANGO** | Baja | • Optimizar estrategia enfocándose en conversión<br>• Prepararse para próximos periodos de alta estacionalidad |
| **POR ENCIMA** | Alta | • Capitalizar éxito con inversión adicional<br>• Documentar factores de éxito |
| **POR ENCIMA** | Baja | • Estudiar y documentar factores de éxito para replicar<br>• Evaluar reasignación de recursos a otros programas |

## Estado Actual del Proyecto

El Motor de Decisión Educativo y Predictivo ha evolucionado a una arquitectura centrada en Streamlit, que permite gestionar marcas educativas independientes, cargar datos, generar reportes y exportar análisis en diferentes formatos.

### Archivos Principales

- **app_motor.py**: Aplicación principal
- **requirements.txt**: Dependencias del proyecto
- **DOCUMENTACION_COMPLETA.md**: Documentación completa del sistema

### Desarrollos Recientes

- Implementación de carga separada de datos
- Configuración flexible de convocatorias
- Soporte para marcas predefinidas
- Mejora de proyecciones y análisis de tendencias
- Exportación de reportes en múltiples formatos

### Próximos Pasos

1. **Mejora de modelos ML**: Implementar más algoritmos predictivos
2. **Internacionalización**: Soporte para múltiples idiomas
3. **Mejoras en Excel**: Continuar optimizando formatos y visualizaciones
4. **API REST**: Desarrollar endpoints para integración con otros sistemas

## Solución de Problemas

### Problemas comunes

1. **Error: "No hay planificación cargada"**
   - Asegúrese de haber cargado un archivo de planificación con las columnas requeridas.

2. **Error: "Modelo predictivo no disponible"**
   - El sistema necesita suficientes datos históricos (al menos 10 registros) con las columnas "leads", "inversion" y "matriculas" para entrenar un modelo.

3. **Los gráficos no se visualizan correctamente**
   - Pruebe a utilizar un navegador moderno (Chrome, Firefox, Edge) y asegúrese de que está actualizado.

4. **Problemas con la exportación Excel**
   - Verifique que tiene XlsxWriter instalado: `pip install xlsxwriter`
   - Asegúrese de que su version de pandas es compatible con la exportación a Excel
   - Evite nombres de archivos muy largos o con caracteres especiales

### Cómo solicitar ayuda

Si encuentra problemas no cubiertos en esta documentación, puede:
1. Revisar el código fuente en app_motor.py
2. Consultar con el equipo de desarrollo interno
3. Verificar que todos los requisitos estén correctamente instalados 