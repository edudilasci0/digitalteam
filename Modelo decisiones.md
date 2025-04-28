# Guía de Toma de Decisiones para Equipos de Marketing y Media Planners

## Introducción

Este documento proporciona instrucciones claras sobre cómo utilizar el Sistema Predictor y Optimizador de Matrículas para la toma de decisiones efectivas en sus campañas. El sistema está diseñado específicamente para que los media planners y equipos de marketing puedan realizar ajustes tácticos semanales o quincenales basados en datos reales y predicciones.

## Frecuencia recomendada de análisis

- **Revisión quincenal**: Análisis completo de rendimiento y ajustes principales
- **Monitoreo semanal**: Seguimiento rápido de KPIs críticos y ajustes menores
- **Análisis mensual**: Evaluación estratégica completa con revisión de estacionalidad

## Herramientas disponibles

El sistema ofrece los siguientes módulos para la toma de decisiones:

1. **Dashboard Comercial**: Visualización del progreso actual vs. estimaciones
2. **Análisis de Estacionalidad**: Patrones históricos y predicciones futuras
3. **Simulación Monte Carlo (NUEVO)**: Intervalos de confianza para predicciones
4. **Análisis de Elasticidad (NUEVO)**: Sensibilidad de conversión a diferentes factores
5. **Dashboards Power BI (NUEVO)**: Visualizaciones interactivas para diferentes roles

## Proceso de toma de decisiones quincenal

### Paso 1: Revisión del Dashboard Comercial

1. Acceda a la carpeta `/salidas/dashboard_comercial/` y abra el archivo HTML con la fecha más reciente, o utilice el Dashboard Power BI.
2. Analice las 3 secciones principales:
   - **Barras de progreso**: Comparan tiempo transcurrido vs. leads captados vs. matrículas
   - **Comparación con estimación**: Muestra si está dentro, por encima o por debajo del rango esperado
   - **Observaciones y recomendaciones**: Lectura detallada de la situación actual

### Paso 2: Interpretación del estado actual

Identifique en qué escenario se encuentra su campaña:

| Estado | Interpretación | Acción general |
|--------|----------------|----------------|
| **POR DEBAJO** | Rendimiento inferior al esperado | Intervención inmediata y redistribución de recursos |
| **DENTRO DEL RANGO** | Rendimiento según lo esperado | Optimizaciones menores y monitoreo |
| **POR ENCIMA** | Rendimiento superior al esperado | Capitalizar éxito y evaluar reasignación |

### Paso 3: Revisión de patrones estacionales

1. Acceda a la carpeta `/salidas/analisis_estacionalidad/` y abra el reporte HTML más reciente, o utilice la sección correspondiente en Power BI.
2. Compare el período actual con los patrones históricos:
   - ¿Es un período de alta o baja estacionalidad para leads?
   - ¿Cómo afecta la estacionalidad a la tasa de conversión?
   - ¿Las predicciones muestran cambios esperados en las próximas semanas?

### Paso 4: Análisis de intervalos de confianza (NUEVO)

1. Revise la sección "Intervalos de confianza" en el Dashboard Analítico de Power BI o en `/dashboard/datos/resultados_analisis/intervalos_confianza.csv`.
2. Determine el nivel de certidumbre de las predicciones:
   - **Alta certidumbre** (intervalo estrecho): La predicción es confiable, tome decisiones con mayor seguridad.
   - **Certidumbre media** (intervalo moderado): Proceda con precaución y monitoreo constante.
   - **Baja certidumbre** (intervalo amplio): Considere escenarios múltiples y planifique con mayor flexibilidad.

3. Identifique los programas con mayor y menor certidumbre:
   - Para programas con alta certidumbre: Implemente estrategias específicas y precisas.
   - Para programas con baja certidumbre: Diseñe planes de contingencia y evite comprometer demasiados recursos.

### Paso 5: Evaluación de elasticidad de factores (NUEVO)

1. Consulte el análisis de elasticidad en el Dashboard Analítico o en `/dashboard/datos/resultados_analisis/elasticidad_factores.csv`.
2. Identifique los canales con mayor elasticidad (más sensibles a cambios en la inversión).
3. Considere las recomendaciones de inversión basadas en elasticidades:
   - **Alta elasticidad (>1.0)**: Una inversión adicional generará retornos proporcionalmente mayores.
   - **Elasticidad unitaria (~1.0)**: Inversión adicional generará retornos proporcionales.
   - **Baja elasticidad (<1.0)**: Inversión adicional generará retornos proporcionalmente menores.

