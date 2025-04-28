# Tarjeta Trello: Configuración inicial del Motor de Decisión

## Título
Configuración inicial del Motor de Decisión - Revisión de repositorio y adaptación de datos

## Descripción
Necesitamos configurar el Motor de Decisión localmente y adaptarlo al formato real de nuestros datos CSV.

## Tareas
- [ ] Revisar el repositorio de GitHub del Motor de Decisión
- [ ] Clonar el repositorio localmente
- [ ] Instalar dependencias según requirements.txt
- [ ] Solicitar a Rebe que comparta ejemplos de los archivos CSV actuales (leads y matrículas)
- [ ] Analizar el formato real de los CSV compartidos
- [ ] Adaptar el código para que funcione con el formato real de nuestros datos
- [ ] Crear archivos de muestra basados en el formato real
- [ ] Probar el sistema con los archivos de muestra
- [ ] Documentar cualquier problema encontrado

## Instrucciones para Mingo

### 1. Revisar el repositorio
- Acceder a: [URL del repositorio]
- Revisar la estructura del proyecto y la documentación

### 2. Configuración local
```bash
# Clonar el repositorio
git clone [URL del repositorio]
cd motor-decision

# Instalar dependencias
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p datos/actual datos/historico output/reportes output/modelos output/graficos logs
```

### 3. Solicitar datos a Rebe
Por favor, contacta a Rebe para que comparta:
- Un ejemplo del archivo CSV de leads actual
- Un ejemplo del archivo CSV de matrículas actual
- Un ejemplo de datos históricos (si están disponibles)

### 4. Adaptación del código
Una vez que tengamos los ejemplos de CSV, necesitaremos:
- Analizar la estructura real de los datos
- Identificar las columnas disponibles vs. las requeridas
- Adaptar el código en `scripts/cargar_datos.py` para que funcione con nuestro formato

### 5. Pruebas
- Crear archivos de muestra basados en el formato real
- Ejecutar el sistema con estos archivos
- Verificar que los resultados sean coherentes

## Formato esperado de los CSV

### Para leads:
- id_lead: Identificador único (También tenemos nombre, apellido y correo electrónico)
- fecha_creacion: Fecha de creación del lead
- origen: Canal de captación
- programa: Programa académico
- marca: Marca educativa
- estado: Estado del lead

### Para matrículas:
- id_matricula: Identificador de matrícula
- id_lead: Identificador del lead asociado
- fecha_matricula: Fecha de matrícula
- programa: Programa académico
- marca: Marca educativa

## Fecha límite
[Fecha límite para completar la configuración inicial]

## Responsables
- Mingo: Configuración local y adaptación del código
- Rebe: Compartir ejemplos de archivos CSV
- [Otro responsable]: [Otra tarea]

## Notas adicionales
- Documentar cualquier problema encontrado durante la configuración
- Compartir capturas de pantalla de errores si los hay
- Mantener comunicación con el equipo de desarrollo para resolver dudas 