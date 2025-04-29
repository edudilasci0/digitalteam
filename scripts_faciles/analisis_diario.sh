#!/bin/bash

# Script para Análisis Diario de Campañas
# Ejecuta los análisis diarios más importantes de forma secuencial

echo "=========================================="
echo "   ANÁLISIS DIARIO DE MARKETING EDUCATIVO"
echo "=========================================="
echo ""
echo "Iniciando análisis diario... $(date)"
echo ""

# 1. Reporte de performance diario
echo "📊 Generando reporte de performance diario..."
python src/main.py --comando performance_diario --fecha hoy

# 2. Análisis de leads recientes
echo ""
echo "🔍 Analizando leads generados hoy..."
python src/analysis/leads.py --periodo hoy --agrupar canal,programa

# 3. Detección de anomalías
echo ""
echo "⚠️ Verificando anomalías en campañas..."
python src/analysis/anomalias.py --periodo hoy --umbral medio

# 4. Generar informe ejecutivo
echo ""
echo "📋 Generando informe ejecutivo diario..."
python src/ui/generador_reportes.py --tipo resumen_diario --formato pdf

echo ""
echo "=========================================="
echo "✅ Análisis diario completado"
echo "Los resultados se han guardado en la carpeta output/"
echo "==========================================" 