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

# Script para limpiar archivos no utilizados del repositorio
echo "Eliminando archivos no utilizados del repositorio..."

# 1. Scripts duplicados o desconectados
echo "Eliminando scripts duplicados o desconectados..."
rm -f ./scripts/calculate_metrics.py
rm -f ./scripts/load_data.py
rm -f ./scripts/generate_report.py
rm -f ./scripts/data_loader.py
rm -f ./scripts/rule_based_predictor.py
rm -f ./scripts/validate_data.py

# 2. Módulos sin referencias claras
echo "Eliminando módulos sin referencias claras..."
rm -f ./src/analysis/proyecciones.py
rm -f ./src/analysis/soporte_comercial.py
rm -f ./src/models/calendario_campanas.py
rm -f ./src/models/evaluador_modelos.py
rm -f ./src/models/model_manager.py
rm -f ./src/report/reporte_estrategico.py
rm -f ./src/visualizacion/visualizador.py

# 3. Código sin llamar o duplicado
echo "Eliminando código sin llamar o duplicado..."
rm -f ./dashboard/actualizar_datos.py
rm -f ./scripts/ejecutar_analisis_completo.py
rm -f ./scripts/ejecutar_sincronizacion.py
rm -f ./scripts/sistema_ajuste_automatico.py

# Limpiar directorios vacíos
echo "Limpiando directorios vacíos..."
find ./src -type d -empty -delete

echo "Limpieza completa. Se han eliminado los archivos no utilizados." 