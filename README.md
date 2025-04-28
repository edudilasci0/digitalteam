# Sistema Predictor y Optimizador de Matrículas basado en CPA

## Introducción

Sistema de optimización de campañas para instituciones educativas que permite predecir y maximizar el número de matrículas en función del CPA (Costo Por Adquisición). Facilita la gestión de leads, proyección de matrículas y optimización del presupuesto.

**Nuevas funciones:** 
- Integración con Google Sheets para facilitar la gestión de datos y toma de decisiones por parte del equipo de marketing.
- **Análisis completo con simulación Monte Carlo** que calcula intervalos de confianza en predicciones.
- **Dashboards interactivos en Power BI** con visualización de métricas de confianza.

## Características

- Carga datos desde CSV/Excel o **directamente desde Google Sheets**
- Calcula métricas clave: CPL, CPA, tasa de conversión
- Analiza patrones de estacionalidad en leads y matrículas
- Predice número de matrículas según tendencias históricas
- **Simulaciones Monte Carlo para intervalos de confianza**
- **Análisis de elasticidad** para optimizar inversión por canal
- Genera reportes visuales (HTML, PNG, Power BI)
- **Dashboard colaborativo** para decisiones de equipo
- Integración bidireccional con Google Sheets

## Estructura del Proyecto

```
├── config/                # Archivos de configuración
│   ├── credentials.json   # Credenciales de Google API
│   └── google_sheets_config.json  # Configuración de hojas
├── dashboard/             # Dashboards y visualizaciones
│   ├── datos/             # Datos para dashboards
│   │   ├── plantillas/    # Plantillas CSV
│   │   ├── procesados/    # Datos procesados
│   │   └── resultados_analisis/ # Resultados de análisis avanzados
│   └── README.md          # Documentación de dashboard
├── datos/
│   ├── actual/            # Datos de la convocatoria actual
│   ├── historico/         # Datos de convocatorias anteriores
│   └── costos/            # Datos de costos e inversión
├── scripts/
│   ├── cargar_datos.py              # Carga de datos desde archivos
│   ├── ejecutar_analisis_completo.py # Nuevo: Análisis integrado con Monte Carlo
│   ├── sincronizar_sheets.py        # Integración con Google Sheets
│   ├── dashboard_comercial.py       # Generación de dashboards
│   ├── analisis_estacionalidad.py   # Análisis de patrones temporales
│   ├── simulacion_montecarlo.py     # Simulaciones para intervalos de confianza
│   └── otros scripts...
├── salidas/               # Reportes y visualizaciones generadas
├── logs/                  # Registros de actividad del sistema
├── Modelo decisiones.md   # Guía para toma de decisiones
└── dashboard/actualizar_dashboard_completo.md # Nuevo: Guía para análisis completo
```

## Requisitos

- Python 3.6 o superior
- Bibliotecas principales:
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - gspread (para integración con Google Sheets)
  - google-auth (para autenticación con API de Google)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/predictor-matriculas.git
cd predictor-matriculas
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar integración con Google Sheets (opcional):
```bash
python scripts/sincronizar_sheets.py
```
Sigue las instrucciones en pantalla para completar la configuración.

## Uso

### Método Tradicional (Archivos CSV)

```bash
python scripts/cargar_datos.py --leads path/to/leads.csv --planificacion path/to/planning.csv
python scripts/dashboard_comercial.py
```

### Nuevo Método (Google Sheets)

1. Ingresa los datos de inversión y campañas en la hoja "Datos de inversión diaria"
2. Ejecuta la sincronización:
```bash
python scripts/sincronizar_sheets.py
```
3. Los resultados se actualizarán automáticamente en la hoja "Resultados" y "Dashboard"
4. Los dashboards HTML detallados estarán disponibles en la carpeta `/salidas/`

### Análisis Completo con Simulación Monte Carlo (NUEVO)

Para un análisis integral que incluye predicciones, simulaciones Monte Carlo y métricas de confianza:

```bash
python scripts/ejecutar_analisis_completo.py
```

Este script ejecuta secuencialmente:
1. Carga de datos
2. Análisis de estacionalidad
3. Predicción de matrículas
4. Simulación Monte Carlo (1000 iteraciones)
5. Análisis de elasticidad
6. Generación de métricas de confianza
7. Actualización de datos para el dashboard

Los resultados se guardan en `dashboard/datos/resultados_analisis/` listos para visualizar en Power BI.

Para más detalles, consulte `dashboard/actualizar_dashboard_completo.md`.

### Sincronización Automática

