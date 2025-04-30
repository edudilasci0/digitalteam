#!/bin/bash

# Script para limpiar el repositorio y dejar solo los archivos necesarios
# según la arquitectura actual del Motor de Decisión Educativo y Predictivo

echo "==========================================="
echo "   Limpieza de Repositorio"
echo "   Motor de Decisión Educativo v1.0.0"
echo "==========================================="
echo ""

# Archivos a eliminar (versiones antiguas/innecesarias)
FILES_TO_REMOVE=(
    "app_simple.py"
    "app_datos.py"
    "app_reportes_avanzados.py"
    "app_completa.py"
    "menu_motor_decision.sh"
)

# Confirmar antes de eliminar
echo "Se eliminarán los siguientes archivos innecesarios:"
for file in "${FILES_TO_REMOVE[@]}"; do
    if [ -f "$file" ]; then
        echo "- $file ✓"
    else
        echo "- $file (no encontrado)"
    fi
done

echo ""
read -p "¿Confirma la eliminación? (s/n): " confirm

if [ "$confirm" != "s" ]; then
    echo "Operación cancelada. No se ha eliminado ningún archivo."
    exit 0
fi

# Eliminar archivos
echo ""
echo "Eliminando archivos innecesarios..."
for file in "${FILES_TO_REMOVE[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "- $file eliminado."
    fi
done

echo ""
echo "==========================================="
echo "   Limpieza completada con éxito"
echo "==========================================="
echo ""
echo "Archivos principales del proyecto:"
echo "- app_motor.py (aplicación principal)"
echo "- requirements.txt (dependencias)"
echo "- README.md (documentación)"
echo "- Manual de Usuario.md (guía detallada)"
echo ""
echo "Ejecute la aplicación con:"
echo "streamlit run app_motor.py" 