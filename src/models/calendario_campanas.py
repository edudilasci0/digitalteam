"""
Módulo para la gestión del calendario visual de campañas.
Permite crear, visualizar y exportar calendario de campañas para PowerBI.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import datetime
import logging
import json
from typing import Dict, List, Optional, Tuple
import uuid

from src.utils.config import get_config
from src.utils.logging import get_module_logger

logger = get_module_logger(__name__)

class CalendarioCampanas:
    """
    Clase para la gestión del calendario visual de campañas.
    Proporciona funcionalidades para visualizar campañas en formato calendario
    y exportar los datos para su uso en PowerBI.
    """
    
    def __init__(self):
        """Inicializa el gestor de calendario de campañas."""
        self.config = get_config()
        
        # Directorios de trabajo
        self.dir_campanas = Path(self.config['paths']['data']) / 'campanas'
        self.dir_campanas.mkdir(exist_ok=True)
        
        self.dir_powerbi = Path(self.config['paths']['output']) / 'powerbi'
        self.dir_powerbi.mkdir(exist_ok=True)
        
        # Archivo de campañas
        self.campanas_file = self.dir_campanas / 'campanas.json'
        self.campanas = self._cargar_campanas()
    
    def _cargar_campanas(self) -> Dict:
        """Carga los datos de campañas del archivo JSON."""
        if self.campanas_file.exists():
            try:
                with open(self.campanas_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error al cargar campañas: {str(e)}")
                return {'campanas': []}
        else:
            return {'campanas': []}
    
    def _guardar_campanas(self):
        """Guarda los datos de campañas en archivo JSON."""
        try:
            with open(self.campanas_file, 'w') as f:
                json.dump(self.campanas, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error al guardar campañas: {str(e)}")
    
    def crear_campana(self, 
                     nombre: str, 
                     marca: str, 
                     canal: str,
                     fecha_inicio: str,
                     fecha_fin: str,
                     presupuesto_total: float,
                     objetivo_leads: int = None,
                     objetivo_matriculas: int = None,
                     distribuciones: Dict = None) -> str:
        """
        Crea una nueva campaña en el calendario.
        
        Args:
            nombre (str): Nombre de la campaña
            marca (str): Marca asociada a la campaña
            canal (str): Canal principal de la campaña
            fecha_inicio (str): Fecha de inicio (formato YYYY-MM-DD)
            fecha_fin (str): Fecha de fin (formato YYYY-MM-DD)
            presupuesto_total (float): Presupuesto total asignado
            objetivo_leads (int, optional): Objetivo de leads
            objetivo_matriculas (int, optional): Objetivo de matrículas
            distribuciones (Dict, optional): Distribución diaria de presupuesto e intensidad
            
        Returns:
            str: ID de la campaña creada
        """
        # Generar ID único
        id_campana = str(uuid.uuid4())
        
        # Validar fechas
        try:
            fecha_inicio_dt = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')
            
            if fecha_fin_dt < fecha_inicio_dt:
                raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
        except ValueError as e:
            logger.error(f"Error en formato de fechas: {str(e)}")
            raise
        
        # Calcular días de duración
        dias_duracion = (fecha_fin_dt - fecha_inicio_dt).days + 1
        
        # Crear distribuciones por defecto si no se proporcionan
        distribuciones_default = {
            'por_fase': {
                'lanzamiento': {
                    'dias': int(dias_duracion * 0.2),
                    'presupuesto_factor': 1.2,
                    'intensidad_factor': 1.2
                },
                'optimizacion': {
                    'dias': int(dias_duracion * 0.6),
                    'presupuesto_factor': 1.0,
                    'intensidad_factor': 1.0
                },
                'cierre': {
                    'dias': int(dias_duracion * 0.2),
                    'presupuesto_factor': 0.8,
                    'intensidad_factor': 0.8
                }
            }
        }
        
        # Usar distribuciones proporcionadas o las predeterminadas
        dist_final = distribuciones or distribuciones_default
        
        # Crear campaña
        nueva_campana = {
            'id': id_campana,
            'nombre': nombre,
            'marca': marca,
            'canal': canal,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'dias_duracion': dias_duracion,
            'presupuesto_total': presupuesto_total,
            'presupuesto_diario_base': presupuesto_total / dias_duracion,
            'objetivo_leads': objetivo_leads,
            'objetivo_matriculas': objetivo_matriculas,
            'leads_diarios_esperados': objetivo_leads / dias_duracion if objetivo_leads else None,
            'matriculas_diarias_esperadas': objetivo_matriculas / dias_duracion if objetivo_matriculas else None,
            'distribuciones': dist_final,
            'intensidad_base': 5,  # En escala 1-10
            'fecha_creacion': datetime.datetime.now().isoformat(),
            'metadata': {}
        }
        
        # Guardar campaña
        self.campanas['campanas'].append(nueva_campana)
        self._guardar_campanas()
        
        logger.info(f"Campaña creada: {nombre} ({id_campana})")
        return id_campana
    
    def generar_calendario_diario(self) -> pd.DataFrame:
        """
        Genera un DataFrame con el calendario diario de todas las campañas.
        
        Returns:
            pd.DataFrame: Calendario diario de campañas
        """
        # Preparar lista para datos diarios
        datos_diarios = []
        
        # Procesar cada campaña
        for campana in self.campanas['campanas']:
            # Obtener fechas de inicio y fin
            fecha_inicio = datetime.datetime.strptime(campana['fecha_inicio'], '%Y-%m-%d')
            fecha_fin = datetime.datetime.strptime(campana['fecha_fin'], '%Y-%m-%d')
            
            # Distribuciones por fase
            dist_fases = campana['distribuciones']['por_fase']
            dias_lanzamiento = dist_fases['lanzamiento']['dias']
            dias_cierre = dist_fases['cierre']['dias']
            
            # Calcular presupuesto e intensidad base
            presupuesto_diario_base = campana['presupuesto_diario_base']
            intensidad_base = campana['intensidad_base']
            
            # Generar datos para cada día
            fecha_actual = fecha_inicio
            dia_campaña = 1
            
            while fecha_actual <= fecha_fin:
                # Determinar fase
                if dia_campaña <= dias_lanzamiento:
                    fase = 'lanzamiento'
                    factor_presupuesto = dist_fases['lanzamiento']['presupuesto_factor']
                    factor_intensidad = dist_fases['lanzamiento']['intensidad_factor']
                elif dia_campaña > (campana['dias_duracion'] - dias_cierre):
                    fase = 'cierre'
                    factor_presupuesto = dist_fases['cierre']['presupuesto_factor']
                    factor_intensidad = dist_fases['cierre']['intensidad_factor']
                else:
                    fase = 'optimizacion'
                    factor_presupuesto = dist_fases['optimizacion']['presupuesto_factor']
                    factor_intensidad = dist_fases['optimizacion']['intensidad_factor']
                
                # Calcular valores diarios
                presupuesto_diario = presupuesto_diario_base * factor_presupuesto
                intensidad = min(10, intensidad_base * factor_intensidad)
                
                # Calcular objetivos diarios con factores de fase
                if campana['objetivo_leads']:
                    leads_esperados = campana['leads_diarios_esperados'] * factor_presupuesto
                else:
                    leads_esperados = None
                    
                if campana['objetivo_matriculas']:
                    matriculas_esperadas = campana['matriculas_diarias_esperadas'] * factor_presupuesto
                else:
                    matriculas_esperadas = None
                
                # Crear registro diario
                datos_diarios.append({
                    'fecha': fecha_actual.strftime('%Y-%m-%d'),
                    'id_campana': campana['id'],
                    'nombre_campana': campana['nombre'],
                    'marca': campana['marca'],
                    'canal': campana['canal'],
                    'presupuesto_diario': round(presupuesto_diario, 2),
                    'intensidad_inversion': round(intensidad),
                    'leads_esperados': round(leads_esperados) if leads_esperados else None,
                    'matriculas_esperadas': round(matriculas_esperadas) if matriculas_esperadas else None,
                    'fase_campana': fase,
                    'dia_campana': dia_campaña
                })
                
                # Avanzar al siguiente día
                fecha_actual += datetime.timedelta(days=1)
                dia_campaña += 1
        
        # Crear DataFrame
        if datos_diarios:
            df_calendario = pd.DataFrame(datos_diarios)
        else:
            # DataFrame vacío con las columnas necesarias
            df_calendario = pd.DataFrame(columns=[
                'fecha', 'id_campana', 'nombre_campana', 'marca', 'canal',
                'presupuesto_diario', 'intensidad_inversion', 'leads_esperados',
                'matriculas_esperadas', 'fase_campana', 'dia_campana'
            ])
        
        return df_calendario
    
    def exportar_calendario_powerbi(self) -> str:
        """
        Exporta el calendario de campañas para PowerBI.
        
        Returns:
            str: Ruta al archivo CSV generado
        """
        try:
            # Generar calendario
            df_calendario = self.generar_calendario_diario()
            
            if df_calendario.empty:
                logger.warning("No hay datos de campañas para exportar")
                return None
            
            # Crear nombre de archivo con timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_archivo = self.dir_powerbi / f"calendario_campanas_{timestamp}.csv"
            
            # Guardar como CSV
            df_calendario.to_csv(ruta_archivo, index=False)
            
            logger.info(f"Calendario exportado para PowerBI: {ruta_archivo}")
            return str(ruta_archivo)
            
        except Exception as e:
            logger.error(f"Error al exportar calendario: {str(e)}", exc_info=True)
            raise
    
    def agregar_datos_reales(self, 
                           datos_reales: pd.DataFrame, 
                           mapeo_columnas: Dict = None) -> bool:
        """
        Agrega datos reales al calendario de campañas.
        
        Args:
            datos_reales (pd.DataFrame): DataFrame con datos reales
            mapeo_columnas (Dict, optional): Mapeo de columnas de datos_reales a columnas del calendario
            
        Returns:
            bool: True si se agregaron datos correctamente
        """
        try:
            # Cargar calendario actual
            df_calendario = self.generar_calendario_diario()
            
            if df_calendario.empty:
                logger.warning("No hay calendario para agregar datos reales")
                return False
            
            # Mapeo de columnas por defecto
            mapeo_default = {
                'fecha': 'fecha',
                'id_campana': 'id_campana',
                'leads_reales': 'leads',
                'matriculas_reales': 'matriculas'
            }
            
            # Usar mapeo proporcionado o el predeterminado
            mapeo = mapeo_columnas or mapeo_default
            
            # Verificar columnas requeridas
            columnas_requeridas = ['fecha', 'id_campana']
            columnas_faltantes = [col for col in columnas_requeridas 
                                if mapeo[col] not in datos_reales.columns]
            
            if columnas_faltantes:
                logger.error(f"Faltan columnas requeridas en datos_reales: {columnas_faltantes}")
                return False
            
            # Renombrar columnas según mapeo
            df_reales = datos_reales.rename(columns={v: k for k, v in mapeo.items() if v in datos_reales.columns})
            
            # Asegurar el formato correcto de fecha
            df_reales['fecha'] = pd.to_datetime(df_reales['fecha']).dt.strftime('%Y-%m-%d')
            
            # Realizar la fusión
            df_combinado = pd.merge(
                df_calendario, 
                df_reales,
                on=['fecha', 'id_campana'],
                how='left'
            )
            
            # Guardar el calendario actualizado
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_archivo = self.dir_powerbi / f"calendario_campanas_actualizado_{timestamp}.csv"
            
            df_combinado.to_csv(ruta_archivo, index=False)
            
            logger.info(f"Calendario actualizado con datos reales: {ruta_archivo}")
            return True
            
        except Exception as e:
            logger.error(f"Error al agregar datos reales: {str(e)}", exc_info=True)
            return False
    
    def generar_datos_ejemplo(self, num_campanas: int = 3) -> Dict:
        """
        Genera datos de ejemplo para demostrar el calendario de campañas.
        
        Args:
            num_campanas (int): Número de campañas a generar
            
        Returns:
            Dict: Diccionario con información de campañas generadas
        """
        # Lista de campañas generadas
        campanas_generadas = []
        
        # Ejemplos de marcas, canales y nombres
        marcas = ['Marca A', 'Marca B', 'Marca C', 'Marca D']
        canales = ['Facebook', 'Google', 'Instagram', 'LinkedIn', 'Email']
        nombres_base = ['Campaña Verano', 'Promoción Otoño', 'Descuentos Primavera', 
                      'Inscripciones Anticipadas', 'Black Friday']
        
        # Fecha actual para referencia
        hoy = datetime.datetime.now()
        
        # Generar campañas aleatorias
        import random
        
        for i in range(num_campanas):
            # Seleccionar valores aleatorios
            marca = random.choice(marcas)
            canal = random.choice(canales)
            nombre_base = random.choice(nombres_base)
            
            # Crear nombre único
            nombre = f"{nombre_base} {hoy.year} - {marca}"
            
            # Fechas aleatorias en un rango razonable
            dias_inicio = random.randint(-30, 30)  # Entre 30 días atrás y 30 días adelante
            duracion = random.randint(15, 60)  # Entre 15 y 60 días
            
            fecha_inicio = (hoy + datetime.timedelta(days=dias_inicio)).strftime('%Y-%m-%d')
            fecha_fin = (hoy + datetime.timedelta(days=dias_inicio + duracion)).strftime('%Y-%m-%d')
            
            # Presupuesto y objetivos
            presupuesto = random.randint(5000, 50000)
            objetivo_leads = random.randint(100, 1000)
            objetivo_matriculas = int(objetivo_leads * random.uniform(0.05, 0.15))
            
            # Crear campaña
            id_campana = self.crear_campana(
                nombre=nombre,
                marca=marca,
                canal=canal,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                presupuesto_total=presupuesto,
                objetivo_leads=objetivo_leads,
                objetivo_matriculas=objetivo_matriculas
            )
            
            # Agregar a lista de generadas
            campanas_generadas.append({
                'id': id_campana,
                'nombre': nombre,
                'fechas': f"{fecha_inicio} a {fecha_fin}"
            })
        
        # Exportar para PowerBI
        ruta_powerbi = self.exportar_calendario_powerbi()
        
        return {
            'campanas_generadas': campanas_generadas,
            'ruta_powerbi': ruta_powerbi
        }

# Función para uso directo del módulo
def generar_calendario_demo():
    """
    Genera un calendario de demostración para PowerBI.
    """
    calendario = CalendarioCampanas()
    resultado = calendario.generar_datos_ejemplo(5)
    
    print(f"Campañas generadas: {len(resultado['campanas_generadas'])}")
    for campana in resultado['campanas_generadas']:
        print(f"- {campana['nombre']} ({campana['fechas']})")
    
    print(f"\nCalendario exportado para PowerBI: {resultado['ruta_powerbi']}")

if __name__ == "__main__":
    generar_calendario_demo() 