import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import statsmodels.api as sm
import streamlit as st
from scipy import stats

class SoporteComercial:
    """
    Módulo específico de soporte comercial que proporciona alertas,
    simulaciones y recomendaciones para el equipo comercial.
    """
    
    def __init__(self, datos_leads=None, datos_matriculas=None, datos_campanas=None):
        """
        Inicializa el módulo de soporte comercial.
        
        Args:
            datos_leads (DataFrame): DataFrame con datos de leads
            datos_matriculas (DataFrame): DataFrame con datos de matrículas
            datos_campanas (DataFrame): DataFrame con datos de planificación de campañas
        """
        self.datos_leads = datos_leads
        self.datos_matriculas = datos_matriculas
        self.datos_campanas = datos_campanas
        self.fecha_actual = datetime.now()
    
    def calcular_estado_actual(self):
        """
        Calcula el estado actual de la campaña.
        
        Returns:
            dict: Estado actual de la campaña
        """
        if self.datos_leads is None or self.datos_campanas is None:
            return None
            
        try:
            # Obtener fechas de campaña
            fecha_inicio = pd.to_datetime(self.datos_campanas['fecha_inicio'].min())
            fecha_fin = pd.to_datetime(self.datos_campanas['fecha_fin'].max())
            
            # Calcular duración y tiempo transcurrido
            duracion_total = (fecha_fin - fecha_inicio).days
            tiempo_transcurrido = (self.fecha_actual - fecha_inicio).days
            
            if duracion_total <= 0 or tiempo_transcurrido < 0:
                return None
                
            # Calcular porcentaje de avance
            porcentaje_tiempo = min(100, (tiempo_transcurrido / duracion_total) * 100)
            
            # Obtener objetivo de leads
            objetivo_leads = self.datos_campanas['objetivo_leads'].sum()
            
            # Calcular leads generados
            leads_generados = len(self.datos_leads)
            
            # Calcular porcentaje de avance en leads
            porcentaje_leads = (leads_generados / objetivo_leads) * 100 if objetivo_leads > 0 else 0
            
            # Calcular tasa objetivo
            tasa_objetivo = 0.1  # valor por defecto
            if 'objetivo_conversion' in self.datos_campanas.columns:
                tasa_objetivo = self.datos_campanas['objetivo_conversion'].mean()
                
            objetivo_matriculas = objetivo_leads * tasa_objetivo
            
            # Calcular matrículas generadas
            matriculas_generadas = 0
            porcentaje_matriculas = 0
            
            if self.datos_matriculas is not None:
                matriculas_generadas = len(self.datos_matriculas)
                porcentaje_matriculas = (matriculas_generadas / objetivo_matriculas) * 100 if objetivo_matriculas > 0 else 0
                
            # Calcular proyección lineal de leads
            leads_proyectados = leads_generados / (porcentaje_tiempo / 100) if porcentaje_tiempo > 0 else 0
            
            # Calcular tasa de conversión actual
            tasa_conversion_actual = matriculas_generadas / leads_generados if leads_generados > 0 else 0
            
            # Calcular proyección de matrículas
            matriculas_proyectadas = leads_proyectados * tasa_conversion_actual
            
            # Calcular cumplimiento proyectado
            cumplimiento_leads = (leads_proyectados / objetivo_leads) * 100 if objetivo_leads > 0 else 0
            cumplimiento_matriculas = (matriculas_proyectadas / objetivo_matriculas) * 100 if objetivo_matriculas > 0 else 0
            
            return {
                'tiempo_transcurrido_dias': tiempo_transcurrido,
                'duracion_total_dias': duracion_total,
                'porcentaje_tiempo': porcentaje_tiempo,
                'leads_generados': leads_generados,
                'objetivo_leads': objetivo_leads,
                'porcentaje_leads': porcentaje_leads,
                'matriculas_generadas': matriculas_generadas,
                'objetivo_matriculas': objetivo_matriculas,
                'porcentaje_matriculas': porcentaje_matriculas,
                'leads_proyectados': leads_proyectados,
                'tasa_conversion_actual': tasa_conversion_actual,
                'tasa_objetivo': tasa_objetivo,
                'matriculas_proyectadas': matriculas_proyectadas,
                'cumplimiento_leads': cumplimiento_leads,
                'cumplimiento_matriculas': cumplimiento_matriculas
            }
            
        except Exception as e:
            print(f"Error al calcular estado actual: {str(e)}")
            return None
    
    def generar_alerta_desvio(self):
        """
        Genera una alerta de desvío anticipado (semáforo de riesgo).
        
        Returns:
            dict: Información de la alerta
        """
        estado = self.calcular_estado_actual()
        if estado is None:
            return None
            
        # Calcular nivel de alerta para leads
        if estado['cumplimiento_leads'] >= 95:
            nivel_leads = "VERDE"
            mensaje_leads = "En camino a cumplir objetivo de leads"
        elif estado['cumplimiento_leads'] >= 80:
            nivel_leads = "AMARILLO"
            mensaje_leads = "Atención: Posible desviación en objetivo de leads"
        else:
            nivel_leads = "ROJO"
            mensaje_leads = "Alerta crítica: Alta probabilidad de no cumplir objetivo de leads"
            
        # Calcular nivel de alerta para matrículas
        if estado['cumplimiento_matriculas'] >= 95:
            nivel_matriculas = "VERDE"
            mensaje_matriculas = "En camino a cumplir objetivo de matrículas"
        elif estado['cumplimiento_matriculas'] >= 80:
            nivel_matriculas = "AMARILLO"
            mensaje_matriculas = "Atención: Posible desviación en objetivo de matrículas"
        else:
            nivel_matriculas = "ROJO"
            mensaje_matriculas = "Alerta crítica: Alta probabilidad de no cumplir objetivo de matrículas"
            
        # Calcular semáforo global (el peor de los dos)
        if nivel_leads == "ROJO" or nivel_matriculas == "ROJO":
            nivel_global = "ROJO"
        elif nivel_leads == "AMARILLO" or nivel_matriculas == "AMARILLO":
            nivel_global = "AMARILLO"
        else:
            nivel_global = "VERDE"
            
        # Generar mensaje global
        if nivel_global == "VERDE":
            mensaje_global = "La campaña avanza según lo esperado en todos los indicadores."
        elif nivel_global == "AMARILLO":
            mensaje_global = "La campaña presenta algunas desviaciones que requieren atención."
        else:
            mensaje_global = "La campaña presenta desviaciones críticas que requieren acción inmediata."
            
        # Calcular días restantes
        dias_restantes = estado['duracion_total_dias'] - estado['tiempo_transcurrido_dias']
        
        return {
            'nivel_global': nivel_global,
            'mensaje_global': mensaje_global,
            'nivel_leads': nivel_leads,
            'mensaje_leads': mensaje_leads,
            'nivel_matriculas': nivel_matriculas,
            'mensaje_matriculas': mensaje_matriculas,
            'porcentaje_tiempo': estado['porcentaje_tiempo'],
            'porcentaje_leads': estado['porcentaje_leads'],
            'porcentaje_matriculas': estado['porcentaje_matriculas'],
            'dias_restantes': dias_restantes
        }
    
    def simular_escenarios_comerciales(self):
        """
        Simula escenarios comerciales para mejorar resultados.
        
        Returns:
            dict: Resultados de la simulación
        """
        estado = self.calcular_estado_actual()
        if estado is None:
            return None
            
        # Escenarios a simular
        escenarios = {
            'base': {
                'descripcion': 'Proyección actual (sin cambios)',
                'mejora_tasa': 0,
                'leads_adicionales': 0
            },
            'mejora_tasa_10': {
                'descripcion': 'Mejorar tasa de conversión 10%',
                'mejora_tasa': 0.1,
                'leads_adicionales': 0
            },
            'mejora_tasa_20': {
                'descripcion': 'Mejorar tasa de conversión 20%',
                'mejora_tasa': 0.2,
                'leads_adicionales': 0
            },
            'leads_adicionales': {
                'descripcion': f'Generar {int(estado["objetivo_leads"] * 0.1)} leads adicionales',
                'mejora_tasa': 0,
                'leads_adicionales': int(estado['objetivo_leads'] * 0.1)
            },
            'combinado': {
                'descripcion': 'Mejorar tasa 10% + leads adicionales',
                'mejora_tasa': 0.1,
                'leads_adicionales': int(estado['objetivo_leads'] * 0.1)
            }
        }
        
        # Calcular resultados para cada escenario
        resultados = {}
        
        for clave, escenario in escenarios.items():
            # Calcular leads totales
            leads_totales = estado['leads_proyectados'] + escenario['leads_adicionales']
            
            # Calcular nueva tasa de conversión
            nueva_tasa = estado['tasa_conversion_actual'] * (1 + escenario['mejora_tasa'])
            
            # Calcular matrículas proyectadas
            matriculas_proyectadas = leads_totales * nueva_tasa
            
            # Calcular porcentaje de cumplimiento
            cumplimiento = (matriculas_proyectadas / estado['objetivo_matriculas']) * 100 if estado['objetivo_matriculas'] > 0 else 0
            
            # Guardar resultados
            resultados[clave] = {
                'descripcion': escenario['descripcion'],
                'leads_totales': leads_totales,
                'tasa_conversion': nueva_tasa,
                'matriculas_proyectadas': matriculas_proyectadas,
                'objetivo_matriculas': estado['objetivo_matriculas'],
                'cumplimiento': cumplimiento,
                'diferencia_base': matriculas_proyectadas - estado['matriculas_proyectadas'] if clave != 'base' else 0
            }
            
        return resultados
    
    def calcular_costo_marginal(self):
        """
        Calcula el costo marginal de generar más leads.
        
        Returns:
            dict: Información sobre el costo marginal
        """
        if self.datos_leads is None or self.datos_campanas is None:
            return None
            
        # Verificar si hay datos de costo
        if 'costo_ejecutado' not in self.datos_campanas.columns:
            return None
            
        try:
            # Calcular costo total actual
            costo_total = self.datos_campanas['costo_ejecutado'].sum()
            
            # Calcular número de leads
            leads_total = len(self.datos_leads)
            
            if leads_total <= 0:
                return None
                
            # Calcular CPL actual
            cpl_actual = costo_total / leads_total
            
            # Calcular estado actual
            estado = self.calcular_estado_actual()
            if estado is None:
                return None
                
            # Factor de incremento para costo marginal
            # Asumimos que el costo marginal aumenta a medida que se saturan los canales
            factor_incremento = 1.0 + (estado['porcentaje_leads'] / 100) * 0.5
            
            # Calcular costo marginal
            cpl_marginal = cpl_actual * factor_incremento
            
            # Calcular opciones de leads adicionales
            opciones = [50, 100, 200, 500]
            resultados = []
            
            for leads_adicionales in opciones:
                # Calcular costo adicional
                costo_adicional = leads_adicionales * cpl_marginal
                
                # Calcular matrículas adicionales
                matriculas_adicionales = leads_adicionales * estado['tasa_conversion_actual']
                
                # Calcular costo por matrícula adicional
                cpa_marginal = costo_adicional / matriculas_adicionales if matriculas_adicionales > 0 else float('inf')
                
                resultados.append({
                    'leads_adicionales': leads_adicionales,
                    'costo_adicional': costo_adicional,
                    'matriculas_adicionales': matriculas_adicionales,
                    'cpa_marginal': cpa_marginal
                })
                
            return {
                'cpl_actual': cpl_actual,
                'cpl_marginal': cpl_marginal,
                'factor_incremento': factor_incremento,
                'opciones': resultados
            }
            
        except Exception as e:
            print(f"Error al calcular costo marginal: {str(e)}")
            return None
    
    def generar_recomendaciones_comerciales(self):
        """
        Genera recomendaciones accionables para el equipo comercial.
        
        Returns:
            list: Lista de recomendaciones
        """
        alerta = self.generar_alerta_desvio()
        escenarios = self.simular_escenarios_comerciales()
        
        if alerta is None or escenarios is None:
            return []
            
        recomendaciones = []
        
        # Recomendaciones basadas en estado global
        if alerta['nivel_global'] == "VERDE":
            recomendaciones.append({
                'tipo': 'general',
                'texto': "La campaña avanza según lo esperado. Mantener estrategia actual.",
                'prioridad': 'baja'
            })
        
        # Recomendaciones para leads
        if alerta['nivel_leads'] == "AMARILLO":
            recomendaciones.append({
                'tipo': 'leads',
                'texto': "Revisar fuentes de tráfico que están generando menos leads de lo esperado.",
                'prioridad': 'media'
            })
        elif alerta['nivel_leads'] == "ROJO":
            recomendaciones.append({
                'tipo': 'leads',
                'texto': "¡Alerta crítica en generación de leads! Solicitar reunión urgente con equipo de marketing.",
                'prioridad': 'alta'
            })
            
        # Recomendaciones para conversión
        if alerta['nivel_matriculas'] == "AMARILLO":
            recomendaciones.append({
                'tipo': 'conversion',
                'texto': "Aumentar frecuencia de contacto con leads existentes para mejorar tasa de conversión.",
                'prioridad': 'media'
            })
            recomendaciones.append({
                'tipo': 'conversion',
                'texto': "Revisar script de llamadas y actualizar argumentos de venta.",
                'prioridad': 'media'
            })
        elif alerta['nivel_matriculas'] == "ROJO":
            recomendaciones.append({
                'tipo': 'conversion',
                'texto': "¡Alerta crítica en conversión! Implementar plan de choque para mejorar tasa de contacto y conversión.",
                'prioridad': 'alta'
            })
            recomendaciones.append({
                'tipo': 'conversion',
                'texto': "Considerar incentivos adicionales para matrículas en los próximos días.",
                'prioridad': 'alta'
            })
            
        # Recomendaciones basadas en simulaciones
        if escenarios:
            # Encontrar el mejor escenario (excluyendo el base)
            mejor_escenario = None
            mejor_diferencia = 0
            
            for clave, escenario in escenarios.items():
                if clave != 'base' and escenario['diferencia_base'] > mejor_diferencia:
                    mejor_escenario = escenario
                    mejor_diferencia = escenario['diferencia_base']
            
            if mejor_escenario:
                recomendaciones.append({
                    'tipo': 'optimizacion',
                    'texto': f"Estrategia recomendada: {mejor_escenario['descripcion']}. Generaría {mejor_escenario['diferencia_base']:.1f} matrículas adicionales.",
                    'prioridad': 'alta'
                })
                
        # Recomendaciones basadas en días restantes
        if alerta['dias_restantes'] < 15:
            recomendaciones.append({
                'tipo': 'tiempo',
                'texto': f"¡Quedan solo {alerta['dias_restantes']} días! Priorizar acciones de seguimiento a leads avanzados en el embudo.",
                'prioridad': 'alta'
            })
        elif alerta['dias_restantes'] < 30:
            recomendaciones.append({
                'tipo': 'tiempo',
                'texto': f"Quedan {alerta['dias_restantes']} días. Equilibrar esfuerzos entre nuevos leads y seguimiento a leads existentes.",
                'prioridad': 'media'
            })
            
        # Calcular costo marginal para recomendaciones específicas
        costo_marginal = self.calcular_costo_marginal()
        if costo_marginal is not None and alerta['nivel_matriculas'] != "VERDE":
            # Encontrar la opción más eficiente (menor CPA marginal que no sea infinito)
            opciones_validas = [op for op in costo_marginal['opciones'] if op['cpa_marginal'] < float('inf')]
            
            if opciones_validas:
                mejor_opcion = min(opciones_validas, key=lambda x: x['cpa_marginal'])
                
                recomendaciones.append({
                    'tipo': 'inversion',
                    'texto': f"Si se necesitan leads adicionales, la opción más eficiente es generar {mejor_opcion['leads_adicionales']} leads (costo aprox. ${mejor_opcion['costo_adicional']:.2f}).",
                    'prioridad': 'media'
                })
                
        return recomendaciones
    
    def generar_barras_progreso_html(self):
        """
        Genera código HTML para mostrar barras de progreso visuales.
        
        Returns:
            str: Código HTML con barras de progreso
        """
        estado = self.calcular_estado_actual()
        if estado is None:
            return "<p>No hay datos suficientes para generar barras de progreso.</p>"
            
        # Generar código HTML para barras de progreso
        html = """
        <style>
            .progress-container {
                width: 100%;
                background-color: #e0e0e0;
                margin: 10px 0;
                border-radius: 4px;
                overflow: hidden;
            }
            .progress-bar {
                height: 24px;
                text-align: center;
                line-height: 24px;
                color: white;
                font-weight: bold;
                transition: width 0.5s;
            }
            .progress-verde {
                background-color: #4CAF50;
            }
            .progress-amarillo {
                background-color: #FFEB3B;
                color: #333;
            }
            .progress-rojo {
                background-color: #F44336;
            }
            .progress-label {
                font-weight: bold;
                margin-bottom: 5px;
            }
        </style>
        """
        
        # Determinar colores según nivel de alerta
        alerta = self.generar_alerta_desvio()
        color_tiempo = "progress-verde"  # El tiempo siempre avanza como se espera
        
        if alerta:
            color_leads = {
                "VERDE": "progress-verde",
                "AMARILLO": "progress-amarillo",
                "ROJO": "progress-rojo"
            }.get(alerta['nivel_leads'], "progress-verde")
            
            color_matriculas = {
                "VERDE": "progress-verde",
                "AMARILLO": "progress-amarillo",
                "ROJO": "progress-rojo"
            }.get(alerta['nivel_matriculas'], "progress-verde")
        else:
            color_leads = "progress-verde"
            color_matriculas = "progress-verde"
        
        # Generar barras
        html += '<div class="progress-label">Tiempo transcurrido</div>'
        html += f'''
        <div class="progress-container">
            <div class="progress-bar {color_tiempo}" style="width:{estado['porcentaje_tiempo']}%">
                {estado['porcentaje_tiempo']:.1f}%
            </div>
        </div>
        '''
        
        html += '<div class="progress-label">Leads generados</div>'
        html += f'''
        <div class="progress-container">
            <div class="progress-bar {color_leads}" style="width:{estado['porcentaje_leads']}%">
                {estado['porcentaje_leads']:.1f}%
            </div>
        </div>
        '''
        
        html += '<div class="progress-label">Matrículas</div>'
        html += f'''
        <div class="progress-container">
            <div class="progress-bar {color_matriculas}" style="width:{estado['porcentaje_matriculas']}%">
                {estado['porcentaje_matriculas']:.1f}%
            </div>
        </div>
        '''
        
        return html
    
    def generar_proyeccion_estrategica(self):
        """
        Genera una proyección estratégica de cumplimiento.
        
        Returns:
            dict: Información de proyección estratégica
        """
        estado = self.calcular_estado_actual()
        if estado is None:
            return None
            
        alerta = self.generar_alerta_desvio()
        if alerta is None:
            return None
            
        escenarios = self.simular_escenarios_comerciales()
        if escenarios is None:
            return None
            
        # Calcular intervalo de confianza para la proyección
        # Usamos un enfoque simple basado en la variabilidad histórica
        
        # Obtener datos de conversión diaria (si disponibles)
        if self.datos_leads is None or self.datos_matriculas is None:
            # Sin datos históricos, usamos un intervalo aproximado
            margen_error = 0.2  # 20% de margen de error
            matriculas_min = estado['matriculas_proyectadas'] * (1 - margen_error)
            matriculas_max = estado['matriculas_proyectadas'] * (1 + margen_error)
        else:
            try:
                # Encontrar columnas de fecha
                fecha_cols_leads = [col for col in self.datos_leads.columns if 'fecha' in col.lower()]
                fecha_cols_matriculas = [col for col in self.datos_matriculas.columns if 'fecha' in col.lower()]
                
                if fecha_cols_leads and fecha_cols_matriculas:
                    # Convertir a datetime
                    self.datos_leads[fecha_cols_leads[0]] = pd.to_datetime(self.datos_leads[fecha_cols_leads[0]])
                    self.datos_matriculas[fecha_cols_matriculas[0]] = pd.to_datetime(self.datos_matriculas[fecha_cols_matriculas[0]])
                    
                    # Agrupar por día
                    leads_diarios = self.datos_leads.groupby(self.datos_leads[fecha_cols_leads[0]].dt.date).size()
                    matriculas_diarias = self.datos_matriculas.groupby(self.datos_matriculas[fecha_cols_matriculas[0]].dt.date).size()
                    
                    # Calcular tasas de conversión diarias
                    fechas_comunes = set(leads_diarios.index).intersection(set(matriculas_diarias.index))
                    
                    if fechas_comunes:
                        tasas_diarias = []
                        
                        for fecha in fechas_comunes:
                            if leads_diarios[fecha] > 0:
                                tasa = matriculas_diarias[fecha] / leads_diarios[fecha]
                                tasas_diarias.append(tasa)
                        
                        if tasas_diarias:
                            # Calcular intervalo de confianza para la tasa
                            media_tasa = np.mean(tasas_diarias)
                            std_tasa = np.std(tasas_diarias)
                            
                            # Intervalo de confianza del 95%
                            tasa_min = max(0, media_tasa - 1.96 * std_tasa / np.sqrt(len(tasas_diarias)))
                            tasa_max = media_tasa + 1.96 * std_tasa / np.sqrt(len(tasas_diarias))
                            
                            # Proyectar con estos intervalos
                            matriculas_min = estado['leads_proyectados'] * tasa_min
                            matriculas_max = estado['leads_proyectados'] * tasa_max
                        else:
                            # Sin datos suficientes
                            margen_error = 0.2
                            matriculas_min = estado['matriculas_proyectadas'] * (1 - margen_error)
                            matriculas_max = estado['matriculas_proyectadas'] * (1 + margen_error)
                    else:
                        # Sin fechas comunes
                        margen_error = 0.2
                        matriculas_min = estado['matriculas_proyectadas'] * (1 - margen_error)
                        matriculas_max = estado['matriculas_proyectadas'] * (1 + margen_error)
                else:
                    # Sin columnas de fecha
                    margen_error = 0.2
                    matriculas_min = estado['matriculas_proyectadas'] * (1 - margen_error)
                    matriculas_max = estado['matriculas_proyectadas'] * (1 + margen_error)
            except Exception as e:
                print(f"Error al calcular intervalo de confianza: {str(e)}")
                margen_error = 0.2
                matriculas_min = estado['matriculas_proyectadas'] * (1 - margen_error)
                matriculas_max = estado['matriculas_proyectadas'] * (1 + margen_error)
        
        # Extraer mejor escenario
        mejor_escenario = None
        mejor_diferencia = 0
        
        for clave, escenario in escenarios.items():
            if clave != 'base' and escenario['diferencia_base'] > mejor_diferencia:
                mejor_escenario = escenario
                mejor_diferencia = escenario['diferencia_base']
        
        # Generar recomendaciones
        recomendaciones = self.generar_recomendaciones_comerciales()
        
        return {
            'estado_actual': estado,
            'alerta': alerta,
            'matriculas_proyectadas': estado['matriculas_proyectadas'],
            'matriculas_min': matriculas_min,
            'matriculas_max': matriculas_max,
            'mejor_escenario': mejor_escenario,
            'recomendaciones': recomendaciones
        }
    
    def generar_dashboard_comercial(self, streamlit=True):
        """
        Genera un dashboard comercial interactivo.
        
        Args:
            streamlit (bool): Si es True, genera componentes para Streamlit
            
        Returns:
            dict: Componentes del dashboard
        """
        # Obtener datos
        estado = self.calcular_estado_actual()
        alerta = self.generar_alerta_desvio()
        proyeccion = self.generar_proyeccion_estrategica()
        
        if estado is None or alerta is None or proyeccion is None:
            return None
            
        if streamlit:
            # Generar dashboard en Streamlit
            st.subheader("Estado de Campaña")
            
            # Mostrar métricas principales
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Tiempo transcurrido",
                    f"{estado['porcentaje_tiempo']:.1f}%",
                    delta=None
                )
                
            with col2:
                st.metric(
                    "Leads generados",
                    f"{estado['leads_generados']}",
                    f"{estado['porcentaje_leads'] - estado['porcentaje_tiempo']:.1f}%" if estado['porcentaje_leads'] >= estado['porcentaje_tiempo'] else f"{estado['porcentaje_leads'] - estado['porcentaje_tiempo']:.1f}%"
                )
                
            with col3:
                st.metric(
                    "Matrículas",
                    f"{estado['matriculas_generadas']}",
                    f"{estado['porcentaje_matriculas'] - estado['porcentaje_tiempo']:.1f}%" if estado['porcentaje_matriculas'] >= estado['porcentaje_tiempo'] else f"{estado['porcentaje_matriculas'] - estado['porcentaje_tiempo']:.1f}%"
                )
                
            # Mostrar barras de progreso
            st.subheader("Progreso de Campaña")
            barras_html = self.generar_barras_progreso_html()
            st.components.v1.html(barras_html, height=200)
            
            # Mostrar semáforo de riesgo
            st.subheader("Semáforo de Riesgo")
            
            # Color según nivel de alerta
            color_semaforo = {
                "VERDE": "#4CAF50",
                "AMARILLO": "#FFEB3B",
                "ROJO": "#F44336"
            }.get(alerta['nivel_global'], "#4CAF50")
            
            # Crear contenedor con color de fondo
            st.markdown(
                f"""
                <div style="background-color: {color_semaforo}; padding: 10px; border-radius: 5px; color: {'white' if alerta['nivel_global'] != 'AMARILLO' else 'black'};">
                    <h3 style="margin: 0;">{alerta['mensaje_global']}</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Mostrar proyección
            st.subheader("Proyección Estratégica de Cumplimiento")
            
            # Mostrar gráfico de proyección
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Crear gráfico de barras
            categorias = ['Matriculas\nActuales', 'Proyección\nSin Cambios', 'Objetivo']
            valores = [estado['matriculas_generadas'], estado['matriculas_proyectadas'], estado['objetivo_matriculas']]
            colores = ['#64B5F6', '#FFB74D', '#81C784']
            
            ax.bar(categorias, valores, color=colores)
            
            # Añadir intervalo de confianza a la proyección
            ax.errorbar(
                'Proyección\nSin Cambios',
                estado['matriculas_proyectadas'],
                yerr=[[estado['matriculas_proyectadas']-proyeccion['matriculas_min']], 
                      [proyeccion['matriculas_max']-estado['matriculas_proyectadas']]],
                fmt='o',
                color='black',
                capsize=5
            )
            
            # Añadir mejor escenario
            if proyeccion['mejor_escenario']:
                categorias.append('Proyección\nMejor Escenario')
                valores.append(proyeccion['mejor_escenario']['matriculas_proyectadas'])
                colores.append('#AB47BC')
            
            # Configurar gráfico
            ax.set_title('Proyección de Matrículas')
            ax.set_ylabel('Número de Matrículas')
            
            # Añadir etiquetas de valor
            for i, valor in enumerate(valores):
                ax.text(i, valor + 1, f"{valor:.0f}", ha='center')
            
            # Mostrar gráfico
            st.pyplot(fig)
            
            # Mostrar recomendaciones
            st.subheader("Recomendaciones Accionables")
            
            if proyeccion['recomendaciones']:
                # Agrupar por prioridad
                alta_prioridad = [r for r in proyeccion['recomendaciones'] if r['prioridad'] == 'alta']
                media_prioridad = [r for r in proyeccion['recomendaciones'] if r['prioridad'] == 'media']
                baja_prioridad = [r for r in proyeccion['recomendaciones'] if r['prioridad'] == 'baja']
                
                if alta_prioridad:
                    st.markdown("### Acciones Urgentes")
                    for recom in alta_prioridad:
                        st.markdown(f"- **{recom['texto']}**")
                
                if media_prioridad:
                    st.markdown("### Acciones Recomendadas")
                    for recom in media_prioridad:
                        st.markdown(f"- {recom['texto']}")
                        
                if baja_prioridad:
                    st.markdown("### Consideraciones Adicionales")
                    for recom in baja_prioridad:
                        st.markdown(f"- {recom['texto']}")
            else:
                st.info("No hay recomendaciones específicas en este momento.")
            
            # Retornar None ya que la visualización se hace directamente
            return None
        else:
            # Retornar datos para uso externo
            return {
                'estado': estado,
                'alerta': alerta,
                'proyeccion': proyeccion,
                'barras_html': self.generar_barras_progreso_html()
            } 