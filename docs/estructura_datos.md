# Estructura de Datos para el Motor de Decisión

Este documento describe la estructura de datos utilizada por el Motor de Decisión para procesar leads y matrículas.

## Archivos CSV

### Leads (leads_ejemplo.csv)

El archivo CSV de leads contiene la siguiente información:

| Campo | Descripción | Notas |
|-------|-------------|-------|
| id_lead | Identificador único del lead | Clave primaria |
| nombre | Nombre del lead | |
| apellido | Apellido del lead | |
| correo | Correo electrónico del lead | |
| fecha_creacion | Fecha de creación del lead | Formato YYYY-MM-DD |
| origen | Canal de captación | Ej: Facebook, Google, LinkedIn |
| programa | Programa académico | |
| marca | Marca educativa | Ej: UTEL, UTEG, UIN |
| estado | Estado del lead | Ej: Nuevo, Contactado, Interesado, Calificado, Matriculado |

**Nota:** El costo de adquisición no está disponible individualmente en el CSV, ya que esta información proviene de la plataforma publicitaria agregada.

### Matrículas (matriculas_ejemplo.csv)

El archivo CSV de matrículas contiene la siguiente información:

| Campo | Descripción | Notas |
|-------|-------------|-------|
| id_matricula | Identificador de matrícula | Clave primaria |
| id_lead | Identificador del lead asociado | Clave foránea |
| fecha_matricula | Fecha de matrícula | Formato YYYY-MM-DD |
| programa | Programa académico | |
| marca | Marca educativa | Ej: UTEL, UTEG, UIN |

**Nota:** El valor de la matrícula no está disponible en el CSV.

## Relación entre tablas

- Un lead puede tener 0 o 1 matrícula asociada.
- Cada matrícula está asociada exactamente a 1 lead.

## Procesamiento de datos

### Carga de datos individuales
El script `scripts/cargar_datos_individuales.py` contiene funciones para:

1. Cargar y validar los archivos CSV de leads y matrículas
2. Calcular métricas de conversión:
   - Tasa de conversión general
   - Conversión por marca
   - Conversión por programa académico
   - Conversión por origen (canal de captación)

### Compatibilidad con formatos anteriores
El script `scripts/cargar_datos.py` ha sido adaptado para:

1. Utilizar los nuevos formatos de datos individuales
2. Consolidar los datos de leads y matrículas para mantener compatibilidad con versiones anteriores
3. Proporcionar una interfaz similar a la versión anterior

### Cálculo de métricas básicas
El script `scripts/estimador_valores.py` proporciona funciones para:

1. Distribuir el presupuesto total invertido entre los leads generados
   - Se distribuye equitativamente el presupuesto total entre todos los leads
   - No se asignan costos fijos por origen, ya que no disponemos de esa información detallada
2. Calcular métricas básicas de eficiencia de marketing:
   - CPL (Costo por Lead)
   - CPA (Costo por Adquisición/Matrícula)
   - Tasa de conversión
   - Métricas segmentadas por marca, origen y programa

**Nota:** El cálculo de ROAS (Return on Ad Spend) no está disponible actualmente, ya que requeriría asignar valores monetarios a las matrículas, dato con el que aún no se cuenta.

## Ejemplo de uso

### Carga de datos
```python
from scripts.cargar_datos_individuales import cargar_datos_leads, cargar_datos_matriculas

# Cargar datos
df_leads = cargar_datos_leads("datos/leads_ejemplo.csv")
df_matriculas = cargar_datos_matriculas("datos/matriculas_ejemplo.csv")
```

### Cálculo de métricas básicas
```python
from scripts.estimador_valores import distribuir_costo_leads, calcular_metricas_basicas

# Definir presupuesto total
presupuesto_total = 5000.0  # USD

# Distribuir costos entre leads
df_leads_con_costo = distribuir_costo_leads(df_leads, presupuesto_total)

# Calcular métricas básicas
metricas = calcular_metricas_basicas(df_leads_con_costo, df_matriculas)

# Mostrar resultados
print(f"Costo por lead (CPL): ${metricas['cpl']:.2f}")
print(f"Costo por adquisición (CPA): ${metricas['cpa']:.2f}")
print(f"Tasa de conversión: {metricas['tasa_conversion']:.2f}%")
``` 