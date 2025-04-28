# Implementación Rápida del Dashboard Comercial y Analítico

## Pasos para implementar el dashboard (30-60 minutos)

### 1. Preparación de datos (5 minutos)
1. Copia los archivos CSV de la carpeta `dashboard/datos/plantillas/` a `dashboard/datos/procesados/`
2. Verifica que todos los archivos CSV estén completos:
   - leads.csv
   - matriculas.csv
   - programas.csv
   - metas_comerciales.csv
   - comerciales.csv
   - usuarios_roles.csv

### 2. Crear el modelo en Power BI (15 minutos)

1. Abre Power BI Desktop
2. Crea un nuevo archivo y guárdalo como `Dashboard_Comercial_Analitico.pbix`

3. **Importar datos:**
   - Haz clic en "Obtener datos" → CSV
   - Navega a la carpeta `dashboard/datos/procesados/`
   - Importa cada archivo CSV (selecciona "Cargar" para cada uno)

4. **Configurar relaciones:**
   - Ve a la vista "Modelo" (icono de diagrama)
   - Crea las siguientes relaciones:
     * `leads[programa_id]` → `programas[id_programa]`
     * `leads[comercial_id]` → `comerciales[id_comercial]`
     * `matriculas[id_lead]` → `leads[id_lead]`
     * `matriculas[programa_id]` → `programas[id_programa]`
     * `matriculas[comercial_id]` → `comerciales[id_comercial]`
     * `metas_comerciales[programa_id]` → `programas[id_programa]`
     * `metas_comerciales[comercial_id]` → `comerciales[id_comercial]`
     * `usuarios_roles[id_comercial]` → `comerciales[id_comercial]`

5. **Crear tabla calendario:**
   - Clic en "Modelado" → "Nueva tabla"
   - Introduce la siguiente fórmula DAX:
   ```
   Calendario = 
   CALENDAR(DATE(2023, 1, 1), DATE(2023, 12, 31))
   ```
   - Añade columnas útiles:
   ```
   Mes = FORMAT([Date], "MMMM")
   Año = YEAR([Date])
   Trimestre = "Q" & QUARTER([Date])
   MesNum = MONTH([Date])
   ```

### 3. Crear medidas esenciales (10 minutos)

Crea las siguientes medidas:

```
# Leads
Total Leads = COUNTROWS(leads)

# Matrículas
Total Matrículas = COUNTROWS(matriculas)

# Tasa de conversión
Tasa Conversión = 
DIVIDE(
    [Total Matrículas],
    [Total Leads],
    0
)

# Objetivo de leads
Meta Leads = SUM(metas_comerciales[meta_leads])

# Objetivo de matrículas
Meta Matrículas = SUM(metas_comerciales[meta_matriculas])

# % Logro leads
% Logro Leads = 
DIVIDE(
    [Total Leads],
    [Meta Leads],
    0
) * 100

# % Logro matrículas
% Logro Matrículas = 
DIVIDE(
    [Total Matrículas],
    [Meta Matrículas],
    0
) * 100

# Leads nuevos
Leads Nuevos = 
COUNTROWS(
    FILTER(
        leads,
        leads[estado] = "Nuevo"
    )
)

# Leads pendientes
Leads Pendientes = 
COUNTROWS(
    FILTER(
        leads,
        leads[estado] = "Nuevo" || leads[estado] = "Contactado"
    )
)
```

### 4. Diseñar Dashboard Comercial (10-15 minutos)

Crea una página llamada "Dashboard Comercial":

1. **Añadir encabezado:**
   - Inserta un objeto "Título" en la parte superior
   - Texto: "Dashboard Comercial"

2. **Panel de KPIs generales:**
   - Añade tarjetas para:
     * % Logro Matrículas
     * Total Leads
     * Total Matrículas
     * Tasa Conversión

3. **Gráfico de evolución temporal:**
   - Añade un gráfico de líneas
   - Eje X: Calendario[Date]
   - Valor: Total Leads, Total Matrículas

