"""
Módulo para implementar un sistema de ajuste automático de presupuesto basado en rendimiento,
con monitoreo continuo y alertas tempranas.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class SistemaAjusteAutomatico:
    """
    Clase que implementa un sistema de ajuste automático de presupuesto
    basado en el rendimiento de las campañas y convocatorias.
    """
    
    def __init__(self, config_file=None):
        """
        Inicializa el sistema de ajuste automático.
        
        Args:
            config_file (str, optional): Ruta al archivo de configuración JSON.
        """
        # Cargar configuración desde archivo si se proporciona
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Configuración predeterminada
            self.config = {
                'umbrales': {
                    'cpa_muy_alto': 1.3,  # CPA actual > 130% del objetivo
                    'cpa_alto': 1.15,     # CPA actual > 115% del objetivo
                    'cpa_bajo': 0.85,     # CPA actual < 85% del objetivo
                    'cpa_muy_bajo': 0.7,  # CPA actual < 70% del objetivo
                    'conversion_baja': 0.5,  # Conversión < 50% de lo esperado
                    'presupuesto_agotado': 0.9,  # 90% del presupuesto gastado
                    'tiempo_agotado': 0.7,  # 70% del tiempo transcurrido
                },
                'alertas': {
                    'recipientes': [],  # Lista de correos para alertas
                    'nivel_minimo': 'medio',  # Nivel mínimo para enviar alertas ('bajo', 'medio', 'alto')
                },
                'ajustes': {
                    'max_incremento': 0.3,  # Máximo incremento de presupuesto (30%)
                    'max_reduccion': 0.4,   # Máxima reducción de presupuesto (40%)
                    'factor_tiempo': True,  # Considerar tiempo restante en ajustes
                    'intervalo_minimo': 3,  # Días mínimos entre ajustes
                },
                'historico': {
                    'directorio': '../datos/historico_ajustes/',  # Directorio para guardar histórico
                    'guardar_ajustes': True,  # Guardar registro de ajustes
                    'guardar_metricas': True,  # Guardar métricas diarias
                }
            }
        
        # Crear directorio para histórico si no existe
        if self.config['historico']['directorio'] and self.config['historico']['guardar_ajustes']:
            os.makedirs(self.config['historico']['directorio'], exist_ok=True)
        
        # Inicializar historiales
        self.historial_ajustes = pd.DataFrame()
        self.historial_alertas = pd.DataFrame()
    
    def guardar_configuracion(self, archivo):
        """
        Guarda la configuración actual en un archivo JSON.
        
        Args:
            archivo (str): Ruta del archivo donde guardar la configuración.
        """
        with open(archivo, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def analizar_rendimiento(self, df_rendimiento):
        """
        Analiza el rendimiento actual de las campañas y genera recomendaciones.
        
        Args:
            df_rendimiento (pandas.DataFrame): DataFrame con datos de rendimiento actual.
            
        Returns:
            pandas.DataFrame: DataFrame con análisis y recomendaciones.
        """
        # Verificar columnas necesarias
        columnas_requeridas = [
            'ID Convocatoria', 'Marca', 'Canal',
            'Presupuesto Asignado (USD)', 'Presupuesto Gastado (USD)',
            'CPA Actual (USD)', 'CPA Objetivo (USD)',
            'Fecha Inicio', 'Fecha Fin'
        ]
        
        for col in columnas_requeridas:
            if col not in df_rendimiento.columns:
                raise ValueError(f"El DataFrame debe contener la columna '{col}'")
        
        # Crear copia para no modificar el original
        df_analisis = df_rendimiento.copy()
        
        # Asegurar que las fechas sean datetime
        for col in ['Fecha Inicio', 'Fecha Fin']:
            if not pd.api.types.is_datetime64_dtype(df_analisis[col]):
                df_analisis[col] = pd.to_datetime(df_analisis[col])
        
        # Fecha actual para cálculos
        fecha_actual = datetime.now()
        
        # Calcular métricas adicionales
        df_analisis['Días Transcurridos'] = (fecha_actual - df_analisis['Fecha Inicio']).dt.days
        df_analisis['Días Totales'] = (df_analisis['Fecha Fin'] - df_analisis['Fecha Inicio']).dt.days
        df_analisis['Porcentaje Tiempo (%)'] = (df_analisis['Días Transcurridos'] / df_analisis['Días Totales'] * 100).clip(0, 100)
        
        df_analisis['Porcentaje Presupuesto (%)'] = (df_analisis['Presupuesto Gastado (USD)'] / df_analisis['Presupuesto Asignado (USD)'] * 100)
        df_analisis['Ratio CPA'] = df_analisis['CPA Actual (USD)'] / df_analisis['CPA Objetivo (USD)']
        
        # Determinar estado basado en umbrales
        condiciones_estado = [
            # Convocatoria no iniciada
            (df_analisis['Días Transcurridos'] <= 0),
            # Convocatoria finalizada
            (fecha_actual >= df_analisis['Fecha Fin']),
            # CPA muy alto (malo)
            (df_analisis['Ratio CPA'] >= self.config['umbrales']['cpa_muy_alto']),
            # CPA alto (precaución)
            (df_analisis['Ratio CPA'] >= self.config['umbrales']['cpa_alto']),
            # CPA óptimo
            (df_analisis['Ratio CPA'] >= self.config['umbrales']['cpa_bajo']) & 
            (df_analisis['Ratio CPA'] < self.config['umbrales']['cpa_alto']),
            # CPA bajo (bueno)
            (df_analisis['Ratio CPA'] >= self.config['umbrales']['cpa_muy_bajo']),
            # CPA muy bajo (excelente)
            (df_analisis['Ratio CPA'] < self.config['umbrales']['cpa_muy_bajo'])
        ]
        
        valores_estado = [
            'No Iniciada',
            'Finalizada',
            'CPA Crítico',
            'CPA Alto',
            'CPA Óptimo',
            'CPA Eficiente',
            'CPA Muy Eficiente'
        ]
        
        df_analisis['Estado'] = np.select(condiciones_estado, valores_estado, default='Indeterminado')
        
        # Determinar si requiere ajuste y qué tipo
        condiciones_ajuste = [
            # No ajustar convocatorias no iniciadas o finalizadas
            (df_analisis['Estado'].isin(['No Iniciada', 'Finalizada'])),
            # Reducir presupuesto para CPA crítico
            (df_analisis['Estado'] == 'CPA Crítico'),
            # Reducir ligeramente para CPA alto
            (df_analisis['Estado'] == 'CPA Alto'),
            # Mantener para CPA óptimo
            (df_analisis['Estado'] == 'CPA Óptimo'),
            # Aumentar ligeramente para CPA eficiente
            (df_analisis['Estado'] == 'CPA Eficiente'),
            # Aumentar significativamente para CPA muy eficiente
            (df_analisis['Estado'] == 'CPA Muy Eficiente')
        ]
        
        valores_ajuste = [
            'No Ajustar',
            'Reducir Significativamente',
            'Reducir Moderadamente',
            'Mantener',
            'Aumentar Moderadamente',
            'Aumentar Significativamente'
        ]
        
        df_analisis['Recomendación'] = np.select(condiciones_ajuste, valores_ajuste, default='Revisar Manualmente')
        
        # Calcular factor de ajuste recomendado
        factores_base = {
            'Reducir Significativamente': -0.25,
            'Reducir Moderadamente': -0.15,
            'Mantener': 0.0,
            'Aumentar Moderadamente': 0.15,
            'Aumentar Significativamente': 0.25,
            'No Ajustar': 0.0,
            'Revisar Manualmente': 0.0
        }
        
        df_analisis['Factor Base'] = df_analisis['Recomendación'].map(factores_base)
        
        # Ajustar según tiempo restante
        if self.config['ajustes']['factor_tiempo']:
            # Inversamente proporcional al tiempo transcurrido (más conservador hacia el final)
            df_analisis['Factor Tiempo'] = 1 - (df_analisis['Porcentaje Tiempo (%)'] / 100)
            df_analisis['Factor Ajuste'] = df_analisis['Factor Base'] * df_analisis['Factor Tiempo']
        else:
            df_analisis['Factor Ajuste'] = df_analisis['Factor Base']
        
        # Aplicar límites de ajuste
        df_analisis['Factor Ajuste'] = df_analisis['Factor Ajuste'].clip(
            -self.config['ajustes']['max_reduccion'],
            self.config['ajustes']['max_incremento']
        )
        
        # Calcular presupuesto ajustado
        df_analisis['Presupuesto Ajustado (USD)'] = df_analisis['Presupuesto Asignado (USD)'] * (1 + df_analisis['Factor Ajuste'])
        df_analisis['Cambio Presupuesto (USD)'] = df_analisis['Presupuesto Ajustado (USD)'] - df_analisis['Presupuesto Asignado (USD)']
        df_analisis['Cambio Porcentual (%)'] = (df_analisis['Cambio Presupuesto (USD)'] / df_analisis['Presupuesto Asignado (USD)'] * 100)
        
        # Determinar nivel de urgencia para alertas
        condiciones_urgencia = [
            (df_analisis['Estado'] == 'CPA Crítico'),
            (df_analisis['Estado'] == 'CPA Alto'),
            (df_analisis['Estado'].isin(['CPA Óptimo', 'CPA Eficiente', 'CPA Muy Eficiente'])),
            (df_analisis['Estado'].isin(['No Iniciada', 'Finalizada']))
        ]
        
        valores_urgencia = ['alto', 'medio', 'bajo', 'ninguno']
        
        df_analisis['Nivel Urgencia'] = np.select(condiciones_urgencia, valores_urgencia, default='bajo')
        
        return df_analisis
    
    def aplicar_ajustes(self, df_analisis, simular=True):
        """
        Aplica los ajustes recomendados o simula su aplicación.
        
        Args:
            df_analisis (pandas.DataFrame): DataFrame con análisis y recomendaciones.
            simular (bool): Si es True, solo simula los ajustes sin aplicarlos.
            
        Returns:
            pandas.DataFrame: DataFrame con resultados de los ajustes.
        """
        # Filtrar solo convocatorias que requieren ajuste
        df_ajustar = df_analisis[~df_analisis['Recomendación'].isin(['No Ajustar', 'Revisar Manualmente'])].copy()
        
        if df_ajustar.empty:
            return pd.DataFrame({"Mensaje": ["No hay campañas que requieran ajustes automáticos"]})
        
        # Verificar último ajuste para cada convocatoria
        if not self.historial_ajustes.empty:
            for idx, row in df_ajustar.iterrows():
                # Buscar último ajuste para esta convocatoria
                ultimos_ajustes = self.historial_ajustes[
                    (self.historial_ajustes['ID Convocatoria'] == row['ID Convocatoria']) &
                    (self.historial_ajustes['Marca'] == row['Marca']) &
                    (self.historial_ajustes['Canal'] == row['Canal'])
                ]
                
                if not ultimos_ajustes.empty:
                    ultimo_ajuste = ultimos_ajustes['Fecha Ajuste'].max()
                    dias_desde_ultimo = (datetime.now() - ultimo_ajuste).days
                    
                    # Si no ha pasado el intervalo mínimo, no ajustar
                    if dias_desde_ultimo < self.config['ajustes']['intervalo_minimo']:
                        df_ajustar.loc[idx, 'Recomendación'] = 'Intervalo Insuficiente'
                        df_ajustar.loc[idx, 'Factor Ajuste'] = 0
                        df_ajustar.loc[idx, 'Presupuesto Ajustado (USD)'] = row['Presupuesto Asignado (USD)']
                        df_ajustar.loc[idx, 'Cambio Presupuesto (USD)'] = 0
                        df_ajustar.loc[idx, 'Cambio Porcentual (%)'] = 0
        
        # Preparar resultados de ajustes
        resultados = df_ajustar.copy()
        resultados['Fecha Ajuste'] = datetime.now()
        resultados['Simulado'] = simular
        
        # Si no es simulación, registrar los ajustes realizados
        if not simular and self.config['historico']['guardar_ajustes']:
            # Preparar datos para guardar
            ajustes_aplicados = resultados[[
                'ID Convocatoria', 'Marca', 'Canal', 
                'Presupuesto Asignado (USD)', 'Presupuesto Ajustado (USD)',
                'Cambio Presupuesto (USD)', 'Cambio Porcentual (%)',
                'Estado', 'Recomendación', 'Fecha Ajuste'
            ]].copy()
            
            # Añadir al historial
            self.historial_ajustes = pd.concat([self.historial_ajustes, ajustes_aplicados])
            
            # Guardar historial actualizado
            fecha_str = datetime.now().strftime('%Y-%m-%d')
            archivo_historial = os.path.join(
                self.config['historico']['directorio'],
                f'ajustes_historico_{fecha_str}.csv'
            )
            
            self.historial_ajustes.to_csv(archivo_historial, index=False)
        
        return resultados
    
    def generar_alertas(self, df_analisis):
        """
        Genera alertas basadas en el análisis de rendimiento.
        
        Args:
            df_analisis (pandas.DataFrame): DataFrame con análisis de rendimiento.
            
        Returns:
            pandas.DataFrame: DataFrame con alertas generadas.
        """
        # Niveles de urgencia en orden
        niveles_urgencia = {
            'alto': 3,
            'medio': 2,
            'bajo': 1,
            'ninguno': 0
        }
        
        # Nivel mínimo de urgencia para alertar
        nivel_minimo = niveles_urgencia.get(self.config['alertas']['nivel_minimo'], 1)
        
        # Filtrar alertas según nivel de urgencia
        df_alertas = df_analisis[
            df_analisis['Nivel Urgencia'].map(lambda x: niveles_urgencia.get(x, 0)) >= nivel_minimo
        ].copy()
        
        if df_alertas.empty:
            return pd.DataFrame({"Mensaje": ["No hay alertas que cumplan el nivel mínimo de urgencia"]})
        
        # Añadir información adicional para las alertas
        df_alertas['Fecha Alerta'] = datetime.now()
        df_alertas['Mensaje Alerta'] = df_alertas.apply(
            lambda row: self._generar_mensaje_alerta(row),
            axis=1
        )
        
        # Añadir al historial de alertas
        self.historial_alertas = pd.concat([self.historial_alertas, df_alertas[
            ['ID Convocatoria', 'Marca', 'Canal', 'Estado', 'Nivel Urgencia', 'Mensaje Alerta', 'Fecha Alerta']
        ]])
        
        return df_alertas
    
    def _generar_mensaje_alerta(self, fila):
        """
        Genera un mensaje de alerta basado en el estado de una convocatoria.
        
        Args:
            fila (pandas.Series): Datos de una convocatoria.
            
        Returns:
            str: Mensaje de alerta.
        """
        if fila['Estado'] == 'CPA Crítico':
            return (f"¡ALERTA CRÍTICA! La campaña '{fila['Canal']}' de '{fila['Marca']}' tiene un CPA muy alto "
                   f"({fila['CPA Actual (USD)']:.2f} USD vs objetivo {fila['CPA Objetivo (USD)']:.2f} USD). "
                   f"Se recomienda reducir presupuesto en {abs(fila['Cambio Porcentual (%)']):.1f}%.")
        
        elif fila['Estado'] == 'CPA Alto':
            return (f"ALERTA: La campaña '{fila['Canal']}' de '{fila['Marca']}' tiene un CPA por encima del objetivo "
                   f"({fila['CPA Actual (USD)']:.2f} USD vs {fila['CPA Objetivo (USD)']:.2f} USD). "
                   f"Se recomienda reducir presupuesto en {abs(fila['Cambio Porcentual (%)']):.1f}%.")
        
        elif fila['Estado'] == 'CPA Muy Eficiente':
            return (f"OPORTUNIDAD: La campaña '{fila['Canal']}' de '{fila['Marca']}' está teniendo un rendimiento excepcional "
                   f"(CPA {fila['CPA Actual (USD)']:.2f} USD, {(1-fila['Ratio CPA'])*100:.1f}% por debajo del objetivo). "
                   f"Se recomienda aumentar presupuesto en {fila['Cambio Porcentual (%)']:.1f}%.")
        
        return f"Alerta para '{fila['Canal']}' de '{fila['Marca']}': Estado {fila['Estado']}"
    
    def enviar_alertas_email(self, df_alertas, graficos=None):
        """
        Envía alertas por correo electrónico.
        
        Args:
            df_alertas (pandas.DataFrame): DataFrame con alertas a enviar.
            graficos (dict, optional): Diccionario con rutas a gráficos para incluir.
            
        Returns:
            bool: True si el envío fue exitoso, False en caso contrario.
        """
        # Verificar si hay destinatarios configurados
        if not self.config['alertas']['recipientes']:
            return False
        
        try:
            # Configuración del servidor de correo (esto se debería configurar en un archivo aparte)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            smtp_user = "sistema.alertas@ejemplo.com"
            smtp_password = "password_seguro"  # Usar variables de entorno en producción
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = ', '.join(self.config['alertas']['recipientes'])
            msg['Subject'] = f"Alertas Sistema de Campaña - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Crear cuerpo del mensaje en HTML
            cuerpo_html = """
            <html>
            <head>
                <style>
                    table { border-collapse: collapse; width: 100%; }
                    th, td { text-align: left; padding: 8px; border: 1px solid #ddd; }
                    tr:nth-child(even) { background-color: #f2f2f2; }
                    th { background-color: #4CAF50; color: white; }
                    .alto { color: red; font-weight: bold; }
                    .medio { color: orange; }
                    .bajo { color: green; }
                </style>
            </head>
            <body>
                <h1>Alertas de Rendimiento de Campañas</h1>
                <p>Se han detectado las siguientes alertas que requieren atención:</p>
                <table>
                    <tr>
                        <th>Marca</th>
                        <th>Canal</th>
                        <th>Estado</th>
                        <th>Nivel</th>
                        <th>Mensaje</th>
                    </tr>
            """
            
            # Añadir filas para cada alerta
            for _, alerta in df_alertas.iterrows():
                cuerpo_html += f"""
                    <tr>
                        <td>{alerta['Marca']}</td>
                        <td>{alerta['Canal']}</td>
                        <td>{alerta['Estado']}</td>
                        <td class="{alerta['Nivel Urgencia']}">{alerta['Nivel Urgencia'].upper()}</td>
                        <td>{alerta['Mensaje Alerta']}</td>
                    </tr>
                """
            
            cuerpo_html += """
                </table>
                <p>Este es un mensaje automático, por favor no responda a este correo.</p>
            </body>
            </html>
            """
            
            # Adjuntar HTML
            msg.attach(MIMEText(cuerpo_html, 'html'))
            
            # Adjuntar gráficos si se proporcionan
            if graficos:
                for nombre, ruta in graficos.items():
                    if os.path.exists(ruta):
                        with open(ruta, 'rb') as archivo:
                            adjunto = MIMEBase('application', 'octet-stream')
                            adjunto.set_payload(archivo.read())
                            encoders.encode_base64(adjunto)
                            adjunto.add_header(
                                'Content-Disposition',
                                f'attachment; filename={os.path.basename(ruta)}'
                            )
                            msg.attach(adjunto)
            
            # Enviar correo
            with smtplib.SMTP(smtp_server, smtp_port) as servidor:
                servidor.starttls()
                servidor.login(smtp_user, smtp_password)
                servidor.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error al enviar alertas por correo: {e}")
            return False


def visualizar_rendimiento_campanas(df_analisis):
    """
    Genera visualizaciones del rendimiento de las campañas.
    
    Args:
        df_analisis (pandas.DataFrame): DataFrame con análisis de rendimiento.
        
    Returns:
        dict: Diccionario con figuras generadas.
    """
    figuras = {}
    
    # 1. Gráfico de CPA actual vs objetivo
    fig1, ax1 = plt.subplots(figsize=(12, 8))
    
    # Ordenar por ratio de CPA
    df_plot = df_analisis.sort_values('Ratio CPA', ascending=False).copy()
    
    # Crear etiquetas combinadas
    df_plot['Etiqueta'] = df_plot['Canal'] + ' - ' + df_plot['Marca']
    
    # Colores según estado
    colores = {
        'CPA Crítico': 'red',
        'CPA Alto': 'orange',
        'CPA Óptimo': 'green',
        'CPA Eficiente': 'lightgreen',
        'CPA Muy Eficiente': 'blue',
        'No Iniciada': 'gray',
        'Finalizada': 'lightgray'
    }
    
    df_plot['Color'] = df_plot['Estado'].map(colores)
    
    # Crear barras para CPA actual
    barras = ax1.barh(df_plot['Etiqueta'], df_plot['CPA Actual (USD)'], color=df_plot['Color'], alpha=0.7)
    
    # Añadir línea para CPA objetivo
    for i, row in df_plot.iterrows():
        ax1.plot(
            [row['CPA Objetivo (USD)'], row['CPA Objetivo (USD)']],
            [i - 0.4, i + 0.4],
            color='black',
            linestyle='--',
            linewidth=2
        )
    
    # Añadir etiquetas con valores
    for i, bar in enumerate(barras):
        valor = bar.get_width()
        objetivo = df_plot.iloc[i]['CPA Objetivo (USD)']
        ratio = valor / objetivo if objetivo > 0 else 0
        
        ax1.text(
            valor + 5,
            bar.get_y() + bar.get_height() / 2,
            f"{valor:.0f} USD ({ratio:.2f}x)",
            va='center',
            fontsize=8
        )
    
    # Configurar gráfico
    ax1.set_title('CPA Actual vs Objetivo por Canal')
    ax1.set_xlabel('CPA (USD)')
    ax1.grid(axis='x', linestyle='--', alpha=0.3)
    
    # Crear leyenda manual
    from matplotlib.patches import Patch
    elementos_leyenda = [
        Patch(facecolor=colores[estado], label=estado)
        for estado in colores.keys()
        if estado in df_plot['Estado'].values
    ]
    ax1.legend(handles=elementos_leyenda, loc='upper right')
    
    figuras['cpa_vs_objetivo'] = fig1
    
    # 2. Gráfico de avance de presupuesto vs tiempo
    fig2, ax2 = plt.subplots(figsize=(12, 8))
    
    # Filtrar campañas activas
    df_activas = df_analisis[~df_analisis['Estado'].isin(['No Iniciada', 'Finalizada'])].copy()
    
    if not df_activas.empty:
        # Scatter plot de tiempo vs presupuesto
        scatter = ax2.scatter(
            df_activas['Porcentaje Tiempo (%)'],
            df_activas['Porcentaje Presupuesto (%)'],
            s=100,
            c=df_activas['Ratio CPA'].map(lambda x: plt.cm.RdYlGn_r(x/2)),
            alpha=0.7
        )
        
        # Añadir etiquetas a los puntos
        for i, row in df_activas.iterrows():
            ax2.annotate(
                f"{row['Canal']} - {row['Marca']}",
                (row['Porcentaje Tiempo (%)'], row['Porcentaje Presupuesto (%)']),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=8
            )
        
        # Añadir línea diagonal (ideal)
        ax2.plot([0, 100], [0, 100], 'k--', alpha=0.5)
        
        # Añadir líneas de cuadrantes
        ax2.axvline(x=50, color='gray', linestyle=':', alpha=0.5)
        ax2.axhline(y=50, color='gray', linestyle=':', alpha=0.5)
        
        # Añadir colorbar para mostrar CPA
        cbar = plt.colorbar(scatter)
        cbar.set_label('Ratio CPA (Actual/Objetivo)')
        
        # Configurar gráfico
        ax2.set_title('Avance de Presupuesto vs Tiempo')
        ax2.set_xlabel('Porcentaje de Tiempo Transcurrido (%)')
        ax2.set_ylabel('Porcentaje de Presupuesto Gastado (%)')
        ax2.set_xlim(0, 105)
        ax2.set_ylim(0, 105)
        ax2.grid(True, linestyle='--', alpha=0.3)
        
        # Añadir texto explicativo en cuadrantes
        ax2.text(25, 75, "Gasto Acelerado", ha='center', fontsize=10, style='italic', bbox=dict(facecolor='white', alpha=0.5))
        ax2.text(75, 25, "Gasto Retrasado", ha='center', fontsize=10, style='italic', bbox=dict(facecolor='white', alpha=0.5))
        ax2.text(25, 25, "Fase Inicial", ha='center', fontsize=10, style='italic', bbox=dict(facecolor='white', alpha=0.5))
        ax2.text(75, 75, "Fase Final", ha='center', fontsize=10, style='italic', bbox=dict(facecolor='white', alpha=0.5))
    
    figuras['avance_presupuesto'] = fig2
    
    # 3. Gráfico de barras para cambios recomendados
    fig3, ax3 = plt.subplots(figsize=(12, 8))
    
    # Filtrar solo convocatorias que requieren ajuste
    df_ajustes = df_analisis[~df_analisis['Recomendación'].isin(['No Ajustar', 'Revisar Manualmente'])].copy()
    
    if not df_ajustes.empty:
        # Ordenar por cambio porcentual
        df_ajustes = df_ajustes.sort_values('Cambio Porcentual (%)')
        
        # Colores según tipo de cambio
        colores_cambio = df_ajustes['Cambio Porcentual (%)'].map(
            lambda x: 'green' if x > 5 else 'lightgreen' if x > 0 else 
                     'orange' if x > -15 else 'red'
        )
        
        # Crear barras
        barras = ax3.barh(
            df_ajustes['Canal'] + ' - ' + df_ajustes['Marca'],
            df_ajustes['Cambio Porcentual (%)'],
            color=colores_cambio,
            alpha=0.7
        )
        
        # Añadir etiquetas con valores
        for i, bar in enumerate(barras):
            valor = bar.get_width()
            ax3.text(
                valor + (1 if valor >= 0 else -1),
                bar.get_y() + bar.get_height() / 2,
                f"{valor:.1f}%",
                va='center',
                ha='left' if valor >= 0 else 'right',
                fontsize=9
            )
        
        # Configurar gráfico
        ax3.set_title('Cambios de Presupuesto Recomendados')
        ax3.set_xlabel('Cambio Porcentual (%)')
        ax3.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        ax3.grid(axis='x', linestyle='--', alpha=0.3)
    
    figuras['cambios_recomendados'] = fig3
    
    return figuras


def guardar_visualizaciones(figuras, directorio='../salidas'):
    """
    Guarda las visualizaciones en el directorio especificado.
    
    Args:
        figuras (dict): Diccionario con figuras a guardar.
        directorio (str): Directorio donde guardar las figuras.
        
    Returns:
        dict: Diccionario con rutas de archivos guardados.
    """
    # Crear directorio si no existe
    os.makedirs(directorio, exist_ok=True)
    
    # Fecha para nombres de archivo
    fecha_str = datetime.now().strftime('%Y-%m-%d_%H%M')
    
    # Guardar cada figura
    rutas = {}
    
    for nombre, figura in figuras.items():
        ruta_archivo = os.path.join(directorio, f'{nombre}_{fecha_str}.png')
        figura.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
        plt.close(figura)
        rutas[nombre] = ruta_archivo
    
    return rutas


if __name__ == "__main__":
    # Ejemplo de uso
    from cargar_datos import cargar_datos_crm, cargar_datos_planificacion
    from validar_datos import validar_datos_crm, validar_datos_planificacion
    from predecir_matriculas import predecir_matriculas
    
    try:
        datos_crm = cargar_datos_crm("../datos/leads_matriculas_reales.csv")
        datos_planificacion = cargar_datos_planificacion("../datos/planificacion_quincenal.csv")
        
        validar_datos_crm(datos_crm)
        validar_datos_planificacion(datos_planificacion)
        
        prediccion = predecir_matriculas(datos_crm, datos_planificacion)
        
        # Simular datos de rendimiento actual
        df_rendimiento = prediccion.copy()
        df_rendimiento['CPA Actual (USD)'] = df_rendimiento['CPA Esperado (USD)'] * np.random.uniform(0.7, 1.3, len(df_rendimiento))
        df_rendimiento['CPA Objetivo (USD)'] = 200  # Ejemplo de CPA objetivo
        df_rendimiento['Presupuesto Gastado (USD)'] = df_rendimiento['Presupuesto Asignado (USD)'] * np.random.uniform(0.2, 0.8, len(df_rendimiento))
        
        # Inicializar sistema de ajuste automático
        sistema = SistemaAjusteAutomatico()
        
        # Guardar configuración para referencia
        sistema.guardar_configuracion("../salidas/config_sistema_ajuste.json")
        
        # Analizar rendimiento
        analisis = sistema.analizar_rendimiento(df_rendimiento)
        
        print("Análisis de rendimiento:")
        print(analisis[['Marca', 'Canal', 'CPA Actual (USD)', 'CPA Objetivo (USD)', 
                       'Ratio CPA', 'Estado', 'Recomendación', 'Factor Ajuste']])
        
        # Simular ajustes
        ajustes = sistema.aplicar_ajustes(analisis, simular=True)
        
        print("\nAjustes recomendados:")
        print(ajustes[['Marca', 'Canal', 'Presupuesto Asignado (USD)', 
                      'Presupuesto Ajustado (USD)', 'Cambio Porcentual (%)']])
        
        # Generar alertas
        alertas = sistema.generar_alertas(analisis)
        
        print("\nAlertas generadas:")
        print(alertas[['Marca', 'Canal', 'Estado', 'Nivel Urgencia', 'Mensaje Alerta']])
        
        # Generar visualizaciones
        figuras = visualizar_rendimiento_campanas(analisis)
        
        # Guardar visualizaciones
        rutas = guardar_visualizaciones(figuras)
        
        print("\nVisualizaciones guardadas en:")
        for nombre, ruta in rutas.items():
            print(f"- {nombre}: {ruta}")
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}") 