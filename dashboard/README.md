# Dashboard de rendimiento 

## Descripción
Este proyecto proporciona una solución completa para implementar dashboards de seguimiento comercial y análisis de matrículas educativas, diseñado específicamente para equipos de marketing y ventas en instituciones educativas.

## Estructura del Proyecto

```
dashboard/
  ├── datos/
  │   ├── plantillas/     # Datos de ejemplo listos para usar
  │   ├── procesados/     # Datos procesados para Power BI
  │   └── originales/     # Ubicación para almacenar datos fuente
  ├── logs/               # Registros de actualizaciones
  ├── actualizar_datos.py # Script para actualizar datos
  ├── ejemplo_dashboard.md # Visualizaciones de ejemplo
  └── plantilla_power_bi.md # Instrucciones de implementación
```

## Implementación Rápida

Para implementar rápidamente el dashboard completo:

1. **Preparar los datos**
   - Los datos de ejemplo están listos en `datos/plantillas/`
   - Ejecutar `python actualizar_datos.py` para preparar el entorno

2. **Crear el dashboard en Power BI**
   - Seguir las instrucciones detalladas en `plantilla_power_bi.md`
   - Tiempo estimado de implementación: 30-60 minutos

3. **Personalizar visualizaciones**
   - Usar `ejemplo_dashboard.md` como referencia visual

## Características Principales

### 1. Dashboard Comercial (para equipo de ventas)
- Vista simplificada con KPIs relevantes para comerciales
- Seguimiento de leads pendientes y conversiones
- Visualización de programas asignados a cada comercial

### 2. Dashboard Analítico (para dirección/marketing)
- Análisis detallado de rendimiento por programa
- Comparativas entre canales de marketing
- Tendencias temporales y proyecciones
- Visualización "Top y Bottom Performers"

### 3. Seguridad y Personalización
- Implementación RLS (Row-Level Security) para mostrar datos relevantes a cada rol
- Filtros personalizados por facultad, nivel educativo y período

## Mantenimiento y Actualización

1. **Actualización de datos**
   - Programar ejecución diaria de `actualizar_datos.py`
   - Para modificar fuentes de datos, editar la función `actualizar_datos_desde_fuentes()`

2. **Ampliación**
   - Añadir nuevas métricas modificando las fórmulas DAX en `plantilla_power_bi.md`
   - Agregar visualizaciones siguiendo ejemplos en `ejemplo_dashboard.md`

## Requisitos Técnicos

- **Software necesario:**
  - Power BI Desktop
  - Python 3.8+
  - Pandas

- **Para publicación:**
  - Cuenta Power BI Pro o Premium
  - Permisos para configurar RLS

## Soporte y Contacto

Para preguntas técnicas sobre la implementación, contacta al equipo de desarrollo interno.

---

*Esta solución fue desarrollada para optimizar la gestión comercial y proporcionar insights accionables para mejorar las tasas de conversión de leads a matrículas.* 
