#!/bin/bash

# Script para Análisis Mensual Estratégico
# Ejecuta análisis profundo y planificación estratégica

echo "=========================================="
echo "   ANÁLISIS MENSUAL ESTRATÉGICO"
echo "=========================================="
echo ""
echo "Iniciando análisis mensual estratégico... $(date)"
echo ""

# 1. Análisis de tendencias y estacionalidad
echo "📊 Analizando tendencias y estacionalidad..."
python src/analysis/tendencias.py --periodo ultimos_6meses --granularidad semana
python src/models/estacionalidad.py --datos historicos --visualizar true

# 2. Evaluación de eficiencia por programa
echo ""
echo "🎓 Evaluando eficiencia por programa educativo..."
python src/analysis/rentabilidad.py --dimension programa --metrica margen_contribucion
python src/analysis/eficiencia.py --agrupar programa --ordenar roi_descendente

# 3. Análisis de customer journey
echo ""
echo "🛣️ Analizando customer journey completo..."
python src/analysis/customer_journey.py --detalle alto --visualizar true
python src/analysis/puntos_friccion.py --umbral alto --sugerir_mejoras true

# 4. Análisis de atribución y canales
echo ""
echo "📱 Evaluando contribución de canales..."
python src/models/atribucion.py --modelo data_driven --ventana 30dias
python src/analysis/asistencia_canales.py --visualizar diagrama_sankey

# 5. Optimización de presupuesto
echo ""
echo "💼 Generando plan de optimización de presupuesto..."
python src/models/optimizador_presupuesto.py --objetivo maximizar_matriculas --restriccion presupuesto_maximo
python src/models/simulador.py --escenarios multiple --variables presupuesto,canales,estacionalidad

# 6. Generación de plan estratégico
echo ""
echo "📑 Creando plan estratégico mensual..."
python src/ui/generador_reportes.py --tipo plan_estrategico --horizonte trimestral

echo ""
echo "=========================================="
echo "✅ Análisis mensual estratégico completado"
echo "El plan estratégico se ha guardado en output/reportes/"
echo "===========================================" 