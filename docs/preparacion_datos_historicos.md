# Guía de Preparación de Datos Históricos

## Introducción

Los modelos predictivos del Motor de Decisión requieren datos históricos de calidad para su entrenamiento. Esta guía describe cómo preparar, estructurar y validar estos datos para un rendimiento óptimo de los modelos.

## Estructura de Datos Históricos

### Organización de Carpetas

```
datos/
└── historico/
    ├── leads/
    │   ├── 2021/
    │   │   ├── leads_2021_Q1.csv
    │   │   ├── leads_2021_Q2.csv
    │   │   ├── leads_2021_Q3.csv
    │   │   └── leads_2021_Q4.csv
    │   ├── 2022/
    │   │   ├── leads_2022_Q1.csv
    │   │   └── ...
    │   └── 2023/
    │       └── ...
    ├── matriculas/
    │   ├── 2021/
    │   │   ├── matriculas_2021_Q1.csv
    │   │   └── ...
    │   └── ...
    └── planificacion/
        ├── planificacion_2021.csv
        ├── planificacion_2022.csv
        └── ...
```

### Requisitos Mínimos de Datos

Para garantizar modelos predictivos precisos, se requiere:

- **Cantidad**: Mínimo 12 meses de datos históricos completos
- **Calidad**: Datos limpios, validados y con formatos consistentes
- **Granularidad**: Datos diarios preferentemente (pueden agregarse después si es necesario)
- **Completitud**: Cubrir ciclos completos para capturar estacionalidad

## Formato de Archivos Históricos

### Leads Históricos (ej: `leads_2022_Q1.csv`)

Deben seguir el mismo formato que los datos actuales:

| Campo | Descripción | Tipo de Dato | Obligatorio |
|-------|-------------|--------------|-------------|
| id_lead | Identificador único | String/Integer | Sí |
| nombre | Nombre del lead | String | No |
| apellido | Apellido del lead | String | No |
| correo | Correo electrónico | String | No |
| fecha_creacion | Fecha de creación | YYYY-MM-DD | Sí |
| origen | Canal de captación | String | Sí |
| programa | Programa académico | String | Sí |
| marca | Marca educativa | String | Sí |
| estado | Estado del lead | String | Sí |

### Matrículas Históricas (ej: `matriculas_2022_Q1.csv`)

| Campo | Descripción | Tipo de Dato | Obligatorio |
|-------|-------------|--------------|-------------|
| id_matricula | Identificador de matrícula | String/Integer | Sí |
| id_lead | ID del lead asociado | String/Integer | Sí |
| fecha_matricula | Fecha de matrícula | YYYY-MM-DD | Sí |
| programa | Programa académico | String | Sí |
| marca | Marca educativa | String | Sí |

### Planificación Histórica (ej: `planificacion_2022.csv`)

Archivo que contiene las campañas históricas con sus presupuestos y objetivos:

| Campo | Descripción | Tipo de Dato | Obligatorio |
|-------|-------------|--------------|-------------|
| Fecha | Fecha de planificación | YYYY-MM-DD | Sí |
| ID_Campaña | Identificador de campaña | String | Sí |
| Nombre_Campaña | Nombre descriptivo | String | Sí |
| Marca | Marca educativa | String | Sí |
| Presupuesto_Total | Presupuesto asignado | Numeric | Sí |
| Objetivo_Matriculas_Total | Objetivo de matrículas | Integer | Sí |
| Fecha_Inicio | Inicio de campaña | YYYY-MM-DD | Sí |
| Fecha_Fin | Fin de campaña | YYYY-MM-DD | Sí |
| Canales_Activos | Canales utilizados | String (sep. por \|) | Sí |
| Programas_Incluidos | Programas incluidos | String (sep. por \|) | Sí |

## Proceso de Preparación

### 1. Extracción de Datos Históricos

Obtener datos históricos del CRM, sistemas de marketing o bases de datos existentes:

```bash
# Ejemplo: Exportar datos desde base de datos
python scripts/exportar_datos_crm.py --inicio="2022-01-01" --fin="2022-12-31" --tipo="leads" --salida="datos/historico/leads/2022/"
```

### 2. Limpieza y Transformación

Utilizar el script `preparar_historico.py` para:

- Estandarizar formatos de fecha
- Unificar nombres de canales y programas
- Eliminar duplicados
- Manejar valores nulos
- Validar integridad referencial entre leads y matrículas

```bash
# Ejemplo: Procesar un período específico
python scripts/preparar_historico.py --ano=2022 --trimestre=1 --tipo=leads
```

### 3. Validación

Verificar que los datos cumplen con los requisitos:

```bash
# Validar estructura y contenido
python scripts/validar_datos.py --ruta="datos/historico/leads/2022/leads_2022_Q1.csv" --tipo=leads
```

El script validará:
- Columnas requeridas presentes
- Formatos de fecha correctos
- Consistencia en canales y programas
- Rangos de valores válidos
- Integridad referencial

### 4. Generación de Metadatos

Crear archivo de metadatos con información de contexto:

```bash
# Generar metadatos
python scripts/generar_metadatos.py --ruta="datos/historico/leads/2022/"
```

Esto generará un archivo `metadatos.json` con:
- Estadísticas descriptivas
- Fechas de cobertura
- Información sobre campañas especiales
- Cambios en nomenclatura o estructura

## Buenas Prácticas para Datos Históricos

- **Consistencia temporal**: Mantener la misma frecuencia y formato de datos a lo largo del tiempo
- **Documentar anomalías**: Registrar eventos especiales que puedan afectar el rendimiento (promociones inusuales, problemas técnicos)
- **Respaldo de datos originales**: Mantener copias de los datos sin procesar
- **Versionado**: Controlar versiones de los datos procesados
- **Actualización periódica**: Incorporar nuevos datos históricos trimestralmente

## Uso en el Motor de Decisión

El Motor de Decisión utilizará automáticamente los datos históricos procesados:

1. Entrenamiento de modelos: Utilizará datos históricos completos
2. Evaluación de rendimiento: Comparará resultados actuales con históricos
3. Detección de anomalías: Identificará desviaciones significativas
4. Ajuste de estacionalidad: Considerará patrones históricos para predicciones

## Requisitos de Almacenamiento

- Tamaño aproximado por año: ~500MB (dependiendo del volumen de leads)
- Espacio recomendado: 5GB para almacenar varios años de datos históricos
- Respaldo: Configurar respaldo automático mensual 