# Flujo de Datos para Generación Manual de Reportes

## Estructura del proceso de datos

El motor de decisión opera siguiendo este flujo de datos para generar los reportes Excel:

1. **Fuentes de datos**
2. **Carga y procesamiento**
3. **Análisis y cálculos**
4. **Generación de reportes Excel**

A continuación se detalla el proceso para que pueda realizarse manualmente sin el programa:

## 1. Fuentes de Datos

Los datos necesarios para el sistema provienen de:

- **Planificación**: Objetivos y metas establecidas (plan_actual.csv)
- **Histórico**: Datos acumulados de campañas (historico.csv)
- **Leads**: Datos individuales de prospectos (leads_actual.csv)
- **Matrículas**: Datos de conversiones (matriculas_actual.csv)

### Ubicación estándar de los archivos:

```
data/
├── [MARCA]/
│   ├── actual/
│   │   ├── leads_actual.csv
│   │   └── matriculas_actual.csv
│   ├── historico/
│   ├── historico.csv
│   └── plan_actual.csv
```

### Estructura de cada archivo:

**plan_actual.csv**
```
fecha,marca,canal,presupuesto,leads_estimados,objetivo_matriculas
2025-03-01,GR,Facebook,10000,500,50
2025-03-01,GR,Google,15000,600,60
...
```

**historico.csv**
```
fecha,marca,canal,leads,matriculas,inversion
2025-03-01,GR,Facebook,25,3,500
2025-03-02,GR,Facebook,30,4,500
...
```

**leads_actual.csv**
```
ID,fecha_generacion,canal,programa,marca,estado
001,2025-03-01,Facebook,MBA,GR,Contactado
002,2025-03-01,Google,MBA,GR,Interesado
...
```

**matriculas_actual.csv**
```
ID,fecha_matricula,canal,marca,programa
001,2025-03-15,Facebook,GR,MBA
005,2025-03-20,Google,GR,MBA
...
```

## 2. Proceso Manual de Carga y Análisis

Para realizar el proceso manualmente:

1. **Consolidar datos históricos**:
   - Utilizar Excel o cualquier herramienta de análisis de datos
   - Agrupar datos de leads por fecha, canal y marca
   - Agrupar datos de matrículas por fecha, canal y marca
   - Calcular totales de inversión por fecha y canal

2. **Calcular métricas clave**:
   ```
   CPA = inversión_total / matriculas_total
   CPL = inversión_total / leads_total
   tasa_conversión = matriculas_total / leads_total
   ```

3. **Evaluar progreso**:
   ```
   progreso_leads = leads_actual / leads_objetivo
   progreso_matriculas = matriculas_actual / matriculas_objetivo
   ratio_tiempo = semanas_transcurridas / duración_total
   ```

4. **Análisis por canal**:
   - Calcular CPA por canal:
     ```
     CPA_por_canal = inversión_canal / matriculas_canal
     ```
   - Calcular tasa de conversión por canal:
     ```
     conversion_canal = matriculas_canal / leads_canal
     ```
   - Identificar canales más eficientes (menor CPA, mayor conversión)

5. **Proyecciones**:
   - Proyección simple basada en tiempo transcurrido:
     ```
     leads_proyectados = leads_actual / ratio_tiempo
     matriculas_proyectadas = matriculas_actual / ratio_tiempo
     ```
   - Proyección basada en tendencia de conversión:
     ```
     leads_proyectados = leads_actual / ratio_tiempo
     matriculas_proyectadas = leads_proyectados * tasa_conversión_actual
     ```

## 3. Creación Manual del Reporte Excel

Para generar un reporte similar al automatizado:

### 3.1. Estructura de hojas

Crear las siguientes hojas en un libro Excel:
1. Resumen Ejecutivo
2. Datos Históricos
3. Análisis por Canal
4. Proyecciones
5. Barras de Progreso

### 3.2. Hoja de Resumen Ejecutivo

