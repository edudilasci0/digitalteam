import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import sys
import tempfile
from io import BytesIO

# Asegurar que src sea accesible
sys.path.append('.')

# Importar módulos necesarios
try:
    from src.report.reporte_estrategico import ReporteEstrategico
    from src.analysis.proyecciones import ProyeccionesAnalyzer
    from src.analysis.soporte_comercial import SoporteComercial
except ImportError:
    st.error("No se pudieron importar los módulos necesarios. Verifica la estructura del proyecto.")
    ReporteEstrategico = None
    ProyeccionesAnalyzer = None
    SoporteComercial = None

class ReportesAvanzadosUI:
    """
    Clase para crear la interfaz de usuario de reportes avanzados en Streamlit.
    """
    
    def __init__(self):
        """
        Inicializa la interfaz de reportes avanzados.
        """
        # Inicializar estado de sesión
        if 'datos_leads' not in st.session_state:
            st.session_state.datos_leads = None
        if 'datos_matriculas' not in st.session_state:
            st.session_state.datos_matriculas = None
        if 'datos_campanas' not in st.session_state:
            st.session_state.datos_campanas = None
            
    def mostrar_carga_datos(self):
        """
        Muestra la sección para cargar datos adicionales.
        """
        st.subheader("Carga de Datos Adicionales")
        
        # Pestañas para diferentes tipos de datos
        tab1, tab2, tab3 = st.tabs(["Leads", "Matrículas", "Planificación de Campañas"])
        
        with tab1:
            st.write("Carga de datos de leads desde archivo externo")
            
            uploaded_file = st.file_uploader(
                "Arrastra o selecciona archivo CSV o Excel con datos de leads", 
                type=["csv", "xlsx", "xls"],
                key="uploader_leads"
            )
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        datos = pd.read_csv(uploaded_file)
                    else:
                        datos = pd.read_excel(uploaded_file)
                        
                    # Mostrar vista previa
                    st.write("Vista previa de datos:")
                    st.dataframe(datos.head(5))
                    
                    # Verificar columnas mínimas requeridas
                    columnas_requeridas = ['fecha', 'origen']
                    columnas_presentes = [col for col in columnas_requeridas if any(col in c.lower() for c in datos.columns)]
                    
                    if len(columnas_presentes) < len(columnas_requeridas):
                        st.warning(f"El archivo no contiene todas las columnas recomendadas: {columnas_requeridas}")
                        
                    # Botón para confirmar carga
                    if st.button("Cargar datos de leads", key="btn_cargar_leads"):
                        st.session_state.datos_leads = datos
                        st.success(f"Datos de leads cargados correctamente: {len(datos)} registros")
                
                except Exception as e:
                    st.error(f"Error al leer el archivo: {str(e)}")
        
        with tab2:
            st.write("Carga de datos de matrículas desde archivo externo")
            
            uploaded_file = st.file_uploader(
                "Arrastra o selecciona archivo CSV o Excel con datos de matrículas", 
                type=["csv", "xlsx", "xls"],
                key="uploader_matriculas"
            )
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        datos = pd.read_csv(uploaded_file)
                    else:
                        datos = pd.read_excel(uploaded_file)
                        
                    # Mostrar vista previa
                    st.write("Vista previa de datos:")
                    st.dataframe(datos.head(5))
                    
                    # Verificar columnas mínimas requeridas
                    columnas_requeridas = ['fecha', 'origen']
                    columnas_presentes = [col for col in columnas_requeridas if any(col in c.lower() for c in datos.columns)]
                    
                    if len(columnas_presentes) < len(columnas_requeridas):
                        st.warning(f"El archivo no contiene todas las columnas recomendadas: {columnas_requeridas}")
                        
                    # Botón para confirmar carga
                    if st.button("Cargar datos de matrículas", key="btn_cargar_matriculas"):
                        st.session_state.datos_matriculas = datos
                        st.success(f"Datos de matrículas cargados correctamente: {len(datos)} registros")
                
                except Exception as e:
                    st.error(f"Error al leer el archivo: {str(e)}")
        
        with tab3:
            st.write("Carga de datos de planificación de campañas")
            
            uploaded_file = st.file_uploader(
                "Arrastra o selecciona archivo CSV o Excel con datos de planificación", 
                type=["csv", "xlsx", "xls"],
                key="uploader_campanas"
            )
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        datos = pd.read_csv(uploaded_file)
                    else:
                        datos = pd.read_excel(uploaded_file)
                        
                    # Mostrar vista previa
                    st.write("Vista previa de datos:")
                    st.dataframe(datos.head(5))
                    
                    # Verificar columnas mínimas requeridas
                    columnas_requeridas = ['fecha_inicio', 'fecha_fin', 'presupuesto_estimado', 'costo_ejecutado', 'objetivo_leads', 'origen']
                    columnas_presentes = [col for col in columnas_requeridas if any(col in c.lower() for c in datos.columns)]
                    
                    if len(columnas_presentes) < len(columnas_requeridas):
                        st.warning(f"El archivo no contiene todas las columnas recomendadas: {columnas_requeridas}")
                        st.write("Columnas presentes:", columnas_presentes)
                        st.write("Columnas requeridas:", columnas_requeridas)
                        
                    # Botón para confirmar carga
                    if st.button("Cargar datos de planificación", key="btn_cargar_campanas"):
                        st.session_state.datos_campanas = datos
                        st.success(f"Datos de planificación cargados correctamente: {len(datos)} registros")
                
                except Exception as e:
                    st.error(f"Error al leer el archivo: {str(e)}")
        
        # Mostrar resumen de datos cargados
        st.subheader("Resumen de datos cargados")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.datos_leads is not None:
                st.success(f"✅ Leads: {len(st.session_state.datos_leads)} registros")
            else:
                st.warning("❌ Datos de leads no cargados")
                
        with col2:
            if st.session_state.datos_matriculas is not None:
                st.success(f"✅ Matrículas: {len(st.session_state.datos_matriculas)} registros")
            else:
                st.warning("❌ Datos de matrículas no cargados")
                
        with col3:
            if st.session_state.datos_campanas is not None:
                st.success(f"✅ Planificación: {len(st.session_state.datos_campanas)} registros")
            else:
                st.warning("❌ Datos de planificación no cargados")
                
        # Opción para cargar datos de ejemplo
        with st.expander("Cargar datos de ejemplo"):
            if st.button("Cargar datos de ejemplo para testing"):
                # Generar datos de ejemplo
                self._cargar_datos_ejemplo()
                st.success("Datos de ejemplo cargados correctamente")
                st.rerun()
    
    def mostrar_calculo_cpl_cpa(self):
        """
        Muestra la sección para el cálculo real de CPL y CPA.
        """
        st.subheader("Cálculo Real de CPL y CPA")
        
        # Verificar que existan los datos necesarios
        if (st.session_state.datos_leads is None or 
            st.session_state.datos_campanas is None):
            st.warning("Para calcular CPL y CPA reales, debes cargar datos de leads y planificación de campañas.")
            return
        
        # Crear instancia de ReporteEstrategico
        reporte = ReporteEstrategico(
            datos_leads=st.session_state.datos_leads,
            datos_matriculas=st.session_state.datos_matriculas,
            datos_campanas=st.session_state.datos_campanas
        )
        
        # Calcular CPL y CPA reales
        cpl_cpa = reporte.calcular_cpl_cpa_reales()
        
        if cpl_cpa is None:
            st.error("No se pudieron calcular los valores de CPL y CPA. Verifica que los datos contengan las columnas necesarias.")
            return
        
        # Mostrar resultados
        st.write("Resultados del cálculo de CPL y CPA reales basados en datos del CRM:")
        
        # Formatear columnas de costo
        cpl_cpa['cpl_real'] = cpl_cpa['cpl_real'].round(2)
        cpl_cpa['cpa_real'] = cpl_cpa['cpa_real'].replace([np.inf, -np.inf], np.nan).round(2)
        
        # Crear columnas formateadas para visualización
        cpl_cpa['CPL Real'] = '$' + cpl_cpa['cpl_real'].astype(str)
        cpl_cpa['CPA Real'] = cpl_cpa['cpa_real'].apply(lambda x: '$' + str(x) if not pd.isna(x) else 'N/A')
        
        # Mostrar tabla
        st.dataframe(cpl_cpa[['origen', 'total_leads', 'total_matriculas', 'costo_ejecutado', 'CPL Real', 'CPA Real']])
        
        # Mostrar gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de CPL por origen
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # Ordenar por CPL
            datos_ordenados = cpl_cpa.sort_values('cpl_real')
            
            sns.barplot(x='origen', y='cpl_real', data=datos_ordenados, ax=ax)
            ax.set_title('CPL Real por Origen')
            ax.set_xlabel('Origen')
            ax.set_ylabel('CPL ($)')
            
            # Rotar etiquetas del eje x
            plt.xticks(rotation=45, ha='right')
            
            # Añadir etiquetas de valor
            for i, val in enumerate(datos_ordenados['cpl_real']):
                ax.text(i, val + 0.5, f'${val:.2f}', ha='center')
            
            st.pyplot(fig)
        
        with col2:
            # Gráfico de CPA por origen (sin valores infinitos)
            datos_cpa = cpl_cpa[cpl_cpa['cpa_real'] < float('inf')].sort_values('cpa_real')
            
            if not datos_cpa.empty:
                fig, ax = plt.subplots(figsize=(8, 5))
                
                sns.barplot(x='origen', y='cpa_real', data=datos_cpa, ax=ax)
                ax.set_title('CPA Real por Origen')
                ax.set_xlabel('Origen')
                ax.set_ylabel('CPA ($)')
                
                # Rotar etiquetas del eje x
                plt.xticks(rotation=45, ha='right')
                
                # Añadir etiquetas de valor
                for i, val in enumerate(datos_cpa['cpa_real']):
                    ax.text(i, val + 0.5, f'${val:.2f}', ha='center')
                
                st.pyplot(fig)
            else:
                st.info("No hay datos suficientes para mostrar CPA por origen.")
        
        # Resumen general
        st.subheader("Resumen General")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cpl_promedio = cpl_cpa['cpl_real'].mean()
            st.metric("CPL Promedio", f"${cpl_promedio:.2f}")
            
        with col2:
            cpa_valores = cpl_cpa['cpa_real'].replace([np.inf, -np.inf], np.nan)
            if not cpa_valores.isna().all():
                cpa_promedio = cpa_valores.mean()
                st.metric("CPA Promedio", f"${cpa_promedio:.2f}")
            else:
                st.metric("CPA Promedio", "N/A")
        
        # Notas explicativas
        st.info("""
        **Nota importante sobre el cálculo:**
        - El CPL (Costo Por Lead) se calcula dividiendo el gasto acumulado entre el total de leads cargados en el CRM.
        - El CPA (Costo Por Adquisición/Matrícula) se calcula dividiendo el gasto acumulado entre el total de matrículas.
        - Estos valores pueden diferir de los reportados por las plataformas publicitarias.
        """)
    
    def mostrar_proyecciones(self):
        """
        Muestra la sección de proyecciones con intervalos de confianza.
        """
        st.subheader("Proyecciones con Intervalos de Confianza")
        
        # Verificar que existan los datos necesarios
        if (st.session_state.datos_leads is None or 
            st.session_state.datos_campanas is None):
            st.warning("Para calcular proyecciones, debes cargar datos de leads y planificación de campañas.")
            return
        
        # Crear instancia de ProyeccionesAnalyzer
        proyecciones = ProyeccionesAnalyzer(
            datos_leads=st.session_state.datos_leads,
            datos_matriculas=st.session_state.datos_matriculas,
            datos_campanas=st.session_state.datos_campanas
        )
        
        # Obtener nivel de confianza
        nivel_confianza = st.slider(
            "Nivel de confianza:",
            min_value=80,
            max_value=99,
            value=95,
            step=1,
            format="%d%%"
        ) / 100
        
        # Proyectar cierre de campaña
        proyeccion = proyecciones.proyectar_cierre_campana(nivel_confianza=nivel_confianza)
        
        if proyeccion is None:
            st.error("No se pudo calcular la proyección. Verifica que los datos contengan las columnas necesarias.")
            return
        
        # Mostrar resultados
        st.write(f"Proyección de cierre de campaña con {nivel_confianza*100:.0f}% de confianza:")
        
        # Crear columnas para mostrar proyecciones
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Proyección de Leads")
            
            # Mostrar métricas
            st.metric(
                "Leads actuales",
                f"{proyeccion['leads_actuales']:.0f}"
            )
            
            st.metric(
                "Leads proyectados al cierre",
                f"{proyeccion['leads_finales']:.0f}",
                f"{(proyeccion['leads_finales']/proyeccion['leads_actuales']-1)*100:.1f}%" if proyeccion['leads_actuales'] > 0 else None
            )
            
            # Intervalo de confianza
            st.write(f"Intervalo de confianza ({nivel_confianza*100:.0f}%):")
            st.write(f"{proyeccion['leads_limite_inferior']:.0f} - {proyeccion['leads_limite_superior']:.0f} leads")
        
        with col2:
            st.subheader("Proyección de Matrículas")
            
            if proyeccion['matriculas_actuales'] is not None and proyeccion['matriculas_proyectadas'] is not None:
                # Mostrar métricas
                st.metric(
                    "Matrículas actuales",
                    f"{proyeccion['matriculas_actuales']:.0f}"
                )
                
                st.metric(
                    "Matrículas proyectadas al cierre",
                    f"{proyeccion['matriculas_proyectadas']:.0f}",
                    f"{(proyeccion['matriculas_proyectadas']/proyeccion['matriculas_actuales']-1)*100:.1f}%" if proyeccion['matriculas_actuales'] > 0 else None
                )
                
                # Intervalo de confianza
                if proyeccion['matriculas_limite_inferior'] is not None and proyeccion['matriculas_limite_superior'] is not None:
                    st.write(f"Intervalo de confianza ({nivel_confianza*100:.0f}%):")
                    st.write(f"{proyeccion['matriculas_limite_inferior']:.0f} - {proyeccion['matriculas_limite_superior']:.0f} matrículas")
            else:
                st.info("No hay datos suficientes para proyectar matrículas.")
        
        # Mostrar gráfico de proyección
        st.subheader("Gráfico de Proyección")
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Datos para el gráfico
        categorias = ['Actual', 'Proyectado']
        valores_leads = [proyeccion['leads_actuales'], proyeccion['leads_finales']]
        
        # Crear barras para leads
        barras_leads = ax.bar(
            [c + ' (Leads)' for c in categorias],
            valores_leads,
            color='skyblue',
            label='Leads'
        )
        
        # Añadir intervalo de confianza
        ax.errorbar(
            'Proyectado (Leads)',
            proyeccion['leads_finales'],
            yerr=[[proyeccion['leads_finales'] - proyeccion['leads_limite_inferior']],
                 [proyeccion['leads_limite_superior'] - proyeccion['leads_finales']]],
            fmt='o',
            color='black',
            capsize=5
        )
        
        # Si hay datos de matrículas, añadirlos
        if proyeccion['matriculas_actuales'] is not None and proyeccion['matriculas_proyectadas'] is not None:
            valores_matriculas = [proyeccion['matriculas_actuales'], proyeccion['matriculas_proyectadas']]
            
            # Crear barras para matrículas
            barras_matriculas = ax.bar(
                [c + ' (Matrículas)' for c in categorias],
                valores_matriculas,
                color='lightgreen',
                label='Matrículas'
            )
            
            # Añadir intervalo de confianza
            if proyeccion['matriculas_limite_inferior'] is not None and proyeccion['matriculas_limite_superior'] is not None:
                ax.errorbar(
                    'Proyectado (Matrículas)',
                    proyeccion['matriculas_proyectadas'],
                    yerr=[[proyeccion['matriculas_proyectadas'] - proyeccion['matriculas_limite_inferior']],
                         [proyeccion['matriculas_limite_superior'] - proyeccion['matriculas_proyectadas']]],
                    fmt='o',
                    color='black',
                    capsize=5
                )
        
        # Configurar gráfico
        ax.set_ylabel('Cantidad')
        ax.set_title(f'Proyección al cierre de campaña (Confianza: {nivel_confianza*100:.0f}%)')
        ax.legend()
        
        # Añadir etiquetas de valor
        for i, rect in enumerate(barras_leads):
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., height,
                    f'{height:.0f}',
                    ha='center', va='bottom')
            
        if proyeccion['matriculas_actuales'] is not None and proyeccion['matriculas_proyectadas'] is not None:
            for i, rect in enumerate(barras_matriculas):
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., height,
                        f'{height:.0f}',
                        ha='center', va='bottom')
        
        # Mostrar gráfico
        st.pyplot(fig)
        
        # Mostrar simulaciones
        st.subheader("Simulación de Escenarios")
        
        # Selector de tipo de simulación
        tipo_simulacion = st.radio(
            "Tipo de simulación:",
            ["Mejora en tasa de conversión", "Cambio en inversión", "Costo marginal de más leads"],
            horizontal=True
        )
        
        # Mapear selección a tipo de simulación
        tipo_sim_map = {
            "Mejora en tasa de conversión": "conversion",
            "Cambio en inversión": "inversion",
            "Costo marginal de más leads": "costo_marginal"
        }
        
        # Ejecutar simulación
        sim_resultados = proyecciones.simular_escenarios(tipo=tipo_sim_map[tipo_simulacion])
        
        if sim_resultados is None:
            st.warning("No se pudieron generar simulaciones con los datos actuales.")
        else:
            # Mostrar resultados de simulación
            st.dataframe(sim_resultados)
            
            # Crear gráfico según tipo de simulación
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if tipo_simulacion == "Mejora en tasa de conversión":
                # Gráfico de barras para escenarios de conversión
                sns.barplot(x='escenario', y='matriculas_proyectadas', data=sim_resultados, ax=ax)
                ax.set_title('Matrículas proyectadas por escenario')
                ax.set_xlabel('Escenario')
                ax.set_ylabel('Matrículas proyectadas')
                
            elif tipo_simulacion == "Cambio en inversión":
                # Gráfico de barras para escenarios de inversión
                sns.barplot(x='escenario', y='matriculas_proyectadas', data=sim_resultados, ax=ax)
                ax.set_title('Matrículas proyectadas por escenario de inversión')
                ax.set_xlabel('Escenario')
                ax.set_ylabel('Matrículas proyectadas')
                
            elif tipo_simulacion == "Costo marginal de más leads":
                # Gráfico para costo marginal
                plt.plot(sim_resultados['leads_adicionales'], sim_resultados['costo_marginal_por_lead'], marker='o')
                ax.set_title('Costo marginal por lead adicional')
                ax.set_xlabel('Leads adicionales')
                ax.set_ylabel('Costo marginal por lead ($)')
            
            # Mostrar gráfico
            st.pyplot(fig)
    
    def mostrar_modulo_soporte_comercial(self):
        """
        Muestra el módulo estratégico de soporte comercial.
        """
        st.subheader("Módulo Estratégico de Soporte Comercial")
        
        # Verificar que existan los datos necesarios
        if (st.session_state.datos_leads is None or 
            st.session_state.datos_campanas is None):
            st.warning("Para utilizar el módulo de soporte comercial, debes cargar datos de leads y planificación de campañas.")
            return
        
        # Crear instancia de SoporteComercial
        soporte = SoporteComercial(
            datos_leads=st.session_state.datos_leads,
            datos_matriculas=st.session_state.datos_matriculas,
            datos_campanas=st.session_state.datos_campanas
        )
        
        # Generar dashboard comercial
        resultado = soporte.generar_dashboard_comercial(streamlit=True)
        
        if resultado is None:
            pass  # El dashboard ya se mostró directamente en streamlit
        else:
            st.error("Error al generar el dashboard comercial.")
    
    def mostrar_exportacion_reportes(self):
        """
        Muestra la sección para exportación de reportes diferenciados.
        """
        st.subheader("Exportación de Reportes Diferenciados")
        
        # Verificar que existan los datos necesarios
        if (st.session_state.datos_leads is None or 
            st.session_state.datos_matriculas is None or
            st.session_state.datos_campanas is None):
            st.warning("Para generar reportes, debes cargar todos los datos (leads, matrículas y planificación).")
            return
        
        # Crear instancia de ReporteEstrategico
        reporte = ReporteEstrategico(
            datos_leads=st.session_state.datos_leads,
            datos_matriculas=st.session_state.datos_matriculas,
            datos_campanas=st.session_state.datos_campanas
        )
        
        # Selector de tipo de reporte
        tipo_reporte = st.radio(
            "Selecciona el tipo de reporte:",
            ["Reporte General Estratégico (Marketing)", "Reporte de Status Comercial"],
            horizontal=True
        )
        
        # Selector de formato
        formatos = {
            "Reporte General Estratégico (Marketing)": ["Excel (.xlsx)", "CSV (.csv)"],
            "Reporte de Status Comercial": ["Excel (.xlsx)", "PDF (.pdf)"]
        }
        
        formato = st.selectbox(
            "Formato de salida:",
            formatos[tipo_reporte]
        )
        
        # Mapear selección a formato real
        formato_map = {
            "Excel (.xlsx)": "xlsx",
            "CSV (.csv)": "csv",
            "PDF (.pdf)": "pdf"
        }
        
        # Botón para generar reporte
        if st.button("Generar y Descargar Reporte"):
            with st.spinner("Generando reporte..."):
                try:
                    if tipo_reporte == "Reporte General Estratégico (Marketing)":
                        # Generar reporte de marketing
                        buffer = reporte.export_report_marketing(formato=formato_map[formato])
                        
                        if buffer:
                            # Preparar nombre de archivo
                            fecha_actual = datetime.now().strftime("%Y%m%d_%H%M")
                            nombre_archivo = f"reporte_marketing_{fecha_actual}.{formato_map[formato]}"
                            
                            # Botón de descarga
                            st.download_button(
                                label="Descargar Reporte",
                                data=buffer,
                                file_name=nombre_archivo,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if formato_map[formato] == "xlsx" else "text/csv"
                            )
                            
                            st.success("Reporte generado correctamente.")
                        else:
                            st.error("Error al generar el reporte.")
                    else:
                        # Generar reporte comercial
                        buffer = reporte.export_report_comercial(formato=formato_map[formato])
                        
                        if buffer:
                            # Preparar nombre de archivo
                            fecha_actual = datetime.now().strftime("%Y%m%d_%H%M")
                            nombre_archivo = f"reporte_comercial_{fecha_actual}.{formato_map[formato]}"
                            
                            # Botón de descarga
                            st.download_button(
                                label="Descargar Reporte",
                                data=buffer,
                                file_name=nombre_archivo,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if formato_map[formato] == "xlsx" else "application/pdf"
                            )
                            
                            st.success("Reporte generado correctamente.")
                        else:
                            st.error("Error al generar el reporte.")
                
                except Exception as e:
                    st.error(f"Error al generar el reporte: {str(e)}")
        
        # Mostrar información sobre el contenido de los reportes
        with st.expander("Ver detalles del contenido de los reportes"):
            if tipo_reporte == "Reporte General Estratégico (Marketing)":
                st.write("""
                **Reporte General Estratégico (Marketing) incluye:**
                - Leads, matrículas, CPA, elasticidad, proyección de cierre
                - Simulaciones de escenarios (conversión, inversión)
                - Intervalos de confianza (95%)
                - Análisis comparativo y recomendaciones
                - Formato compatible con Power BI
                """)
            else:
                st.write("""
                **Reporte de Status Comercial incluye:**
                - Barra de progreso visual por convocatoria
                - Estado quincenal con observaciones
                - Predicción de matrícula final con intervalo de confianza
                - Semáforo de riesgo con recomendaciones accionables
                - Datos optimizados para toma de decisiones comerciales
                """)
    
    def _cargar_datos_ejemplo(self):
        """
        Carga datos de ejemplo para testing.
        """
        # Datos de ejemplo para leads
        data_leads = {
            'id_lead': range(1, 501),
            'fecha': pd.date_range(start='2023-01-01', periods=500),
            'origen': np.random.choice(['Facebook', 'Google', 'Instagram', 'Email', 'Referidos'], size=500),
            'programa': np.random.choice(['Programa A', 'Programa B', 'Programa C'], size=500),
            'estado': np.random.choice(['Nuevo', 'Contactado', 'Interesado', 'Demo', 'Matriculado'], size=500)
        }
        
        # Datos de ejemplo para matrículas (aproximadamente 10% de conversión)
        indices_matriculados = np.random.choice(range(500), size=50, replace=False)
        data_matriculas = {
            'id_matricula': range(1, 51),
            'id_lead': [data_leads['id_lead'][i] for i in indices_matriculados],
            'fecha': pd.date_range(start='2023-01-15', periods=50),
            'origen': [data_leads['origen'][i] for i in indices_matriculados],
            'programa': [data_leads['programa'][i] for i in indices_matriculados],
            'valor': np.random.uniform(1000, 5000, size=50)
        }
        
        # Datos de ejemplo para planificación de campañas
        data_campanas = {
            'id_campana': range(1, 6),
            'nombre': ['Campaña 1', 'Campaña 2', 'Campaña 3', 'Campaña 4', 'Campaña 5'],
            'origen': ['Facebook', 'Google', 'Instagram', 'Email', 'Referidos'],
            'fecha_inicio': pd.date_range(start='2023-01-01', periods=5),
            'fecha_fin': pd.date_range(start='2023-03-31', periods=5),
            'presupuesto_estimado': np.random.uniform(5000, 10000, size=5),
            'costo_ejecutado': np.random.uniform(4000, 9000, size=5),
            'objetivo_leads': [150, 100, 80, 50, 20],
            'objetivo_conversion': [0.1, 0.12, 0.09, 0.15, 0.2]
        }
        
        # Convertir a DataFrames
        st.session_state.datos_leads = pd.DataFrame(data_leads)
        st.session_state.datos_matriculas = pd.DataFrame(data_matriculas)
        st.session_state.datos_campanas = pd.DataFrame(data_campanas)

def mostrar_ui_reportes_avanzados():
    """
    Función principal para mostrar la interfaz de reportes avanzados.
    """
    # Crear instancia de la UI
    ui = ReportesAvanzadosUI()
    
    # Título principal
    st.title("Reportes Estratégicos Avanzados")
    
    # Menú lateral
    menu = st.sidebar.radio(
        "Menú de Reportes Avanzados",
        ["Carga de Datos", "Cálculo de CPL y CPA", "Proyecciones e Intervalos", 
         "Módulo de Soporte Comercial", "Exportación de Reportes"]
    )
    
    # Mostrar sección según selección
    if menu == "Carga de Datos":
        ui.mostrar_carga_datos()
    elif menu == "Cálculo de CPL y CPA":
        ui.mostrar_calculo_cpl_cpa()
    elif menu == "Proyecciones e Intervalos":
        ui.mostrar_proyecciones()
    elif menu == "Módulo de Soporte Comercial":
        ui.mostrar_modulo_soporte_comercial()
    elif menu == "Exportación de Reportes":
        ui.mostrar_exportacion_reportes()

if __name__ == "__main__":
    mostrar_ui_reportes_avanzados() 