Para configurar la sincronización automática diaria:
```bash
# Consulta las instrucciones según tu sistema operativo
cat config/instrucciones_programacion.txt
```

## Google Sheets - Estructura y Uso

La integración con Google Sheets incluye las siguientes hojas:

1. **Datos de inversión diaria** - Aquí el equipo ingresa los datos de campañas:
   - Fecha, Canal, Inversión, Impresiones, Clics, etc.

2. **Leads y Matrículas** - Registro de leads y matrículas:
   - ID, Fecha, Tipo, Canal, Estado, etc.

3. **Resultados** - Actualizado automáticamente con:
   - Leads reales vs predicciones
   - Métricas de rendimiento (CPL, CPA)
   - Proyecciones para próximos días

4. **Dashboard** - Resumen visual del estado actual:
   - Progreso de la campaña
   - Predicciones por canal
   - Alertas y recomendaciones

5. **Registro de Decisiones** - Para documentar acciones tomadas:
   - Fecha, Decisión, Canales afectados, Responsable, etc.

## Dashboard Power BI (NUEVO)

El sistema ahora incluye dashboards en Power BI con:

1. **Dashboard Comercial**: Para el equipo de ventas
   - KPIs fundamentales de seguimiento diario
   - Leads pendientes y conversiones
   - Visualización por programa

2. **Dashboard Analítico**: Para equipo de marketing y dirección
   - Análisis detallado por programa y comercial
   - Distribución de leads y matrículas
   - Métricas de confianza y proyecciones

Para implementar el dashboard:
1. Seguir las instrucciones en `docs/implementacion_dashboard.md`
2. Ejecutar `python dashboard/actualizar_datos.py`

## Intervalos de Confianza y Simulación Monte Carlo (NUEVO)

El sistema ahora calcula intervalos de confianza para predicciones mediante:

1. **Simulación Monte Carlo**: Genera 1000 escenarios posibles variando parámetros clave
2. **Intervalos de confianza**: Calcula rangos al 80%, 90% y 95% de confianza
3. **Métricas de precisión**: Evalúa la confianza de las predicciones

Estos datos permiten:
- Tomar decisiones basadas en la certeza de las predicciones
- Considerar escenarios pesimistas y optimistas
- Evaluar riesgos de forma cuantitativa

## Archivos de Entrada

### Si utilizas archivos CSV:

- **leads.csv**: Registro de leads y matrículas con columnas: ID, Fecha, Tipo, Canal, etc.
- **costos.csv**: Registro de inversión por canal con columnas: Fecha, Canal, Inversión, etc.

### Si utilizas Google Sheets:

Simplemente completa las hojas correspondientes en el spreadsheet creado automáticamente.

## Reportes Generados

El sistema genera varios tipos de reportes:

1. **Dashboard HTML**: Visualización interactiva de métricas clave
2. **Análisis de Estacionalidad**: Patrones históricos y predicciones
3. **Google Sheets Dashboard**: Actualizado automáticamente para el equipo
4. **Archivos PNG**: Gráficos de barras de progreso y comparaciones
5. **Reportes de Confianza**: Métricas de precisión e intervalos de confianza
6. **Visualizaciones Power BI**: Dashboards interactivos completos

## Variables Configurables

- **Rutas de archivos**: Configurable en `scripts/cargar_datos.py`
- **Frecuencia de análisis**: Configurable en `scripts/analisis_estacionalidad.py`
- **Integración con Google Sheets**: Configurable en `config/google_sheets_config.json`
- **Parámetros de simulación**: Ajustables en `scripts/ejecutar_analisis_completo.py`

## Resolución de Problemas

### Errores comunes:

1. **Error de autenticación con Google Sheets**:
   - Verifica que el archivo `config/credentials.json` existe
   - Asegúrate de haber habilitado las APIs necesarias en Google Cloud Console

2. **No se actualizan los datos en Google Sheets**:
   - Verifica que la hoja de cálculo existe y tiene la estructura correcta
   - Comprueba los permisos de la cuenta de servicio

3. **Errores en la simulación Monte Carlo**:
   - Revisa los logs en `/logs/analisis_completo_YYYYMMDD.log`
   - Considera reducir el número de simulaciones si hay problemas de memoria

## Guía de Toma de Decisiones

Para instrucciones detalladas sobre cómo utilizar los datos para tomar decisiones de marketing, consulta el archivo `Modelo decisiones.md`.

## Contribución

Si deseas contribuir a este proyecto:

1. Haz fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva funcionalidad'`)
4. Sube los cambios a tu fork (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.