### Paso 6: Toma de decisiones tácticas

Basándose en los datos, tome decisiones tácticas según esta matriz extendida:

| Estado | Estacionalidad | Certidumbre | Decisiones recomendadas |
|--------|----------------|-------------|-------------------------|
| **POR DEBAJO** | Alta | Alta | • Aumentar inversión significativamente en canales de alta elasticidad<br>• Implementar promociones especiales inmediatas<br>• Activar canales secundarios de refuerzo |
| **POR DEBAJO** | Alta | Baja | • Aumentar inversión moderadamente, priorizando canales probados<br>• Implementar A/B testing para identificar mensajes efectivos<br>• Preparar plan de contingencia si el rendimiento no mejora |
| **POR DEBAJO** | Baja | Alta | • Aumentar inversión en canales específicos según elasticidad<br>• Implementar promociones especiales<br>• Optimizar proceso de conversión |
| **POR DEBAJO** | Baja | Baja | • Mantener inversión actual pero redistribuir entre canales<br>• Realizar pruebas de concepto en escala pequeña<br>• Analizar datos con mayor frecuencia para reducir incertidumbre |
| **DENTRO DEL RANGO** | Alta | Alta | • Mantener estrategia actual<br>• Optimizar asignación entre canales según elasticidad<br>• Planificar recursos para picos de demanda |
| **DENTRO DEL RANGO** | Alta | Baja | • Mantener inversión global pero diversificar canales<br>• Reforzar seguimiento a leads de alta calidad<br>• Implementar pruebas para reducir incertidumbre |
| **DENTRO DEL RANGO** | Baja | Alta | • Optimizar estrategia enfocándose en conversión<br>• Considerar inversión adicional en canales de alta elasticidad<br>• Prepararse para próximos periodos de alta estacionalidad |
| **DENTRO DEL RANGO** | Baja | Baja | • Mantener inversión planificada<br>• Diversificar canales y estrategias<br>• Mejorar calidad de datos para reducir incertidumbre |
| **POR ENCIMA** | Alta | Alta | • Capitalizar éxito con inversión adicional<br>• Documentar factores de éxito<br>• Reforzar equipo comercial para atender demanda |
| **POR ENCIMA** | Alta | Baja | • Mantener inversión actual pero monitorear diariamente<br>• Identificar y reforzar factores de éxito<br>• Desarrollar capacidad para escalar si el rendimiento se mantiene |
| **POR ENCIMA** | Baja | Alta | • Estudiar y documentar factores de éxito para replicar<br>• Evaluar reasignación de recursos a otros programas<br>• Considerar ajuste al alza de metas |
| **POR ENCIMA** | Baja | Baja | • Mantener estrategia exitosa<br>• Implementar pruebas para identificar factores de éxito<br>• Preparar plan de capitalización si el éxito se confirma |

## Decisiones específicas por métrica

### Cuando la captación de leads está por debajo del objetivo

1. **Inversión en canales**:
   - Revise el informe de ROI por canal (disponible en `/salidas/analisis_roi/`)
   - Aumente presupuesto en los 2-3 canales con mejor rendimiento actual
   - Reduzca o pause canales con CPA superior al 150% del objetivo

2. **Creatividades y mensajes**:
   - Revise las tasas de clic (CTR) de las creatividades activas
   - Retire o modifique anuncios con CTR inferior al 50% del promedio
   - Destaque elementos de urgencia si el período de inscripción está avanzado

3. **Segmentación**:
   - Amplíe criterios de segmentación para aumentar alcance si hay presupuesto disponible
   - Revise comportamiento de audiencias lookalike y ajuste porcentajes de similitud
   - Considere nuevos segmentos basados en intereses complementarios

### Cuando la tasa de conversión está por debajo del objetivo

1. **Calidad de leads**:
   - Revise las fuentes de tráfico que generan leads con menor conversión
   - Ajuste filtros de calificación para eliminar segmentos de baja conversión
   - Modifique formularios para incluir preguntas de calificación adicionales

2. **Proceso de seguimiento**:
   - Verifique tiempo de respuesta a leads nuevos (debe ser <1 hora en horario laboral)
   - Aumente frecuencia de contacto para leads no contactados
   - Implemente contenido nurturing adicional para leads en fase de consideración

