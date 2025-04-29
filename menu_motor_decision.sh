#!/bin/bash

# Menú Interactivo para Motor de Decisión de Marketing Educativo
# Proporciona una interfaz amigable para usuarios sin experiencia técnica

# Función para mostrar el encabezado
mostrar_encabezado() {
    clear
    echo "========================================================="
    echo "      MOTOR DE DECISIÓN DE MARKETING EDUCATIVO"
    echo "========================================================="
    echo "               $(date '+%d/%m/%Y %H:%M')"
    echo ""
}

# Función para mostrar el menú principal
mostrar_menu_principal() {
    mostrar_encabezado
    echo "MENÚ PRINCIPAL:"
    echo ""
    echo "  1️⃣  Análisis Diarios"
    echo "  2️⃣  Análisis Quincenales"
    echo "  3️⃣  Análisis Mensuales"
    echo "  4️⃣  Detección de Anomalías"
    echo "  5️⃣  Interfaz Web (Streamlit)"
    echo "  6️⃣  Exportaciones"
    echo "  7️⃣  Ayuda"
    echo "  0️⃣  Salir"
    echo ""
    echo "--------------------------------------------------------"
    read -p "Selecciona una opción [0-7]: " opcion_principal
}

# Función para el submenú de análisis diarios
menu_analisis_diarios() {
    mostrar_encabezado
    echo "ANÁLISIS DIARIOS:"
    echo ""
    echo "  1. Ejecutar análisis diario completo"
    echo "  2. Reporte de performance diario"
    echo "  3. Análisis de leads recientes"
    echo "  4. Monitoreo de campañas activas"
    echo "  0. Volver al menú principal"
    echo ""
    echo "--------------------------------------------------------"
    read -p "Selecciona una opción [0-4]: " opcion_diarios
    
    case $opcion_diarios in
        1)
            echo "Ejecutando análisis diario completo..."
            bash scripts_faciles/analisis_diario.sh
            read -p "Presiona Enter para continuar..."
            ;;
        2)
            echo "Ejecutando reporte de performance diario..."
            python src/main.py --comando performance_diario --fecha hoy
            read -p "Presiona Enter para continuar..."
            ;;
        3)
            echo "Analizando leads recientes..."
            python src/analysis/leads.py --periodo hoy --agrupar canal,programa
            read -p "Presiona Enter para continuar..."
            ;;
        4)
            echo "Monitoreando campañas activas..."
            python src/ui/dashboard.py --vista monitoreo --periodo hoy
            read -p "Presiona Enter para continuar..."
            ;;
        0)
            return
            ;;
        *)
            echo "Opción inválida"
            sleep 2
            ;;
    esac
}

# Función para el submenú de análisis quincenales
menu_analisis_quincenales() {
    mostrar_encabezado
    echo "ANÁLISIS QUINCENALES:"
    echo ""
    echo "  1. Ejecutar análisis quincenal completo"
    echo "  2. Análisis de ROI por canal y programa"
    echo "  3. Recomendaciones de redistribución"
    echo "  4. Proyecciones a corto plazo"
    echo "  0. Volver al menú principal"
    echo ""
    echo "--------------------------------------------------------"
    read -p "Selecciona una opción [0-4]: " opcion_quincenales
    
    case $opcion_quincenales in
        1)
            echo "Ejecutando análisis quincenal completo..."
            bash scripts_faciles/analisis_quincenal.sh
            read -p "Presiona Enter para continuar..."
            ;;
        2)
            echo "Analizando ROI por canal y programa..."
            python src/analysis/roi.py --periodo ultimos_15dias --agrupar canal,programa
            read -p "Presiona Enter para continuar..."
            ;;
        3)
            echo "Generando recomendaciones de redistribución..."
            python src/models/optimizador.py --tipo redistribucion --restriccion presupuesto_fijo
            read -p "Presiona Enter para continuar..."
            ;;
        4)
            echo "Calculando proyecciones para próximos 15 días..."
            python src/models/forecast.py --metrica leads --horizonte 15dias
            read -p "Presiona Enter para continuar..."
            ;;
        0)
            return
            ;;
        *)
            echo "Opción inválida"
            sleep 2
            ;;
    esac
}