1. **Diseño del encabezado**:
   - Insertar título: "REPORTE ESTRATÉGICO - [MARCA]"
   - Subtítulo: "Generado: [FECHA ACTUAL]"
   - Usar formato grande, negrita y color corporativo (#1E3A8A)

2. **Tabla de métricas clave**:
   - Columnas: "Métrica" y "Valor"
   - Filas con las siguientes métricas:
     - Fecha Reporte
     - Marca
     - Semana Actual (ej: "10 de 13")
     - Progreso Tiempo (%)
     - Leads Obtenidos
     - Meta Leads
     - Matrículas Actuales
     - Meta Matrículas
     - CPA Actual
     - CPL Actual
     - Conversión Actual (%)

3. **Formato**:
   - Encabezados en azul corporativo (#1E3A8A) con texto blanco
   - Valores numéricos con formato adecuado (moneda, porcentaje, etc.)

### 3.3. Hoja de Datos Históricos

1. **Crear tabla con datos completos**:
   - Incluir todos los registros del archivo historico.csv
   - Agregar filtros automáticos

2. **Formato**:
   - Formato de moneda para inversión: `$#,##0.00`
   - Formato numérico para leads y matrículas: `#,##0`
   - Formato de fecha para columna fecha: `DD/MM/YYYY`

### 3.4. Hoja de Análisis por Canal

1. **Crear tabla resumen por canal**:
   - Agrupar datos por canal
   - Calcular totales de leads, matrículas e inversión por canal
   - Calcular CPA y conversión por canal

2. **Crear gráficos**:
   - Gráfico de columnas para CPA por canal
   - Gráfico de columnas para conversión por canal

3. **Interpretación**:
   - Añadir notas sobre canales más eficientes
   - Identificar canales con problemas (alto CPA o baja conversión)

### 3.5. Hoja de Proyecciones

1. **Tabla de proyecciones**:
   - Escenario actual (proyección lineal)
   - Escenario optimista (mejora de 5% en conversión)
   - Escenario agresivo (aumento de 20% en inversión)

2. **Gráfico de proyecciones**:
   - Representar visualmente los diferentes escenarios
   - Incluir línea para objetivo

3. **Intervalos de confianza**:
   - Calcular margen de error basado en semanas restantes
   - Mostrar límites superior e inferior de la proyección

### 3.6. Hoja de Barras de Progreso

1. **Crear tabla de progreso**:
   - Filas: "Tiempo transcurrido", "Leads entregados", "Matrículas confirmadas"
   - Columnas: "Valor Actual", "Valor Objetivo", "Porcentaje"

2. **Crear barras de progreso visual**:
   - Utilizar formato condicional para crear barras
   - Código de colores:
     - Verde (≥90%): `#AAFFAA`
     - Amarillo (60-89%): `#FFFFAA`
     - Rojo (<60%): `#FFAAAA`

## 4. Implementación de atribución manual

Para el análisis de atribución multicanal:

### 4.1. Modelo último clic (básico)

1. Filtrar matrículas y sus leads correspondientes
2. Asignar 100% del mérito al último canal de contacto
3. Contar frecuencia por canal
4. Calcular porcentajes del total

### 4.2. Modelo primer clic

1. Filtrar matrículas y sus leads correspondientes
2. Asignar 100% del mérito al primer canal de contacto
3. Contar frecuencia por canal
4. Calcular porcentajes del total

### 4.3. Modelo lineal

1. Identificar todos los canales únicos por los que pasó cada lead convertido
2. Dividir el mérito equitativamente (1/número de canales)
3. Sumar la atribución por canal
4. Calcular porcentajes del total

## 5. Ejemplo práctico paso a paso

### 5.1. Preparación inicial

1. **Consolidar datos**:
   - Abrir Excel y crear un nuevo libro
   - Importar los archivos CSV a hojas separadas
   - Crear hoja adicional para cálculos

2. **Calcular métricas globales**:
   - Total de leads: Suma(leads_historico)
   - Total de matrículas: Suma(matriculas_historico)
   - Total inversión: Suma(inversion_historico)
   - CPA global: inversión_total / matriculas_total
   - CPL global: inversión_total / leads_total
   - Tasa de conversión: matriculas_total / leads_total

### 5.2. Análisis por canal

Crear tabla dinámica para analizar datos por canal:
1. Seleccionar datos históricos completos
2. Insertar tabla dinámica
3. Configuración:
   - Filas: Canal
   - Valores: Suma(Leads), Suma(Matrículas), Suma(Inversión)
4. Añadir campos calculados:
   - CPA = Suma(Inversión) / Suma(Matrículas)
   - CPL = Suma(Inversión) / Suma(Leads)
   - Conversión = Suma(Matrículas) / Suma(Leads)

### 5.3. Proyecciones

1. Calcular progreso de tiempo:
   ```
   semanas_transcurridas / duración_total_convocatoria
   ```

2. Calcular proyecciones:
   ```
   leads_proyectados = leads_actual / progreso_tiempo
   matriculas_proyectadas = matriculas_actual / progreso_tiempo
   ```

3. Calcular escenarios alternativos:
   ```
   escenario_optimista = matriculas_proyectadas * 1.05
   escenario_agresivo = matriculas_proyectadas * 1.2
   ```

### 5.4. Formatos y gráficos finales

1. **Formato profesional**:
   - Colores corporativos
   - Formato condicional para métricas clave
   - Ordenar datos para facilitar la interpretación

2. **Gráficos sugeridos**:
   - Gráfico de columnas para CPA por canal
   - Gráfico de líneas para tendencia temporal
   - Gráfico combinado para objetivos vs actual
   - Gráfico de proyecciones con intervalos

3. **Barras de progreso visual**:
   - Usar formato condicional de barras de datos
   - Personalizar con colores según el progreso

## 6. Recomendaciones para el análisis manual

1. **Frecuencia**:
   - Realizar análisis semanal de métricas básicas
   - Análisis completo quincenal con proyecciones
   - Revisión mensual de tendencias y patrones

2. **Enfoque**:
   - Priorizar análisis de canales con mayor inversión
   - Identificar oportunidades de optimización (canales con buen CPL pero baja conversión)
   - Monitorear tendencias para detectar cambios significativos

3. **Visualización**:
   - Mantener consistencia en formatos y colores
   - Usar gráficos simples y claros
   - Incluir comparativas con periodos anteriores cuando sea posible

4. **Interpretación**:
   - Evaluar si el progreso es proporcional al tiempo transcurrido
   - Analizar si algún canal requiere ajustes inmediatos
   - Identificar si las proyecciones están alineadas con los objetivos 