3. **Ofertas y promociones**:
   - Evalúe implementar promociones temporales para acelerar decisiones
   - Considere descuentos por pronto pago o beneficios exclusivos por tiempo limitado
   - Destaque casos de éxito y testimonios en comunicaciones de seguimiento

## Uso de simulaciones Monte Carlo en decisiones (NUEVO)

Las simulaciones Monte Carlo proporcionan una visión más completa del rango de posibles resultados, permitiendo:

1. **Evaluar el riesgo de no alcanzar objetivos**:
   - Si más del 20% de las simulaciones quedan por debajo del objetivo mínimo, el riesgo es alto
   - Si menos del 10% quedan por debajo, el riesgo es bajo

2. **Determinar la probabilidad de diferentes escenarios**:
   - Determinar la probabilidad de superar el 120% del objetivo (escenario excelente)
   - Determinar la probabilidad de no alcanzar el 80% del objetivo (escenario crítico)
   - Usar estas probabilidades para planificar recursos y expectativas

3. **Tomar decisiones basadas en tolerancia al riesgo**:
   - Estrategias conservadoras: Planificar basándose en el percentil 25 de simulaciones
   - Estrategias moderadas: Planificar basándose en el valor medio
   - Estrategias optimistas: Planificar basándose en el percentil 75

### Ejemplo de aplicación:

**Situación**: Las simulaciones Monte Carlo para conversiones de leads muestran:
- Valor promedio: 100 matrículas
- Rango 80% confianza: [85-115] matrículas
- Objetivo establecido: 95 matrículas

**Análisis**:
1. Probabilidad de alcanzar el objetivo: ~65% de simulaciones están por encima de 95 matrículas
2. Riesgo de fallar objetivo dramáticamente: ~10% de simulaciones por debajo de 85 matrículas
3. Potencial de sobrecumplimiento: ~20% de simulaciones superan 115 matrículas

**Decisiones tácticas**:
1. Mantener inversión actual pero redistribuir entre canales con mayor elasticidad
2. Preparar plan de contingencia en caso de caer por debajo de 90 matrículas
3. Planificar recursos comerciales para escenarios entre 90-110 matrículas
4. Revisar análisis semanalmente para ajustar según evolución

## Interpretación de métricas de confianza (NUEVO)

Para tomar decisiones basadas en la confiabilidad de las predicciones:

### Métricas R² (coeficiente de determinación)

| Valor R² | Interpretación | Acción recomendada |
|----------|----------------|-------------------|
| >0.8 | Modelo altamente predictivo | Confianza alta en predicciones, invertir según recomendaciones |
| 0.6-0.8 | Buena capacidad predictiva | Confianza moderada, verificar con otras métricas antes de decisiones grandes |
| <0.6 | Capacidad predictiva limitada | Usar predicciones como guía general, no como base única para decisiones |

### Error porcentual absoluto medio (MAPE)

| MAPE | Interpretación | Acción recomendada |
|------|----------------|-------------------|
| <10% | Alta precisión | Planificar con confianza basado en valores puntuales |
| 10-20% | Precisión aceptable | Considerar un margen de error en planificación |
| >20% | Precisión limitada | Planificar escenarios múltiples, ser conservador en compromisos |

## Herramientas de análisis adicionales

Para análisis más detallados, utilice:

1. **Análisis de Elasticidad** (`scripts/analizar_elasticidad.py` o Power BI):
   - Revise cómo responde la captación de leads a cambios en la inversión
   - Determine puntos óptimos de inversión por canal
   - Identifique canales saturados vs. canales con potencial de escalabilidad

2. **Proyección de Convocatoria con intervalos de confianza** (`scripts/ejecutar_analisis_completo.py`):
   - Evalúe escenarios "qué pasaría si" con diferentes niveles de inversión
   - Revise la distribución completa de posibles resultados (no solo el promedio)
   - Ajuste estimaciones de matrículas finales considerando probabilidades

3. **Dashboard Power BI Analítico**:
   - Acceda a visualizaciones interactivas para análisis detallado
   - Use filtros para evaluar programas y canales específicos
   - Aproveche los tooltips enriquecidos para información adicional

## Calendario de decisiones

El calendario ha sido actualizado para incorporar el nuevo flujo de análisis:

