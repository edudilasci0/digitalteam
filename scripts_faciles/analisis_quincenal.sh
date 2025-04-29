#!/bin/bash

# Script para Análisis Quincenal
# Ejecuta los análisis quincenales para optimización de campañas

echo "=========================================="
echo "   ANÁLISIS QUINCENAL DE MARKETING"
echo "=========================================="
echo ""
echo "Iniciando análisis quincenal... $(date)"
echo ""

# 1. Análisis de campañas por fase
echo "🔄 Analizando fases de campañas activas..."
python src/models/calendario_campanas.py --analisis fases --periodo ultimos_15dias

# 2. Análisis de ROI por canal y programa
echo ""
echo "💰 Calculando ROI por canal y programa..."
python src/analysis/roi.py --periodo ultimos_15dias --agrupar canal,programa

# 3. Recomendaciones de optimización
echo ""
echo "🚀 Generando recomendaciones de optimización..."
python src/models/optimizador.py --tipo redistribucion --restriccion presupuesto_fijo

# 4. Proyecciones a corto plazo
echo ""
echo "📈 Calculando proyecciones para próximos 15 días..."
python src/models/forecast.py --metrica leads --horizonte 15dias
python src/models/forecast.py --metrica matriculas --horizonte 30dias

# 5. Generar informe ejecutivo
echo ""
echo "📋 Generando informe quincenal completo..."
python src/ui/generador_reportes.py --tipo performance_quincenal --formato powerpoint

echo ""
echo "=========================================="
echo "✅ Análisis quincenal completado"
echo "El informe se ha guardado en output/reportes/"
echo "===========================================" 