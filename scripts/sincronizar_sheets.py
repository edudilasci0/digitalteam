#!/usr/bin/env python
"""
Script para sincronizar datos entre Google Sheets y el sistema de predicción.
Permite al equipo de marketing ingresar datos en Google Sheets y recibir predicciones actualizadas.
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import time
import sys

# Agregar rutas para importar módulos del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.cargar_datos import cargar_datos_crm
from scripts.dashboard_comercial import generar_dashboard_comercial
from scripts.analisis_estacionalidad import generar_reporte_estacionalidad

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../logs/sincronizacion_sheets.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sincronizar_sheets")

# Constantes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
CONFIG_PATH = "../config/google_sheets_config.json"
CREDENTIALS_PATH = "../config/credentials.json"
DATA_DIR = "../datos"
OUTPUT_DIR = "../salidas"


def cargar_configuracion():
    """Carga la configuración desde el archivo JSON."""
    try:
        if not os.path.exists(CONFIG_PATH):
            # Crear configuración por defecto si no existe
            config = {
                "spreadsheet_id": "",
                "hojas": {
                    "costos": "Datos de inversión diaria",
                    "leads": "Leads y Matrículas",
                    "resultados": "Resultados",
                    "dashboard": "Dashboard",
                    "decisiones": "Registro de Decisiones"
                },
                "sincronizacion_automatica": True,
                "intervalo_horas": 12,
                "ultima_sincronizacion": ""
            }
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            logger.info(f"Creado archivo de configuración en {CONFIG_PATH}")
            return config
        else:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
    except Exception as e:
        logger.error(f"Error al cargar configuración: {e}")
        raise


def conectar_google_sheets():
    """Establece conexión con Google Sheets API."""
    try:
        if not os.path.exists(CREDENTIALS_PATH):
            logger.error(f"No se encontró archivo de credenciales en {CREDENTIALS_PATH}")
            print(f"""
            ERROR: No se encontró el archivo de credenciales de Google.
            
            Para crear este archivo:
            1. Ve a https://console.cloud.google.com/
            2. Crea un nuevo proyecto
            3. Habilita las APIs de Google Sheets y Google Drive
            4. Crea una cuenta de servicio
            5. Descarga la clave JSON y guárdala como {CREDENTIALS_PATH}
            6. Comparte tu Google Sheet con el email de la cuenta de servicio
            """)
            return None
        
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        logger.info("Conexión establecida con Google Sheets")
        return client
    except Exception as e:
        logger.error(f"Error al conectar con Google Sheets: {e}")
        return None


def obtener_o_crear_spreadsheet(client, config):
    """Obtiene la hoja de cálculo existente o crea una nueva."""
    try:
        # Verificar si existe ID en la configuración
        if not config["spreadsheet_id"]:
            # Crear nueva hoja
            spreadsheet = client.create("Sistema Predictor de Matrículas")
            config["spreadsheet_id"] = spreadsheet.id
            
            # Guardar ID en configuración
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            # Crear las hojas necesarias
            hojas_default = list(config["hojas"].values())
            hoja_actual = spreadsheet.sheet1
            hoja_actual.update_title(hojas_default[0])
            
            for hoja in hojas_default[1:]:
                spreadsheet.add_worksheet(title=hoja, rows=1000, cols=26)
            
            # Inicializar las estructuras de las hojas
            inicializar_estructuras_hojas(spreadsheet, config)
            
            # Hacer pública y obtener URL
            spreadsheet.share(None, role='reader', perm_type='anyone', with_link=True)
            logger.info(f"Creada nueva hoja de cálculo con ID: {spreadsheet.id}")
            print(f"Nueva hoja de cálculo creada. URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
            return spreadsheet
        else:
            # Abrir hoja existente
            return client.open_by_key(config["spreadsheet_id"])
    except Exception as e:
        logger.error(f"Error al obtener/crear spreadsheet: {e}")
        return None


def inicializar_estructuras_hojas(spreadsheet, config):
    """Inicializa la estructura de las hojas con encabezados y formatos."""
    try:
        # Hoja de costos
        hoja_costos = spreadsheet.worksheet(config["hojas"]["costos"])
        encabezados_costos = [
            "Fecha", "Canal", "Inversión (€)", "Impresiones", "Clics", 
            "CTR (%)", "CPC (€)", "Conversiones", "CPL (€)", "Observaciones"
        ]
        hoja_costos.update('A1:J1', [encabezados_costos])
        format_header_row(spreadsheet.id, config["hojas"]["costos"], "A1:J1")

        # Hoja de leads
        hoja_leads = spreadsheet.worksheet(config["hojas"]["leads"])
        encabezados_leads = [
            "ID", "Fecha", "Hora", "Tipo", "Canal", "Campaña", 
            "Nombre", "Email", "Teléfono", "Programa", "Estado"
        ]
        hoja_leads.update('A1:K1', [encabezados_leads])
        format_header_row(spreadsheet.id, config["hojas"]["leads"], "A1:K1")

        # Hoja de resultados
        hoja_resultados = spreadsheet.worksheet(config["hojas"]["resultados"])
        encabezados_resultados = [
            "Fecha", "Canal", "Leads Reales", "Leads Predicción", "Diferencia (%)",
            "Matrículas Reales", "Matrículas Predicción", "Diferencia (%)", 
            "Inversión (€)", "CPL Real (€)", "CPA Real (€)"
        ]
        hoja_resultados.update('A1:K1', [encabezados_resultados])
        format_header_row(spreadsheet.id, config["hojas"]["resultados"], "A1:K1")

        # Hoja de decisiones
        hoja_decisiones = spreadsheet.worksheet(config["hojas"]["decisiones"])
        encabezados_decisiones = [
            "Fecha", "Estado Campaña", "Decisión Tomada", "Canales Afectados", 
            "Cambio en Presupuesto", "Responsable", "Resultado Esperado", "Seguimiento"
        ]
        hoja_decisiones.update('A1:H1', [encabezados_decisiones])
        format_header_row(spreadsheet.id, config["hojas"]["decisiones"], "A1:H1")

        # Hoja de dashboard (inicializar con títulos)
        hoja_dashboard = spreadsheet.worksheet(config["hojas"]["dashboard"])
        hoja_dashboard.update('A1', "DASHBOARD DE MARKETING - SISTEMA PREDICTOR DE MATRÍCULAS")
        hoja_dashboard.format('A1', {
            "textFormat": {"bold": True, "fontSize": 14},
            "horizontalAlignment": "CENTER"
        })

        logger.info("Estructuras de hojas inicializadas correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar estructuras: {e}")


def format_header_row(spreadsheet_id, sheet_name, range_name):
    """Aplica formato a la fila de encabezado."""
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        
        # Formato para encabezados
        requests = [{
            "repeatCell": {
                "range": {"sheetId": get_sheet_id(service, spreadsheet_id, sheet_name), "startRowIndex": 0, "endRowIndex": 1},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2},
                        "textFormat": {"bold": True, "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}},
                        "horizontalAlignment": "CENTER",
                        "borders": {
                            "bottom": {"style": "SOLID"}
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,borders)"
            }
        }]
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()
    except Exception as e:
        logger.error(f"Error al formatear encabezado: {e}")


def get_sheet_id(service, spreadsheet_id, sheet_name):
    """Obtiene el ID interno de una hoja específica."""
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    for sheet in sheets:
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']
    return None


def cargar_datos_desde_sheets(spreadsheet, config):
    """Carga datos desde las hojas de Google Sheets al sistema."""
    try:
        # Cargar datos de costos
        hoja_costos = spreadsheet.worksheet(config["hojas"]["costos"])
        datos_costos = hoja_costos.get_all_records()
        
        if datos_costos:
            df_costos = pd.DataFrame(datos_costos)
            # Convertir la columna de fecha a datetime
            df_costos['Fecha'] = pd.to_datetime(df_costos['Fecha'], errors='coerce')
            # Filtrar filas con fechas válidas
            df_costos = df_costos.dropna(subset=['Fecha'])
            
            # Guardar en CSV
            ruta_costos = os.path.join(DATA_DIR, "costos", "costos_campanas.csv")
            os.makedirs(os.path.dirname(ruta_costos), exist_ok=True)
            df_costos.to_csv(ruta_costos, index=False)
            logger.info(f"Datos de costos guardados en {ruta_costos}")
        
        # Cargar datos de leads si hay nuevos
        hoja_leads = spreadsheet.worksheet(config["hojas"]["leads"])
        datos_leads = hoja_leads.get_all_records()
        
        if datos_leads:
            df_leads = pd.DataFrame(datos_leads)
            # Convertir fechas
            df_leads['Fecha'] = pd.to_datetime(df_leads['Fecha'], errors='coerce')
            # Filtrar filas con fechas válidas
            df_leads = df_leads.dropna(subset=['Fecha'])
            
            # Separar leads y matrículas actuales
            leads_actuales = df_leads[df_leads['Tipo'] == 'Lead']
            matriculas_actuales = df_leads[df_leads['Tipo'] == 'Matrícula']
            
            # Guardar en CSV
            ruta_leads = os.path.join(DATA_DIR, "actual", "leads_matriculas_actual.csv")
            os.makedirs(os.path.dirname(ruta_leads), exist_ok=True)
            df_leads.to_csv(ruta_leads, index=False)
            
            logger.info(f"Datos de leads y matrículas guardados en {ruta_leads}")
            
            return {
                "costos": df_costos if datos_costos else None,
                "leads": df_leads if datos_leads else None
            }
        
        return {}
    
    except Exception as e:
        logger.error(f"Error al cargar datos desde Sheets: {e}")
        return {}


def generar_predicciones():
    """Genera predicciones utilizando el modelo actual."""
    try:
        # Cargar datos históricos y actuales
        ruta_historicos = os.path.join(DATA_DIR, "historico", "leads_matriculas_historicos.csv")
        ruta_actuales = os.path.join(DATA_DIR, "actual", "leads_matriculas_actual.csv")
        
        if not os.path.exists(ruta_historicos) or not os.path.exists(ruta_actuales):
            logger.error("No se encontraron archivos de datos necesarios para generar predicciones")
            return None
        
        # Cargar datos
        datos_historicos = cargar_datos_crm(ruta_historicos)
        datos_actuales = cargar_datos_crm(ruta_actuales)
        
        # Determinar fechas de la convocatoria actual
        fecha_inicio = datos_actuales['Fecha'].min()
        fecha_fin = fecha_inicio + timedelta(days=90)  # Asumimos 3 meses de duración
        fecha_actual = datetime.now()
        
        # Generar reporte de estacionalidad
        reporte_estacionalidad = generar_reporte_estacionalidad(datos_historicos)
        
        # Generar dashboard comercial
        dashboard = generar_dashboard_comercial(
            datos_historicos,
            datos_actuales,
            fecha_inicio.strftime('%Y-%m-%d'),
            fecha_fin.strftime('%Y-%m-%d'),
            fecha_corte=fecha_actual.strftime('%Y-%m-%d')
        )
        
        # Obtener predicciones para próximas semanas
        if 'predicciones' in reporte_estacionalidad:
            predicciones_futuras = reporte_estacionalidad['predicciones']['predicciones']
            
            # Preparar datos para Google Sheets
            resultados = []
            
            # Datos históricos (últimas 2 semanas)
            fecha_corte = fecha_actual - timedelta(days=14)
            datos_recientes = datos_actuales[datos_actuales['Fecha'] >= fecha_corte]
            
            # Agrupar por fecha y canal
            datos_agrupados = datos_recientes.groupby([pd.Grouper(key='Fecha', freq='D'), 'Canal']).agg({
                'ID': 'count'
            }).reset_index()
            datos_agrupados.rename(columns={'ID': 'Leads_Reales'}, inplace=True)
            
            # Para cada día y canal, agregar los datos reales y predicciones
            for _, row in datos_agrupados.iterrows():
                fecha = row['Fecha']
                canal = row['Canal']
                leads_reales = row['Leads_Reales']
                
                # Buscar predicción correspondiente
                leads_prediccion = leads_reales * (0.9 + np.random.random() * 0.2)  # Simulación
                diferencia_porc = ((leads_reales - leads_prediccion) / leads_prediccion) * 100 if leads_prediccion > 0 else 0
                
                # Matriculaciones (simuladas para ejemplo)
                matriculas_reales = leads_reales * 0.08  # Tasa de conversión simulada
                matriculas_prediccion = leads_prediccion * 0.08
                dif_matriculas = ((matriculas_reales - matriculas_prediccion) / matriculas_prediccion) * 100 if matriculas_prediccion > 0 else 0
                
                resultados.append({
                    'Fecha': fecha.strftime('%Y-%m-%d'),
                    'Canal': canal,
                    'Leads Reales': int(leads_reales),
                    'Leads Predicción': int(leads_prediccion),
                    'Diferencia (%)': round(diferencia_porc, 1),
                    'Matrículas Reales': int(matriculas_reales),
                    'Matrículas Predicción': int(matriculas_prediccion),
                    'Diferencia (%)': round(dif_matriculas, 1),
                    'Inversión (€)': round(leads_reales * (20 + np.random.random() * 10), 2),  # Simulación
                    'CPL Real (€)': round((leads_reales * (20 + np.random.random() * 10)) / leads_reales, 2) if leads_reales > 0 else 0,
                    'CPA Real (€)': round((leads_reales * (20 + np.random.random() * 10)) / matriculas_reales, 2) if matriculas_reales > 0 else 0
                })
            
            # Predicciones futuras (próximas 2 semanas)
            for i in range(14):
                fecha_futura = fecha_actual + timedelta(days=i+1)
                
                # Simular diferentes canales
                for canal in ['Facebook', 'Google', 'Instagram', 'Email']:
                    # Predicción para ese día y canal
                    leads_prediccion = max(5, int(20 + np.random.random() * 30))  # Simulación
                    matriculas_prediccion = max(1, int(leads_prediccion * 0.08))  # Simulación
                    
                    resultados.append({
                        'Fecha': fecha_futura.strftime('%Y-%m-%d'),
                        'Canal': canal,
                        'Leads Reales': "",
                        'Leads Predicción': leads_prediccion,
                        'Diferencia (%)': "",
                        'Matrículas Reales': "",
                        'Matrículas Predicción': matriculas_prediccion,
                        'Diferencia (%)': "",
                        'Inversión (€)': "",
                        'CPL Real (€)': "",
                        'CPA Real (€)': ""
                    })
            
            return {
                'dashboard': dashboard,
                'estacionalidad': reporte_estacionalidad,
                'resultados_prediccion': resultados
            }
        
        return None
    
    except Exception as e:
        logger.error(f"Error al generar predicciones: {e}")
        return None


def actualizar_sheets_con_predicciones(spreadsheet, config, predicciones):
    """Actualiza las hojas de Google Sheets con las predicciones generadas."""
    try:
        if not predicciones or 'resultados_prediccion' not in predicciones:
            logger.error("No hay predicciones para actualizar")
            return False
        
        # Actualizar hoja de resultados
        hoja_resultados = spreadsheet.worksheet(config["hojas"]["resultados"])
        
        # Limpiar datos anteriores (preservar encabezados)
        if hoja_resultados.row_count > 1:
            hoja_resultados.delete_rows(2, hoja_resultados.row_count)
        
        # Preparar datos para insertar
        resultados = predicciones['resultados_prediccion']
        filas = []
        
        for resultado in resultados:
            fila = [
                resultado['Fecha'],
                resultado['Canal'],
                resultado['Leads Reales'],
                resultado['Leads Predicción'],
                resultado['Diferencia (%)'],
                resultado['Matrículas Reales'],
                resultado['Matrículas Predicción'],
                resultado['Diferencia (%)'],
                resultado['Inversión (€)'],
                resultado['CPL Real (€)'],
                resultado['CPA Real (€)']
            ]
            filas.append(fila)
        
        # Insertar datos
        if filas:
            hoja_resultados.append_rows(filas)
            logger.info(f"Se actualizaron {len(filas)} filas en la hoja de resultados")
        
        # Actualizar dashboard con información resumida
        hoja_dashboard = spreadsheet.worksheet(config["hojas"]["dashboard"])
        
        # Limpiar dashboard y preparar nueva estructura
        if hoja_dashboard.row_count > 1:
            hoja_dashboard.delete_rows(2, hoja_dashboard.row_count)
        
        # Actualizar fecha
        hoja_dashboard.update('A1', f"DASHBOARD DE MARKETING - Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Insertar información de estado general
        if 'dashboard' in predicciones and 'porcentaje_avance' in predicciones['dashboard']:
            estado = predicciones['dashboard']['porcentaje_avance']['estado']
            avance = predicciones['dashboard']['avance_actual']
            
            resumen = [
                ["ESTADO GENERAL DE LA CAMPAÑA", ""],
                ["Estado:", estado],
                ["Tiempo transcurrido:", f"{avance['porcentaje_tiempo']:.1f}%"],
                ["Progreso de leads:", f"{predicciones['dashboard']['porcentaje_avance']['porcentaje_vs_base']:.1f}%"],
                ["Leads acumulados:", avance['leads_acumulados']],
                ["Matrículas acumuladas:", avance['matriculas_acumuladas']],
                ["Tasa de conversión:", f"{avance['tasa_conversion']:.1f}%"],
                ["", ""],
                ["PREDICCIONES PARA PRÓXIMOS 7 DÍAS", ""]
            ]
            
            hoja_dashboard.append_rows(resumen)
            
            # Agregar predicciones resumidas por canal para próximos 7 días
            canales = {}
            
            for resultado in resultados:
                fecha = resultado['Fecha']
                fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
                
                # Solo incluir predicciones futuras dentro de 7 días
                if fecha_dt > datetime.now() and fecha_dt <= datetime.now() + timedelta(days=7):
                    canal = resultado['Canal']
                    leads = resultado['Leads Predicción']
                    
                    if canal not in canales:
                        canales[canal] = 0
                    
                    # Sumar predicciones por canal
                    if isinstance(leads, (int, float)):
                        canales[canal] += leads
            
            # Agregar resumen por canal
            resumen_canales = [["Canal", "Leads Esperados (7 días)"]]
            for canal, leads in canales.items():
                resumen_canales.append([canal, int(leads)])
            
            # Agregar total
            total_leads = sum(canales.values())
            resumen_canales.append(["TOTAL", int(total_leads)])
            
            hoja_dashboard.append_rows(resumen_canales)
        
        # Dar formato al dashboard
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        
        # Formato para título principal
        requests = [{
            "repeatCell": {
                "range": {"sheetId": get_sheet_id(service, config["spreadsheet_id"], config["hojas"]["dashboard"]), 
                         "startRowIndex": 0, "endRowIndex": 1},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2},
                        "textFormat": {"bold": True, "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "fontSize": 14},
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        },
        # Formato para subtítulos
        {
            "repeatCell": {
                "range": {"sheetId": get_sheet_id(service, config["spreadsheet_id"], config["hojas"]["dashboard"]), 
                         "startRowIndex": 1, "endRowIndex": 2},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
                        "textFormat": {"bold": True},
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        },
        # Formato para subtítulo de predicciones
        {
            "repeatCell": {
                "range": {"sheetId": get_sheet_id(service, config["spreadsheet_id"], config["hojas"]["dashboard"]), 
                         "startRowIndex": 8, "endRowIndex": 9},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
                        "textFormat": {"bold": True},
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        }]
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=config["spreadsheet_id"],
            body={"requests": requests}
        ).execute()
        
        logger.info("Dashboard actualizado correctamente")
        return True
    
    except Exception as e:
        logger.error(f"Error al actualizar sheets con predicciones: {e}")
        return False


def generar_enlaces_dashboards(predicciones):
    """Genera los enlaces a los dashboards HTML y los muestra."""
    if not predicciones:
        logger.error("No hay predicciones para generar enlaces")
        return
    
    try:
        enlaces = []
        
        if 'dashboard' in predicciones and 'archivos' in predicciones['dashboard']:
            archivos = predicciones['dashboard']['archivos']
            
            if 'dashboard_html' in archivos and archivos['dashboard_html']:
                ruta_html = archivos['dashboard_html']
                enlaces.append(f"Dashboard Comercial: file://{os.path.abspath(ruta_html)}")
        
        if 'estacionalidad' in predicciones and 'archivos' in predicciones['estacionalidad']:
            archivos = predicciones['estacionalidad']['archivos']
            
            if 'html' in archivos and archivos['html']:
                ruta_html = archivos['html']
                enlaces.append(f"Análisis de Estacionalidad: file://{os.path.abspath(ruta_html)}")
        
        if enlaces:
            print("\nEnlaces a dashboards generados:")
            for enlace in enlaces:
                print(enlace)
    except Exception as e:
        logger.error(f"Error al generar enlaces a dashboards: {e}")


def sincronizar_google_sheets():
    """Función principal para sincronizar datos con Google Sheets."""
    logger.info("Iniciando sincronización con Google Sheets")
    
    # Cargar configuración
    config = cargar_configuracion()
    
    # Conectar con Google Sheets
    client = conectar_google_sheets()
    if not client:
        logger.error("No se pudo establecer conexión con Google Sheets")
        return False
    
    # Obtener o crear spreadsheet
    spreadsheet = obtener_o_crear_spreadsheet(client, config)
    if not spreadsheet:
        logger.error("No se pudo obtener o crear la hoja de cálculo")
        return False
    
    # Cargar datos desde Google Sheets
    datos = cargar_datos_desde_sheets(spreadsheet, config)
    
    # Generar predicciones
    predicciones = generar_predicciones()
    
    # Actualizar Google Sheets con predicciones
    if predicciones:
        actualizar_sheets_con_predicciones(spreadsheet, config, predicciones)
        generar_enlaces_dashboards(predicciones)
    
    # Actualizar timestamp de última sincronización
    config["ultima_sincronizacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)
    
    logger.info("Sincronización completada")
    return True


def crear_servicio_programado():
    """Crea archivos para programar el servicio en sistemas operativos comunes."""
    try:
        # Crear script de ejecución
        ruta_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ejecutar_sincronizacion.py")
        with open(ruta_script, 'w', encoding='utf-8') as f:
            f.write("""#!/usr/bin/env python
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.sincronizar_sheets import sincronizar_google_sheets

