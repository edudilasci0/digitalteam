# Instrucciones para Implementación de Dashboard Comercial y Analítico

## Arquitectura de la Solución

### Componentes Principales
1. Script Python para preparación de datos
2. Modelo de datos Power BI
3. Dashboard comercial simplificado
4. Dashboard analítico completo
5. Configuración de seguridad y roles

## 1. Preparación del Entorno

### Requisitos Previos
- Power BI Desktop (última versión)
- Cuenta Power BI Pro/Premium (para publicación)
- Python 3.8+ para scripts de preparación
- Acceso a fuentes de datos (CRM, Google Sheets)

### Estructura de Carpetas
```
/dashboard/
  /datos/
    /procesados/      # Datos limpios para Power BI
    /originales/      # Datos fuente sin procesar
  /scripts/           # Scripts de proceso ETL
  /reportes/          # Archivos PBIX
  /documentacion/     # Guías y manuales
```

## 2. Preparación de Datos

### Script ETL Centralizado
Crear el archivo `scripts/preparar_datos_dashboard.py`:

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def preparar_datos_dashboard(ruta_origen, ruta_destino):
    """
    Procesa los datos para el dashboard unificado.
    
    Args:
        ruta_origen: Ruta a los datos originales
        ruta_destino: Ruta donde guardar los datos procesados
    """
    # 1. Cargar datos
    df_leads = pd.read_csv(f"{ruta_origen}/leads.csv")
    df_matriculas = pd.read_csv(f"{ruta_origen}/matriculas.csv")
    df_programas = pd.read_csv(f"{ruta_origen}/programas.csv")
    df_metas = pd.read_csv(f"{ruta_origen}/metas_comerciales.csv")
    
    # 2. Transformar fechas
    df_leads['fecha_creacion'] = pd.to_datetime(df_leads['fecha_creacion'])
    
    # 3. Crear tabla de hechos principal
    df_rendimiento = calcular_metricas_rendimiento(df_leads, df_matriculas, 
                                                 df_programas, df_metas)
    
    # 4. Crear tablas dimensionales
    df_tiempo = crear_dimension_tiempo(df_leads)
    df_comerciales = crear_dimension_comerciales(df_leads)
    
    # 5. Exportar para Power BI
    df_rendimiento.to_csv(f"{ruta_destino}/rendimiento.csv", index=False)
    df_tiempo.to_csv(f"{ruta_destino}/dimension_tiempo.csv", index=False)
    df_comerciales.to_csv(f"{ruta_destino}/dimension_comerciales.csv", index=False)
    df_programas.to_csv(f"{ruta_destino}/dimension_programas.csv", index=False)
    
    print(f"Datos procesados y guardados en {ruta_destino}")
    
def calcular_metricas_rendimiento(df_leads, df_matriculas, df_programas, df_metas):
    """Calcula métricas principales de rendimiento por programa y comercial"""
    # Código para cálculo de métricas
    # [Implementación detallada de cálculos]
    
    return df_resultado

def crear_dimension_tiempo(df_leads):
    """Crea tabla calendario para análisis temporal"""
    # Crear tabla de fechas con atributos para análisis
    # [Implementación de calendario]
    
    return df_tiempo

def crear_dimension_comerciales(df_leads):
    """Crea dimensión para análisis por comercial"""
    # [Implementación]
    
    return df_comerciales

if __name__ == "__main__":
    preparar_datos_dashboard("datos/originales", "datos/procesados")
```

### Campos Requeridos
Para cada fuente necesitas asegurar estos campos mínimos:

**Leads:**
- ID único
- Fecha creación
- Programa
- Estado (nuevo, contactado, etc.)
- Comercial asignado
- Origen (canal marketing)

**Matrículas:**
- ID único
- ID Lead asociado
- Fecha matrícula
- Programa
- Valor

**Programas:**
- ID único
- Nombre
- Nivel (grado, posgrado)
- Facultad/Área
- Categoría

**Metas comerciales:**
- Comercial
- Programa
- Período
- Meta leads
- Meta matrículas

## 3. Modelo de Datos Power BI

### Importación de Datos
1. Abrir Power BI Desktop
2. Usar "Obtener datos" → Seleccionar CSV
3. Importar todas las tablas de `datos/procesados/`

### Modelado
1. **Relaciones:**
   - Rendimiento → Dimensión Tiempo (por fecha)
   - Rendimiento → Dimensión Programas (por id_programa)
   - Rendimiento → Dimensión Comerciales (por id_comercial)

2. **Medidas DAX esenciales:**

```
// % Logro general
% Logro = 
DIVIDE(
    SUM(Rendimiento[matriculas]),
    SUM(Rendimiento[meta_matriculas]),
    0
) * 100

// Tasa conversión
Tasa Conversión = 
DIVIDE(
    SUM(Rendimiento[matriculas]),
    SUM(Rendimiento[leads]),
    0
) * 100

