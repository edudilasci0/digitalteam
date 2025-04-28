# Manual de Planificación de Campañas con Google Sheets

## Introducción

Este manual describe el proceso para utilizar Google Sheets en la planificación de campañas de marketing educativo. La integración con Google Sheets permite una colaboración eficiente entre equipos y una transición fluida de los datos hacia el Motor de Decisión.

## Proceso de Planificación

### 1. Estructura de Planificación

El modelo de planificación se basa en **campañas** que abarcan **múltiples programas**:

- Se asigna presupuesto a nivel de campaña por marca
- Los programas incluidos en la campaña se benefician del presupuesto común
- Los objetivos se establecen a nivel de campaña total
- La demanda natural determina qué programas atraen más leads

### 2. Plantilla de Google Sheets

#### 2.1 Creación de la Plantilla

1. Crear una nueva hoja de cálculo en Google Sheets
2. Configurarla con las siguientes columnas principales:
   - Fecha
   - ID_Campaña
   - Nombre_Campaña
   - Marca
   - Presupuesto_Total
   - Objetivo_Matriculas_Total
   - Fecha_Inicio
   - Fecha_Fin
   - Canales_Activos (separados por |)
   - Programas_Incluidos (separados por |)
   - Notas

#### 2.2 Ejemplo de Estructura

| Fecha       | ID_Campaña  | Nombre_Campaña | Marca | Presupuesto_Total | Objetivo_Matriculas_Total | Fecha_Inicio | Fecha_Fin   | Canales_Activos                   | Programas_Incluidos                                           | Notas                    |
|-------------|-------------|----------------|-------|-------------------|---------------------------|--------------|-------------|------------------------------------|---------------------------------------------------------------|--------------------------|
| 2023-07-01  | CAM-2023-Q3 | Campaña Q3 2023| UTEL  | 75000             | 120                       | 2023-07-15   | 2023-09-15  | Facebook\|Google\|LinkedIn\|Email | Maestría en Educación\|Maestría en Administración\|Licenciatura en Derecho | Enfoque en profesionales|

## 3. Flujo de Trabajo con Google Sheets

### 3.1 Planificación de Campaña

1. **Crear la planificación** en Google Sheets usando la plantilla proporcionada
2. **Completar los datos** de la campaña, incluyendo:
   - Información básica (fechas, ID, nombre)
   - Presupuesto total asignado
   - Objetivo total de matrículas
   - Canales que estarán activos
   - Listado de todos los programas incluidos

### 3.2 Exportación para el Motor de Decisión

1. **Exportar como CSV**:
   - En Google Sheets: Archivo > Descargar > Valores separados por comas (.csv)
   - Guardar con el nombre: `YYYYMMDD_planificacion_campaña.csv` (donde YYYYMMDD es la fecha actual)

2. **Colocar en la carpeta de datos**:
   - Guardar el archivo en: `datos/planificacion/`

### 3.3 Procesamiento y Resultados

1. El Motor de Decisión detectará automáticamente el archivo más reciente
2. Procesará los datos y generará recomendaciones
3. Los resultados estarán disponibles en la carpeta `resultados/`

## 4. Análisis de Rendimiento por Programa

Aunque la planificación y presupuestación se realiza a nivel de campaña, el sistema proporciona análisis detallado de rendimiento por programa:

- Tasas de conversión por programa
- Distribución natural de leads entre programas
- Análisis de eficiencia (CPA) por programa
- Recomendaciones para optimizar material promocional por programa

Este análisis se utiliza para tomar decisiones tácticas dentro de una campaña en ejecución, no para la planificación inicial de presupuesto.

## 5. Formato de las Recomendaciones

Las recomendaciones generadas por el Motor de Decisión incluirán:

### 5.1 Distribución Recomendada por Canal

| Canal    | Porcentaje | Presupuesto |
|----------|------------|-------------|
| Facebook | 35%        | $26,250     |
| Google   | 30%        | $22,500     |
| LinkedIn | 20%        | $15,000     |
| Instagram| 10%        | $7,500      |
| Email    | 5%         | $3,750      |

### 5.2 Proyecciones de la Campaña

- **Leads totales esperados**: XXX
- **Tasa de conversión estimada**: X.X%
- **Matrículas proyectadas**: XXX
- **CPA proyectado**: $XXX

### 5.3 Calendarización Sugerida

| Período     | Porcentaje | Presupuesto |
|-------------|------------|-------------|
| Semana 1-2  | 30%        | $22,500     |
| Semana 3-4  | 25%        | $18,750     |
| Semana 5-6  | 25%        | $18,750     |
| Semana 7-8  | 20%        | $15,000     |

## 6. Consejos Prácticos

- **Consistencia en nombres**: Mantener formatos consistentes para programas y canales
- **Campos separados por pipe (|)**: Usar el carácter | como separador para listas
- **Sincronización periódica**: Exportar/actualizar los archivos al menos semanalmente
- **Retroalimentación continua**: Verificar los resultados reales vs. proyectados

---

## Apéndice: Plantilla Lista para Usar

Se incluye una plantilla CSV preconstruida que puede importarse directamente a Google Sheets:
`datos/plantillas/planificacion_campaña.csv`

Para importarla:
1. Abrir Google Sheets
2. Seleccionar Archivo > Importar
3. Seleccionar la pestaña "Subir" y seleccionar el archivo
4. Elegir "Reemplazar hoja de cálculo actual" y hacer clic en "Importar datos" 