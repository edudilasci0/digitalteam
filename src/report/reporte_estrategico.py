import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import streamlit as st
from pathlib import Path
import xlsxwriter
from io import BytesIO
import base64
from matplotlib.ticker import PercentFormatter
import statsmodels.api as sm

class ReporteEstrategico:
    """
    Clase para generar reportes estratégicos diferenciados para marketing y comercial.
    Incluye proyecciones, intervalos de confianza y análisis predictivos.
    """
    
    def __init__(self, datos_leads=None, datos_matriculas=None, datos_campanas=None):
        """
        Inicializa el generador de reportes con los datos necesarios.
        
        Args:
            datos_leads (DataFrame): DataFrame con datos de leads
            datos_matriculas (DataFrame): DataFrame con datos de matrículas
            datos_campanas (DataFrame): DataFrame con datos de planificación de campañas
        """
        self.datos_leads = datos_leads
        self.datos_matriculas = datos_matriculas
        self.datos_campanas = datos_campanas
        self.fecha_generacion = datetime.now()
        
    def cargar_datos_campanas(self, archivo):
        """
        Carga datos de planificación de campañas desde un archivo
        
        Args:
            archivo: Archivo cargado (CSV o Excel)
            
        Returns:
            bool: True si la carga fue exitosa, False en caso contrario
        """
        try:
            if archivo.name.endswith('.csv'):
                self.datos_campanas = pd.read_csv(archivo)
            elif archivo.name.endswith(('.xlsx', '.xls')):
                self.datos_campanas = pd.read_excel(archivo)
            return True
        except Exception as e:
            st.error(f"Error al cargar datos de campañas: {str(e)}")
            return False
    
    def cargar_datos_manuales(self, archivo, tipo="leads"):
        """
        Carga datos de leads o matrículas manualmente desde un archivo
        
        Args:
            archivo: Archivo cargado (CSV o Excel)
            tipo (str): Tipo de datos ('leads' o 'matriculas')
            
        Returns:
            bool: True si la carga fue exitosa, False en caso contrario
        """
        try:
            if archivo.name.endswith('.csv'):
                datos = pd.read_csv(archivo)
            elif archivo.name.endswith(('.xlsx', '.xls')):
                datos = pd.read_excel(archivo)
                
            if tipo.lower() == "leads":
                self.datos_leads = datos
            elif tipo.lower() == "matriculas":
                self.datos_matriculas = datos
            return True
        except Exception as e:
            st.error(f"Error al cargar datos manuales de {tipo}: {str(e)}")
            return False
    
    def calcular_cpl_cpa_reales(self):
        """
        Calcula CPL y CPA reales basados en datos del CRM
        
        Returns:
            dict: Diccionario con CPL y CPA por origen
        """
        if self.datos_leads is None or self.datos_campanas is None:
            return None
            
        # Agrupar datos por origen
        leads_por_origen = self.datos_leads.groupby('origen').size().reset_index(name='total_leads')
        
        # Si existen datos de matrículas, calcular también por ese lado
        if self.datos_matriculas is not None:
            matriculas_por_origen = self.datos_matriculas.groupby('origen').size().reset_index(name='total_matriculas')
            # Unir con leads
            datos_unidos = leads_por_origen.merge(matriculas_por_origen, on='origen', how='left')
            datos_unidos['total_matriculas'] = datos_unidos['total_matriculas'].fillna(0)
        else:
            datos_unidos = leads_por_origen
            datos_unidos['total_matriculas'] = 0
            
        # Obtener costos por origen desde datos de campañas
        if 'origen' in self.datos_campanas.columns and 'costo_ejecutado' in self.datos_campanas.columns:
            costos_por_origen = self.datos_campanas.groupby('origen')['costo_ejecutado'].sum().reset_index()
            
            # Unir con datos anteriores
            datos_completos = datos_unidos.merge(costos_por_origen, on='origen', how='left')
            datos_completos['costo_ejecutado'] = datos_completos['costo_ejecutado'].fillna(0)
            
            # Calcular CPL y CPA
            datos_completos['cpl_real'] = datos_completos['costo_ejecutado'] / datos_completos['total_leads']
            datos_completos['cpa_real'] = datos_completos.apply(
                lambda x: x['costo_ejecutado'] / x['total_matriculas'] if x['total_matriculas'] > 0 else float('inf'), 
                axis=1
            )
            
            return datos_completos
        
        return None
    
    def calcular_proyeccion_leads(self, nivel_confianza=0.95):
        """
        Calcula proyección de leads totales con intervalos de confianza
        
        Args:
            nivel_confianza (float): Nivel de confianza para el intervalo (0-1)
            
        Returns:
            dict: Diccionario con proyección e intervalos
        """
        if self.datos_leads is None or self.datos_campanas is None:
            return None
            
        try:
            # Obtener fechas de inicio y fin de campaña
            fecha_inicio = pd.to_datetime(self.datos_campanas['fecha_inicio'].min())
            fecha_fin = pd.to_datetime(self.datos_campanas['fecha_fin'].max())
            
            # Convertir columna de fecha en datos_leads
            fecha_col = [col for col in self.datos_leads.columns if 'fecha' in col.lower()][0]
            self.datos_leads[fecha_col] = pd.to_datetime(self.datos_leads[fecha_col])
            
            # Determinar el avance actual (porcentaje de tiempo transcurrido)
            hoy = datetime.now()
            duracion_total = (fecha_fin - fecha_inicio).days
            dias_transcurridos = (hoy - fecha_inicio).days
            
            if duracion_total <= 0 or dias_transcurridos < 0:
                return None
                
            porcentaje_avance = min(100, (dias_transcurridos / duracion_total) * 100)
            
            # Contar leads actuales
            leads_actuales = len(self.datos_leads)
            
            # Proyección simple basada en porcentaje de avance
            leads_proyectados = leads_actuales / (porcentaje_avance / 100)
            
            # Calcular intervalo de confianza (usando aprox. normal)
            # Asumimos que el error estándar disminuye a medida que avanza la campaña
            z_value = {
                0.90: 1.645,
                0.95: 1.96,
                0.99: 2.576
            }.get(nivel_confianza, 1.96)
            
            # Simular error estándar como función del avance
            error_std = leads_proyectados * (1 - porcentaje_avance/100)
            
            # Intervalo de confianza
            limite_inferior = max(0, leads_proyectados - z_value * error_std)
            limite_superior = leads_proyectados + z_value * error_std
            
            return {
                'avance_actual': porcentaje_avance,
                'leads_actuales': leads_actuales,
                'leads_proyectados': leads_proyectados,
                'limite_inferior': limite_inferior,
                'limite_superior': limite_superior,
                'nivel_confianza': nivel_confianza * 100
            }
            
        except Exception as e:
            st.error(f"Error en proyección de leads: {str(e)}")
            return None
    
    def calcular_proyeccion_matriculas(self, nivel_confianza=0.95):
        """
        Calcula proyección de matrículas con intervalos de confianza
        
        Args:
            nivel_confianza (float): Nivel de confianza para el intervalo (0-1)
            
        Returns:
            dict: Diccionario con proyección e intervalos
        """
        if self.datos_leads is None or self.datos_matriculas is None:
            return None
            
        try:
            # Proyección de leads
            proy_leads = self.calcular_proyeccion_leads(nivel_confianza)
            if proy_leads is None:
                return None
                
            # Calcular tasa de conversión actual
            matriculas_actuales = len(self.datos_matriculas)
            leads_actuales = proy_leads['leads_actuales']
            
            if leads_actuales <= 0:
                return None
                
            tasa_conversion = matriculas_actuales / leads_actuales
            
            # Proyectar matrículas
            matriculas_proyectadas = proy_leads['leads_proyectados'] * tasa_conversion
            
            # Intervalo de confianza para matrículas
            # Combinamos la incertidumbre en leads y en tasa de conversión
            z_value = {
                0.90: 1.645,
                0.95: 1.96,
                0.99: 2.576
            }.get(nivel_confianza, 1.96)
            
            # Error estándar para la proyección de matrículas (más conservador)
            error_std = matriculas_proyectadas * (1.2 - proy_leads['avance_actual']/100)
            
            # Intervalo de confianza
            limite_inferior = max(0, matriculas_proyectadas - z_value * error_std)
            limite_superior = matriculas_proyectadas + z_value * error_std
            
            return {
                'avance_actual': proy_leads['avance_actual'],
                'matriculas_actuales': matriculas_actuales,
                'matriculas_proyectadas': matriculas_proyectadas,
                'limite_inferior': limite_inferior,
                'limite_superior': limite_superior,
                'tasa_conversion': tasa_conversion,
                'nivel_confianza': nivel_confianza * 100
            }
            
        except Exception as e:
            st.error(f"Error en proyección de matrículas: {str(e)}")
            return None
    
    def simular_escenarios(self, tipo="conversion", variaciones=None):
        """
        Simula escenarios alternativos
        
        Args:
            tipo (str): Tipo de simulación ('conversion' o 'inversion')
            variaciones (list): Lista de variaciones a simular
            
        Returns:
            DataFrame: Resultados de simulación
        """
        if tipo == "conversion":
            # Simulación de mejora en tasas de conversión
            if variaciones is None:
                variaciones = [0.05, 0.1, 0.15, 0.2]  # 5%, 10%, 15%, 20%
            
            # Obtener proyección actual
            proy_actual = self.calcular_proyeccion_matriculas()
            if proy_actual is None:
                return None
            
            # Simular escenarios
            resultados = []
            for var in variaciones:
                nueva_tasa = proy_actual['tasa_conversion'] * (1 + var)
                nuevas_matriculas = proy_actual['leads_proyectados'] * nueva_tasa
                
                # Calcular diferencia
                diferencia = nuevas_matriculas - proy_actual['matriculas_proyectadas']
                
                resultados.append({
                    'escenario': f"+{var*100:.0f}% conversión",
                    'tasa_conversion': nueva_tasa,
                    'matriculas_proyectadas': nuevas_matriculas,
                    'diferencia': diferencia,
                    'diferencia_porcentual': (diferencia / proy_actual['matriculas_proyectadas']) * 100
                })
            
            return pd.DataFrame(resultados)
            
        elif tipo == "inversion":
            # Simulación de cambios en la inversión
            if variaciones is None:
                variaciones = [-0.2, -0.1, 0.1, 0.2]  # -20%, -10%, +10%, +20%
                
            # Proyección actual
            proy_leads = self.calcular_proyeccion_leads()
            proy_matriculas = self.calcular_proyeccion_matriculas()
            
            if proy_leads is None or proy_matriculas is None:
                return None
                
            # Calcular elasticidad (simulada, en un caso real vendría de un modelo)
            elasticidad = 0.8  # Ejemplo: si aumentamos inversión 10%, leads aumentan 8%
            
            # Simular escenarios
            resultados = []
            for var in variaciones:
                nuevos_leads = proy_leads['leads_proyectados'] * (1 + (elasticidad * var))
                nuevas_matriculas = nuevos_leads * proy_matriculas['tasa_conversion']
                
                # Calcular diferencia
                diferencia = nuevas_matriculas - proy_matriculas['matriculas_proyectadas']
                
                resultados.append({
                    'escenario': f"{var*100:+.0f}% inversión",
                    'leads_proyectados': nuevos_leads,
                    'matriculas_proyectadas': nuevas_matriculas,
                    'diferencia': diferencia,
                    'diferencia_porcentual': (diferencia / proy_matriculas['matriculas_proyectadas']) * 100
                })
            
            return pd.DataFrame(resultados)
            
        return None
    
    def export_report_marketing(self, formato="xlsx"):
        """
        Genera y exporta el reporte estratégico para marketing
        
        Args:
            formato (str): Formato de salida ('xlsx' o 'csv')
            
        Returns:
            BytesIO: Buffer con el reporte generado
        """
        # Verificar que tenemos los datos necesarios
        if self.datos_leads is None or self.datos_matriculas is None or self.datos_campanas is None:
            st.error("No hay datos suficientes para generar el reporte de marketing")
            return None
        
        # Crear buffer para el archivo
        output = BytesIO()
        
        if formato == "xlsx":
            # Crear Excel Writer
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # 1. Hoja de Resumen
                # Calcular métricas clave
                cpl_cpa = self.calcular_cpl_cpa_reales()
                proy_leads = self.calcular_proyeccion_leads()
                proy_matriculas = self.calcular_proyeccion_matriculas()
                
                # Crear DataFrame de resumen
                resumen_data = {
                    'Métrica': [
                        'Leads generados', 
                        'Matrículas actuales', 
                        'Tasa de conversión', 
                        'CPL promedio', 
                        'CPA promedio',
                        'Leads proyectados',
                        'Matrículas proyectadas',
                        'Avance de campaña'
                    ],
                    'Valor': [
                        len(self.datos_leads),
                        len(self.datos_matriculas),
                        f"{len(self.datos_matriculas)/len(self.datos_leads)*100:.2f}%",
                        f"${cpl_cpa['cpl_real'].mean():.2f}" if cpl_cpa is not None else 'N/A',
                        f"${cpl_cpa['cpa_real'].replace([np.inf, -np.inf], np.nan).mean():.2f}" if cpl_cpa is not None else 'N/A',
                        f"{proy_leads['leads_proyectados']:.0f} (±{(proy_leads['limite_superior']-proy_leads['limite_inferior'])/2:.0f})" if proy_leads else 'N/A',
                        f"{proy_matriculas['matriculas_proyectadas']:.0f} (±{(proy_matriculas['limite_superior']-proy_matriculas['limite_inferior'])/2:.0f})" if proy_matriculas else 'N/A',
                        f"{proy_leads['avance_actual']:.1f}%" if proy_leads else 'N/A'
                    ]
                }
                
                df_resumen = pd.DataFrame(resumen_data)
                df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
                
                # 2. Hoja de Datos por Canal
                if cpl_cpa is not None:
                    cpl_cpa.to_excel(writer, sheet_name='Métricas por Canal', index=False)
                
                # 3. Hoja de Proyecciones
                if proy_leads is not None and proy_matriculas is not None:
                    # Combinar proyecciones en un solo DataFrame
                    df_proy = pd.DataFrame({
                        'Métrica': ['Leads', 'Matrículas'],
                        'Valor Actual': [proy_leads['leads_actuales'], proy_matriculas['matriculas_actuales']],
                        'Proyección': [proy_leads['leads_proyectados'], proy_matriculas['matriculas_proyectadas']],
                        'Límite Inferior': [proy_leads['limite_inferior'], proy_matriculas['limite_inferior']],
                        'Límite Superior': [proy_leads['limite_superior'], proy_matriculas['limite_superior']]
                    })
                    
                    df_proy.to_excel(writer, sheet_name='Proyecciones', index=False)
                
                # 4. Hojas de Simulaciones
                # Simulación de mejora en conversión
                sim_conv = self.simular_escenarios(tipo="conversion")
                if sim_conv is not None:
                    sim_conv.to_excel(writer, sheet_name='Simulación Conversión', index=False)
                
                # Simulación de cambios en inversión
                sim_inv = self.simular_escenarios(tipo="inversion")
                if sim_inv is not None:
                    sim_inv.to_excel(writer, sheet_name='Simulación Inversión', index=False)
                
                # 5. Hoja de Recomendaciones
                # Generamos recomendaciones basadas en los análisis
                recomendaciones = []
                
                if cpl_cpa is not None:
                    # Identificar canal con mejor CPL
                    mejor_canal_cpl = cpl_cpa.loc[cpl_cpa['cpl_real'].idxmin()]
                    recomendaciones.append(f"El canal con mejor CPL es {mejor_canal_cpl['origen']} (${mejor_canal_cpl['cpl_real']:.2f}).")
                    
                    # Identificar canal con mejor CPA
                    cpa_filtrado = cpl_cpa[cpl_cpa['cpa_real'] < float('inf')]
                    if not cpa_filtrado.empty:
                        mejor_canal_cpa = cpa_filtrado.loc[cpa_filtrado['cpa_real'].idxmin()]
                        recomendaciones.append(f"El canal con mejor CPA es {mejor_canal_cpa['origen']} (${mejor_canal_cpa['cpa_real']:.2f}).")
                
                if proy_matriculas is not None:
                    # Verificar si estamos en camino de cumplir objetivo
                    objetivo_matriculas = self.datos_campanas['objetivo_leads'].sum() * 0.1  # Asumimos 10% conversión objetivo
                    
                    if proy_matriculas['matriculas_proyectadas'] < objetivo_matriculas * 0.9:
                        recomendaciones.append(f"ALERTA: La proyección actual ({proy_matriculas['matriculas_proyectadas']:.0f}) está por debajo del objetivo ({objetivo_matriculas:.0f}).")
                        
                        # Recomendar acciones según simulaciones
                        if sim_conv is not None:
                            mejor_sim = sim_conv.iloc[-1]  # La última es la mayor mejora
                            recomendaciones.append(f"Una mejora de {mejor_sim['escenario']} generaría {mejor_sim['diferencia']:.0f} matrículas adicionales.")
                        
                        if sim_inv is not None:
                            mejor_sim = sim_inv.iloc[-1]  # La última es la mayor mejora
                            recomendaciones.append(f"Un incremento de {mejor_sim['escenario']} generaría {mejor_sim['diferencia']:.0f} matrículas adicionales.")
                    else:
                        recomendaciones.append(f"La campaña va en buen camino para alcanzar el objetivo de {objetivo_matriculas:.0f} matrículas.")
                
                # Crear DataFrame de recomendaciones
                df_recom = pd.DataFrame({
                    'Recomendación': recomendaciones
                })
                
                df_recom.to_excel(writer, sheet_name='Recomendaciones', index=False)
                
                # Dar formato a las hojas
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    # Ajustar ancho de columnas
                    for i, col in enumerate(writer.sheets[sheet_name].df_dtypes.index):
                        max_width = max(
                            writer.sheets[sheet_name].df_dtypes.iloc[:, i].astype(str).map(len).max(),
                            len(col)
                        )
                        worksheet.set_column(i, i, max_width + 2)
        
        elif formato == "csv":
            # Crear un CSV con la información principal
            # Esto es simplificado, idealmente se crearían múltiples CSVs
            cpl_cpa = self.calcular_cpl_cpa_reales()
            if cpl_cpa is not None:
                cpl_cpa.to_csv(output, index=False)
        
        # Regresar al inicio del buffer
        output.seek(0)
        return output
    
    def export_report_comercial(self, formato="xlsx"):
        """
        Genera y exporta el reporte de status comercial
        
        Args:
            formato (str): Formato de salida ('xlsx' o 'pdf')
            
        Returns:
            BytesIO: Buffer con el reporte generado
        """
        # Verificar que tenemos los datos necesarios
        if self.datos_leads is None or self.datos_matriculas is None or self.datos_campanas is None:
            st.error("No hay datos suficientes para generar el reporte comercial")
            return None
        
        # Crear buffer para el archivo
        output = BytesIO()
        
        if formato == "xlsx":
            # Crear Excel Writer
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # 1. Datos de avance de campaña
                proy_leads = self.calcular_proyeccion_leads()
                proy_matriculas = self.calcular_proyeccion_matriculas()
                
                if proy_leads is None or proy_matriculas is None:
                    st.error("No se pueden calcular proyecciones para el reporte comercial")
                    return None
                
                # Calcular métricas de avance
                tiempo_transcurrido = proy_leads['avance_actual']
                leads_generados_pct = (proy_leads['leads_actuales'] / proy_leads['leads_proyectados']) * 100
                matriculas_pct = (proy_matriculas['matriculas_actuales'] / proy_matriculas['matriculas_proyectadas']) * 100
                
                # Crear DataFrame de avance
                avance_data = {
                    'Métrica': ['Tiempo transcurrido', 'Leads generados', 'Matrículas'],
                    'Porcentaje': [tiempo_transcurrido, leads_generados_pct, matriculas_pct],
                    'Valor Actual': [f"{tiempo_transcurrido:.1f}%", 
                                    f"{proy_leads['leads_actuales']:.0f}", 
                                    f"{proy_matriculas['matriculas_actuales']:.0f}"],
                    'Valor Objetivo': [f"100%", 
                                      f"{proy_leads['leads_proyectados']:.0f}", 
                                      f"{proy_matriculas['matriculas_proyectadas']:.0f}"]
                }
                
                df_avance = pd.DataFrame(avance_data)
                df_avance.to_excel(writer, sheet_name='Estado Campaña', index=False)
                
                # 2. Hoja de predicciones
                prediccion_data = {
                    'Métrica': ['Matrículas actuales', 'Predicción matrícula final', 'Límite inferior', 'Límite superior'],
                    'Valor': [f"{proy_matriculas['matriculas_actuales']:.0f}",
                             f"{proy_matriculas['matriculas_proyectadas']:.0f}",
                             f"{proy_matriculas['limite_inferior']:.0f}",
                             f"{proy_matriculas['limite_superior']:.0f}"]
                }
                
                df_prediccion = pd.DataFrame(prediccion_data)
                df_prediccion.to_excel(writer, sheet_name='Predicción Final', index=False)
                
                # 3. Hoja de acciones sugeridas
                # Simulaciones
                sim_conv = self.simular_escenarios(tipo="conversion", variaciones=[0.1, 0.2, 0.3])
                if sim_conv is not None:
                    sim_conv['escenario'] = sim_conv['escenario'].str.replace("conversión", "mejora tasa contacto")
                    sim_conv.to_excel(writer, sheet_name='Acciones Sugeridas', index=False)
                
                # 4. Generar una hoja con el semáforo de riesgo
                # Calcular semáforo basado en métricas
                objetivo_matriculas = self.datos_campanas['objetivo_leads'].sum() * 0.1  # Asumimos 10% conversión objetivo
                proporcion_objetivo = proy_matriculas['matriculas_proyectadas'] / objetivo_matriculas
                
                if proporcion_objetivo >= 0.9:
                    estado = "VERDE - En camino"
                    recomendacion = "Mantener estrategia actual"
                elif proporcion_objetivo >= 0.7:
                    estado = "AMARILLO - Alerta"
                    recomendacion = "Aumentar eficacia de contactación y seguimiento"
                else:
                    estado = "ROJO - Riesgo alto"
                    recomendacion = "Revisar urgentemente estrategia comercial y considerar aumento de leads"
                
                semaforo_data = {
                    'Estado': [estado],
                    'Matrículas proyectadas': [f"{proy_matriculas['matriculas_proyectadas']:.0f}"],
                    'Objetivo': [f"{objetivo_matriculas:.0f}"],
                    'Cumplimiento proyectado': [f"{proporcion_objetivo*100:.1f}%"],
                    'Recomendación principal': [recomendacion]
                }
                
                df_semaforo = pd.DataFrame(semaforo_data)
                df_semaforo.to_excel(writer, sheet_name='Semáforo de Riesgo', index=False)
                
                # 5. Hoja de observaciones quincenales (simulada)
                observaciones = [
                    f"Periodo: {self.fecha_generacion.strftime('%d/%m/%Y')}",
                    f"Avance actual: {tiempo_transcurrido:.1f}% del tiempo",
                    f"Leads generados: {proy_leads['leads_actuales']:.0f} ({leads_generados_pct:.1f}% del proyectado)",
                    f"Matrículas: {proy_matriculas['matriculas_actuales']:.0f} ({matriculas_pct:.1f}% del proyectado)",
                    f"Estado: {estado}",
                    f"Recomendación: {recomendacion}"
                ]
                
                df_obs = pd.DataFrame({'Observaciones': observaciones})
                df_obs.to_excel(writer, sheet_name='Observaciones', index=False)
                
                # Dar formato a las hojas
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    # Ajustar ancho de columnas
                    for i, col in enumerate(writer.sheets[sheet_name].df_dtypes.index):
                        max_width = max(
                            writer.sheets[sheet_name].df_dtypes.iloc[:, i].astype(str).map(len).max(),
                            len(col)
                        )
                        worksheet.set_column(i, i, max_width + 2)
                        
                    # Formato especial para la hoja de estado
                    if sheet_name == 'Estado Campaña':
                        # Formato para las barras de progreso
                        progress_format = workbook.add_format({'bg_color': '#4CAF50', 'border': 1})
                        empty_format = workbook.add_format({'bg_color': '#E0E0E0', 'border': 1})
                        
                        # Agregar barras de progreso visuales
                        worksheet.write(8, 0, "Barras de progreso visual:")
                        
                        # Para cada métrica, crear una barra de progreso
                        for i, row in enumerate(df_avance.itertuples()):
                            # Posición de la barra
                            row_pos = 10 + i*2
                            
                            # Etiqueta
                            worksheet.write(row_pos, 0, row.Métrica)
                            
                            # Barra de progreso (20 celdas de ancho)
                            progress_cells = int(row.Porcentaje / 5)  # Cada celda representa 5%
                            progress_cells = min(20, max(0, progress_cells))
                            
                            # Dibujar celdas llenas
                            for j in range(progress_cells):
                                worksheet.write(row_pos, j+1, "", progress_format)
                            
                            # Dibujar celdas vacías
                            for j in range(progress_cells, 20):
                                worksheet.write(row_pos, j+1, "", empty_format)
                            
                            # Porcentaje al final
                            worksheet.write(row_pos, 21, f"{row.Porcentaje:.1f}%")
        
        elif formato == "pdf":
            # Implementación simplificada para PDF (en la práctica, se necesitaría una biblioteca como ReportLab)
            # Por ahora, generamos un HTML que se podría convertir a PDF
            html_content = """
            <html>
            <head>
                <title>Reporte de Status Comercial</title>
                <style>
                    body { font-family: Arial, sans-serif; }
                    .progress-container { width: 100%; background-color: #e0e0e0; margin: 10px 0; }
                    .progress-bar { height: 20px; background-color: #4CAF50; text-align: center; color: white; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    .semaforo { font-weight: bold; padding: 5px; border-radius: 5px; }
                    .verde { background-color: #4CAF50; color: white; }
                    .amarillo { background-color: #FFEB3B; }
                    .rojo { background-color: #F44336; color: white; }
                </style>
            </head>
            <body>
            """
            
            # Obtener datos
            proy_leads = self.calcular_proyeccion_leads()
            proy_matriculas = self.calcular_proyeccion_matriculas()
            
            if proy_leads is None or proy_matriculas is None:
                st.error("No se pueden calcular proyecciones para el reporte comercial")
                return None
                
            # Calcular métricas de avance
            tiempo_transcurrido = proy_leads['avance_actual']
            leads_generados_pct = (proy_leads['leads_actuales'] / proy_leads['leads_proyectados']) * 100
            matriculas_pct = (proy_matriculas['matriculas_actuales'] / proy_matriculas['matriculas_proyectadas']) * 100
            
            # Título y fecha
            html_content += f"""
            <h1>Reporte de Status Comercial</h1>
            <p>Generado el {self.fecha_generacion.strftime('%d/%m/%Y')}</p>
            <hr>
            
            <h2>Estado de Avance</h2>
            
            <div>
                <h3>Tiempo transcurrido</h3>
                <div class="progress-container">
                    <div class="progress-bar" style="width:{tiempo_transcurrido}%">{tiempo_transcurrido:.1f}%</div>
                </div>
                
                <h3>Leads generados</h3>
                <div class="progress-container">
                    <div class="progress-bar" style="width:{leads_generados_pct}%">{leads_generados_pct:.1f}%</div>
                </div>
                
                <h3>Matrículas</h3>
                <div class="progress-container">
                    <div class="progress-bar" style="width:{matriculas_pct}%">{matriculas_pct:.1f}%</div>
                </div>
            </div>
            
            <h2>Predicción de Matrícula Final</h2>
            <table>
                <tr>
                    <th>Métrica</th>
                    <th>Valor</th>
                </tr>
                <tr>
                    <td>Matrículas actuales</td>
                    <td>{proy_matriculas['matriculas_actuales']:.0f}</td>
                </tr>
                <tr>
                    <td>Predicción matrícula final</td>
                    <td>{proy_matriculas['matriculas_proyectadas']:.0f}</td>
                </tr>
                <tr>
                    <td>Intervalo de confianza ({proy_matriculas['nivel_confianza']}%)</td>
                    <td>{proy_matriculas['limite_inferior']:.0f} - {proy_matriculas['limite_superior']:.0f}</td>
                </tr>
            </table>
            """
            
            # Calcular semáforo basado en métricas
            objetivo_matriculas = self.datos_campanas['objetivo_leads'].sum() * 0.1  # Asumimos 10% conversión objetivo
            proporcion_objetivo = proy_matriculas['matriculas_proyectadas'] / objetivo_matriculas
            
            if proporcion_objetivo >= 0.9:
                estado = "VERDE - En camino"
                clase_semaforo = "verde"
                recomendacion = "Mantener estrategia actual"
            elif proporcion_objetivo >= 0.7:
                estado = "AMARILLO - Alerta"
                clase_semaforo = "amarillo"
                recomendacion = "Aumentar eficacia de contactación y seguimiento"
            else:
                estado = "ROJO - Riesgo alto"
                clase_semaforo = "rojo"
                recomendacion = "Revisar urgentemente estrategia comercial y considerar aumento de leads"
            
            html_content += f"""
            <h2>Semáforo de Riesgo</h2>
            <div>
                <span class="semaforo {clase_semaforo}">{estado}</span>
                <p>Proyección actual: {proy_matriculas['matriculas_proyectadas']:.0f} matrículas</p>
                <p>Objetivo: {objetivo_matriculas:.0f} matrículas</p>
                <p>Cumplimiento proyectado: {proporcion_objetivo*100:.1f}%</p>
                <p><strong>Recomendación principal:</strong> {recomendacion}</p>
            </div>
            """
            
            # Simulaciones
            sim_conv = self.simular_escenarios(tipo="conversion", variaciones=[0.1, 0.2, 0.3])
            if sim_conv is not None:
                html_content += """
                <h2>Simulación de Mejoras</h2>
                <table>
                    <tr>
                        <th>Escenario</th>
                        <th>Matrículas proyectadas</th>
                        <th>Diferencia</th>
                    </tr>
                """
                
                for _, row in sim_conv.iterrows():
                    html_content += f"""
                    <tr>
                        <td>{row['escenario'].replace('conversión', 'mejora tasa contacto')}</td>
                        <td>{row['matriculas_proyectadas']:.0f}</td>
                        <td>+{row['diferencia']:.0f}</td>
                    </tr>
                    """
                
                html_content += "</table>"
            
            # Cerrar HTML
            html_content += """
            </body>
            </html>
            """
            
            # Guardar HTML en el buffer (en la práctica, se convertiría a PDF)
            output.write(html_content.encode('utf-8'))
        
        # Regresar al inicio del buffer
        output.seek(0)
        return output 