// Delta vs periodo anterior
Delta Periodo = 
VAR ActualPeriodo = [% Logro]
VAR AnteriorPeriodo = 
    CALCULATE(
        [% Logro],
        DATEADD(DimTiempo[Fecha], -1, MONTH)
    )
RETURN
    ActualPeriodo - AnteriorPeriodo
```

## 4. Dashboard Comercial (Simplificado)

### Diseño de Página
1. **Cabecera:**
   - Título: "Dashboard Comercial [Nombre Comercial]"
   - Selector de fechas (últimos 7/15/30 días)

2. **Panel General:**
   - Tarjeta KPI grande: "% Logro Personal"
   - Indicador: "Leads pendientes hoy"
   - Mini-gráfico líneas: "Evolución últimos días"

3. **Programas Asignados:**
   - Tabla o gráfico barras horizontal
   - Columnas: Programa, % Logro, Tendencia (sparkline)
   - Orden descendente por % logro

### Filtros y Segmentación
- Selector por programa
- Filtro por estado del lead
- Segmentador temporal

## 5. Dashboard Analítico (Completo)

### Diseño de Página Principal
1. **Panel General:**
   - KPIs globales (% logro, leads, matriculas, tasa conversión)
   - Gráfico líneas: Evolución temporal
   - Gráfico barras: Top/Bottom programas

2. **Análisis por Programa:**
   - Matriz detallada con todas las métricas
   - Gráfico dispersión: Volumen vs Conversión
   - Mapa de calor: Rendimiento por programa y tiempo

3. **Análisis por Comercial:**
   - Tabla comparativa comerciales
   - Distribución carga trabajo
   - Eficiencia conversión

### Navegación y Páginas Adicionales
- Pestañas para diferentes análisis
- Botones de navegación entre secciones
- Tooltips enriquecidos con información adicional

## 6. Configuración de Seguridad (RLS)

### Crear Tabla de Roles
1. Importar o crear tabla con estructura:
   ```
   - UsuarioEmail
   - Rol (Comercial, Analista, Dirección)
   - ProgramasPermitidos
   - VerDashboardCompleto (0/1)
   ```

2. Configurar relaciones con resto del modelo

### Definir Roles en Power BI
1. Menú Modelado → Administrar Roles
2. Crear rol "Comercial":
   ```
   Rendimiento[id_comercial] = LOOKUPVALUE(
       Usuarios[id_comercial],
       Usuarios[UsuarioEmail], USERPRINCIPALNAME()
   )
   ```

3. Crear rol "Analista":
   ```
   Usuarios[VerDashboardCompleto] = 1 && 
   Usuarios[UsuarioEmail] = USERPRINCIPALNAME()
   ```

## 7. Publicación

### Publicar en Power BI Service
1. "Archivo" → "Publicar" → Seleccionar Workspace
2. Configurar programación de actualización (recomendado: 2 veces al día)
3. Configurar enlaces de acceso directo para usuarios

### Distribución de Acceso
1. Compartir dashboard con usuarios según roles
2. Configurar alertas automáticas
3. Implementar envío programado de informes por correo

## 8. Actualización e Interpretación

### Proceso de Actualización
1. Ejecutar script ETL `preparar_datos_dashboard.py` diariamente
2. Verificar actualización automática en Power BI Service
3. Revisar errores en el registro de actualización

### Interpretación de Métricas

#### Para Comerciales:
- **% Logro:** Porcentaje completado del objetivo asignado
  - <70%: Atención inmediata requerida
  - 70-90%: Seguimiento necesario
  - >90%: Buen rendimiento

- **Leads Pendientes:** Número de leads sin contactar
  - Color rojo: Urgentes (>48h sin contacto)
  - Color amarillo: Atención hoy
  - Color verde: Al día

#### Para Analistas/Dirección:
- **Análisis de Varianza:** Comparación entre períodos
  - Identificar patrones estacionales
  - Detectar programas con oportunidades de mejora

- **Comparativa Programas:**
  - Cuadrante superior derecho: Alto volumen + alta conversión → Mantener estrategia
  - Cuadrante superior izquierdo: Bajo volumen + alta conversión → Aumentar marketing
  - Cuadrante inferior derecho: Alto volumen + baja conversión → Mejorar calificación/seguimiento
  - Cuadrante inferior izquierdo: Bajo volumen + baja conversión → Revisar viabilidad

## 9. Solución de Problemas

### Errores Comunes
- **Datos no actualizados:** Verificar ejecución del script ETL
- **Filtros incorrectos:** Revisar configuración RLS
- **Visualizaciones vacías:** Comprobar relaciones entre tablas

### Soporte
Para asistencia técnica, contactar al equipo de BI en: [correo@soporte.com] 