# Manual de Usuario - Motor de Decisión

## Introducción

Bienvenido al Manual de Usuario del Motor de Decisión, la herramienta integral para análisis predictivo y optimización de campañas de captación de matrículas educativas de Digital Team. Este manual te guiará paso a paso en el uso del sistema, desde la configuración inicial hasta la interpretación de resultados y generación de reportes.

## Índice

1. [Primeros Pasos](#primeros-pasos)
   - [Requisitos del Sistema](#requisitos-del-sistema)
   - [Acceso al Sistema](#acceso-al-sistema)
   - [Interfaz de Usuario](#interfaz-de-usuario)

2. [Carga de Datos](#carga-de-datos)
   - [Formatos Soportados](#formatos-soportados)
   - [Estructura de Datos Requerida](#estructura-de-datos-requerida)
   - [Proceso de Carga](#proceso-de-carga)
   - [Validación de Datos](#validación-de-datos)

3. [Análisis de Datos](#análisis-de-datos)
   - [Análisis Descriptivo](#análisis-descriptivo)
   - [Análisis Predictivo](#análisis-predictivo)
   - [Análisis de Estacionalidad](#análisis-de-estacionalidad)
   - [Simulaciones Monte Carlo](#simulaciones-monte-carlo)

4. [Visualización de Resultados](#visualización-de-resultados)
   - [Gráficos Interactivos](#gráficos-interactivos)
   - [Dashboards](#dashboards)
   - [Interpretación de Visualizaciones](#interpretación-de-visualizaciones)

5. [Generación de Reportes](#generación-de-reportes)
   - [Tipos de Reportes](#tipos-de-reportes)
   - [Personalización de Reportes](#personalización-de-reportes)
   - [Exportación y Compartición](#exportación-y-compartición)

6. [Planificación de Campañas](#planificación-de-campañas)
   - [Definición de Objetivos](#definición-de-objetivos)
   - [Asignación de Presupuesto](#asignación-de-presupuesto)
   - [Optimización de Canales](#optimización-de-canales)

7. [Funcionalidades Avanzadas](#funcionalidades-avanzadas)
   - [Integración con Google Sheets](#integración-con-google-sheets)
   - [Automatización de Reportes](#automatización-de-reportes)
   - [Calendario de Campañas](#calendario-de-campañas)

8. [Solución de Problemas](#solución-de-problemas)
   - [Problemas Comunes](#problemas-comunes)
   - [Preguntas Frecuentes](#preguntas-frecuentes)
   - [Soporte Técnico](#soporte-técnico)

## Primeros Pasos

### Requisitos del Sistema

Para utilizar el Motor de Decisión necesitas:

- Navegador web moderno (Chrome, Firefox, Edge o Safari recomendados)
- Conexión a internet para acceso a la aplicación
- Archivos de datos en formato CSV, Excel o conexión a Google Sheets

### Acceso al Sistema

1. **Ejecutar la aplicación**:
   
   Si la aplicación está instalada localmente:
   ```
   streamlit run src/ui/carga_datos.py
   ```
   
   Si estás accediendo a una instancia ya desplegada, usa la URL proporcionada por tu administrador.

2. **Autenticación**:
   
   Cuando se abra la aplicación en tu navegador, verás una pantalla de inicio de sesión:
   
   ![Pantalla de Inicio de Sesión](../docs/images/login_screen.png)
   
   - Ingresa la contraseña: `teamdigital` (o la contraseña personalizada proporcionada por tu administrador)
   - Haz clic en "Iniciar Sesión"

3. **Navegación segura**:
   
   Una vez autenticado, permanecerás con la sesión activa hasta que:
   - Cierres el navegador
   - Hagas clic en "Cerrar Sesión" en el menú lateral
   - Transcurran 12 horas de inactividad

### Interfaz de Usuario

La interfaz del Motor de Decisión está organizada de la siguiente manera:

1. **Barra Lateral Izquierda**:
   - Menú principal de navegación
   - Opciones de configuración
   - Botón de cierre de sesión
   - Logo de team digital

2. **Área Principal**:
   - Contenido interactivo según la sección seleccionada
   - Formularios de entrada de datos
   - Visualizaciones y gráficos
   - Reportes y análisis

3. **Menú Principal**:
   - **Carga de Datos**: Para subir nuevos archivos al sistema
   - **Análisis**: Herramientas de análisis descriptivo y predictivo
   - **Reportes**: Generación y descarga de informes
   - **Configuración**: Ajustes del sistema y preferencias

## Carga de Datos

### Formatos Soportados

El sistema acepta los siguientes formatos de archivos:

- **CSV** (Valores separados por comas)
- **Excel** (.xlsx, .xls)
- **JSON** (para usuarios avanzados)

También puedes conectar directamente con **Google Sheets** para importación de datos en tiempo real.

### Estructura de Datos Requerida

#### Archivos de Leads

Columnas requeridas para archivos de leads:

| Columna | Tipo de Dato | Descripción |
|---------|--------------|-------------|
| id | Texto | Identificador único del lead |
| fecha_creacion | Fecha (YYYY-MM-DD) | Fecha de creación del lead |
| programa | Texto | Programa académico solicitado |
| origen | Texto | Canal de origen del lead (ej. Facebook, Google) |
| marca | Texto | Marca asociada a la campaña |
| costo | Numérico | Costo asociado al lead |
| utm_source | Texto | Fuente de UTM (opcional) |
| utm_medium | Texto | Medio de UTM (opcional) |
| utm_campaign | Texto | Campaña de UTM (opcional) |

#### Archivos de Matrículas

Columnas requeridas para archivos de matrículas:

| Columna | Tipo de Dato | Descripción |
|---------|--------------|-------------|
| id | Texto | Identificador único de la matrícula |
| id_lead | Texto | ID del lead asociado |
| fecha_matricula | Fecha (YYYY-MM-DD) | Fecha de realización de la matrícula |
| programa | Texto | Programa académico matriculado |
| valor_matricula | Numérico | Valor monetario de la matrícula |
| modalidad | Texto | Modalidad de estudio (opcional) |
| sede | Texto | Sede de estudio (opcional) |

### Proceso de Carga

Para cargar nuevos datos al sistema:

1. Accede a la sección "Carga de Datos" en el menú principal

2. Selecciona el tipo de datos que vas a cargar:
   - **Leads**: Datos de prospectos o interesados
   - **Matrículas**: Registros de matrículas completadas
   - **Auto-detectar**: El sistema intentará determinar el tipo automáticamente

3. Arrastra y suelta el archivo en la zona de carga, o haz clic para seleccionar desde tu explorador de archivos

4. Espera mientras el sistema analiza y valida tus datos

5. Revisa la vista previa y el resumen estadístico mostrado

6. Si se detectan problemas, sigue las recomendaciones mostradas para corregirlos

7. Haz clic en "Cargar y procesar datos" para confirmar

8. Una vez completada la carga, se te mostrará un mensaje de confirmación

### Validación de Datos

El sistema realiza automáticamente las siguientes validaciones:

1. **Verificación de estructura**: Comprueba que estén todas las columnas requeridas
2. **Validación de tipos de datos**: Detecta si hay fechas o valores numéricos incorrectos
3. **Identificación de duplicados**: Alerta sobre registros repetidos
4. **Análisis de valores nulos**: Identifica campos vacíos y su impacto

Los problemas identificados se muestran categorizados por gravedad:
- **Alta** (Rojo): Problemas críticos que deben corregirse antes de continuar
- **Media** (Amarillo): Advertencias que pueden afectar a los resultados
- **Baja** (Azul): Información que no impide el procesamiento pero debe revisarse

## Análisis de Datos

### Análisis Descriptivo

El análisis descriptivo te permite entender y explorar los datos cargados:

1. Navega a la sección "Análisis" en el menú principal

2. Selecciona "Análisis Descriptivo" en el submenú

3. Configura los parámetros de análisis:
   - **Periodo**: Selecciona el rango de fechas a analizar
   - **Programas**: Elige los programas académicos a incluir
   - **Canales**: Selecciona los canales de marketing a analizar
   - **Métricas**: Escoge las métricas principales a visualizar

4. Haz clic en "Generar Análisis" para procesar los datos

5. Explora las diferentes secciones del informe resultante:
   - **Resumen de métricas clave**: CPL, CPA, tasa de conversión
   - **Análisis por canal**: Rendimiento comparativo por origen
   - **Análisis por programa**: Distribución de leads y matrículas
   - **Evolución temporal**: Tendencias a lo largo del tiempo
   - **Correlaciones**: Relaciones entre variables clave

### Análisis Predictivo

El análisis predictivo usa modelos de machine learning para predecir resultados futuros:

1. Navega a la sección "Análisis" en el menú principal

2. Selecciona "Análisis Predictivo" en el submenú

3. Configura los parámetros del modelo:
   - **Variable objetivo**: Selecciona qué quieres predecir (matrículas, CPL, conversión)
   - **Horizonte temporal**: Define cuánto tiempo hacia el futuro predecir
   - **Modelo**: Elige el tipo de modelo a utilizar
   - **Variables independientes**: Selecciona qué factores considerar

4. Haz clic en "Entrenar Modelo" para comenzar el proceso

5. Revisa las métricas de precisión del modelo mostradas

6. Explora las predicciones generadas:
   - **Valores predichos**: Estimaciones puntuales
   - **Intervalos de confianza**: Rangos de probabilidad
   - **Gráficos comparativos**: Valores reales vs. predicciones

### Análisis de Estacionalidad

El análisis de estacionalidad identifica patrones temporales recurrentes:

1. Navega a la sección "Análisis" en el menú principal

2. Selecciona "Análisis de Estacionalidad" en el submenú

3. Configura los parámetros:
   - **Variable**: Selecciona qué métrica analizar (leads, CPL, conversiones)
   - **Periodo**: Define el nivel de agregación (diario, semanal, mensual)
   - **Rango temporal**: Selecciona el periodo histórico a considerar

4. Haz clic en "Analizar Estacionalidad"

5. Interpreta los resultados mostrados:
   - **Descomposición de series temporales**: Tendencia, estacionalidad y residuos
   - **Patrones semanales**: Variaciones dentro de la semana
   - **Patrones mensuales**: Variaciones dentro del mes
   - **Patrones anuales**: Variaciones a lo largo del año

### Simulaciones Monte Carlo

Las simulaciones Monte Carlo permiten evaluar escenarios futuros con incertidumbre:

1. Navega a la sección "Análisis" en el menú principal

2. Selecciona "Simulación Monte Carlo" en el submenú

3. Configura los parámetros de simulación:
   - **Presupuesto total**: Define el presupuesto a distribuir
   - **Variables de interés**: Selecciona qué métricas simular
   - **Número de simulaciones**: Define la cantidad de iteraciones
   - **Distribuciones**: Configura los parámetros estadísticos

4. Haz clic en "Ejecutar Simulación"

5. Analiza los resultados de la simulación:
   - **Distribuciones de probabilidad**: Resultados posibles y su probabilidad
   - **Métricas clave**: Media, mediana, percentiles
   - **Escenarios**: Optimista, realista y pesimista
   - **Análisis de sensibilidad**: Impacto de cambios en variables clave

## Visualización de Resultados

### Gráficos Interactivos

Los gráficos interactivos te permiten explorar los datos visualmente:

1. Al generar cualquier análisis, se mostrarán automáticamente visualizaciones relevantes

2. Interactúa con los gráficos utilizando:
   - **Zoom**: Para enfocarte en áreas específicas
   - **Hover**: Pasa el ratón sobre elementos para ver detalles
   - **Filtros**: Usa los selectores para mostrar subconjuntos de datos
   - **Descarga**: Haz clic en el ícono de descarga para guardar el gráfico

3. Tipos de gráficos disponibles:
   - **Líneas temporales**: Para evolución a lo largo del tiempo
   - **Barras comparativas**: Para comparar categorías
   - **Dispersión**: Para relaciones entre variables
   - **Cajas y bigotes**: Para distribuciones estadísticas
   - **Mapas de calor**: Para correlaciones y patrones
   - **Gráficos de embudo**: Para conversiones en el funnel

### Dashboards

Los dashboards combinan múltiples visualizaciones en una vista unificada:

1. Navega a la sección "Reportes" en el menú principal

2. Selecciona "Dashboards" en el submenú

3. Elige entre los dashboards predefinidos:
   - **Dashboard ejecutivo**: Resumen de alto nivel
   - **Dashboard operativo**: Métricas detalladas de desempeño
   - **Dashboard predictivo**: Enfocado en previsiones futuras
   - **Dashboard de campañas**: Análisis específico por campaña

4. Personaliza el dashboard según tus necesidades:
   - Selecciona el periodo de datos
   - Filtra por programas y canales
   - Ajusta la disposición de los gráficos

5. Usa las funcionalidades interactivas:
   - Filtrado en tiempo real
   - Exploración de detalles
   - Vistas combinadas

### Interpretación de Visualizaciones

Para interpretar correctamente las visualizaciones:

1. **Leyenda de colores**: Cada visualización tiene una leyenda que explica el significado de los colores utilizados

2. **Escalas y ejes**: Presta atención a las unidades y escalas de los ejes

3. **Intervalos de confianza**: Las áreas sombreadas representan los rangos de incertidumbre

4. **Tooltips informativos**: Pasa el cursor sobre elementos para obtener información detallada

5. **Indicadores de referencia**: Las líneas horizontales o verticales indican valores de referencia o umbrales importantes

## Generación de Reportes

### Tipos de Reportes

El sistema permite generar varios tipos de reportes:

1. **Reportes Ejecutivos**: Resumen de alto nivel para toma de decisiones estratégicas
   - Métricas clave y tendencias principales
   - Recomendaciones estratégicas
   - Visión global del rendimiento

2. **Reportes de Performance**: Análisis detallado del desempeño de campañas
   - Análisis por canal, programa y periodo
   - Métricas de eficiencia y conversión
   - Comparativas con periodos anteriores

3. **Reportes Predictivos**: Proyecciones y escenarios futuros
   - Predicciones de matrículas y leads
   - Análisis de escenarios
   - Recomendaciones para optimizar resultados

4. **Reportes de Campaña**: Enfocados en campañas específicas
   - Análisis pre y post campaña
   - Métricas de inversión y retorno
   - Recomendaciones tácticas

### Personalización de Reportes

Para personalizar tus reportes:

1. Navega a la sección "Reportes" en el menú principal

2. Selecciona "Generar Reporte" en el submenú

3. Configura los parámetros de personalización:
   - **Tipo de reporte**: Selecciona el formato deseado
   - **Periodo**: Define el rango de fechas a incluir
   - **Programas**: Selecciona qué programas incluir
   - **Canales**: Elige qué canales de marketing analizar
   - **Métricas**: Selecciona las métricas principales a destacar
   - **Secciones**: Elige qué secciones incluir u omitir

4. Personaliza la apariencia:
   - Selecciona la plantilla visual
   - Ajusta colores y logotipos
   - Define formato de datos y fechas

5. Haz clic en "Generar Reporte" para crear el documento

### Exportación y Compartición

Los reportes pueden exportarse y compartirse de varias formas:

1. **Formatos de exportación**:
   - **PowerPoint (.pptx)**: Presentaciones editables
   - **PDF**: Documentos para lectura e impresión
   - **Excel (.xlsx)**: Datos tabulares para análisis adicional
   - **HTML**: Versiones web interactivas

2. **Opciones de compartición**:
   - **Correo electrónico**: Envío directo a destinatarios
   - **Enlace compartible**: URL para acceso web (requiere permisos)
   - **Descarga directa**: Guardar archivo localmente

3. **Programación de reportes**:
   - Configura reportes recurrentes automáticos
   - Define frecuencia (diaria, semanal, mensual)
   - Selecciona destinatarios y formato de entrega

## Planificación de Campañas

### Definición de Objetivos

Para definir objetivos de campaña:

1. Navega a la sección "Planificación" en el menú principal

2. Selecciona "Definir Objetivos" en el submenú

3. Configura los parámetros de la campaña:
   - **Nombre de campaña**: Identificador único de la campaña
   - **Periodo**: Fecha de inicio y fin de la campaña
   - **Programas**: Selecciona los programas objetivo
   - **Objetivos de matrículas**: Define metas por programa
   - **Presupuesto total**: Establece el presupuesto disponible

4. Haz clic en "Guardar Objetivos" para registrar la configuración

### Asignación de Presupuesto

Para asignar y optimizar presupuesto:

1. Navega a la sección "Planificación" en el menú principal

2. Selecciona "Distribución de Presupuesto" en el submenú

3. Selecciona la campaña previamente configurada

4. Elige el método de distribución:
   - **Manual**: Asigna porcentajes o montos manualmente
   - **Histórico**: Basado en distribución de campañas anteriores
   - **Optimizado**: Recomendación basada en modelado predictivo

5. Ajusta la distribución según necesidad:
   - Por canal de marketing
   - Por programa académico
   - Por periodo de tiempo

6. Haz clic en "Calcular Métricas Esperadas" para ver proyecciones

7. Revisa y ajusta hasta obtener la distribución óptima

8. Haz clic en "Confirmar Distribución" para guardar

### Optimización de Canales

Para optimizar la selección y configuración de canales:

1. Navega a la sección "Planificación" en el menú principal

2. Selecciona "Optimización de Canales" en el submenú

3. Selecciona la campaña a optimizar

4. El sistema mostrará recomendaciones basadas en:
   - Rendimiento histórico de los canales
   - Estacionalidad y tendencias detectadas
   - Objetivos de la campaña actual
   - Presupuesto disponible

5. Revisa las recomendaciones para cada canal:
   - CPL (Costo por Lead) esperado
   - Volumen de leads proyectado
   - Tasa de conversión estimada
   - ROI proyectado

6. Ajusta manualmente si es necesario

7. Haz clic en "Aplicar Optimización" para guardar

## Funcionalidades Avanzadas

### Integración con Google Sheets

Para conectar con Google Sheets:

1. Navega a la sección "Carga de Datos" en el menú principal

2. Selecciona la opción "Conectar con Google Sheets"

3. Ingresa la URL del documento de Google Sheets o selecciona uno de los documentos previamente conectados

4. Autoriza el acceso (solo la primera vez)

5. Selecciona la hoja específica a importar

6. Configura la importación:
   - Tipo de datos (leads o matrículas)
   - Mapeo de columnas si es necesario
   - Frecuencia de sincronización (manual o automática)

7. Haz clic en "Conectar" para establecer la vinculación

Una vez conectado, podrás:
- Importar datos en tiempo real
- Configurar actualizaciones automáticas
- Exportar resultados directamente a Google Sheets

### Automatización de Reportes

Para configurar reportes automáticos:

1. Navega a la sección "Reportes" en el menú principal

2. Selecciona "Programación de Reportes" en el submenú

3. Haz clic en "Nuevo Reporte Programado"

4. Configura los parámetros:
   - **Tipo de reporte**: Selecciona la plantilla a utilizar
   - **Frecuencia**: Define cada cuánto se generará (diario, semanal, mensual)
   - **Destinatarios**: Agrega las direcciones de correo de los receptores
   - **Formato**: Selecciona entre PowerPoint, PDF, Excel
   - **Contenido**: Configura qué elementos incluir

5. Programa la fecha y hora de inicio

6. Haz clic en "Activar Programación"

### Calendario de Campañas

El Calendario de Campañas permite visualizar y planificar todas las campañas:

1. Navega a la sección "Planificación" en el menú principal

2. Selecciona "Calendario de Campañas" en el submenú

3. Visualiza las campañas en formato de calendario:
   - Vista mensual, trimestral o anual
   - Codificación por colores según tipo de campaña
   - Marcadores de hitos importantes

4. Interactúa con el calendario:
   - Haz clic en una campaña para ver detalles
   - Arrastra para ajustar fechas
   - Usa el botón "+" para añadir nuevas campañas
   - Filtra por programa o canal

5. Analiza superposiciones y distribución temporal

6. Exporta el calendario en diferentes formatos

## Solución de Problemas

### Problemas Comunes

#### Problemas de Carga de Datos

1. **"Error al cargar archivo"**:
   - Verifica que el formato del archivo sea compatible (CSV, Excel, JSON)
   - Comprueba que el archivo no está corrupto abriéndolo en otra aplicación
   - Intenta con un archivo más pequeño para identificar si es un problema de tamaño

2. **"Columnas requeridas faltantes"**:
   - Descarga la plantilla desde la aplicación
   - Compara tu archivo con la plantilla para identificar diferencias
   - Añade las columnas faltantes o corrige sus nombres

3. **"Error en el formato de fechas"**:
   - Asegúrate de que las fechas estén en formato YYYY-MM-DD
   - Si usas Excel, configura el formato de celda como texto antes de exportar
   - Revisa si hay fechas inválidas en tus datos

#### Problemas de Visualización

1. **"Los gráficos no se cargan"**:
   - Actualiza la página del navegador
   - Verifica tu conexión a internet
   - Intenta con otro navegador web

2. **"Datos inconsistentes en visualizaciones"**:
   - Verifica los filtros aplicados
   - Comprueba el rango de fechas seleccionado
   - Asegúrate de que no haya duplicados en los datos

#### Problemas de Generación de Reportes

1. **"Error al generar reporte"**:
   - Verifica que hay datos suficientes para el periodo seleccionado
   - Comprueba que tienes permisos para la generación de reportes
   - Intenta con un periodo de tiempo más corto

2. **"Reporte incompleto o con datos faltantes"**:
   - Verifica que todas las fuentes de datos necesarias están cargadas
   - Comprueba los filtros aplicados
   - Asegúrate de que la selección de métricas es correcta

### Preguntas Frecuentes

#### Sobre Datos y Formatos

1. **¿Qué formato de archivo es el más recomendable?**
   
   CSV es el formato más estable y compatible. Sin embargo, si trabajas con Excel, puedes importar directamente archivos .xlsx y preservar los formatos de fecha.

2. **¿Hay un límite de tamaño para los archivos?**
   
   Sí, el límite recomendado es de 50 MB por archivo. Para conjuntos de datos más grandes, considera dividirlos o usar la conexión con Google Sheets.

3. **¿Se pueden importar datos desde otras fuentes?**
   
   Actualmente se soporta CSV, Excel, JSON y Google Sheets. Para otras fuentes, exporta primero a uno de estos formatos.

#### Sobre Análisis y Modelos

1. **¿Qué modelo predictivo es el más preciso?**
   
   Depende del caso específico. El sistema selecciona automáticamente el mejor modelo basado en los datos, pero puedes seleccionar manualmente si prefieres otro enfoque.

2. **¿Cuántos datos históricos se necesitan para predicciones confiables?**
   
   Se recomienda al menos 12 meses de datos para capturar patrones estacionales completos, pero el mínimo funcional es de 3 meses.

3. **¿Cómo se manejan los valores atípicos (outliers)?**
   
   El sistema detecta automáticamente valores atípicos y ofrece opciones para filtrarlos o tratarlos según metodologías estadísticas.

#### Sobre Seguridad y Acceso

1. **¿Cómo cambiar la contraseña de acceso?**
   
   La contraseña se configura en el código fuente. Contacta al administrador del sistema para cambiarla.

2. **¿Los datos se almacenan de forma segura?**
   
   Sí, los datos se almacenan localmente en una base de datos SQLite con acceso protegido. No se comparten en la nube a menos que configures integraciones específicas.

3. **¿Se pueden establecer diferentes niveles de acceso?**
   
   La versión actual tiene un solo nivel de acceso. Las versiones futuras implementarán roles y permisos.

### Soporte Técnico

Si encuentras problemas no cubiertos en esta documentación:

1. **Consulta la Documentación Avanzada**:
   - Revisa los documentos técnicos en la carpeta `docs/`
   - Verifica las actualizaciones en el repositorio de GitHub

2. **Contacta al Equipo de Soporte**:
   - Envía un correo a soporte@digital-team.com
   - Incluye capturas de pantalla y descripción detallada del problema
   - Menciona la versión del sistema que estás utilizando

3. **Reporta Bugs o Solicita Funcionalidades**:
   - Crea un issue en el repositorio de GitHub
   - Describe claramente el comportamiento esperado vs. el actual
   - Proporciona pasos para reproducir el problema

## Apéndices

### Glosario de Términos

- **CPL (Costo por Lead)**: Costo promedio de adquisición de un lead.
- **CPA (Costo por Adquisición)**: Costo promedio de conseguir una matrícula.
- **Tasa de Conversión**: Porcentaje de leads que se convierten en matrículas.
- **Forecast**: Predicción de resultados futuros basada en datos históricos.
- **Simulación Monte Carlo**: Método estadístico para modelar la probabilidad de diferentes resultados.
- **Estacionalidad**: Patrones recurrentes en datos temporales.

### Recursos Adicionales

- [Modelo de Decisiones](../docs/Modelo_de_decisiones.md): Documento técnico sobre la metodología
- [Estructura de Datos](../docs/estructura_datos.md): Especificaciones detalladas de formatos
- [API Documentation](../docs/api.md): Para integraciones avanzadas (si aplica)
- [Canal de Digital Team en YouTube](https://youtube.com/digitalteam): Tutoriales en video

### Actualizaciones

Este manual se actualiza regularmente. Versión actual: 2.0 (Abril 2025)

Para sugerencias sobre el manual, contacta a documentacion@digital-team.com

