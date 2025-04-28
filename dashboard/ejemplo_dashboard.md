# Visualización del Dashboard Final

A continuación se muestran ejemplos de cómo debería verse el dashboard una vez implementado:

## Dashboard Comercial (Simplificado)

```
+-----------------------------------------------------------------------+
|                                                                       |
|                      DASHBOARD COMERCIAL                              |
|                                                                       |
+---------------+---------------------+-------------------------------+
|               |                     |                               |
| % LOGRO       | LEADS PENDIENTES    | TASA CONVERSIÓN              |
| 78%           | 12                  | 25%                          |
|               |                     |                               |
+---------------+---------------------+-------------------------------+
|                                                                       |
|                    EVOLUCIÓN TEMPORAL                                 |
|    ↗                                                                  |
|   ↗  ↘                                                                |
|  ↗     ↘     ↗                                                        |
| ↗        ↘ ↗                                                          |
+-----------------------------------------------------------------------+
|                                                                       |
|               RENDIMIENTO POR PROGRAMA                                |
|                                                                       |
| PROGRAMA                  | % LOGRO | LEADS | MATRÍC. | CONVERSIÓN   |
| --------------------------+--------+-------+---------+-------------- |
| 1. Administración         | 95%    | 18    | 5       | 28%           |
| 2. Ing. Informática       | 85%    | 25    | 6       | 24%           |
| 3. Marketing Digital      | 76%    | 15    | 3       | 20%           |
| 4. Ciencia de Datos       | 65%    | 12    | 2       | 17%           |
| 5. MBA                    | 50%    | 10    | 1       | 10%           |
|                                                                       |
+-----------------------------------------------------------------------+
```

## Dashboard Analítico (Completo)

```
+-----------------------------------------------------------------------+
|                                                                       |
|                      DASHBOARD ANALÍTICO                              |
|                                                                       |
+---------------+---------------------+-------------------------------+
|               |                     |                               |
| TOTAL LEADS   | TOTAL MATRÍCULAS    | % GLOBAL LOGRO               |
| 80            | 17                  | 85%                          |
|               |                     |                               |
+---------------+---------------------+-------------------------------+
|                           |                                          |
|    COMPARATIVA PROGRAMAS  |        RENDIMIENTO COMERCIALES           |
|                           |                                          |
|    o                      |  Juan  ■■■■■■■■■■■■■■                    |
|   o  o                    |  María ■■■■■■■■■■■                       |
|  o      o                 |  Carlos ■■■■■■■■■■■■                     |
| o         o               |                                          |
+---------------------------+------------------------------------------+
|                                                                       |
|               RENDIMIENTO TEMPORAL POR PROGRAMA                       |
|                                                                       |
| PROGRAMA           | ENE | FEB | MAR | ABR | MAY | ... | TOTAL       |
| ------------------+-----+-----+-----+-----+-----+-----+------------- |
| Administración    | 3   | 5   | 4   | ... | ... | ... | 25           |
| Ing. Informática  | 6   | 8   | 7   | ... | ... | ... | 42           |
| Marketing Digital | 4   | 3   | 5   | ... | ... | ... | 32           |
| Ciencia de Datos  | 2   | 4   | 3   | ... | ... | ... | 18           |
|                                                                       |
+-----------------------------------------------------------------------+
```

## Visualización de "Top y Bottom Performers"

```
+-----------------------------------------------------------------------+
|                                                                       |
|                 TOP PERFORMERS (% LOGRO)                              |
|                                                                       |
| 1. Administración (Grado)      ■■■■■■■■■■■■■■■■■■■■■  145%           |
| 2. Ing. Informática (Grado)    ■■■■■■■■■■■■■■■■■■■    132%           |
| 3. Marketing Digital (Posg.)   ■■■■■■■■■■■■■■         105%           |
| 4. Derecho (Grado)             ■■■■■■■■■■■■           95%            |
| 5. MBA (Posgrado)              ■■■■■■■■■■             90%            |
|                                                                       |
+-----------------------------------------------------------------------+
|                                                                       |
|                 BOTTOM PERFORMERS (% LOGRO)                           |
|                                                                       |
| 22. Arquitectura (Grado)       ■■■■■■                 48%            |
| 23. Medicina (Grado)           ■■■■■                  45%            |
| 24. Enfermería (Grado)         ■■■■                   38%            |
| 25. Psicología (Grado)         ■■■                    32%            |
| 26. Diseño Gráfico (Grado)     ■■                     22%            |
|                                                                       |
+-----------------------------------------------------------------------+
```

## Gráfico de Dispersión (Volumen vs Conversión)

```
+-----------------------------------------------------------------------+
|                MAPA DE RENDIMIENTO POR PROGRAMA                        |
|  ^                                                                     |
|  |                                                                     |
|  |    o MBA                    o Ingeniería                            |
|  |                                                                     |
|C |                                                                     |
|O |    o Derecho                                                        |
|N |                                                                     |
|V |                                                                     |
|E |                             o Marketing                             |
|R |    o Psicología                                                     |
|S |                                                                     |
|I |                                                                     |
|Ó |    o Medicina               o Arquitectura                          |
|N |                                                                     |
|  |                                                                     |
|  +--------------------------------------------------------------->     |
|                          VOLUMEN DE LEADS                              |
+-----------------------------------------------------------------------+

    Tamaño círculo = Presupuesto asignado
    Color = % Logro (Verde > 90%, Amarillo 70-90%, Rojo < 70%)
```

## Dashboard para Comerciales (Simplificado)

```
+-----------------------------------------------------------------------+
|                                                                       |
|             DASHBOARD COMERCIAL - JUAN MARTÍNEZ                       |
|                                                                       |
+---------------+---------------------+-------------------------------+
|               |                     |                               |
| MI % LOGRO    | MIS LEADS PENDIENTES| MI CONV. MEDIA                |
| 82%           | 5                   | 27%                          |
|               |                     |                               |
+---------------+---------------------+-------------------------------+
|                                                                       |
|                 MIS PROGRAMAS ASIGNADOS                               |
|                                                                       |
| PROGRAMA                  | % LOGRO | PENDIENT.| MATRÍC. | OBJETIVO  |
| --------------------------+--------+----------+---------+----------- |
| 1. Administración         | 95%    | 2        | 5       | 5          |
| 3. Marketing Digital      | 76%    | 3        | 3       | 4          |
| 4. Ciencia de Datos       | 65%    | 0        | 2       | 3          |
|                                                                       |
+-----------------------------------------------------------------------+
```

## Instrucciones para personalizar visuales

Para que el dashboard se asemeje a estos ejemplos:

1. **Uso de iconos y colores:**
   - Para KPIs: usar tarjetas con iconos (↑/↓) según tendencia
   - Esquema de colores: verde (#007559) para positivo, rojo (#B42F37) para negativo

2. **Formato condicional:**
   - Aplicar formato condicional a % de logro:
     * >95%: Verde oscuro
     * 80-95%: Verde claro
     * 65-80%: Amarillo
     * <65%: Rojo

3. **Tooltips enriquecidos:**
   - Configurar tooltips que muestren:
     * Detalles adicionales al pasar el mouse
     * Tendencia vs período anterior
     * Recomendaciones de acción

4. **Segmentación de datos:**
   - Utilizar segmentadores sincronizados entre páginas
   - Configurar filtros predeterminados para inicio 