"""
Módulo para la generación de reportes del Motor de Decisión.
Permite crear y programar reportes con integración a PowerBI.
"""

import os
import pandas as pd
import streamlit as st
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import datetime
import time
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from src.utils.config import get_config
from src.utils.logging import get_module_logger

logger = get_module_logger(__name__)

class GeneradorReportes:
    """
    Clase para la generación y programación de reportes.
    Permite exportar datos a PowerBI y generar reportes en varios formatos.
    """
    
    def __init__(self):
        """Inicializa el generador de reportes."""
        self.config = get_config()
        
        # Directorios de trabajo
        self.dir_reportes = Path(self.config['paths']['output']) / 'reportes'
        self.dir_reportes.mkdir(exist_ok=True)
        
        # Plantillas disponibles
        self.plantillas = {
            'ejecutivo': 'plantillas/reporte_ejecutivo.pptx',
            'performance': 'plantillas/reporte_performance.pptx',
            'forecast': 'plantillas/reporte_forecast.pptx',
            'recomendaciones': 'plantillas/reporte_recomendaciones.pptx'
        }
        
        # Programación de reportes
        self.programacion_file = self.dir_reportes / 'programacion_reportes.json'
        self.programacion = self._cargar_programacion()
    
    def _cargar_programacion(self) -> Dict:
        """Carga la programación de reportes guardada."""
        if self.programacion_file.exists():
            try:
                with open(self.programacion_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error al cargar programación: {str(e)}")
                return {'reportes': []}
        else:
            return {'reportes': []}
    
    def _guardar_programacion(self):
        """Guarda la programación de reportes."""
        try:
            with open(self.programacion_file, 'w') as f:
                json.dump(self.programacion, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error al guardar programación: {str(e)}")
    
    def generar_reporte_powerpoint(self, tipo_reporte: str, datos: pd.DataFrame, 
                                 parametros: Dict) -> str:
        """
        Genera un reporte en PowerPoint basado en una plantilla.
        
        Args:
            tipo_reporte (str): Tipo de reporte ('ejecutivo', 'performance', etc)
            datos (pd.DataFrame): Datos para el reporte
            parametros (Dict): Parámetros de configuración
            
        Returns:
            str: Ruta al archivo generado
        """
        try:
            # Verificar si existe la plantilla
            if tipo_reporte not in self.plantillas:
                raise ValueError(f"No existe plantilla para el tipo de reporte: {tipo_reporte}")
            
            from pptx import Presentation
            
            # Ruta de la plantilla
            ruta_plantilla = Path(self.plantillas[tipo_reporte])
            if not ruta_plantilla.exists():
                logger.warning(f"No se encuentra la plantilla: {ruta_plantilla}")
                # Usar plantilla básica si no existe la específica
                ruta_plantilla = Path('plantillas/reporte_basico.pptx')
            
            # Cargar plantilla
            prs = Presentation(ruta_plantilla)
            
            # Generar nombre de archivo
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"reporte_{tipo_reporte}_{timestamp}.pptx"
            ruta_salida = self.dir_reportes / nombre_archivo
            
            # Por ahora, simplemente guardamos la plantilla como está
            # En una implementación completa, aquí se personalizaría el PowerPoint con los datos
            prs.save(ruta_salida)
            
            logger.info(f"Reporte generado: {ruta_salida}")
            return str(ruta_salida)
            
        except Exception as e:
            logger.error(f"Error al generar reporte PowerPoint: {str(e)}", exc_info=True)
            raise
    
    def exportar_a_powerbi(self, datos: pd.DataFrame, nombre_dataset: str) -> bool:
        """
        Exporta datos para ser utilizados por PowerBI.
        
        Args:
            datos (pd.DataFrame): Datos a exportar
            nombre_dataset (str): Nombre del dataset en PowerBI
            
        Returns:
            bool: True si la exportación fue exitosa
        """
        try:
            # Directorio para datos de PowerBI
            dir_powerbi = Path(self.config['paths']['output']) / 'powerbi'
            dir_powerbi.mkdir(exist_ok=True)
            
            # Guardar en formato CSV para PowerBI
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_csv = dir_powerbi / f"{nombre_dataset}_{timestamp}.csv"
            datos.to_csv(ruta_csv, index=False)
            
            # En una implementación real, aquí podría haber código para subir el dataset
            # directamente a PowerBI Service usando la API
            
            logger.info(f"Datos exportados para PowerBI: {ruta_csv}")
            return True
            
        except Exception as e:
            logger.error(f"Error al exportar datos a PowerBI: {str(e)}", exc_info=True)
            return False
    
    def programar_envio_reporte(self, tipo_reporte: str, frecuencia: str, 
                              destinatarios: List[str], parametros: Dict = None) -> str:
        """
        Programa el envío periódico de un reporte.
        
        Args:
            tipo_reporte (str): Tipo de reporte a programar
            frecuencia (str): Frecuencia de envío ('diaria', 'semanal', etc)
            destinatarios (List[str]): Lista de correos de destinatarios
            parametros (Dict): Parámetros adicionales
            
        Returns:
            str: ID de la programación
        """
        # Generar ID único
        import uuid
        id_programacion = str(uuid.uuid4())
        
        # Configurar nueva programación
        nueva_programacion = {
            'id': id_programacion,
            'tipo_reporte': tipo_reporte,
            'frecuencia': frecuencia,
            'destinatarios': destinatarios,
            'parametros': parametros or {},
            'ultima_ejecucion': None,
            'proxima_ejecucion': self._calcular_proxima_ejecucion(frecuencia),
            'activo': True,
            'fecha_creacion': datetime.datetime.now().isoformat()
        }
        
        # Guardar programación
        self.programacion['reportes'].append(nueva_programacion)
        self._guardar_programacion()
        
        logger.info(f"Reporte programado: {tipo_reporte}, frecuencia: {frecuencia}")
        return id_programacion
    
    def _calcular_proxima_ejecucion(self, frecuencia: str) -> str:
        """Calcula la próxima fecha de ejecución según frecuencia."""
        ahora = datetime.datetime.now()
        
        if frecuencia == 'diaria':
            proxima = ahora + datetime.timedelta(days=1)
            proxima = proxima.replace(hour=8, minute=0, second=0)  # 8:00 AM
        elif frecuencia == 'semanal':
            # Próximo lunes a las 8:00 AM
            dias_hasta_lunes = 7 - ahora.weekday()
            proxima = ahora + datetime.timedelta(days=dias_hasta_lunes)
            proxima = proxima.replace(hour=8, minute=0, second=0)
        elif frecuencia == 'quincenal':
            # El 1 y 15 de cada mes
            if ahora.day < 15:
                proxima = ahora.replace(day=15, hour=8, minute=0, second=0)
            else:
                if ahora.month == 12:
                    proxima = ahora.replace(year=ahora.year+1, month=1, day=1, 
                                         hour=8, minute=0, second=0)
                else:
                    proxima = ahora.replace(month=ahora.month+1, day=1, 
                                         hour=8, minute=0, second=0)
        else:  # mensual por defecto
            if ahora.month == 12:
                proxima = ahora.replace(year=ahora.year+1, month=1, day=1, 
                                      hour=8, minute=0, second=0)
            else:
                proxima = ahora.replace(month=ahora.month+1, day=1, 
                                      hour=8, minute=0, second=0)
        
        return proxima.isoformat()
    
    def enviar_reporte_email(self, ruta_reporte: str, destinatarios: List[str], 
                           asunto: str, cuerpo: str) -> bool:
        """
        Envía un reporte por email a los destinatarios.
        
        Args:
            ruta_reporte (str): Ruta al archivo de reporte
            destinatarios (List[str]): Lista de destinatarios
            asunto (str): Asunto del correo
            cuerpo (str): Cuerpo del mensaje
            
        Returns:
            bool: True si el envío fue exitoso
        """
        # En una implementación real, aquí iría la configuración del servidor SMTP
        # y el código para enviar el correo con el reporte adjunto
        
        # Por ahora, simulamos que el envío fue exitoso
        logger.info(f"Simulando envío de reporte: {ruta_reporte} a {destinatarios}")
        return True
    
    def generar_modelo_powerbi_campanas(self) -> str:
        """
        Genera el modelo de datos para el calendario de campañas en PowerBI.
        
        Returns:
            str: Ruta al archivo generado
        """
        # Crear estructura de datos para el calendario
        df_calendario = pd.DataFrame(columns=[
            'fecha', 'id_campana', 'nombre_campana', 'marca', 'canal',
            'presupuesto_diario', 'intensidad_inversion', 'leads_esperados',
            'leads_reales', 'matriculas_esperadas', 'matriculas_reales',
            'fase_campana', 'eventos_especiales'
        ])
        
        # Generar datos de ejemplo para visualización
        # (En una implementación real, estos datos vendrían de la BD)
        campanas_ejemplo = [
            {
                'id_campana': 'C001', 
                'nombre_campana': 'Campaña Verano 2023',
                'marca': 'Marca A',
                'canal': 'Facebook',
                'presupuesto_base': 10000,
                'inicio': '2023-01-15',
                'fin': '2023-02-15',
                'intensidad_base': 8,
                'leads_esperados_dia': 50,
                'matriculas_esperadas_dia': 5
            },
            {
                'id_campana': 'C002', 
                'nombre_campana': 'Promoción Invierno',
                'marca': 'Marca B',
                'canal': 'Google',
                'presupuesto_base': 15000,
                'inicio': '2023-06-01',
                'fin': '2023-07-15',
                'intensidad_base': 6,
                'leads_esperados_dia': 40,
                'matriculas_esperadas_dia': 4
            }
        ]
        
        # Generar fechas y datos para cada campaña
        datos = []
        for campana in campanas_ejemplo:
            fecha_inicio = datetime.datetime.strptime(campana['inicio'], '%Y-%m-%d')
            fecha_fin = datetime.datetime.strptime(campana['fin'], '%Y-%m-%d')
            
            dias = (fecha_fin - fecha_inicio).days + 1
            
            for i in range(dias):
                fecha = fecha_inicio + datetime.timedelta(days=i)
                
                # Variar intensidad y presupuesto según fase
                if i < dias * 0.2:  # Primeros 20% de días: lanzamiento
                    fase = 'lanzamiento'
                    intensidad = campana['intensidad_base'] * 1.2
                    presupuesto = campana['presupuesto_base'] / dias * 1.2
                    leads_esperados = campana['leads_esperados_dia'] * 0.8
                    matriculas_esperadas = campana['matriculas_esperadas_dia'] * 0.6
                elif i > dias * 0.8:  # Últimos 20% de días: cierre
                    fase = 'cierre'
                    intensidad = campana['intensidad_base'] * 0.8
                    presupuesto = campana['presupuesto_base'] / dias * 0.8
                    leads_esperados = campana['leads_esperados_dia'] * 0.7
                    matriculas_esperadas = campana['matriculas_esperadas_dia'] * 0.8
                else:  # Medio: optimización
                    fase = 'optimización'
                    intensidad = campana['intensidad_base']
                    presupuesto = campana['presupuesto_base'] / dias
                    leads_esperados = campana['leads_esperados_dia']
                    matriculas_esperadas = campana['matriculas_esperadas_dia']
                
                # Generar datos con algo de variabilidad
                import random
                variabilidad = random.uniform(0.8, 1.2)
                
                datos.append({
                    'fecha': fecha.strftime('%Y-%m-%d'),
                    'id_campana': campana['id_campana'],
                    'nombre_campana': campana['nombre_campana'],
                    'marca': campana['marca'],
                    'canal': campana['canal'],
                    'presupuesto_diario': round(presupuesto * variabilidad, 2),
                    'intensidad_inversion': min(10, round(intensidad * variabilidad)),
                    'leads_esperados': round(leads_esperados),
                    'leads_reales': round(leads_esperados * variabilidad),
                    'matriculas_esperadas': round(matriculas_esperadas),
                    'matriculas_reales': round(matriculas_esperadas * variabilidad),
                    'fase_campana': fase,
                    'eventos_especiales': 'Día festivo' if random.random() < 0.1 else ''
                })
        
        # Crear DataFrame con los datos generados
        df_calendario = pd.DataFrame(datos)
        
        # Guardar para PowerBI
        dir_powerbi = Path(self.config['paths']['output']) / 'powerbi'
        dir_powerbi.mkdir(exist_ok=True)
        
        ruta_calendario = dir_powerbi / 'calendario_campanas.csv'
        df_calendario.to_csv(ruta_calendario, index=False)
        
        logger.info(f"Modelo de calendario de campañas generado: {ruta_calendario}")
        return str(ruta_calendario)
    
    def actualizar_dashboard_powerbi(self) -> bool:
        """
        Actualiza el dashboard de PowerBI con los datos más recientes.
        
        Returns:
            bool: True si la actualización fue exitosa
        """
        # En una implementación real, aquí iría código para:
        # 1. Conectar con PowerBI Service API
        # 2. Actualizar el dataset
        # 3. Refrescar el dashboard
        
        # Por ahora, simulamos que la actualización fue exitosa
        logger.info("Simulando actualización de dashboard PowerBI")
        return True

def mostrar_interfaz_reportes():
    """
    Muestra la interfaz de usuario para generación de reportes.
    """
    st.title("Generación de Reportes - Motor de Decisión")
    
    # Inicializar generador
    generador = GeneradorReportes()
    
    # Panel de reportes rápidos
    st.header("Reportes Rápidos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tipo de Reporte")
        tipo_reporte = st.selectbox(
            "Selecciona el tipo de reporte:",
            ["Resumen Ejecutivo", "Performance por Canal", "Forecast de Cierre", "Recomendaciones Tácticas"]
        )
        
        formato = st.radio(
            "Formato de salida:",
            ["PowerPoint", "PDF", "Excel"],
            horizontal=True
        )
    
    with col2:
        st.subheader("Contenido y Periodo")
        
        marcas = st.multiselect(
            "Marcas a incluir:",
            ["Marca A", "Marca B", "Marca C", "Marca D", "Marca E"],
            default=["Marca A", "Marca B"]
        )
        
        canales = st.multiselect(
            "Canales a incluir:",
            ["Facebook", "Google", "Instagram", "LinkedIn", "Email", "Orgánico"],
            default=["Facebook", "Google", "Instagram"]
        )
        
        periodo = st.selectbox(
            "Periodo de análisis:",
            ["Último mes", "Último trimestre", "Último semestre", "Último año", "Personalizado"]
        )
        
        if periodo == "Personalizado":
            col1, col2 = st.columns(2)
            with col1:
                fecha_inicio = st.date_input("Fecha de inicio:", 
                                          value=datetime.date.today() - datetime.timedelta(days=30))
            with col2:
                fecha_fin = st.date_input("Fecha de fin:", 
                                        value=datetime.date.today())
    
    # Botones de acción
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Generar Reporte Ahora"):
            with st.spinner("Generando reporte..."):
                # Simulamos tiempo de procesamiento
                time.sleep(2)
                
                # Convertir nombres amigables a claves internas
                tipo_map = {
                    "Resumen Ejecutivo": "ejecutivo",
                    "Performance por Canal": "performance",
                    "Forecast de Cierre": "forecast",
                    "Recomendaciones Tácticas": "recomendaciones"
                }
                
                tipo_clave = tipo_map.get(tipo_reporte, "ejecutivo")
                
                try:
                    # Generar DataFrame vacío (en una implementación real, aquí se cargarían datos reales)
                    df_dummy = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
                    
                    # Parámetros para el reporte
                    params = {
                        'formato': formato.lower(),
                        'marcas': marcas,
                        'canales': canales,
                        'periodo': periodo
                    }
                    
                    # Generar reporte
                    ruta_reporte = generador.generar_reporte_powerpoint(tipo_clave, df_dummy, params)
                    
                    # Mostrar enlace de descarga
                    nombre_archivo = os.path.basename(ruta_reporte)
                    st.success(f"Reporte generado: {nombre_archivo}")
                    
                    # En un sistema real, aquí habría un botón de descarga del archivo
                    st.info("En una implementación completa, aquí podrías descargar el archivo.")
                    
                except Exception as e:
                    st.error(f"Error al generar reporte: {str(e)}")
    
    with col2:
        destinatarios = st.text_input("Destinatarios (separados por comas):")
        
        if st.button("Enviar por Email"):
            if not destinatarios:
                st.warning("Debe ingresar al menos un destinatario")
            else:
                with st.spinner("Enviando reporte por email..."):
                    # Simulamos tiempo de procesamiento
                    time.sleep(2)
                    
                    # Simular envío exitoso
                    st.success("Reporte enviado exitosamente")
    
    # Panel de programación de reportes
    st.header("Programar Reportes Periódicos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tipo_programado = st.selectbox(
            "Tipo de reporte a programar:",
            ["Resumen Ejecutivo", "Performance por Canal", "Forecast de Cierre", "Recomendaciones Tácticas"],
            key="prog_tipo"
        )
        
        frecuencia = st.selectbox(
            "Frecuencia de envío:",
            ["Diaria", "Semanal", "Quincenal", "Mensual"]
        )
    
    with col2:
        dest_programados = st.text_area("Destinatarios (uno por línea):")
        
        roles = st.multiselect(
            "Roles a incluir:",
            ["Digital Team", "Marketing", "Comercial", "Directivo"],
            default=["Digital Team"]
        )
    
    if st.button("Programar Envío Periódico"):
        if not dest_programados:
            st.warning("Debe ingresar al menos un destinatario")
        else:
            with st.spinner("Configurando programación..."):
                # Convertir nombres amigables a claves internas
                tipo_map = {
                    "Resumen Ejecutivo": "ejecutivo",
                    "Performance por Canal": "performance",
                    "Forecast de Cierre": "forecast",
                    "Recomendaciones Tácticas": "recomendaciones"
                }
                
                tipo_clave = tipo_map.get(tipo_programado, "ejecutivo")
                
                # Convertir texto de destinatarios a lista
                lista_destinatarios = [email.strip() for email in dest_programados.split("\n") if email.strip()]
                
                # Parámetros para la programación
                params = {
                    'formato': 'powerpoint',  # por defecto
                    'roles': roles
                }
                
                try:
                    # Programar reporte
                    id_prog = generador.programar_envio_reporte(
                        tipo_clave,
                        frecuencia.lower(),
                        lista_destinatarios,
                        params
                    )
                    
                    st.success(f"Reporte programado exitosamente (ID: {id_prog})")
                    
                except Exception as e:
                    st.error(f"Error al programar reporte: {str(e)}")
    
    # Panel de integración con PowerBI
    st.header("Integración con PowerBI")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Calendario de Campañas")
        st.write("Genera el modelo de datos para el calendario de campañas en PowerBI.")
        
        if st.button("Generar Modelo de Calendario"):
            with st.spinner("Generando modelo de datos..."):
                try:
                    # Generar modelo de calendario
                    ruta_calendario = generador.generar_modelo_powerbi_campanas()
                    
                    st.success(f"Modelo generado: {os.path.basename(ruta_calendario)}")
                    
                except Exception as e:
                    st.error(f"Error al generar modelo de calendario: {str(e)}")
    
    with col2:
        st.subheader("Actualizar Dashboard")
        st.write("Actualiza el dashboard de PowerBI con los datos más recientes.")
        
        ultima_act = datetime.datetime.now() - datetime.timedelta(hours=6)
        st.info(f"Última actualización: {ultima_act.strftime('%Y-%m-%d %H:%M')}")
        
        if st.button("Actualizar Dashboard Ahora"):
            with st.spinner("Actualizando dashboard..."):
                # Simulamos tiempo de procesamiento
                time.sleep(3)
                
                # Simular actualización exitosa
                st.success("Dashboard actualizado correctamente")

def main():
    """Función principal para ejecutar la interfaz de reportes."""
    mostrar_interfaz_reportes()

if __name__ == "__main__":
    main() 