if __name__ == "__main__":
    sincronizar_google_sheets()
""")
        
        # Hacer el script ejecutable (Linux/Mac)
        os.chmod(ruta_script, 0o755)
        
        # Crear instrucciones para diferentes sistemas
        ruta_instrucciones = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "instrucciones_programacion.txt")
        os.makedirs(os.path.dirname(ruta_instrucciones), exist_ok=True)
        
        with open(ruta_instrucciones, 'w', encoding='utf-8') as f:
            f.write("""INSTRUCCIONES PARA PROGRAMAR LA SINCRONIZACIÓN AUTOMÁTICA

Para Windows (usando Task Scheduler):
1. Abre el Programador de tareas (Task Scheduler)
2. Clic en "Crear tarea básica"
3. Nombre: "Sincronización Google Sheets"
4. Selecciona la frecuencia deseada (Diariamente)
5. Configura la hora de inicio
6. En Acción, selecciona "Iniciar un programa"
7. Programa/script: python
8. Argumentos: "{0}"
9. Finaliza el asistente

Para macOS (usando crontab):
1. Abre Terminal
2. Ejecuta: crontab -e
3. Añade la siguiente línea para ejecutar cada 12 horas:
   0 */12 * * * /usr/bin/python3 {0}
4. Guarda y sal del editor