# Función para el submenú de análisis mensuales
menu_analisis_mensuales() {
    mostrar_encabezado
    echo "ANÁLISIS MENSUALES:"
    echo ""
    echo "  1. Ejecutar análisis mensual completo"
    echo "  2. Análisis de tendencias y estacionalidad"
    echo "  3. Evaluación de eficiencia por programa"
    echo "  4. Análisis de customer journey"
    echo "  5. Optimización de presupuesto"
    echo "  0. Volver al menú principal"
    echo ""
    echo "--------------------------------------------------------"
    read -p "Selecciona una opción [0-5]: " opcion_mensuales
    
    case $opcion_mensuales in
        1)
            echo "Ejecutando análisis mensual completo..."
            bash scripts_faciles/analisis_mensual.sh
            read -p "Presiona Enter para continuar..."
            ;;
        2)
            echo "Analizando tendencias y estacionalidad..."
            python src/analysis/tendencias.py --periodo ultimos_6meses --granularidad semana
            read -p "Presiona Enter para continuar..."
            ;;
        3)
            echo "Evaluando eficiencia por programa educativo..."
            python src/analysis/rentabilidad.py --dimension programa --metrica margen_contribucion
            read -p "Presiona Enter para continuar..."
            ;;
        4)
            echo "Analizando customer journey completo..."
            python src/analysis/customer_journey.py --detalle alto --visualizar true
            read -p "Presiona Enter para continuar..."
            ;;
        5)
            echo "Generando plan de optimización de presupuesto..."
            python src/models/optimizador_presupuesto.py --objetivo maximizar_matriculas
            read -p "Presiona Enter para continuar..."
            ;;
        0)
            return
            ;;
        *)
            echo "Opción inválida"
            sleep 2
            ;;
    esac
}

# Función para el submenú de exportaciones
menu_exportaciones() {
    mostrar_encabezado
    echo "EXPORTACIONES:"
    echo ""
    echo "  1. Exportar datos a Excel"
    echo "  2. Generar informe ejecutivo PDF"
    echo "  3. Generar presentación PowerPoint"
    echo "  4. Exportar datasets para PowerBI"
    echo "  0. Volver al menú principal"
    echo ""
    echo "--------------------------------------------------------"
    read -p "Selecciona una opción [0-4]: " opcion_export
    
    case $opcion_export in
        1)
            echo "Exportando datos a Excel..."
            python src/data/exportar.py --formato excel
            read -p "Presiona Enter para continuar..."
            ;;
        2)
            echo "Generando informe ejecutivo PDF..."
            python src/ui/generador_reportes.py --tipo resumen_diario --formato pdf
            read -p "Presiona Enter para continuar..."
            ;;
        3)
            echo "Generando presentación PowerPoint..."
            python src/ui/generador_reportes.py --tipo performance_quincenal --formato powerpoint
            read -p "Presiona Enter para continuar..."
            ;;
        4)
            echo "Exportando datasets para PowerBI..."
            python src/data/powerbi_datasets.py --regenerar todos --publicar false
            read -p "Presiona Enter para continuar..."
            ;;
        0)
            return
            ;;
        *)
            echo "Opción inválida"
            sleep 2
            ;;
    esac
}

# Función para iniciar la interfaz Streamlit
iniciar_streamlit() {
    mostrar_encabezado
    echo "INICIANDO INTERFAZ WEB STREAMLIT"
    echo ""
    echo "La interfaz web se abrirá en tu navegador..."
    echo "Para cerrar la interfaz, presiona Ctrl+C en esta terminal."
    echo ""
    echo "--------------------------------------------------------"
    echo "Presiona Enter para iniciar Streamlit..."
    read
    
    # Ejecutar Streamlit
    streamlit run src/ui/dashboard.py
}

