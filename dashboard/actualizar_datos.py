#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para automatizar la actualización de datos para el dashboard Power BI.
Este script puede programarse para ejecutarse diariamente.
"""

import pandas as pd
import os
import shutil
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard/logs/actualizacion.log'),
        logging.StreamHandler()
    ]
)

def crear_directorios():
    """Crea la estructura de directorios necesaria si no existe."""
    directorios = [
        'dashboard/datos/originales',
        'dashboard/datos/procesados',
        'dashboard/logs'
    ]
    for dir in directorios:
        if not os.path.exists(dir):
            os.makedirs(dir)
            logging.info(f"Directorio creado: {dir}")

def copiar_plantillas():
    """Copia los archivos de plantilla a la carpeta de procesados si están vacíos."""
    origen = 'dashboard/datos/plantillas'
    destino = 'dashboard/datos/procesados'
    
    if not os.path.exists(destino):
        os.makedirs(destino)
    
    # Comprobar si los archivos de destino existen y copiar si no
    for archivo in os.listdir(origen):
        if archivo.endswith('.csv'):
            archivo_destino = os.path.join(destino, archivo)
            if not os.path.exists(archivo_destino):
                shutil.copy(os.path.join(origen, archivo), archivo_destino)
                logging.info(f"Plantilla copiada: {archivo}")

def actualizar_datos_desde_fuentes():
    """
    Actualiza los datos desde las fuentes originales.
    
    Aquí deberías implementar la lógica para:
    1. Conectar con las fuentes de datos reales (CRM, Excel, etc.)
    2. Procesar los datos según sea necesario
    3. Guardar los resultados en la carpeta procesados
    
    Este es un ejemplo simplificado.
    """
    try:
        # Aquí implementar la conexión a fuentes reales
        # Por ejemplo, conexión a una base de datos, API o archivos
        
        # Simulación de actualización (para demo)
        logging.info("Simulando actualización de datos...")
        
        # 1. Cargar datos procesados actuales
        df_leads = pd.read_csv('dashboard/datos/procesados/leads.csv')
        df_matriculas = pd.read_csv('dashboard/datos/procesados/matriculas.csv')
        
        # 2. Agregar algunos datos nuevos (simulado)
        ultimos_dias = 5
        ultima_fecha = datetime.strptime(df_leads['fecha_creacion'].max(), '%Y-%m-%d')
        ultimo_id_lead = df_leads['id_lead'].max()
        ultimo_id_matricula = df_matriculas['id_matricula'].max() if len(df_matriculas) > 0 else 0
        
        # Generar nuevos leads
        nuevos_leads = []
        for i in range(1, ultimos_dias+1):
            nueva_fecha = (ultima_fecha + timedelta(days=i)).strftime('%Y-%m-%d')
            nuevo_id = ultimo_id_lead + i
            
            # Simular un nuevo lead
            nuevo_lead = {
                'id_lead': nuevo_id,
                'fecha_creacion': nueva_fecha,
                'programa_id': 101 + (i % 4),  # Alterna entre programas
                'estado': 'Nuevo',
                'comercial_id': 1 + (i % 3),   # Alterna entre comerciales
                'origen': 'Facebook' if i % 2 == 0 else 'Google',
                'utm_source': 'facebook' if i % 2 == 0 else 'google',
                'utm_medium': 'cpc',
                'utm_campaign': 'febrero2023',
                'telefono': f'555-{i}00-{i}000',
                'email': f'nuevo{i}@ejemplo.com',
                'nombre': f'Nuevo{i}',
                'apellido': f'Apellido{i}'
            }
            nuevos_leads.append(nuevo_lead)
        
        # Agregar nuevos leads al dataframe
        df_leads_nuevos = pd.DataFrame(nuevos_leads)
        df_leads = pd.concat([df_leads, df_leads_nuevos], ignore_index=True)
        
        # Simular algunas matrículas nuevas (conversiones de leads existentes)
        nuevas_matriculas = []
        for i in range(1, min(3, ultimos_dias)+1):  # Convertir algunos leads en matrículas
            lead_id_a_convertir = ultimo_id_lead - i  # Convertir leads anteriores
            nueva_fecha = (ultima_fecha + timedelta(days=i)).strftime('%Y-%m-%d')
            
            # Obtener programa y comercial del lead
            lead_info = df_leads[df_leads['id_lead'] == lead_id_a_convertir]
            if len(lead_info) > 0:
                programa_id = lead_info.iloc[0]['programa_id']
                comercial_id = lead_info.iloc[0]['comercial_id']
                
                # Crear nueva matrícula
                nueva_matricula = {
                    'id_matricula': ultimo_id_matricula + i,
                    'id_lead': lead_id_a_convertir,
                    'fecha_matricula': nueva_fecha,
                    'programa_id': programa_id,
                    'valor_matricula': 1500 + (programa_id % 4) * 500,  # Valor basado en programa
                    'forma_pago': 'Tarjeta' if i % 2 == 0 else 'Transferencia',
                    'comercial_id': comercial_id
                }
                nuevas_matriculas.append(nueva_matricula)
                
                # Actualizar estado del lead a "Matriculado"
                df_leads.loc[df_leads['id_lead'] == lead_id_a_convertir, 'estado'] = 'Matriculado'
        
        # Agregar nuevas matrículas al dataframe
        if nuevas_matriculas:
            df_matriculas_nuevas = pd.DataFrame(nuevas_matriculas)
            df_matriculas = pd.concat([df_matriculas, df_matriculas_nuevas], ignore_index=True)
        
        # 3. Guardar datos actualizados
        df_leads.to_csv('dashboard/datos/procesados/leads.csv', index=False)
        df_matriculas.to_csv('dashboard/datos/procesados/matriculas.csv', index=False)
        
        logging.info(f"Datos actualizados: {len(nuevos_leads)} nuevos leads, {len(nuevas_matriculas)} nuevas matrículas")
        return True
        
    except Exception as e:
        logging.error(f"Error en la actualización de datos: {str(e)}")
        return False

def ejecutar_actualizacion():
    """Función principal para ejecutar la actualización de datos."""
    try:
        inicio = datetime.now()
        logging.info("Iniciando actualización de datos para dashboard...")
        
        # Crear estructura de directorios si no existe
        crear_directorios()
        
        # Copiar plantillas si es necesario
        copiar_plantillas()
        
        # Actualizar datos desde fuentes originales
        if actualizar_datos_desde_fuentes():
            fin = datetime.now()
            duracion = (fin - inicio).total_seconds()
            logging.info(f"Actualización completada exitosamente en {duracion:.2f} segundos")
            return True
        else:
            logging.warning("La actualización de datos falló o está incompleta")
            return False
            
    except Exception as e:
        logging.error(f"Error en la ejecución de la actualización: {str(e)}")
        return False

if __name__ == "__main__":
    ejecutar_actualizacion() 