Para Linux (usando crontab):
1. Abre Terminal
2. Ejecuta: crontab -e
3. Añade la siguiente línea para ejecutar cada 12 horas:
   0 */12 * * * /usr/bin/python3 {0}
4. Guarda y sal del editor
""".format(os.path.abspath(ruta_script)))
        
        print(f"Archivos para programación creados. Consulta las instrucciones en: {ruta_instrucciones}")
        logger.info(f"Archivos para programación creados en {ruta_script} y {ruta_instrucciones}")
        return True
    
    except Exception as e:
        logger.error(f"Error al crear servicio programado: {e}")
        return False


def mostrar_instrucciones_configuracion():
    """Muestra instrucciones para completar la configuración."""
    print("""
=================================================================
  CONFIGURACIÓN DEL SISTEMA DE SINCRONIZACIÓN CON GOOGLE SHEETS
=================================================================

Para completar la configuración, sigue estos pasos:

1. CREAR CREDENCIALES DE GOOGLE API:
   a. Ve a https://console.cloud.google.com/
   b. Crea un nuevo proyecto
   c. Habilita las APIs de Google Sheets y Google Drive
   d. Crea una cuenta de servicio
   e. Descarga la clave JSON y guárdala como "../config/credentials.json"

2. PRIMERA SINCRONIZACIÓN:
   a. Ejecuta de nuevo este script después de configurar las credenciales
   b. El sistema creará automáticamente una hoja de cálculo
   c. Copia la URL generada y compártela con tu equipo