# Función para el submenú de detección de anomalías
menu_anomalias() {
    mostrar_encabezado
    echo "DETECCIÓN DE ANOMALÍAS:"
    echo ""
    echo "  1. Ejecutar detección completa de anomalías"
    echo "  2. Verificar anomalías de rendimiento (CPA, CPC, CTR)"
    echo "  3. Verificar anomalías de calidad de leads"
    echo "  4. Verificar anomalías técnicas"
    echo "  0. Volver al menú principal"
    echo ""
    echo "--------------------------------------------------------"
    read -p "Selecciona una opción [0-4]: " opcion_anomalias
    
    case $opcion_anomalias in
        1)
            echo "Ejecutando detección completa de anomalías..."
            python src/analysis/anomalias.py --periodo hoy --umbral medio --notificar true
            read -p "Presiona Enter para continuar..."
            ;;
        2)
            echo "Verificando anomalías de rendimiento..."
            python src/analysis/anomalias.py --tipo rendimiento --periodo hoy
            read -p "Presiona Enter para continuar..."
            ;;
        3)
            echo "Verificando anomalías de calidad de leads..."
            python src/analysis/anomalias.py --tipo calidad --periodo hoy
            read -p "Presiona Enter para continuar..."
            ;;
        4)
            echo "Verificando anomalías técnicas..."
            python src/analysis/anomalias.py --tipo tecnico --periodo hoy
            read -p "Presiona Enter para continuar..."
            ;;
        0)
            return
            ;;
        *)
            echo "Opción inválida"
            sleep 2
            ;;
    esac
}

# Función para mostrar ayuda
mostrar_ayuda() {
    mostrar_encabezado
    echo "AYUDA DEL MOTOR DE DECISIÓN"
    echo ""
    echo "Este sistema le permite realizar diferentes tipos de análisis"
    echo "de marketing educativo sin necesidad de conocimientos técnicos."
    echo ""
    echo "TIPOS DE ANÁLISIS:"
    echo ""
    echo "• Análisis Diarios: Monitoreo operativo y detección de"
    echo "  problemas inmediatos en sus campañas."
    echo ""
    echo "• Análisis Quincenales: Ajustes tácticos para optimizar"
    echo "  las campañas en curso y redistribuir presupuesto."
    echo ""
    echo "• Análisis Mensuales: Planificación estratégica y"
    echo "  evaluación profunda de tendencias a largo plazo."
    echo ""
    echo "• Detección de Anomalías: Identificación automática de"
    echo "  problemas o oportunidades excepcionales."
    echo ""
    echo "• Interfaz Web: Acceso a análisis interactivos con gráficos"
    echo "  y visualizaciones en su navegador."
    echo ""
    echo "Los resultados de los análisis se guardan en la carpeta output/"
    echo ""
    echo "--------------------------------------------------------"
    read -p "Presiona Enter para volver al menú principal..."
}

# Bucle principal del menú
while true; do
    mostrar_menu_principal
    
    case $opcion_principal in
        1)
            menu_analisis_diarios
            ;;
        2)
            menu_analisis_quincenales
            ;;
        3)
            menu_analisis_mensuales
            ;;
        4)
            menu_anomalias
            ;;
        5)
            iniciar_streamlit
            ;;
        6)
            menu_exportaciones
            ;;
        7)
            mostrar_ayuda
            ;;
        0)
            mostrar_encabezado
            echo "Gracias por usar el Motor de Decisión de Marketing Educativo"
            echo "Saliendo del sistema..."
            echo ""
            exit 0
            ;;
        *)
            echo "Opción inválida. Por favor, selecciona una opción del 0 al 7."
            sleep 2
            ;;
    esac
done 