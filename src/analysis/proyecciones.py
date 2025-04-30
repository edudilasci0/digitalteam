import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta

class ProyeccionesAnalyzer:
    """
    Clase para realizar proyecciones, calcular intervalos de confianza
    y generar análisis predictivos para el Motor de Decisión.
    """
    
    def __init__(self, datos_leads=None, datos_matriculas=None, datos_campanas=None):
        """
        Inicializa el analizador de proyecciones con los datos necesarios.
        
        Args:
            datos_leads (DataFrame): DataFrame con datos de leads
            datos_matriculas (DataFrame): DataFrame con datos de matrículas
            datos_campanas (DataFrame): DataFrame con datos de campañas
        """
        self.datos_leads = datos_leads
        self.datos_matriculas = datos_matriculas
        self.datos_campanas = datos_campanas
        
    def calcular_intervalo_confianza(self, datos, nivel_confianza=0.95):
        """
        Calcula un intervalo de confianza para los datos proporcionados.
        
        Args:
            datos (array-like): Datos para calcular el intervalo
            nivel_confianza (float): Nivel de confianza (0-1)
            
        Returns:
            tuple: (media, límite_inferior, límite_superior)
        """
        datos = np.array(datos)
        media = np.mean(datos)
        error_std = stats.sem(datos)
        
        # Calcular intervalo de confianza
        intervalo = stats.t.interval(
            nivel_confianza, 
            len(datos)-1, 
            loc=media, 
            scale=error_std
        )
        
        return media, intervalo[0], intervalo[1]
    
    def proyectar_tendencia_lineal(self, x, y, x_pred, nivel_confianza=0.95):
        """
        Proyecta valores utilizando regresión lineal y calcula intervalos de confianza.
        
        Args:
            x (array-like): Variable independiente (ej. días)
            y (array-like): Variable dependiente (ej. leads acumulados)
            x_pred (array-like): Valores de x para los que se quiere predecir
            nivel_confianza (float): Nivel de confianza (0-1)
            
        Returns:
            tuple: (predicciones, límites_inferiores, límites_superiores)
        """
        # Convertir a arrays numpy
        x = np.array(x).reshape(-1, 1)
        y = np.array(y)
        x_pred = np.array(x_pred).reshape(-1, 1)
        
        # Ajustar modelo de regresión lineal
        modelo = sm.OLS(y, sm.add_constant(x))
        resultado = modelo.fit()
        
        # Realizar predicciones
        x_pred_const = sm.add_constant(x_pred)
        predicciones = resultado.predict(x_pred_const)
        
        # Calcular intervalos de confianza para predicciones
        prediccion_intervalos = resultado.get_prediction(x_pred_const)
        intervalos = prediccion_intervalos.conf_int(alpha=1-nivel_confianza)
        
        return predicciones, intervalos[:, 0], intervalos[:, 1]
    
    def proyectar_serie_temporal(self, serie, periodos_futuros=30, nivel_confianza=0.95):
        """
        Proyecta una serie temporal utilizando ARIMA y calcula intervalos de confianza.
        
        Args:
            serie (Series): Serie temporal de pandas con índice de fechas
            periodos_futuros (int): Número de períodos a proyectar
            nivel_confianza (float): Nivel de confianza (0-1)
            
        Returns:
            tuple: (predicciones, límites_inferiores, límites_superiores)
        """
        # Ajustar modelo ARIMA (parámetros simples por defecto)
        try:
            modelo = ARIMA(serie, order=(1, 1, 1))
            resultado = modelo.fit()
            
            # Realizar predicción con intervalos de confianza
            prediccion = resultado.get_forecast(steps=periodos_futuros)
            predicciones = prediccion.predicted_mean
            intervalos = prediccion.conf_int(alpha=1-nivel_confianza)
            
            return predicciones, intervalos.iloc[:, 0], intervalos.iloc[:, 1]
            
        except Exception as e:
            # Si falla ARIMA, usar proyección más simple
            print(f"Error en proyección ARIMA: {str(e)}")
            print("Usando proyección lineal simple...")
            
            # Crear índice numérico para x
            x = np.arange(len(serie))
            y = serie.values
            
            # Valores a predecir
            x_pred = np.arange(len(serie), len(serie) + periodos_futuros)
            
            # Usar proyección lineal
            return self.proyectar_tendencia_lineal(x, y, x_pred, nivel_confianza)
    
    def proyectar_cierre_campana(self, nivel_confianza=0.95):
        """
        Proyecta el cierre de la campaña basado en datos actuales.
        
        Args:
            nivel_confianza (float): Nivel de confianza (0-1)
            
        Returns:
            dict: Diccionario con proyecciones e intervalos
        """
        if self.datos_leads is None or self.datos_campanas is None:
            return None
            
        try:
            # Obtener fechas de campaña
            fecha_inicio = pd.to_datetime(self.datos_campanas['fecha_inicio'].min())
            fecha_fin = pd.to_datetime(self.datos_campanas['fecha_fin'].max())
            
            # Encontrar columna de fecha en leads
            fecha_cols = [col for col in self.datos_leads.columns if 'fecha' in col.lower()]
            if not fecha_cols:
                return None
                
            fecha_col = fecha_cols[0]
            self.datos_leads[fecha_col] = pd.to_datetime(self.datos_leads[fecha_col])
            
            # Crear serie temporal de leads diarios
            leads_diarios = self.datos_leads.groupby(self.datos_leads[fecha_col].dt.date).size()
            
            # Calcular leads acumulados
            leads_acumulados = leads_diarios.cumsum()
            
            # Crear serie temporal completa con ceros para días sin leads
            fecha_completa = pd.date_range(fecha_inicio, fecha_fin)
            leads_acumulados_completo = pd.Series(index=fecha_completa, dtype=float).fillna(0)
            
            # Rellenar con datos reales
            for fecha, valor in leads_acumulados.items():
                if pd.to_datetime(fecha) in leads_acumulados_completo.index:
                    leads_acumulados_completo[pd.to_datetime(fecha)] = valor
            
            # Rellenar valores faltantes con interpolación forward fill
            leads_acumulados_completo = leads_acumulados_completo.fillna(method='ffill')
            
            # Determinar cuántos días faltan para terminar la campaña
            hoy = datetime.now().date()
            dias_restantes = (fecha_fin.date() - hoy).days
            
            if dias_restantes <= 0:
                # Campaña ya terminada
                return {
                    'leads_finales': leads_acumulados_completo.iloc[-1],
                    'limite_inferior': leads_acumulados_completo.iloc[-1],
                    'limite_superior': leads_acumulados_completo.iloc[-1],
                    'dias_restantes': 0
                }
            
            # Proyectar leads finales
            # Usar datos hasta hoy para proyectar
            leads_hasta_hoy = leads_acumulados_completo[leads_acumulados_completo.index <= pd.Timestamp(hoy)]
            
            # Calcular días desde inicio
            dias_desde_inicio = [(d - fecha_inicio).days for d in leads_hasta_hoy.index]
            
            # Proyectar tendencia lineal
            dias_futuros = np.arange(dias_desde_inicio[-1] + 1, dias_desde_inicio[-1] + dias_restantes + 1)
            pred, lower, upper = self.proyectar_tendencia_lineal(
                dias_desde_inicio, 
                leads_hasta_hoy.values, 
                dias_futuros,
                nivel_confianza
            )
            
            # Obtener proyección final (último valor)
            leads_finales = pred[-1]
            limite_inferior = lower[-1]
            limite_superior = upper[-1]
            
            # Calcular tasa de conversión si hay datos de matrículas
            tasa_conversion = None
            matriculas_proyectadas = None
            matriculas_limite_inferior = None
            matriculas_limite_superior = None
            
            if self.datos_matriculas is not None:
                # Calcular tasa de conversión actual
                matriculas_actuales = len(self.datos_matriculas)
                leads_actuales = len(self.datos_leads)
                
                if leads_actuales > 0:
                    tasa_conversion = matriculas_actuales / leads_actuales
                    
                    # Proyectar matrículas
                    matriculas_proyectadas = leads_finales * tasa_conversion
                    
                    # Calcular intervalos para matrículas
                    # Usamos bootstrapping para calcular el intervalo de confianza
                    n_bootstrap = 1000
                    bootstrap_samples = []
                    
                    for _ in range(n_bootstrap):
                        # Simular variación en tasa de conversión
                        tasa_simulada = np.random.beta(
                            matriculas_actuales + 1,
                            leads_actuales - matriculas_actuales + 1
                        )
                        
                        # Simular leads finales
                        leads_simulados = np.random.normal(
                            leads_finales,
                            (upper[-1] - lower[-1]) / (2 * stats.norm.ppf(0.5 + nivel_confianza/2))
                        )
                        
                        # Calcular matrículas simuladas
                        matriculas_simuladas = leads_simulados * tasa_simulada
                        bootstrap_samples.append(matriculas_simuladas)
                    
                    # Calcular intervalo de confianza
                    matriculas_limite_inferior = np.percentile(bootstrap_samples, (1-nivel_confianza)*100/2)
                    matriculas_limite_superior = np.percentile(bootstrap_samples, 100 - (1-nivel_confianza)*100/2)
            
            return {
                'leads_actuales': leads_hasta_hoy.iloc[-1],
                'leads_finales': leads_finales,
                'leads_limite_inferior': limite_inferior,
                'leads_limite_superior': limite_superior,
                'dias_restantes': dias_restantes,
                'tasa_conversion': tasa_conversion,
                'matriculas_actuales': matriculas_actuales if self.datos_matriculas is not None else None,
                'matriculas_proyectadas': matriculas_proyectadas,
                'matriculas_limite_inferior': matriculas_limite_inferior,
                'matriculas_limite_superior': matriculas_limite_superior,
                'nivel_confianza': nivel_confianza
            }
            
        except Exception as e:
            print(f"Error al proyectar cierre: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def simular_escenarios(self, tipo="conversion", variaciones=None):
        """
        Simula diferentes escenarios y calcula el impacto en las métricas finales.
        
        Args:
            tipo (str): Tipo de simulación ('conversion', 'inversion', o 'costo_marginal')
            variaciones (list): Lista de variaciones a simular
            
        Returns:
            DataFrame: Resultados de la simulación
        """
        # Obtener proyección base
        proyeccion = self.proyectar_cierre_campana()
        if proyeccion is None:
            return None
            
        resultados = []
            
        if tipo == "conversion":
            # Simular mejoras en tasa de conversión
            if variaciones is None:
                variaciones = [0.05, 0.1, 0.15, 0.2, 0.3]  # 5% a 30%
                
            if proyeccion['tasa_conversion'] is None:
                return None
                
            # Calcular escenarios
            for var in variaciones:
                nueva_tasa = proyeccion['tasa_conversion'] * (1 + var)
                nuevas_matriculas = proyeccion['leads_finales'] * nueva_tasa
                
                # Calcular diferencia
                diferencia = nuevas_matriculas - proyeccion['matriculas_proyectadas']
                
                resultados.append({
                    'escenario': f"+{var*100:.0f}% en conversión",
                    'tasa_conversion': nueva_tasa,
                    'matriculas_proyectadas': nuevas_matriculas,
                    'diferencia': diferencia,
                    'diferencia_porcentual': (diferencia / proyeccion['matriculas_proyectadas']) * 100 if proyeccion['matriculas_proyectadas'] > 0 else 0
                })
                
        elif tipo == "inversion":
            # Simular cambios en la inversión publicitaria
            if variaciones is None:
                variaciones = [-0.2, -0.1, 0.1, 0.2, 0.3]  # -20% a +30%
                
            # Calcular elasticidad (simulada, en un caso real se estimaría a partir de datos históricos)
            elasticidad = 0.8  # Ejemplo: si aumentamos inversión 10%, leads aumentan 8%
                
            # Calcular escenarios
            for var in variaciones:
                nuevos_leads = proyeccion['leads_finales'] * (1 + elasticidad * var)
                
                if proyeccion['tasa_conversion'] is not None:
                    nuevas_matriculas = nuevos_leads * proyeccion['tasa_conversion']
                    diferencia_matriculas = nuevas_matriculas - proyeccion['matriculas_proyectadas']
                else:
                    nuevas_matriculas = None
                    diferencia_matriculas = None
                    
                # Diferencia en leads
                diferencia_leads = nuevos_leads - proyeccion['leads_finales']
                
                resultados.append({
                    'escenario': f"{var*100:+.0f}% en inversión",
                    'leads_proyectados': nuevos_leads,
                    'diferencia_leads': diferencia_leads,
                    'matriculas_proyectadas': nuevas_matriculas,
                    'diferencia_matriculas': diferencia_matriculas
                })
                
        elif tipo == "costo_marginal":
            # Simular costo marginal de generar más leads
            if variaciones is None:
                variaciones = [50, 100, 200, 300, 500]  # Leads adicionales
                
            # Calcular costo promedio por lead (CPL actual)
            if self.datos_campanas is None or 'costo_ejecutado' not in self.datos_campanas.columns:
                return None
                
            costo_total = self.datos_campanas['costo_ejecutado'].sum()
            leads_actuales = proyeccion['leads_actuales']
            
            if leads_actuales <= 0:
                return None
                
            cpl_actual = costo_total / leads_actuales
            
            # Factor de incremento de costo marginal
            # En la mayoría de casos, el costo marginal aumenta a medida que se agregan más leads
            factor_incremento = 1.2  # Ejemplo: cada nuevo lead cuesta 20% más que el anterior
            
            # Calcular escenarios
            for leads_adicionales in variaciones:
                # Calcular costo marginal con incremento exponencial
                costo_marginal = cpl_actual * (1 + (leads_adicionales / leads_actuales) * factor_incremento)
                costo_total_adicional = leads_adicionales * costo_marginal
                
                # Calcular impacto en matrículas
                if proyeccion['tasa_conversion'] is not None:
                    matriculas_adicionales = leads_adicionales * proyeccion['tasa_conversion']
                    cpa_marginal = costo_total_adicional / matriculas_adicionales if matriculas_adicionales > 0 else float('inf')
                else:
                    matriculas_adicionales = None
                    cpa_marginal = None
                
                resultados.append({
                    'leads_adicionales': leads_adicionales,
                    'costo_marginal_por_lead': costo_marginal,
                    'costo_total_adicional': costo_total_adicional,
                    'matriculas_adicionales': matriculas_adicionales,
                    'costo_por_matricula_marginal': cpa_marginal
                })
        
        return pd.DataFrame(resultados)
    
    def calcular_alerta_desvio(self):
        """
        Calcula el nivel de alerta por desvío en la campaña.
        
        Returns:
            dict: Información de alerta
        """
        proyeccion = self.proyectar_cierre_campana()
        if proyeccion is None:
            return None
            
        if self.datos_campanas is None or 'objetivo_leads' not in self.datos_campanas.columns:
            return None
            
        # Obtener objetivo de leads
        objetivo_leads = self.datos_campanas['objetivo_leads'].sum()
        
        # Calcular porcentaje de cumplimiento proyectado
        if objetivo_leads <= 0:
            return None
            
        cumplimiento_leads = (proyeccion['leads_finales'] / objetivo_leads) * 100
        
        # Determinar nivel de alerta para leads
        if cumplimiento_leads >= 90:
            nivel_alerta_leads = "VERDE"
            mensaje_leads = "En camino a cumplir objetivo de leads"
        elif cumplimiento_leads >= 70:
            nivel_alerta_leads = "AMARILLO"
            mensaje_leads = "Alerta: Posible incumplimiento de objetivo de leads"
        else:
            nivel_alerta_leads = "ROJO"
            mensaje_leads = "Peligro: Alto riesgo de incumplimiento en leads"
            
        # Calcular alerta para matrículas si hay datos
        if proyeccion['matriculas_proyectadas'] is not None:
            # Asumir objetivo de conversión del 10% si no hay otro dato
            tasa_objetivo = 0.1
            if 'objetivo_conversion' in self.datos_campanas.columns:
                tasa_objetivo = self.datos_campanas['objetivo_conversion'].mean()
                
            objetivo_matriculas = objetivo_leads * tasa_objetivo
            
            if objetivo_matriculas > 0:
                cumplimiento_matriculas = (proyeccion['matriculas_proyectadas'] / objetivo_matriculas) * 100
                
                # Determinar nivel de alerta para matrículas
                if cumplimiento_matriculas >= 90:
                    nivel_alerta_matriculas = "VERDE"
                    mensaje_matriculas = "En camino a cumplir objetivo de matrículas"
                elif cumplimiento_matriculas >= 70:
                    nivel_alerta_matriculas = "AMARILLO"
                    mensaje_matriculas = "Alerta: Posible incumplimiento de objetivo de matrículas"
                else:
                    nivel_alerta_matriculas = "ROJO"
                    mensaje_matriculas = "Peligro: Alto riesgo de incumplimiento en matrículas"
                    
                return {
                    'nivel_alerta_leads': nivel_alerta_leads,
                    'mensaje_leads': mensaje_leads,
                    'cumplimiento_leads': cumplimiento_leads,
                    'nivel_alerta_matriculas': nivel_alerta_matriculas,
                    'mensaje_matriculas': mensaje_matriculas,
                    'cumplimiento_matriculas': cumplimiento_matriculas,
                    'dias_restantes': proyeccion['dias_restantes']
                }
            
        # Si no hay datos de matrículas, solo devolver alerta de leads
        return {
            'nivel_alerta_leads': nivel_alerta_leads,
            'mensaje_leads': mensaje_leads,
            'cumplimiento_leads': cumplimiento_leads,
            'dias_restantes': proyeccion['dias_restantes']
        }
    
    def generar_recomendaciones_accionables(self):
        """
        Genera recomendaciones accionables basadas en el análisis de los datos.
        
        Returns:
            list: Lista de recomendaciones
        """
        alerta = self.calcular_alerta_desvio()
        if alerta is None:
            return []
            
        recomendaciones = []
        
        # Recomendaciones basadas en estado de leads
        if alerta['nivel_alerta_leads'] == "VERDE":
            recomendaciones.append("Mantener estrategia actual de generación de leads")
        elif alerta['nivel_alerta_leads'] == "AMARILLO":
            recomendaciones.append("Incrementar inversión en canales con mejor CPL")
            recomendaciones.append("Revisar y optimizar landing pages para mejorar tasa de conversión")
        else:  # ROJO
            recomendaciones.append("¡Acción urgente! Revisar y ajustar estrategia de generación de leads")
            recomendaciones.append("Considerar nuevos canales o reajustar presupuesto entre canales existentes")
            
        # Recomendaciones basadas en matrículas
        if 'nivel_alerta_matriculas' in alerta:
            if alerta['nivel_alerta_matriculas'] == "VERDE":
                recomendaciones.append("Mantener proceso de contactación y conversión actual")
            elif alerta['nivel_alerta_matriculas'] == "AMARILLO":
                recomendaciones.append("Incrementar frecuencia de contacto con leads existentes")
                recomendaciones.append("Revisar script de llamadas y mejorar argumentos de venta")
            else:  # ROJO
                recomendaciones.append("¡Acción urgente en equipo comercial! Revisar proceso completo")
                recomendaciones.append("Implementar incentivos adicionales para matrículas")
                recomendaciones.append("Considerar contratación de teleoperadores adicionales")
                
        # Recomendaciones basadas en tiempo restante
        if alerta['dias_restantes'] < 15:
            recomendaciones.append(f"¡Quedan solo {alerta['dias_restantes']} días! Priorizar acciones de corto plazo")
        
        # Simulación para determinar mejor acción
        sim_conv = self.simular_escenarios(tipo="conversion", variaciones=[0.1, 0.2, 0.3])
        if sim_conv is not None and 'diferencia' in sim_conv.columns:
            mejor_sim = sim_conv.loc[sim_conv['diferencia'].idxmax()]
            recomendaciones.append(f"Enfoque prioritario: Si mejora la tasa de conversión en {mejor_sim['escenario']}, podría generar {mejor_sim['diferencia']:.0f} matrículas adicionales")
        
        return recomendaciones 