4. **Tabla de programas:**
   - Añade una tabla o matriz
   - Filas: programas[nombre]
   - Valores: Total Leads, Total Matrículas, % Logro Matrículas, Tasa Conversión

5. **Filtros esenciales:**
   - Añade segmentadores para:
     * Calendario[Mes]
     * programas[facultad]
     * comerciales[nombre]

### 5. Diseñar Dashboard Analítico (10-15 minutos)

Crea una página llamada "Dashboard Analítico":

1. **Añadir encabezado:**
   - Inserta un objeto "Título" en la parte superior
   - Texto: "Dashboard Analítico"

2. **Panel de métricas detalladas:**
   - Añade matriz con:
     * Filas: programas[nombre]
     * Columnas: Calendario[Mes]
     * Valores: Total Leads, Total Matrículas, % Logro Matrículas

3. **Gráfico de dispersión:**
   - Añade un gráfico de dispersión
   - Eje X: Total Leads
   - Eje Y: Tasa Conversión
   - Tamaño: Total Matrículas
   - Leyenda: programas[facultad]
   - Detalles: programas[nombre]

4. **Análisis por comercial:**
   - Añade un gráfico de barras
   - Eje X: comerciales[nombre]
   - Valor: Total Matrículas, Meta Matrículas

5. **Filtros avanzados:**
   - Añade segmentadores para:
     * programas[nivel]
     * programas[facultad]
     * leads[origen]
     * Calendario[Trimestre]

### 6. Configurar seguridad (opcional, 5 minutos)

1. En la pestaña "Modelado", selecciona "Administrar roles"
2. Crea un rol "Comercial" con la restricción:
   ```
   usuarios_roles[id_comercial] = [id_comercial que corresponda]
   ```
3. Crea un rol "Coordinador" con restricciones adecuadas
4. Crea un rol "Dirección" sin restricciones

### 7. Publicar y compartir (5 minutos)

1. Prueba el informe utilizando "Ver como roles"
2. Guarda el archivo
3. Haz clic en "Publicar" en la pestaña Inicio
4. Selecciona un espacio de trabajo en Power BI Service

## Recursos adicionales

### Plantillas de DAX avanzadas

```
# Tendencia mensual
Tendencia MoM = 
VAR ActualMes = [Total Matrículas]
VAR MesAnterior = 
    CALCULATE(
        [Total Matrículas],
        DATEADD(Calendario[Date], -1, MONTH)
    )
RETURN
    DIVIDE(ActualMes - MesAnterior, MesAnterior, 0)

# Proyección
Proyección Fin Mes = 
VAR DiasTranscurridos = DAY(MAX(Calendario[Date]))
VAR DiasEnMes = DAY(EOMONTH(MAX(Calendario[Date]), 0))
VAR RitmoActual = [Total Matrículas]
RETURN
    RitmoActual * DiasEnMes / DiasTranscurridos
```

### Consejos para optimización

1. **Rendimiento:**
   - Mantén los archivos CSV actualizados en la carpeta procesados
   - Programa actualizaciones automáticas en Power BI Service

2. **Visuales personalizados:**
   - Considera usar visuales como "Card with States" para KPIs
   - Prueba "Power KPI" para visualizaciones más completas

3. **Publicación:**
   - Configura actualizaciones automáticas de datos
   - Establece alertas para métricas críticas
   - Usa Power BI Mobile para acceso en movimiento

## Solución de problemas comunes

1. **No se ven los datos:**
   - Verifica que los archivos CSV estén correctamente formateados
   - Comprueba las relaciones en el modelo

2. **Errores en cálculos:**
   - Revisa las fórmulas DAX
   - Verifica que los tipos de datos estén correctamente definidos

3. **Problemas de seguridad:**
   - Asegúrate de que la tabla usuarios_roles esté correctamente relacionada
   - Verifica la sintaxis de las reglas de seguridad

## Próximos pasos

Una vez implementada esta versión básica, puedes:

1. Añadir más visualizaciones específicas para tu equipo
2. Integrar fuentes de datos adicionales
3. Implementar actualizaciones automáticas
4. Crear paneles personalizados para diferentes roles 