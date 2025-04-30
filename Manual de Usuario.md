# Manual de Usuario - Motor de Decisión Educativo y Predictivo

## Índice

1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Estructura del Sistema](#estructura-del-sistema)
4. [Navegación por la Interfaz](#navegación-por-la-interfaz)
5. [Gestión de Marcas](#gestión-de-marcas)
6. [Carga de Datos](#carga-de-datos)
7. [Reportes Disponibles](#reportes-disponibles)
   - [Estratégicos (Marketing)](#reportes-estratégicos)
   - [Comerciales (Status)](#reportes-comerciales)
   - [Exploratorios (Diagnóstico)](#reportes-exploratorios)
8. [Exportación de Datos](#exportación-de-datos)
9. [Modelos Predictivos](#modelos-predictivos)
10. [Preguntas Frecuentes](#preguntas-frecuentes)
11. [Solución de Problemas](#solución-de-problemas)

## Introducción

El Motor de Decisión Educativo y Predictivo es una herramienta especializada para equipos de marketing educativo diseñada para:

- Analizar datos históricos y actuales de campañas, leads y matrículas
- Generar reportes diferenciados para equipos de marketing y comercial
- Construir modelos predictivos para estimar matrículas futuras
- Identificar anomalías y puntos de mejora en el funnel de conversión
- Exportar análisis en múltiples formatos (Excel, PDF, PowerPoint)

## Instalación

### Requisitos previos

- Python 3.7 o superior
- Pip (gestor de paquetes de Python)
- Navegador web moderno

### Pasos de instalación

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

- Cada **marca** representa una unidad educativa independiente
- Para cada marca se pueden cargar **datos de planificación** e **históricos**
- Los **reportes** se generan específicamente para cada marca
- Los **modelos predictivos** se entrenan por separado para cada marca

La estructura de directorios creada automáticamente es:

```
data/
├── MARCA1/
│   ├── historico.csv
│   ├── plan_actual.csv
│   ├── modelo_rf.joblib
│   └── reportes/
├── MARCA2/
│   └── ...
```

## Navegación por la Interfaz

La aplicación está dividida en las siguientes secciones:

1. **Barra lateral**: Selección de marca y navegación principal
2. **Carga de Datos**: Carga de archivos de planificación e históricos
3. **Reporte Estratégico**: Análisis orientado a marketing y planificación
4. **Reporte Comercial**: Status semanal de avance y proyecciones
5. **Reporte Exploratorio**: Diagnóstico y exploración detallada de datos

## Gestión de Marcas

Para gestionar marcas educativas:

1. En la barra lateral, seleccione "<Nueva marca>" del desplegable
2. Ingrese el nombre de la nueva marca
3. El sistema creará automáticamente la estructura de directorios
4. Seleccione marcas existentes del desplegable en cualquier momento

## Carga de Datos

El sistema requiere dos tipos de archivos CSV:

### Planificación (plan_actual.csv)

Debe contener al menos:
- `leads_estimados`: Objetivo de leads para el periodo
- `objetivo_matriculas`: Objetivo de matrículas para el periodo

### Histórico (historico.csv)

Debe contener al menos:
- `fecha`: Fecha de registro (YYYY-MM-DD)
- `leads`: Cantidad de leads generados
- `matriculas`: Cantidad de matrículas realizadas
- `inversion`: Inversión realizada
- `canal` (opcional): Canal de captación

Para cargar archivos:
1. Navegue a la sección "Carga de Datos"
2. Utilice los botones de carga para subir los archivos CSV
3. Verifique la vista previa para confirmar la carga correcta

## Reportes Disponibles

### Reportes Estratégicos

Diseñados para equipos de marketing y planificación estratégica:

- **Métricas clave**: CPA, CPL, progreso de leads y matrículas
- **Comparativa de plataformas**: CPA y tasas de conversión por canal
- **Curva de avance**: Evolución temporal de leads, matrículas e inversión
- **Escenarios simulados**: Proyecciones con diferentes escenarios de inversión
- **Predicciones ML**: Estimaciones de matrículas basadas en machine learning
- **Alertas automáticas**: Identificación de problemas o ineficiencias

### Reportes Comerciales

Enfocados en el seguimiento semanal para equipos comerciales:

- **Barras de progreso**: Visualización de avance hacia los objetivos
- **Proyección lineal**: Estimación de resultados finales con intervalos de confianza
- **Observaciones ejecutivas**: Conclusiones y recomendaciones automatizadas
- **Exportación a Excel**: Descarga de datos procesados para análisis adicional

### Reportes Exploratorios

Para análisis detallado y diagnóstico de datos:

- **Distribución por canal**: Análisis de la distribución de leads por origen
- **Matriz de correlación**: Relaciones entre variables principales
- **Detección de anomalías**: Identificación de valores atípicos mediante Z-score
- **Análisis temporal**: Patrones por día de la semana y tendencias

## Exportación de Datos

El sistema permite exportar los análisis en diferentes formatos:

- **Excel**: Datos completos para análisis posterior
- **PDF**: Informes ejecutivos para distribución
- **PowerPoint**: Presentaciones para reuniones estratégicas

Para exportar:
1. Navegue al reporte deseado
2. Utilice los botones de exportación en la parte inferior
3. El archivo se generará y podrá descargarse automáticamente

## Modelos Predictivos

El sistema utiliza modelos de machine learning para realizar predicciones:

- **Algoritmo**: Random Forest Regressor
- **Variables de entrada**: Leads históricos e inversión
- **Salida**: Proyección de matrículas con intervalos de confianza
- **Entrenamiento**: Automático con datos históricos disponibles

## Preguntas Frecuentes

**P: ¿Cómo puedo agregar una nueva marca?**

R: En la barra lateral, seleccione "<Nueva marca>" y escriba el nombre de la marca deseada.

**P: ¿Qué formato deben tener mis archivos CSV?**

R: Los archivos deben estar en formato CSV con separador coma. Las columnas mínimas necesarias se describen en la sección "Carga de Datos".

**P: ¿Puedo exportar los gráficos generados?**

R: Sí, puede exportar los análisis completos en formato PDF, PowerPoint o Excel desde cada reporte.

**P: ¿Cómo funciona la predicción de matrículas?**

R: El sistema entrena automáticamente un modelo de Random Forest con sus datos históricos y proyecta matrículas futuras basándose en leads e inversión.

## Solución de Problemas

**Error: "No hay planificación cargada"**

Asegúrese de haber cargado un archivo de planificación con las columnas requeridas.

**Error: "Modelo predictivo no disponible"**

El sistema necesita suficientes datos históricos (al menos 10 registros) con las columnas "leads", "inversion" y "matriculas" para entrenar un modelo.

**Los gráficos no se visualizan correctamente**

Pruebe a utilizar un navegador moderno (Chrome, Firefox, Edge) y asegúrese de que está actualizado.

**Error en la exportación de archivos**

Verifique que tiene instaladas las dependencias opcionales necesarias:
- Para PDF: `pip install fpdf`
- Para PowerPoint: `pip install python-pptx` 