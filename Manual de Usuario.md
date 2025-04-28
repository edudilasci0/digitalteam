# Manual de Usuario - Sistema Predictor y Optimizador de Matrículas

## Índice

1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Google Sheets - Configuración y Uso](#google-sheets---configuración-y-uso)
4. [Trabajando con Archivos CSV (método tradicional)](#trabajando-con-archivos-csv-método-tradicional)
5. [Dashboard Comercial](#dashboard-comercial)
6. [Análisis de Estacionalidad](#análisis-de-estacionalidad)
7. [Análisis Completo y Simulación Monte Carlo (NUEVO)](#análisis-completo-y-simulación-monte-carlo-nuevo)
8. [Dashboards Power BI (NUEVO)](#dashboards-power-bi-nuevo)
9. [Automatización de tareas](#automatización-de-tareas)
10. [Guía de resolución de problemas](#guía-de-resolución-de-problemas)
11. [Preguntas frecuentes](#preguntas-frecuentes)

## Introducción

El Sistema Predictor y Optimizador de Matrículas es una herramienta diseñada para equipos de marketing educativo que permite:

- Predecir resultados de campañas basándose en datos históricos
- Visualizar el progreso actual contra objetivos
- Recibir recomendaciones para optimizar presupuestos de medios
- Tomar decisiones basadas en datos sobre la gestión de campañas
- **NUEVO:** Analizar intervalos de confianza en predicciones
- **NUEVO:** Visualizar datos en dashboards interactivos Power BI

Este manual está dirigido a tres tipos de usuarios:
- **Media planners**: Encargados de planificar y optimizar campañas
- **Analistas de datos**: Responsables de mantener el sistema y generar informes
- **Directores de marketing**: Quienes supervisan los resultados y toman decisiones estratégicas

## Instalación

### Requisitos previos

- Python 3.6 o superior
- Acceso a internet para la sincronización con Google Sheets
- Permisos para crear credenciales de Google API (solo para configuración inicial)
- **NUEVO:** Power BI Desktop (para visualizaciones avanzadas)

### Pasos de instalación

1. Descargar el código fuente:
```bash
git clone https://github.com/tu-usuario/predictor-matriculas.git
cd predictor-matriculas
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar Google Sheets (solo primera vez):
```bash
python scripts/sincronizar_sheets.py
```

4. Seguir las instrucciones en pantalla para:
   - Crear un proyecto en Google Cloud Console
   - Habilitar APIs necesarias
   - Crear y descargar credenciales
   - Colocar archivo de credenciales en la carpeta correcta

5. **NUEVO:** Configurar Power BI (para visualizaciones avanzadas):
   - Instalar Power BI Desktop
   - Seguir instrucciones en `docs/implementacion_dashboard.md`

## Google Sheets - Configuración y Uso

### Configuración inicial

Después de ejecutar `python scripts/sincronizar_sheets.py` por primera vez:

1. El sistema creará automáticamente una hoja de cálculo en Google Sheets
2. La URL de la hoja se mostrará en la terminal - guárdala y compártela con tu equipo
3. Por defecto, cualquier persona con el enlace puede ver la hoja, pero solo la cuenta que la creó puede editarla
4. Para permitir edición a otros miembros del equipo:
   - Abre la hoja en Google Sheets
   - Haz clic en "Compartir" en la esquina superior derecha
   - Añade los correos electrónicos de los miembros del equipo con permisos de "Editor"

### Estructura de hojas

El sistema crea las siguientes hojas:

1. **Datos de inversión diaria**
   - Aquí se ingresan los datos de costos e inversión por canal
   - Columnas: Fecha, Canal, Inversión (€), Impresiones, Clics, CTR (%), CPC (€), Conversiones, CPL (€), Observaciones
   - **Responsabilidad**: Media planner / Analista de medios

2. **Leads y Matrículas**
   - Registro de leads y matrículas generados
   - Columnas: ID, Fecha, Hora, Tipo, Canal, Campaña, Nombre, Email, Teléfono, Programa, Estado
   - **Responsabilidad**: Analista de datos / Coordinador CRM

3. **Resultados**
   - Actualizado automáticamente con predicciones del sistema
   - **No editar manualmente** - Se sobrescribe en cada sincronización

4. **Dashboard**
   - Resumen visual del estado de la campaña
   - **No editar manualmente** - Se sobrescribe en cada sincronización

5. **Registro de Decisiones**
   - Bitácora de decisiones tomadas por el equipo
   - Columnas: Fecha, Estado Campaña, Decisión Tomada, Canales Afectados, Cambio en Presupuesto, Responsable, Resultado Esperado, Seguimiento
   - **Responsabilidad**: Todo el equipo

### Instrucciones para media planners

Como media planner, tu principal interacción será:

1. **Actualizar datos de inversión diaria**:
   - Completa la hoja "Datos de inversión diaria" con información de tus campañas
   - Es crucial mantener actualizados los datos de inversión, especialmente para canales pagados
   - Se recomienda actualizar diariamente o al menos 3 veces por semana

2. **Consultar resultados y predicciones**:
   - Revisa la hoja "Dashboard" para ver el estado general de la campaña
   - Consulta la hoja "Resultados" para ver predicciones detalladas por canal
   - Los valores predichos para las próximas semanas te ayudarán a planificar ajustes

3. **Registrar decisiones**:
   - En la hoja "Registro de Decisiones", documenta cada cambio significativo:
     - Aumento o reducción de presupuesto
     - Pausado o activación de canales
     - Cambios en creatividades o audiencias
   - Esto permite evaluar posteriormente el impacto de tus decisiones

### Sincronización

Para actualizar las predicciones después de ingresar nuevos datos:

```bash
python scripts/sincronizar_sheets.py
```

Esto realizará:
- Lectura de datos ingresados en Google Sheets
- Generación de nuevas predicciones basadas en datos actualizados
- Actualización de las hojas "Resultados" y "Dashboard"
- Generación de reportes HTML detallados (accesibles en la carpeta `/salidas/`)

## Trabajando con Archivos CSV (método tradicional)

Si prefieres no utilizar Google Sheets, puedes seguir usando el sistema con archivos CSV:

1. Prepara tus archivos:
   - `leads_matriculas_actual.csv`: Datos de leads y matrículas actuales
   - `leads_matriculas_historicos.csv`: Datos históricos para comparación
   - `costos_campanas.csv`: Datos de inversión por canal

2. Coloca los archivos en las carpetas correspondientes:
   - `/datos/actual/`
   - `/datos/historico/`
   - `/datos/costos/`

3. Ejecuta los scripts individualmente:
```bash
python scripts/dashboard_comercial.py
python scripts/analisis_estacionalidad.py
```

4. Revisa los reportes generados en la carpeta `/salidas/`

## Dashboard Comercial

### Comprendiendo el dashboard

El dashboard comercial proporciona una visión completa del estado actual de la campaña, incluyendo:

1. **Barras de progreso**:
   - Compara el tiempo transcurrido vs. leads captados vs. matrículas
   - Color verde: Por encima del objetivo
   - Color amarillo: Dentro del rango esperado
   - Color rojo: Por debajo del objetivo

2. **Comparación con estimación**:
   - Gráfico de líneas que muestra leads acumulados vs. proyección
   - Área sombreada que representa el rango estimado
   - Línea vertical que marca la fecha actual

3. **Observaciones y recomendaciones**:
   - Estado general (POR DEBAJO, DENTRO DEL RANGO, POR ENCIMA)
   - Recomendaciones específicas según el estado
   - Métricas clave y diferencias porcentuales

### Interpretación del estado

Para interpretar correctamente el dashboard:

- **POR DEBAJO** → Rendimiento inferior al esperado
  - Requiere intervención inmediata
  - Redistribuir presupuesto hacia canales mejor performantes
  - Revisar calidad de leads y mensajes

- **DENTRO DEL RANGO** → Rendimiento según lo esperado
  - Realizar optimizaciones menores
  - Monitorear indicadores clave semanalmente
  - Mantener estrategia general

- **POR ENCIMA** → Rendimiento superior al esperado
  - Capitalizar el éxito
  - Evaluar posible reasignación de recursos
  - Documentar factores de éxito para futuras campañas

## Análisis de Estacionalidad

### Comprendiendo el análisis de estacionalidad

El análisis de estacionalidad permite identificar patrones temporales en la captación de leads y matrículas, incluyendo:

1. **Descomposición estacional**:
   - Componente de tendencia (dirección general)
   - Componente estacional (patrones recurrentes)
   - Componente residual (variación no explicada)

2. **Índices estacionales**:
   - Valores que indican periodos de alta o baja demanda
   - Útiles para planificar inversión y recursos

3. **Predicciones futuras**:
   - Proyecciones basadas en patrones históricos
   - Intervalos de confianza para las estimaciones

### Uso en la planificación

Utiliza el análisis de estacionalidad para:

- Planificar presupuestos de marketing considerando épocas de alta y baja demanda
- Ajustar objetivos de lead generation según patrones estacionales
- Preparar al equipo comercial para picos de actividad
- Planificar promociones o incentivos en periodos de baja actividad natural

## Análisis Completo y Simulación Monte Carlo (NUEVO)

### Comprendiendo el análisis completo

El análisis completo ejecuta en secuencia todas las herramientas analíticas del sistema, incluyendo:

1. **Análisis de estacionalidad**: Identifica patrones temporales en leads y matrículas
2. **Predicción de matrículas**: Entrena modelos predictivos basados en datos históricos
3. **Simulación Monte Carlo**: Ejecuta 1000 simulaciones para calcular intervalos de confianza
4. **Análisis de elasticidad**: Determina sensibilidad a diferentes factores y canales
5. **Métricas de confianza**: Calcula y guarda indicadores de fiabilidad de predicciones

### Ejecutando el análisis completo

Para ejecutar todos los análisis en un solo paso:

```bash
python scripts/ejecutar_analisis_completo.py
```

El proceso completo puede tardar entre 5-10 minutos dependiendo del volumen de datos y la capacidad de procesamiento. Al finalizar, los resultados se guardan en `dashboard/datos/resultados_analisis/` y están listos para visualizar en Power BI.

### Comprendiendo los resultados

Los archivos generados incluyen:

- `estacionalidad_leads.csv`: Índices estacionales para leads
- `estacionalidad_matriculas.csv`: Índices estacionales para matrículas
- `predicciones_matriculas.csv`: Predicciones futuras
- `intervalos_confianza.csv`: Intervalos de confianza de predicciones
- `muestreo_simulaciones.csv`: Muestra de las simulaciones Monte Carlo
- `elasticidad_factores.csv`: Análisis de elasticidad por factores
- `recomendaciones_inversion.csv`: Recomendaciones de inversión
- `resumen_confianza.csv`: Resumen de métricas de confianza

### Interpretación de intervalos de confianza

Los intervalos de confianza indican el rango en el que, con cierta probabilidad, se encontrará el valor real:

- **Intervalo al 80%**: Rango donde esperamos que esté el resultado con un 80% de probabilidad
- **Intervalo al 90%**: Rango más amplio con mayor certeza (90% de probabilidad)
- **Intervalo al 95%**: Rango más conservador con 95% de probabilidad

**Ejemplo de interpretación**:
- Si la predicción es 100 matrículas con un intervalo al 90% de [85-115], significa que hay un 90% de probabilidad de que el resultado final esté entre 85 y 115 matrículas.
- Un intervalo más estrecho indica mayor confianza en la predicción.
- Un intervalo muy amplio sugiere mayor incertidumbre.

### Métricas de confianza

El sistema calcula varias métricas para evaluar la confianza en las predicciones:

1. **R²**: Indica qué porcentaje de la variación se explica por el modelo
   - >0.8: Excelente confianza
   - 0.6-0.8: Buena confianza
   - <0.6: Confianza moderada

2. **MAPE** (Error Porcentual Absoluto Medio):
   - <10%: Excelente precisión
   - 10-20%: Buena precisión
   - >20%: Precisión moderada

3. **Amplitud relativa del intervalo**:
   - <20% de la predicción: Alta certidumbre
   - 20-40% de la predicción: Certidumbre moderada
   - >40% de la predicción: Alta incertidumbre

### Personalización del análisis

Para modificar parámetros del análisis, edite el archivo `scripts/ejecutar_analisis_completo.py`:

- **Número de simulaciones**: Ajuste `num_simulaciones=1000` (más simulaciones = mayor precisión pero más tiempo)
- **Variabilidad en simulaciones**: Ajuste `variabilidad=0.15` (15% por defecto)
- **Horizonte de predicción**: Ajuste `horizonte_meses=6` para cambiar el periodo futuro a predecir

## Dashboards Power BI (NUEVO)

### Configuración inicial

Para configurar los dashboards Power BI:

1. Siga las instrucciones detalladas en `docs/implementacion_dashboard.md`
2. Ejecute el análisis completo para generar todos los datos necesarios:
   ```bash
   python scripts/ejecutar_analisis_completo.py
   ```
3. Abra Power BI Desktop y cargue el modelo predefinido o cree uno siguiendo las instrucciones
4. Conecte a los datos en `dashboard/datos/procesados/` y `dashboard/datos/resultados_analisis/`

### Dashboard Comercial (para equipo de ventas)

El Dashboard Comercial está diseñado específicamente para el equipo de ventas y muestra:

1. **Panel general**:
   - % de logro de objetivos
   - Leads pendientes de gestión
   - Tasa de conversión actual

2. **Evolución temporal**:
   - Gráfico de líneas con tendencia
   - Comparativa con periodos anteriores

3. **Rendimiento por programa**:
   - Listado de programas con % de logro
   - Clasificación de programas (Top/Bottom performers)

Este dashboard está optimizado para uso diario y seguimiento operativo.

### Dashboard Analítico (para marketing/dirección)

El Dashboard Analítico proporciona análisis en profundidad para toma de decisiones estratégicas:

1. **Panel general**:
   - KPIs globales (leads, matrículas, % logro)
   - Métricas de confianza e intervalos de predicción

2. **Análisis por programa**:
   - Gráfico de dispersión (volumen vs conversión)
   - Matriz detallada con todas las métricas
   - Mapa de calor de rendimiento temporal

3. **Análisis de simulación**:
   - Distribución de resultados Monte Carlo
   - Visualización de escenarios (optimista/pesimista)
   - Rangos de confianza por programa

4. **Análisis de elasticidad**:
   - Sensibilidad por canal y factor
   - Recomendaciones de inversión

Este dashboard está diseñado para análisis profundo y planificación estratégica.

### Actualización de datos

Para actualizar los datos en Power BI:

1. Ejecute el análisis completo si desea actualizar todas las métricas:
   ```bash
   python scripts/ejecutar_analisis_completo.py
   ```

2. O actualice solo los datos básicos del dashboard:
   ```bash
   python dashboard/actualizar_datos.py
   ```

3. En Power BI Desktop, haga clic en "Actualizar" para cargar los nuevos datos

### Consejos para Power BI

- Utilice los filtros y segmentadores para analizar datos específicos
- Use el formato condicional para identificar rápidamente valores problemáticos
- Aproveche los tooltips enriquecidos al pasar el cursor sobre los elementos
- Configure alertas en Power BI Service para recibir notificaciones automáticas

## Automatización de tareas

### Configurar sincronización automática

Para automatizar la sincronización diaria:

#### En Windows:

1. Abre el Programador de tareas
2. Clic en "Crear tarea básica"
3. Nombre: "Sincronización Google Sheets"
4. Selecciona la frecuencia (Diariamente)
5. Configura la hora de inicio (recomendado: 8:00 AM)
6. En Acción, selecciona "Iniciar un programa"
7. Programa/script: `python`
8. Argumentos: ruta completa a `scripts/ejecutar_sincronizacion.py`
9. Finaliza el asistente

#### En macOS o Linux:

1. Abre Terminal
2. Ejecuta: `crontab -e`
3. Añade la siguiente línea para ejecutar cada 12 horas:
   ```
   0 8,20 * * * /usr/bin/python3 /ruta/completa/scripts/ejecutar_sincronizacion.py
   ```
4. Guarda y sal del editor

### Automatizar análisis completo (NUEVO)

Para automatizar el análisis completo diario:

#### En Windows:

1. Abre el Programador de tareas
2. Clic en "Crear tarea básica"
3. Nombre: "Análisis Completo Predictivo"
4. Selecciona la frecuencia (Diariamente)
5. Configura la hora de inicio (recomendado: 1:00 AM)
6. En Acción, selecciona "Iniciar un programa"
7. Programa/script: `python`
8. Argumentos: ruta completa a `scripts/ejecutar_analisis_completo.py`
9. Finaliza el asistente

#### En macOS o Linux:

1. Abre Terminal
2. Ejecuta: `crontab -e`
3. Añade la siguiente línea para ejecutar cada noche a la 1 AM:
   ```
   0 1 * * * /usr/bin/python3 /ruta/completa/scripts/ejecutar_analisis_completo.py
   ```
4. Guarda y sal del editor

### Automatizar reportes especiales

Para automatizar la generación de reportes especiales:

1. Crea un script personalizado que:
   - Llame a los módulos necesarios
   - Genere reportes específicos
   - Envíe por correo los resultados (opcional)

2. Programa su ejecución regular:
   - Semanal para reportes de rendimiento
   - Mensual para análisis de tendencias
   - Trimestral para evaluación estratégica

## Guía de resolución de problemas

### Problemas comunes y soluciones

1. **"Error al conectar con Google Sheets"**
   - Verifica que existe el archivo `config/credentials.json`
   - Asegúrate de que las APIs de Google Sheets y Drive están habilitadas
   - Comprueba que la cuenta de servicio tiene permisos en la hoja

2. **"No se encuentran datos suficientes para generar predicciones"**
   - Verifica que las hojas "Datos de inversión diaria" y "Leads y Matrículas" tienen datos
   - Asegúrate de que las fechas están en formato correcto (YYYY-MM-DD)
   - Comprueba que existen datos históricos en `datos/historico/`

3. **"Error en simulación de Monte Carlo"**:
   - Verifique los logs en `logs/analisis_completo_YYYYMMDD.log`
   - Intente reducir el número de simulaciones en `scripts/ejecutar_analisis_completo.py`
   - Asegúrese de que hay suficiente memoria disponible

4. **"No se cargan los datos en Power BI"**:
   - Verifique que el análisis completo se ejecutó correctamente
   - Compruebe que las rutas en Power BI coinciden con su estructura de carpetas
   - Verifique que los tipos de datos en Power BI son correctos

### Consulta de logs

Para diagnosticar problemas más complejos:

1. Revisa los archivos de log en la carpeta `/logs/`:
   - `sincronizacion_sheets.log`: Detalles de la sincronización con Google Sheets
   - `sincronizacion_auto.log`: Registros de ejecuciones automáticas programadas
   - `analisis_completo_YYYYMMDD.log`: Detalles del análisis completo y simulación

2. Busca mensajes de error específicos:
   - ERROR: Indica un problema grave que impidió la operación
   - WARNING: Señala posibles problemas que no detuvieron la ejecución
   - INFO: Proporciona información sobre el proceso normal

## Preguntas frecuentes

### Sobre Google Sheets

**P: ¿Puedo modificar manualmente las hojas "Resultados" o "Dashboard"?**
R: No es recomendable, ya que se sobrescriben en cada sincronización. Usa la hoja "Registro de Decisiones" para comentarios o notas.

**P: ¿Cuántas personas pueden editar la hoja simultáneamente?**
R: Google Sheets permite edición colaborativa de múltiples usuarios, pero es recomendable coordinar los tiempos para evitar conflictos.

**P: ¿La información es confidencial en Google Sheets?**
R: Por defecto, solo personas con el enlace pueden ver la hoja. Para mayor seguridad, comparte la hoja solo con correos específicos y no con el enlace público.

### Sobre sincronización y automatización

**P: ¿Con qué frecuencia debo sincronizar los datos?**
R: Idealmente, una vez al día para mantener las predicciones actualizadas. En periodos críticos de la campaña, puede ser útil sincronizar dos veces al día.

**P: ¿Puedo programar envíos automáticos de los reportes?**
R: El sistema actual no incluye envío por email, pero puedes extenderlo usando módulos como `smtplib` para enviar reportes automáticamente.

**P: ¿Qué pasa si se cae la conexión durante la sincronización?**
R: El sistema implementa manejo de errores para evitar datos corruptos. Si se interrumpe, simplemente vuelve a ejecutar la sincronización.

### Sobre predicciones y análisis

**P: ¿Qué tan precisas son las predicciones?**
R: La precisión depende de la calidad y cantidad de datos históricos. Con buenos datos históricos, la precisión suele estar entre 80-90%.

**P: ¿Cómo mejoro la precisión de las predicciones?**
R: Mantén datos históricos limpios y detallados, actualiza frecuentemente los datos actuales, y documenta factores externos que puedan afectar los resultados.

**P: ¿El sistema considera factores externos como vacaciones o eventos especiales?**
R: No automáticamente. Es importante registrar estos factores en la columna "Observaciones" de la hoja "Datos de inversión diaria" para contextualizar los análisis.

### Sobre análisis completo y simulación (NUEVO)

**P: ¿Cuánto tiempo tarda en ejecutarse el análisis completo?**
R: Dependiendo del volumen de datos y la capacidad de procesamiento, entre 5-10 minutos. Las simulaciones Monte Carlo son la parte más intensiva.

**P: ¿Qué tan precisos son los intervalos de confianza?**
R: Los intervalos reflejan la variabilidad inherente al modelo y los datos. Para intervalos más precisos, mejore la calidad de los datos históricos y ajuste los parámetros de variabilidad.

**P: ¿Puedo usar los dashboards sin Power BI?**
R: Sí, los datos procesados se guardan en formato CSV y pueden visualizarse con otras herramientas como Excel, Tableau o Google Data Studio.

**P: ¿Cómo interpreto las recomendaciones de elasticidad?**
R: Indican qué canales responderían mejor a cambios en la inversión. Mayor elasticidad significa que un pequeño incremento en inversión generará un mayor incremento porcentual en leads.

### Sobre Power BI (NUEVO)

**P: ¿Necesito licencia Power BI Pro?**
R: Para uso personal o dentro de un equipo pequeño, Power BI Desktop (gratuito) es suficiente. Para compartir en toda la organización o configurar actualizaciones automáticas en la nube, se requiere Power BI Pro.

**P: ¿Cómo comparto los dashboards con mi equipo?**
R: Puede publicar en Power BI Service (requiere licencia) o compartir el archivo .pbix directamente. También puede exportar como PDF para informes estáticos.

**P: ¿Se pueden personalizar los dashboards?**
R: Sí, todos los dashboards son completamente personalizables. Siga las guías en `docs/implementacion_dashboard.md` para modificar visualizaciones y añadir nuevas métricas. 