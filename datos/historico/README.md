# Datos Históricos

Esta carpeta contiene los datos históricos utilizados por el Motor de Decisión para entrenar sus modelos predictivos.

## Estructura de Carpetas

```
historico/
├── leads/              # Datos históricos de leads
│   ├── 2021/           # Leads organizados por año
│   ├── 2022/
│   └── 2023/
├── matriculas/         # Datos históricos de matrículas
│   ├── 2021/           # Matrículas organizadas por año
│   ├── 2022/
│   └── 2023/
└── planificacion/      # Datos históricos de planificación de campañas
    ├── planificacion_2021.csv
    ├── planificacion_2022.csv
    └── planificacion_2023.csv
```

## Convenciones de Nomenclatura

- Archivos de leads: `leads_YYYY_QZ.csv` donde:
  - `YYYY` = Año (ej: 2022)
  - `Z` = Trimestre (1-4)

- Archivos de matrículas: `matriculas_YYYY_QZ.csv`

- Archivos de planificación: `planificacion_YYYY.csv`

## Requisitos para Datos Históricos

- Mínimo 12 meses de datos para capturar la estacionalidad completa
- Archivos de leads y matrículas organizados por trimestres
- Formatos consistentes con la estructura actual (ver `docs/estructura_datos.md`)
- Metadatos asociados para cada archivo (archivos `*_metadatos.json`)

## Procesamiento de Datos Históricos

Para procesar datos históricos crudos:

```bash
# Procesar datos de leads por trimestre
python scripts/preparar_historico.py --ano=2022 --trimestre=1 --tipo=leads

# Procesar datos de matrículas por trimestre
python scripts/preparar_historico.py --ano=2022 --trimestre=1 --tipo=matriculas

# Procesar datos de planificación por año
python scripts/preparar_historico.py --ano=2022 --tipo=planificacion
```

## Uso en el Motor de Decisión

Los datos históricos se utilizan para:

1. Entrenar modelos de predicción
2. Identificar patrones de estacionalidad
3. Establecer líneas base de rendimiento
4. Comparar rendimiento actual vs. histórico
5. Calibrar recomendaciones de asignación de presupuesto

Consulte `docs/preparacion_datos_historicos.md` para obtener instrucciones detalladas sobre cómo preparar y mantener estos datos. 