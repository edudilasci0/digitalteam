#!/bin/bash
# Script para realizar backup automático del Motor de Decisión
# Crea copias de seguridad de los datos, modelos y configuración

# Configuración
BACKUP_DIR="$(pwd)/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="motor_decision_backup_${TIMESTAMP}"
BACKUP_FILE="${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

# Directorios a respaldar
DATA_DIR="$(pwd)/datos"
CONFIG_DIR="$(pwd)/config"
MODELS_DIR="$(pwd)/output/modelos"
LOGS_DIR="$(pwd)/logs"

# Crear directorio de backup si no existe
mkdir -p "$BACKUP_DIR"

# Verificar si los directorios existen
if [ ! -d "$DATA_DIR" ]; then
    echo "Error: Directorio de datos no encontrado: $DATA_DIR"
    exit 1
fi

if [ ! -d "$CONFIG_DIR" ]; then
    echo "Error: Directorio de configuración no encontrado: $CONFIG_DIR"
    exit 1
fi

# Informar inicio
echo "Iniciando backup: $(date)"
echo "Destino: $BACKUP_FILE"

# Crear directorio temporal
TEMP_DIR=$(mktemp -d)
echo "Usando directorio temporal: $TEMP_DIR"

# Copiar archivos a directorio temporal
echo "Copiando datos..."
cp -r "$DATA_DIR" "$TEMP_DIR/"

echo "Copiando configuración..."
cp -r "$CONFIG_DIR" "$TEMP_DIR/"

# Copiar modelos si existen
if [ -d "$MODELS_DIR" ]; then
    echo "Copiando modelos..."
    cp -r "$MODELS_DIR" "$TEMP_DIR/"
fi

# Copiar logs si existen
if [ -d "$LOGS_DIR" ]; then
    echo "Copiando logs..."
    mkdir -p "$TEMP_DIR/logs"
    # Solo copiar logs de los últimos 7 días
    find "$LOGS_DIR" -type f -mtime -7 -exec cp {} "$TEMP_DIR/logs/" \;
fi

# Crear archivo README con información del backup
cat > "$TEMP_DIR/README_BACKUP.txt" << EOF
Motor de Decisión - Backup
==========================
Fecha: $(date)
Contenido:
- Datos
- Configuración
- Modelos (si existen)
- Logs recientes (si existen)

Para restaurar:
1. Descomprimir con: tar -xzf $BACKUP_NAME.tar.gz
2. Copiar contenido a los directorios correspondientes
EOF

# Crear archivo tar.gz
echo "Creando archivo de backup..."
tar -czf "$BACKUP_FILE" -C "$TEMP_DIR" .

# Verificar si se creó correctamente
if [ $? -eq 0 ] && [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "Backup completado exitosamente."
    echo "Tamaño: $BACKUP_SIZE"
    echo "Ubicación: $BACKUP_FILE"
    
    # Registrar en log de backups
    LOG_FILE="${BACKUP_DIR}/backup_history.log"
    echo "$(date) | $BACKUP_NAME | $BACKUP_SIZE" >> "$LOG_FILE"
    
    # Limpiar backups antiguos (mantener últimos 5)
    echo "Limpiando backups antiguos..."
    cd "$BACKUP_DIR" && ls -t *.tar.gz | tail -n +6 | xargs -r rm
    
    # Mostrar backups disponibles
    echo "Backups disponibles:"
    ls -lh "$BACKUP_DIR"/*.tar.gz | awk '{print $9, $5}'
else
    echo "Error: Fallo al crear backup."
    exit 1
fi

# Limpiar directorio temporal
echo "Limpiando archivos temporales..."
rm -rf "$TEMP_DIR"

echo "Proceso finalizado: $(date)"
exit 0 