# Comandos de Referencia: Motor de Decisión Marketing Educativo

Este documento es una guía de referencia rápida de los comandos disponibles para realizar diferentes tipos de análisis con el Motor de Decisión. Está organizado por frecuencia recomendada de uso (diario, quincenal, mensual).

## Análisis Diarios

### 1. Monitoreo de Rendimiento de Campañas

```bash
# Reporte básico de rendimiento diario
python src/main.py --comando performance_diario --fecha hoy

# Monitoreo con detección de anomalías
python src/analysis/anomalias.py --periodo hoy --umbral medio --notificar true

# Dashboard de métricas críticas
python src/ui/dashboard.py --vista operativa --periodo ultimas_24h --actualizar true
```

### 2. Seguimiento de Leads Recientes

```bash
# Resumen de leads generados
python src/analysis/leads.py --periodo hoy --agrupar canal,programa

# Análisis de calidad de leads
python src/analysis/calidad_leads.py --periodo ultimas_24h --exportar csv

# Seguimiento de velocidad de contacto
python src/analysis/velocidad_contacto.py --periodo hoy --alerta true
```

### 3. Alertas Automáticas

```bash
# Configurar sistema de alertas
python src/notifications/config.py --metricas cpa,ctr,conversion --sensibilidad alta

# Ejecutar verificación de alertas
python src/notifications/check_alerts.py --ejecutar ahora

# Ver historial de alertas recientes
python src/notifications/historico.py --periodo ultimas_48h
```

## Análisis Quincenales

### 1. Evaluación de Campañas por Fase

```bash
# Análisis por fase de campañas
python src/models/calendario_campanas.py --analisis fases --periodo ultimos_15dias

# Recomendaciones por fase
python src/models/recomendaciones.py --tipo fase_campana --detalle true

# Visualización de estado de campañas
python src/visualizacion/estado_campanas.py --vista fases --exportar powerbi
```

### 2. Redistribución de Presupuesto

```bash
# Análisis de ROI por canal y programa
python src/analysis/roi.py --periodo ultimos_15dias --agrupar canal,programa

# Recomendaciones de redistribución
python src/models/optimizador.py --tipo redistribucion --restriccion presupuesto_fijo

# Simulación de escenarios
python src/models/simulador.py --escenario redistribucion_optima --horizonte 15dias
```

### 3. Análisis de Velocidad de Conversión

```bash
# Análisis de ciclo de conversión
python src/analysis/ciclo_conversion.py --periodo ultimos_30dias --agrupar canal,programa

# Identificación de aceleradores
python src/analysis/factores_conversion.py --tipo aceleradores --top 10

# Reporte de embudo de conversión
python src/ui/generador_reportes.py --tipo embudo_conversion --formato powerpoint
```

### 4. Forecast a Corto Plazo

```bash
# Proyección de leads próximos 15 días
python src/models/forecast.py --metrica leads --horizonte 15dias

# Proyección de matrículas
python src/models/forecast.py --metrica matriculas --horizonte 30dias

# Dashboard integrado de proyecciones
python src/ui/dashboard.py --vista forecast --periodo proximos_15dias
```

## Análisis Mensuales

### 1. Análisis de Tendencias

```bash
# Análisis de tendencias temporales
python src/analysis/tendencias.py --periodo ultimos_6meses --granularidad semana

# Detección de estacionalidad
python src/models/estacionalidad.py --datos historicos --visualizar true

# Comparativa interanual
python src/analysis/comparativa.py --periodo mes_actual --vs mismo_mes_anterior
```

### 2. Evaluación de Eficiencia por Programa

```bash
# Análisis de rentabilidad por programa
python src/analysis/rentabilidad.py --dimension programa --metrica margen_contribucion

# Eficiencia de conversión por programa
python src/analysis/eficiencia.py --agrupar programa --ordenar roi_descendente

# Reporte ejecutivo de performance por programa
python src/ui/generador_reportes.py --tipo performance_programa --periodo ultimo_mes
```

### 3. Análisis de Customer Journey

```bash
# Mapeo completo del journey
python src/analysis/customer_journey.py --detalle alto --visualizar true

# Identificación de puntos de fricción
python src/analysis/puntos_friccion.py --umbral alto --sugerir_mejoras true

# Análisis de interacciones multi-touch
python src/analysis/touchpoints.py --modelo atribucion_data_driven
```

### 4. Evaluación de Canales y Fuentes

```bash
# Análisis de atribución avanzada
python src/models/atribucion.py --modelo data_driven --ventana 30dias

# Valor del ciclo de vida por canal
python src/analysis/ltv.py --segmentar canal_origen --horizonte 12meses

# Análisis de asistencia entre canales
python src/analysis/asistencia_canales.py --visualizar diagrama_sankey
```

### 5. Planificación de Presupuesto

```bash
# Optimización de presupuesto mensual
python src/models/optimizador_presupuesto.py --objetivo maximizar_matriculas --restriccion presupuesto_maximo

# Simulación de escenarios
python src/models/simulador.py --escenarios multiple --variables presupuesto,canales,estacionalidad

# Generación de plan estratégico
python src/ui/generador_reportes.py --tipo plan_estrategico --horizonte trimestral
```

## Comandos de Utilidad

### Configuración y Mantenimiento

```bash
# Verificar estado del sistema
python src/utils/system_check.py --componentes todos

# Actualizar datos de referencia
python src/data/actualizar_referencias.py --fuente todas

# Respaldo de configuraciones
python src/utils/backup.py --elementos configuracion,modelos
```

### Acceso Rápido a Datos

```bash
# Extraer datos para análisis ad-hoc
python src/data/extractor.py --query personalizada --params "canal=Facebook,fecha_inicio=2023-01-01"

# Exportar datos procesados
python src/data/exportar.py --formato excel --filtro "programa=MBA,periodo=ultimo_mes"

# Generar datasets para PowerBI
python src/data/powerbi_datasets.py --regenerar todos --publicar true
```

## Notas Importantes

- Los comandos pueden requerir permisos específicos según el rol del usuario.
- Se recomienda configurar el archivo `.env` con las credenciales necesarias.
- Para análisis personalizados, use el parámetro `--help` con cualquier comando para ver opciones adicionales.
- Todos los reportes se guardan por defecto en la carpeta `output/` a menos que se especifique lo contrario.

---

Última actualización: 28 de abril de 2024 