| Día | Actividad | Responsable |
|-----|-----------|-------------|
| **Lunes** | Ejecución de análisis completo y generación de informes | Analista de datos |
| **Martes AM** | Revisión básica de métricas y alertas | Media planner + Coordinador de marketing |
| **Martes PM** | Revisión de intervalos de confianza y elasticidad | Media planner + Analista |
| **Miércoles** | Ajustes tácticos basados en análisis | Media planner |
| **Jueves** | Seguimiento de ajustes implementados | Media planner |
| **Viernes** | Resumen semanal y planificación | Equipo completo |
| **Quincenal (1 y 15)** | Revisión estratégica con simulaciones Monte Carlo | Director + Media planner + Analista |
| **Mensual (fin de mes)** | Evaluación completa y ajuste de modelos | Comité directivo |

## Cómo generar los informes

Para generar nuevos informes con datos actualizados:

1. **Análisis Completo** (incluye todos los análisis):
   ```bash
   cd scripts
   python ejecutar_analisis_completo.py
   ```

2. **Dashboard Comercial** (si solo se requiere este informe):
   ```bash
   cd scripts
   python dashboard_comercial.py
   ```

3. **Análisis de Estacionalidad** (si solo se requiere este análisis):
   ```bash
   cd scripts
   python analisis_estacionalidad.py
   ```

4. **Actualizar dashboard Power BI**:
   - Ejecute los análisis anteriores según sea necesario
   - Abra Power BI y haga clic en "Actualizar"

## Ejemplos prácticos

### Escenario 1: Campaña por debajo del objetivo a mitad de periodo con baja certidumbre

**Situación**: 
- El dashboard muestra que estamos al 60% del tiempo, pero solo al 40% del objetivo de leads
- Las simulaciones Monte Carlo muestran un intervalo de confianza amplio (certidumbre baja)
- R² del modelo predictivo: 0.62 (predictividad moderada)

**Análisis**:
1. Estado: POR DEBAJO
2. Revisión de estacionalidad: Periodo de demanda normal
3. Tasa de conversión: 8% (dentro de lo esperado)
4. Certidumbre: BAJA (intervalo amplio)
5. Elasticidad: Facebook (1.2), Instagram (0.9), Google Search (0.5)

**Decisiones tácticas**:
1. Aumentar presupuesto solo en Facebook (canal con mayor elasticidad) en 30%
2. Pausar Google Search para keywords con CPA >150% del objetivo
3. Implementar pruebas A/B en creatividades para reducir incertidumbre
4. Diversificar mensajes para captar diferentes segmentos
5. Aumentar frecuencia de análisis a cada 3 días
6. Preparar plan de contingencia si no se observa mejora en 1 semana

### Escenario 2: Resultados sobre expectativas pero con incertidumbre en predicciones futuras

**Situación**: 
- Rendimiento actual 20% por encima del objetivo
- Intervalo de confianza para próximas semanas es muy amplio (certidumbre baja)
- Análisis de elasticidad muestra signos de saturación en canales principales

**Análisis**:
1. Estado: POR ENCIMA
2. Revisión de estacionalidad: Inicio de período de alta estacionalidad
3. Certidumbre: BAJA (difícil predecir si el rendimiento se mantendrá)
4. Elasticidad: Decreciente en canales principales

**Decisiones tácticas**:
1. Mantener inversión global pero redistribuir entre canales:
   - Reducir 15% en canales con señales de saturación
   - Probar canales alternativos con pequeños presupuestos de prueba
2. Documentar factores de éxito actual (mensajes, audiencias, creatividades)
3. Reforzar equipo comercial para mantener buenos tiempos de respuesta
4. Implementar sistema de alertas tempranas para detectar cambios de tendencia
5. Realizar análisis de cohortes para entender calidad de leads recientes
6. Mantener reserva presupuestaria para reaccionar según evolución

## Notas importantes

1. **Considere factores externos**: El sistema predice basado en patrones históricos, pero tenga en cuenta factores externos nuevos (cambios económicos, competencia, etc.)

2. **Balance entre reacción y sobre-reacción**: Observe tendencias de al menos 3-7 días antes de hacer cambios drásticos

3. **Documente decisiones**: Registre cambios realizados y sus resultados para mejorar futuras decisiones

4. **NUEVO - Incorpore intervalos de confianza**: No tome decisiones basándose solo en predicciones puntuales, considere el rango completo de posibles resultados

5. **NUEVO - Considere la calidad de predicciones**: Verifique las métricas de confianza (R², MAPE) antes de tomar decisiones basadas en predicciones

---

## Soporte

Para consultas sobre la interpretación de datos o el uso del sistema:
- Contacte al equipo de análisis: analisis@ejemplo.com
- Programar capacitación adicional: capacitacion@ejemplo.com 