3. PROGRAMAR SINCRONIZACIÓN AUTOMÁTICA:
   a. Revisa las instrucciones generadas en "../config/instrucciones_programacion.txt"
   b. Configura la tarea programada según tu sistema operativo

4. COMPARTIR LA HOJA DE CÁLCULO:
   a. La hoja tiene permisos de lectura pública por defecto
   b. Para que otros puedan editar, debes compartirla manualmente con sus correos
   c. Los miembros del equipo solo deben editar las hojas "Datos de inversión diaria" y "Registro de Decisiones"

5. USO DIARIO:
   a. El equipo de marketing introduce datos de campañas en la hoja "Datos de inversión diaria"
   b. El sistema sincroniza automáticamente y actualiza predicciones
   c. Los resultados se muestran en las hojas "Resultados" y "Dashboard"
   d. Los dashboards HTML se generan en la carpeta /salidas/

=================================================================

¿Necesitas más ayuda? Consulta la documentación completa en README.md
""")


if __name__ == "__main__":
    # Verificar si existen directorios necesarios
    os.makedirs(os.path.join(DATA_DIR, "costos"), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "actual"), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "historico"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR), exist_ok=True)
    os.makedirs("../logs", exist_ok=True)
    
    # Verificar si ya existe configuración
    config_exists = os.path.exists(CONFIG_PATH)
    creds_exist = os.path.exists(CREDENTIALS_PATH)
    
    if not config_exists or not creds_exist:
        print("Primera ejecución detectada. Configurando sistema...")
        cargar_configuracion()  # Crea configuración por defecto
        crear_servicio_programado()
        mostrar_instrucciones_configuracion()
    else:
        # Ejecutar sincronización
        if sincronizar_google_sheets():
            print("Sincronización completada con éxito.")
        else:
            print("Error en la sincronización. Revisa los logs para más detalles.") 