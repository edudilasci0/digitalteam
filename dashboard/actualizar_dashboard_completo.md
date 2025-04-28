# Guía de Análisis Completo y Actualización del Dashboard

## Introducción

Esta guía explica cómo ejecutar el análisis completo del sistema, incluyendo simulación Monte Carlo, análisis de estacionalidad, predicciones y métricas de confianza. Todos estos resultados se integran automáticamente en el dashboard de Power BI.

## Requisitos previos

1. Tener instaladas todas las dependencias (ver `requirements.txt`)
2. Tener acceso a los datos fuente en el formato adecuado
3. Tener configurado Power BI Desktop

## Ejecución del Análisis Completo

### Paso 1: Ejecutar el script integrador

```bash
python scripts/ejecutar_analisis_completo.py
```

Este script ejecuta secuencialmente:
1. Carga de datos
2. Análisis de estacionalidad
3. Predicción de matrículas
4. Simulación Monte Carlo
5. Análisis de elasticidad
6. Generación de métricas de confianza
7. Actualización de datos para el dashboard

El proceso completo puede tardar entre 5-10 minutos dependiendo del volumen de datos.

### Paso 2: Verificar resultados

Los resultados se guardan en la carpeta:
```
dashboard/datos/resultados_analisis/
```

Archivos generados:
- `estacionalidad_leads.csv` - Índices estacionales para leads
- `estacionalidad_matriculas.csv` - Índices estacionales para matrículas
- `predicciones_matriculas.csv` - Predicciones futuras
- `intervalos_confianza.csv` - Intervalos de confianza de predicciones
- `elasticidad_factores.csv` - Análisis de elasticidad por factores
- `recomendaciones_inversion.csv` - Recomendaciones de inversión
- `resumen_confianza.csv` - Resumen de métricas de confianza

Adicionalmente, se genera un archivo de registro en:
```
logs/analisis_completo_YYYYMMDD.log
```

### Paso 3: Actualizar el dashboard en Power BI

1. Abrir el archivo Power BI (`Dashboard_Comercial_Analitico.pbix`)
2. Ir a "Inicio" → "Actualizar"
3. Verificar que los datos han sido actualizados

## Configuración del Análisis

### Ajustar parámetros de simulación

Para modificar los parámetros de la simulación Monte Carlo, editar:

```python
# En scripts/ejecutar_analisis_completo.py
resultados_simulacion = simulacion_montecarlo.ejecutar_simulacion(
    predicciones["predicciones"],
    num_simulaciones=1000,  # Cambiar número de simulaciones
    variabilidad=0.15       # Cambiar variabilidad (15% por defecto)
)
```

### Ajustar horizonte de predicción

Para cambiar el horizonte de predicción futuro:

```python
# En scripts/ejecutar_analisis_completo.py
predicciones = predecir_matriculas.generar_prediccion_futura(
    modelo, 
    datos["df_crm"],
    resultados_estacionalidad["estacionalidad_leads"]["indices_estacionales"],
    resultados_estacionalidad["estacionalidad_matriculas"]["indices_estacionales"],
    horizonte_meses=6  # Cambiar horizonte de predicción
)
```

## Integración con el Dashboard

### Panel de Confianza en Power BI

El dashboard incluye un panel dedicado a mostrar las métricas de confianza:

1. **Confianza general:** Basada en R² del modelo predictivo
2. **Intervalos de confianza:** Visualización de rangos al 80%, 90% y 95%
3. **Estabilidad histórica:** Indicador de consistencia en patrones temporales

### Visualización de Simulaciones

Las simulaciones Monte Carlo permiten visualizar:

1. **Distribución de escenarios:** Histogramas de posibles resultados
2. **Análisis de sensibilidad:** Impacto de variables en el resultado
3. **Escenarios extremos:** Identificación de casos "mejor/peor caso"

## Programación y Automatización

Para ejecutar el análisis completo de forma automática, puede configurar:

### Programación en Linux/Mac:

Añadir al crontab:
```
0 1 * * * cd /ruta/al/proyecto && python scripts/ejecutar_analisis_completo.py >> logs/cron.log 2>&1
```

### Programación en Windows:

Usar el Programador de tareas:
1. Crear una tarea nueva
2. Acción: Iniciar un programa
3. Programa/script: `python`
4. Argumentos: `scripts/ejecutar_analisis_completo.py`
5. Iniciar en: `C:\ruta\al\proyecto`

## Solución de problemas

### Error en carga de módulos:

Si aparece "No se pudo importar el módulo X", verificar:
- Que todos los scripts están en la carpeta correcta
- Que las dependencias están instaladas
- Que los nombres de módulo coinciden con los archivos .py

### Error en carga de datos:

Si falla la carga de datos, verificar:
- Que los archivos fuente existen y tienen el formato correcto
- Que los paths están configurados correctamente
- Que hay suficiente memoria para cargar los datasets

### Error en simulación Monte Carlo:

Si la simulación falla, considerar:
- Reducir el número de simulaciones
- Verificar que las predicciones base están disponibles
- Aumentar el timeout si es necesario

## Contacto y Soporte

Para soporte técnico con esta herramienta, contacte al equipo de desarrollo interno. 