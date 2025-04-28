"""
Módulo para generar reportes y visualizaciones de datos de marketing.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import xlsxwriter
import json

# Configurar estilo de visualización
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("Set2")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


def crear_directorio_reportes(directorio='../reportes'):
    """
    Crea un directorio para almacenar los reportes si no existe.
    
    Args:
        directorio (str): Ruta del directorio a crear.
        
    Returns:
        str: Ruta del directorio creado.
    """
    # Crear directorio si no existe
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    
    # Crear subdirectorio con la fecha actual
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    directorio_fecha = os.path.join(directorio, fecha_actual)
    
    if not os.path.exists(directorio_fecha):
        os.makedirs(directorio_fecha)
    
    return directorio_fecha


def generar_reporte_excel(datos_metricas, nombre_archivo, directorio=None):
    """
    Genera un reporte Excel con los datos y métricas calculadas.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas calculadas.
        nombre_archivo (str): Nombre del archivo Excel.
        directorio (str, opcional): Directorio donde guardar el archivo.
        
    Returns:
        str: Ruta completa del archivo generado.
    """
    # Crear directorio si no se especifica
    if directorio is None:
        directorio = crear_directorio_reportes()
    
    # Asegurar que el nombre de archivo termine en .xlsx
    if not nombre_archivo.endswith('.xlsx'):
        nombre_archivo += '.xlsx'
    
    # Ruta completa del archivo
    ruta_archivo = os.path.join(directorio, nombre_archivo)
    
    # Crear el escritor de Excel
    writer = pd.ExcelWriter(ruta_archivo, engine='xlsxwriter')
    
    # Convertir a formato porcentual para mejor visualización
    df_formato = datos_metricas.copy()
    
    # Aplicar formato a columnas de porcentaje
    columnas_porcentaje = [col for col in df_formato.columns if '%' in col or 'Tasa' in col]
    for col in columnas_porcentaje:
        df_formato[col] = df_formato[col] / 100
    
    # Guardar en Excel
    df_formato.to_excel(writer, sheet_name='Métricas', index=False)
    
    # Obtener el libro y la hoja de trabajo
    workbook = writer.book
    worksheet = writer.sheets['Métricas']
    
    # Definir formatos
    formato_moneda = workbook.add_format({'num_format': '$#,##0.00'})
    formato_porcentaje = workbook.add_format({'num_format': '0.00%'})
    formato_numero = workbook.add_format({'num_format': '#,##0'})
    formato_encabezado = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'bg_color': '#D9E1F2',
        'border': 1
    })
    
    # Aplicar formatos a columnas específicas
    for idx, col in enumerate(df_formato.columns):
        # Aplicar formato de encabezado a la primera fila
        worksheet.write(0, idx, col, formato_encabezado)
        
        # Aplicar formatos específicos a las columnas
        if 'USD' in col or 'CPA' in col or 'CPL' in col:
            worksheet.set_column(idx, idx, 15, formato_moneda)
        elif '%' in col or 'Tasa' in col:
            worksheet.set_column(idx, idx, 15, formato_porcentaje)
        elif 'Leads' in col or 'Matrículas' in col:
            worksheet.set_column(idx, idx, 12, formato_numero)
        else:
            worksheet.set_column(idx, idx, 15)
    
    # Agregar filtros automáticos
    worksheet.autofilter(0, 0, len(df_formato), len(df_formato.columns) - 1)
    
    # Guardar el archivo
    writer.close()
    
    return ruta_archivo


def visualizar_rendimiento_por_canal(datos_metricas, metricas_a_visualizar, directorio=None):
    """
    Genera visualizaciones del rendimiento por canal y marca.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas calculadas.
        metricas_a_visualizar (list): Lista de métricas a visualizar.
        directorio (str, opcional): Directorio donde guardar las visualizaciones.
        
    Returns:
        list: Lista de rutas de los archivos generados.
    """
    # Crear directorio si no se especifica
    if directorio is None:
        directorio = crear_directorio_reportes()
    
    archivos_generados = []
    
    # Agrupar datos por marca y canal
    datos_agrupados = datos_metricas.groupby(['Marca', 'Canal']).agg({
        'Leads': 'sum',
        'Matrículas': 'sum',
        'Tasa Conversión': 'mean',
        'CPA': 'mean',
        'CPL': 'mean',
        'Presupuesto Asignado (USD)': 'sum'
    }).reset_index()
    
    # Generar visualizaciones para cada métrica solicitada
    for metrica in metricas_a_visualizar:
        if metrica not in datos_agrupados.columns:
            print(f"Advertencia: La métrica '{metrica}' no está disponible en los datos.")
            continue
        
        plt.figure(figsize=(12, 7))
        
        # Crear gráfico de barras
        ax = sns.barplot(x='Canal', y=metrica, hue='Marca', data=datos_agrupados)
        
        # Configurar títulos y etiquetas
        plt.title(f'{metrica} por Canal y Marca', fontsize=14)
        plt.xlabel('Canal', fontsize=12)
        plt.ylabel(metrica, fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        # Añadir valores en las barras
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f' if 'Tasa' in metrica else '%.0f')
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar figura
        nombre_archivo = f'rendimiento_{metrica.lower().replace(" ", "_")}_por_canal.png'
        ruta_archivo = os.path.join(directorio, nombre_archivo)
        plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
        plt.close()
        
        archivos_generados.append(ruta_archivo)
    
    return archivos_generados


def visualizar_tendencias(datos_tendencias, metricas_a_visualizar, directorio=None):
    """
    Genera visualizaciones de tendencias temporales de métricas.
    
    Args:
        datos_tendencias (pandas.DataFrame): DataFrame con tendencias calculadas.
        metricas_a_visualizar (list): Lista de métricas a visualizar.
        directorio (str, opcional): Directorio donde guardar las visualizaciones.
        
    Returns:
        list: Lista de rutas de los archivos generados.
    """
    # Crear directorio si no se especifica
    if directorio is None:
        directorio = crear_directorio_reportes()
    
    archivos_generados = []
    
    # Generar visualizaciones para cada métrica solicitada
    for metrica in metricas_a_visualizar:
        if metrica not in datos_tendencias.columns:
            print(f"Advertencia: La métrica '{metrica}' no está disponible en los datos.")
            continue
        
        # Crear una figura por cada marca
        for marca in datos_tendencias['Marca'].unique():
            plt.figure(figsize=(12, 7))
            
            # Filtrar datos por marca
            df_marca = datos_tendencias[datos_tendencias['Marca'] == marca]
            
            # Crear gráfico de líneas
            ax = sns.lineplot(
                data=df_marca,
                x='Periodo',
                y=metrica,
                hue='Canal',
                marker='o',
                linewidth=2
            )
            
            # Configurar títulos y etiquetas
            plt.title(f'Tendencia de {metrica} - {marca}', fontsize=14)
            plt.xlabel('Periodo', fontsize=12)
            plt.ylabel(metrica, fontsize=12)
            plt.xticks(rotation=45, ha='right')
            
            # Añadir valores en los puntos
            for line in ax.lines:
                for x, y in zip(line.get_xdata(), line.get_ydata()):
                    if not pd.isna(y):
                        ax.annotate(
                            f"{y:.1f}" if 'Tasa' in metrica else f"{y:.0f}",
                            (x, y),
                            textcoords="offset points",
                            xytext=(0, 5),
                            ha='center',
                            fontsize=8
                        )
            
            # Ajustar layout
            plt.tight_layout()
            
            # Guardar figura
            nombre_archivo = f'tendencia_{metrica.lower().replace(" ", "_")}_{marca.lower()}.png'
            ruta_archivo = os.path.join(directorio, nombre_archivo)
            plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
            plt.close()
            
            archivos_generados.append(ruta_archivo)
    
    return archivos_generados


def generar_alertas_automaticas(datos_metricas, umbral_desviacion=20, directorio=None):
    """
    Genera alertas automáticas cuando métricas clave se desvían significativamente.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas calculadas.
        umbral_desviacion (float): Umbral de desviación porcentual para generar alertas.
        directorio (str, opcional): Directorio donde guardar las visualizaciones.
        
    Returns:
        tuple: DataFrame con alertas y ruta del archivo de visualización.
    """
    # Crear directorio si no se especifica
    if directorio is None:
        directorio = crear_directorio_reportes()
    
    # Verificar columnas necesarias
    columnas_requeridas = ['Marca', 'Canal', 'CPA', 'Tasa Conversión']
    for col in columnas_requeridas:
        if col not in datos_metricas.columns:
            raise ValueError(f"El DataFrame debe contener la columna '{col}'")
    
    # Agrupar datos por marca y canal
    datos_agrupados = datos_metricas.groupby(['Marca', 'Canal']).agg({
        'CPA': 'mean',
        'Tasa Conversión': 'mean',
        'Leads': 'sum',
        'Matrículas': 'sum'
    }).reset_index()
    
    # Calcular CPA y Tasa de Conversión promedio global
    cpa_promedio = datos_agrupados['CPA'].mean()
    tasa_promedio = datos_agrupados['Tasa Conversión'].mean()
    
    # Calcular desviaciones
    datos_agrupados['Desviación CPA (%)'] = ((datos_agrupados['CPA'] - cpa_promedio) / cpa_promedio) * 100
    datos_agrupados['Desviación Tasa Conversión (pp)'] = datos_agrupados['Tasa Conversión'] - tasa_promedio
    
    # Identificar alertas
    alertas = []
    
    # Alertas de CPA alto
    cpa_alto = datos_agrupados[datos_agrupados['Desviación CPA (%)'] > umbral_desviacion]
    for _, row in cpa_alto.iterrows():
        alertas.append({
            'Tipo': 'CPA Alto',
            'Marca': row['Marca'],
            'Canal': row['Canal'],
            'Valor Actual': row['CPA'],
            'Valor Promedio': cpa_promedio,
            'Desviación (%)': row['Desviación CPA (%)'],
            'Severidad': 'Alta' if row['Desviación CPA (%)'] > 2*umbral_desviacion else 'Media',
            'Impacto': 'Negativo',
            'Recomendación': 'Revisar estrategia de campaña y segmentación'
        })
    
    # Alertas de CPA bajo (positivo)
    cpa_bajo = datos_agrupados[datos_agrupados['Desviación CPA (%)'] < -umbral_desviacion]
    for _, row in cpa_bajo.iterrows():
        alertas.append({
            'Tipo': 'CPA Bajo',
            'Marca': row['Marca'],
            'Canal': row['Canal'],
            'Valor Actual': row['CPA'],
            'Valor Promedio': cpa_promedio,
            'Desviación (%)': row['Desviación CPA (%)'],
            'Severidad': 'Baja',
            'Impacto': 'Positivo',
            'Recomendación': 'Considerar aumentar inversión en este canal'
        })
    
    # Alertas de tasa de conversión baja
    tasa_baja = datos_agrupados[datos_agrupados['Desviación Tasa Conversión (pp)'] < -umbral_desviacion/100]
    for _, row in tasa_baja.iterrows():
        alertas.append({
            'Tipo': 'Conversión Baja',
            'Marca': row['Marca'],
            'Canal': row['Canal'],
            'Valor Actual': row['Tasa Conversión'],
            'Valor Promedio': tasa_promedio,
            'Desviación (pp)': row['Desviación Tasa Conversión (pp)'],
            'Severidad': 'Alta' if row['Desviación Tasa Conversión (pp)'] < -2*umbral_desviacion/100 else 'Media',
            'Impacto': 'Negativo',
            'Recomendación': 'Revisar calidad de leads y proceso de conversión'
        })
    
    # Alertas de tasa de conversión alta (positivo)
    tasa_alta = datos_agrupados[datos_agrupados['Desviación Tasa Conversión (pp)'] > umbral_desviacion/100]
    for _, row in tasa_alta.iterrows():
        alertas.append({
            'Tipo': 'Conversión Alta',
            'Marca': row['Marca'],
            'Canal': row['Canal'],
            'Valor Actual': row['Tasa Conversión'],
            'Valor Promedio': tasa_promedio,
            'Desviación (pp)': row['Desviación Tasa Conversión (pp)'],
            'Severidad': 'Baja',
            'Impacto': 'Positivo',
            'Recomendación': 'Replicar estrategia en otros canales'
        })
    
    # Convertir a DataFrame
    df_alertas = pd.DataFrame(alertas)
    
    # Si no hay alertas, devolver DataFrame vacío
    if df_alertas.empty:
        return df_alertas, None
    
    # Generar visualización de alertas
    plt.figure(figsize=(14, 8))
    
    # Preparar datos para visualización
    df_plot = df_alertas.copy()
    df_plot['Valor'] = np.where(
        df_plot['Tipo'].str.contains('CPA'),
        df_plot['Desviación (%)'],
        df_plot['Desviación (pp)'] * 100  # Convertir a porcentaje para visualización
    )
    
    # Crear paleta de colores según impacto
    colors = {'Positivo': 'green', 'Negativo': 'red'}
    
    # Crear gráfico de barras
    ax = sns.barplot(
        x='Canal',
        y='Valor',
        hue='Tipo',
        data=df_plot,
        palette='Set2'
    )
    
    # Colorear barras según impacto
    for i, imp in enumerate(df_plot['Impacto']):
        ax.patches[i].set_alpha(0.7 if imp == 'Positivo' else 0.9)
        if imp == 'Positivo':
            ax.patches[i].set_edgecolor('green')
            ax.patches[i].set_linewidth(2)
    
    # Configurar títulos y etiquetas
    plt.title('Alertas Automáticas de Desviaciones Significativas', fontsize=14)
    plt.xlabel('Canal', fontsize=12)
    plt.ylabel('Desviación (%)', fontsize=12)
    plt.axhline(y=0, color='grey', linestyle='-', alpha=0.5)
    plt.xticks(rotation=45, ha='right')
    
    # Añadir etiquetas
    for i, p in enumerate(ax.patches):
        height = p.get_height()
        if height != 0:  # Solo añadir etiquetas a barras no vacías
            ax.text(
                p.get_x() + p.get_width() / 2.,
                height + (0.5 if height >= 0 else -2),
                f"{height:.1f}%",
                ha='center',
                fontsize=9
            )
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    ruta_archivo = os.path.join(directorio, 'alertas_desviaciones.png')
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    return df_alertas, ruta_archivo


def incluir_simulaciones_mejora(datos_metricas, directorio=None):
    """
    Incluye simulaciones de mejora de conversión en el reporte.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas calculadas.
        directorio (str, opcional): Directorio donde guardar las visualizaciones.
        
    Returns:
        dict: Resultados y rutas de archivos de la simulación.
    """
    # Importar función de simulación
    from simular_mejora_conversion import generar_reporte_mejora_conversion
    
    # Generar reporte de simulación
    return generar_reporte_mejora_conversion(datos_metricas, directorio)


def incluir_analisis_elasticidad(datos_historicos, datos_planificacion, directorio=None):
    """
    Incluye análisis de elasticidad de presupuesto en el reporte.
    
    Args:
        datos_historicos (pandas.DataFrame): DataFrame con datos históricos.
        datos_planificacion (pandas.DataFrame): DataFrame con datos de planificación.
        directorio (str, opcional): Directorio donde guardar las visualizaciones.
        
    Returns:
        dict: Resultados y rutas de archivos del análisis.
    """
    # Importar función de análisis de elasticidad
    from analizar_elasticidad import generar_reporte_elasticidad
    
    # Generar reporte de elasticidad
    variaciones = [-0.2, -0.1, 0, 0.1, 0.2]
    return generar_reporte_elasticidad(datos_historicos, datos_planificacion, variaciones, directorio)


def incluir_proyeccion_cierre(datos_actuales, info_convocatoria, directorio=None):
    """
    Incluye proyección de cierre de matrícula en el reporte.
    
    Args:
        datos_actuales (pandas.DataFrame): DataFrame con datos actuales.
        info_convocatoria (pandas.DataFrame): DataFrame con información de convocatorias.
        directorio (str, opcional): Directorio donde guardar las visualizaciones.
        
    Returns:
        dict: Resultados y rutas de archivos de la proyección.
    """
    # Importar función de proyección
    from proyectar_convocatoria import generar_reporte_proyeccion
    
    # Generar reporte de proyección
    escenarios = [-0.05, -0.01, 0, 0.01, 0.05]
    return generar_reporte_proyeccion(datos_actuales, info_convocatoria, escenarios, directorio)


def incluir_analisis_estacionalidad(datos_historicos, datos_actuales, directorio=None):
    """
    Incluye análisis de estacionalidad en el reporte.
    
    Args:
        datos_historicos (pandas.DataFrame): DataFrame con datos históricos.
        datos_actuales (pandas.DataFrame): DataFrame con datos actuales.
        directorio (str, opcional): Directorio donde guardar las visualizaciones.
        
    Returns:
        dict: Resultados y rutas de archivos del análisis.
    """
    # Importar función de análisis de estacionalidad
    from modelo_estacionalidad import generar_reporte_estacionalidad
    
    # Determinar quincena actual
    mes_actual = datetime.now().month
    dia_actual = datetime.now().day
    quincena_actual = (mes_actual - 1) * 2 + (2 if dia_actual > 15 else 1)
    
    # Generar reporte de estacionalidad
    return generar_reporte_estacionalidad(
        datos_historicos,
        datos_actuales,
        quincena_actual,
        'quincena',
        directorio
    )


def generar_dashboard_completo(datos_metricas, datos_tendencias, oportunidades_mejora, 
                              datos_historicos=None, info_convocatoria=None, directorio=None):
    """
    Genera un dashboard completo con todas las visualizaciones y reporte Excel.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas calculadas.
        datos_tendencias (pandas.DataFrame): DataFrame con tendencias calculadas.
        oportunidades_mejora (dict): Diccionario con oportunidades de mejora.
        datos_historicos (pandas.DataFrame, opcional): DataFrame con datos históricos para análisis adicionales.
        info_convocatoria (pandas.DataFrame, opcional): DataFrame con información de convocatorias.
        directorio (str, opcional): Directorio donde guardar el dashboard.
        
    Returns:
        dict: Diccionario con rutas de todos los archivos generados.
    """
    # Crear directorio si no se especifica
    if directorio is None:
        directorio = crear_directorio_reportes()
    
    archivos_generados = {}
    reportes_adicionales = {}
    
    # 1. Generar reporte Excel
    archivo_excel = generar_reporte_excel(
        datos_metricas,
        'reporte_rendimiento_marketing',
        directorio
    )
    archivos_generados['excel'] = archivo_excel
    
    # 2. Visualizaciones de rendimiento por canal
    metricas_rendimiento = ['Leads', 'Matrículas', 'Tasa Conversión', 'CPA', 'CPL']
    archivos_rendimiento = visualizar_rendimiento_por_canal(
        datos_metricas,
        metricas_rendimiento,
        directorio
    )
    archivos_generados['rendimiento'] = archivos_rendimiento
    
    # 3. Visualizaciones de tendencias
    metricas_tendencias = ['Leads', 'Matrículas', 'Tasa Conversión', 'CPA']
    archivos_tendencias = visualizar_tendencias(
        datos_tendencias,
        metricas_tendencias,
        directorio
    )
    archivos_generados['tendencias'] = archivos_tendencias
    
    # 4. Generar informe de oportunidades de mejora
    plt.figure(figsize=(12, 8))
    
    # Oportunidades de CPA alto
    cpa_alto = oportunidades_mejora['cpa_alto']
    if not cpa_alto.empty:
        ax1 = plt.subplot(2, 1, 1)
        sns.barplot(
            data=cpa_alto,
            x='Canal',
            y='CPA',
            hue='Marca',
            ax=ax1
        )
        plt.title(f'Canales con CPA Alto (>{oportunidades_mejora["umbral_cpa"]:.2f})', fontsize=14)
        plt.xlabel('Canal', fontsize=12)
        plt.ylabel('CPA (USD)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
    
    # Oportunidades de CR bajo
    cr_bajo = oportunidades_mejora['cr_bajo']
    if not cr_bajo.empty:
        ax2 = plt.subplot(2, 1, 2)
        sns.barplot(
            data=cr_bajo,
            x='Canal',
            y='Tasa Conversión',
            hue='Marca',
            ax=ax2
        )
        plt.title(f'Canales con Tasa de Conversión Baja (<{oportunidades_mejora["umbral_cr"]:.2%})', fontsize=14)
        plt.xlabel('Canal', fontsize=12)
        plt.ylabel('Tasa de Conversión', fontsize=12)
        plt.xticks(rotation=45, ha='right')
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    archivo_oportunidades = os.path.join(directorio, 'oportunidades_mejora.png')
    plt.savefig(archivo_oportunidades, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos_generados['oportunidades'] = archivo_oportunidades
    
    # 5. Generar alertas automáticas
    try:
        alertas, archivo_alertas = generar_alertas_automaticas(datos_metricas, directorio=directorio)
        if archivo_alertas:
            archivos_generados['alertas'] = archivo_alertas
            reportes_adicionales['alertas'] = alertas
    except Exception as e:
        print(f"Error al generar alertas automáticas: {e}")
    
    # 6. Incluir simulaciones de mejora de conversión
    try:
        resultado_simulacion = incluir_simulaciones_mejora(datos_metricas, directorio)
        archivos_generados['simulacion'] = resultado_simulacion['archivos']
        reportes_adicionales['simulacion'] = resultado_simulacion
    except Exception as e:
        print(f"Error al incluir simulaciones de mejora: {e}")
    
    # 7. Incluir análisis de elasticidad si se proporcionan datos históricos y planificación
    if datos_historicos is not None and info_convocatoria is not None:
        try:
            resultado_elasticidad = incluir_analisis_elasticidad(
                datos_historicos,
                info_convocatoria,
                directorio
            )
            archivos_generados['elasticidad'] = resultado_elasticidad['archivos']
            reportes_adicionales['elasticidad'] = resultado_elasticidad
        except Exception as e:
            print(f"Error al incluir análisis de elasticidad: {e}")
    
    # 8. Incluir proyección de cierre si se proporcionan datos actuales e info de convocatoria
    if datos_historicos is not None and info_convocatoria is not None:
        try:
            resultado_proyeccion = incluir_proyeccion_cierre(
                datos_historicos,
                info_convocatoria,
                directorio
            )
            archivos_generados['proyeccion'] = resultado_proyeccion['archivos']
            reportes_adicionales['proyeccion'] = resultado_proyeccion
        except Exception as e:
            print(f"Error al incluir proyección de cierre: {e}")
    
    # 9. Incluir análisis de estacionalidad si se proporcionan datos históricos y actuales
    if datos_historicos is not None:
        try:
            resultado_estacionalidad = incluir_analisis_estacionalidad(
                datos_historicos,
                datos_metricas,
                directorio
            )
            archivos_generados['estacionalidad'] = resultado_estacionalidad['archivos']
            reportes_adicionales['estacionalidad'] = resultado_estacionalidad
        except Exception as e:
            print(f"Error al incluir análisis de estacionalidad: {e}")
    
    # Generar un índice HTML con todas las visualizaciones
    try:
        generar_indice_html(archivos_generados, directorio)
    except Exception as e:
        print(f"Error al generar índice HTML: {e}")
    
    return {
        'archivos': archivos_generados,
        'reportes_adicionales': reportes_adicionales
    }


def generar_indice_html(archivos_generados, directorio):
    """
    Genera un archivo HTML que muestra todas las visualizaciones generadas.
    
    Args:
        archivos_generados (dict): Diccionario con rutas de archivos generados.
        directorio (str): Directorio donde guardar el archivo HTML.
        
    Returns:
        str: Ruta del archivo HTML generado.
    """
    # Nombre del archivo HTML
    ruta_html = os.path.join(directorio, 'dashboard.html')
    
    # Mapeo de categorías a títulos
    titulos_categorias = {
        'rendimiento': 'Rendimiento por Canal',
        'tendencias': 'Tendencias Temporales',
        'oportunidades': 'Oportunidades de Mejora',
        'alertas': 'Alertas Automáticas',
        'simulacion': 'Simulación de Mejora de Conversión',
        'elasticidad': 'Análisis de Elasticidad de Presupuesto',
        'proyeccion': 'Proyección de Cierre de Matrícula',
        'estacionalidad': 'Análisis de Estacionalidad'
    }
    
    # Preparar contenido HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard de Marketing</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            h1, h2 {{ color: #333; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; margin-bottom: 20px; }}
            .section {{ background-color: white; margin-bottom: 30px; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
            .image-container {{ margin: 15px 0; }}
            img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
            .links {{ margin-top: 20px; }}
            .links a {{ display: inline-block; margin-right: 10px; padding: 8px 15px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 3px; }}
            .links a:hover {{ background-color: #45a049; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Dashboard de Marketing - {datetime.now().strftime('%d/%m/%Y')}</h1>
            </div>
            
            <div class="section">
                <h2>Índice</h2>
                <ul>
    """
    
    # Agregar enlaces a secciones
    for categoria in archivos_generados:
        if categoria in titulos_categorias and (isinstance(archivos_generados[categoria], list) or isinstance(archivos_generados[categoria], dict)):
            html_content += f'<li><a href="#{categoria}">{titulos_categorias.get(categoria, categoria)}</a></li>\n'
    
    html_content += """
                </ul>
                <div class="links">
                    <a href="reporte_rendimiento_marketing.xlsx" download>Descargar Reporte Excel</a>
    """
    
    # Agregar enlaces a otros reportes Excel
    for categoria, archivos in archivos_generados.items():
        if categoria != 'excel' and isinstance(archivos, dict) and 'excel' in archivos:
            nombre_archivo = os.path.basename(archivos['excel'])
            html_content += f'<a href="{nombre_archivo}" download>Descargar {titulos_categorias.get(categoria, categoria)}</a>\n'
    
    html_content += """
                </div>
            </div>
    """
    
    # Agregar secciones con imágenes
    for categoria, archivos in archivos_generados.items():
        if categoria in titulos_categorias and (isinstance(archivos, list) or isinstance(archivos, dict)):
            html_content += f"""
            <div class="section" id="{categoria}">
                <h2>{titulos_categorias.get(categoria, categoria)}</h2>
                <div class="image-container">
            """
            
            # Agregar imágenes
            if isinstance(archivos, list):
                for archivo in archivos:
                    nombre_archivo = os.path.basename(archivo)
                    html_content += f'<img src="{nombre_archivo}" alt="{nombre_archivo}">\n'
            elif isinstance(archivos, dict):
                for key, archivo in archivos.items():
                    if key != 'excel' and isinstance(archivo, str) and (archivo.endswith('.png') or archivo.endswith('.jpg')):
                        nombre_archivo = os.path.basename(archivo)
                        html_content += f'<img src="{nombre_archivo}" alt="{nombre_archivo}">\n'
            
            html_content += """
                </div>
            </div>
            """
    
    # Cerrar HTML
    html_content += """
            <div class="footer">
                <p>Generado automáticamente por el Sistema Predictor de Matrículas</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Escribir archivo HTML
    with open(ruta_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return ruta_html


def generar_reporte_comparativo(df_real, df_proyeccion, periodo=None):
    """
    Genera un reporte comparativo entre resultados reales y proyecciones.
    
    Args:
        df_real (pandas.DataFrame): DataFrame con datos reales.
        df_proyeccion (pandas.DataFrame): DataFrame con proyecciones.
        periodo (str, optional): Periodo de reporte ('diario', 'semanal', 'mensual').
        
    Returns:
        pandas.DataFrame: DataFrame con la comparación y análisis de desviación.
    """
    # Verificar columnas requeridas
    columnas_requeridas = ['Marca', 'Canal', 'ID Convocatoria']
    
    for df in [df_real, df_proyeccion]:
        for col in columnas_requeridas:
            if col not in df.columns:
                raise ValueError(f"El DataFrame debe contener la columna '{col}'")
    
    # Crear copia para no modificar originales
    real = df_real.copy()
    proyeccion = df_proyeccion.copy()
    
    # Unificar por marca, canal y convocatoria
    columnas_comparacion = ['Marca', 'Canal', 'ID Convocatoria']
    
    # Crear reporte comparativo
    reporte = pd.merge(
        real, 
        proyeccion, 
        on=columnas_comparacion, 
        how='outer', 
        suffixes=('_Real', '_Proyectado')
    )
    
    # Limpiar NaN
    reporte = reporte.fillna(0)
    
    # Calcular KPIs principales para comparación
    kpis = ['Leads', 'Matrículas', 'CPL (USD)', 'CPA (USD)', 'Tasa de Conversión (%)']
    
    for kpi in kpis:
        if f'{kpi}_Real' in reporte.columns and f'{kpi}_Proyectado' in reporte.columns:
            # Calcular diferencia absoluta
            reporte[f'Dif_{kpi}'] = reporte[f'{kpi}_Real'] - reporte[f'{kpi}_Proyectado']
            
            # Calcular diferencia porcentual (evitar división por cero)
            denominador = reporte[f'{kpi}_Proyectado'].replace(0, np.nan)
            reporte[f'Dif_{kpi} (%)'] = (reporte[f'Dif_{kpi}'] / denominador) * 100
            reporte[f'Dif_{kpi} (%)'] = reporte[f'Dif_{kpi} (%)'].fillna(0)
            
            # Determinar si se cumplió la meta
            if kpi in ['CPL (USD)', 'CPA (USD)']:
                # Para costos, un valor real MENOR es positivo
                reporte[f'Cumplimiento_{kpi}'] = np.where(
                    reporte[f'{kpi}_Real'] <= reporte[f'{kpi}_Proyectado'],
                    'Cumplido', 'No Cumplido'
                )
            else:
                # Para leads, matrículas y conversión, un valor real MAYOR es positivo
                reporte[f'Cumplimiento_{kpi}'] = np.where(
                    reporte[f'{kpi}_Real'] >= reporte[f'{kpi}_Proyectado'],
                    'Cumplido', 'No Cumplido'
                )
    
    # Calcular puntaje de desempeño general
    reporte['Puntaje_Desempeño'] = 0
    
    # Ponderación de KPIs
    ponderaciones = {
        'Matrículas': 0.4,  # 40% del puntaje
        'CPA (USD)': 0.3,   # 30% del puntaje
        'Leads': 0.2,       # 20% del puntaje
        'Tasa de Conversión (%)': 0.1  # 10% del puntaje
    }
    
    # Calcular puntaje (de 0 a 100)
    for kpi, peso in ponderaciones.items():
        if f'Cumplimiento_{kpi}' in reporte.columns:
            reporte['Puntaje_Desempeño'] += np.where(
                reporte[f'Cumplimiento_{kpi}'] == 'Cumplido',
                100 * peso,
                0
            )
    
    # Determinar nivel de desempeño
    condiciones = [
        (reporte['Puntaje_Desempeño'] >= 85),
        (reporte['Puntaje_Desempeño'] >= 70),
        (reporte['Puntaje_Desempeño'] >= 50),
        (reporte['Puntaje_Desempeño'] >= 0)
    ]
    
    valores = [
        'Excelente',
        'Bueno',
        'Regular',
        'Deficiente'
    ]
    
    reporte['Nivel_Desempeño'] = np.select(condiciones, valores, default='No Evaluado')
    
    # Generar recomendaciones automáticas
    reporte['Recomendación'] = reporte.apply(generar_recomendacion, axis=1)
    
    # Agregar fecha de generación del reporte
    reporte['Fecha_Reporte'] = datetime.now()
    
    return reporte


def generar_recomendacion(fila):
    """
    Genera una recomendación automática basada en los resultados comparativos.
    
    Args:
        fila (pandas.Series): Fila con datos de comparación para una campaña.
        
    Returns:
        str: Recomendación automática basada en el análisis.
    """
    # Variables para evaluar
    marca = fila['Marca']
    canal = fila['Canal']
    nivel = fila['Nivel_Desempeño']
    
    # Casos de CPA
    if 'CPA (USD)_Real' in fila and 'CPA (USD)_Proyectado' in fila:
        # CPA mucho más alto de lo proyectado (mal desempeño)
        if fila['CPA (USD)_Real'] > fila['CPA (USD)_Proyectado'] * 1.3:
            return f"REVISAR URGENTE: El CPA de {marca} en {canal} está muy por encima de lo proyectado. Considerar ajustes inmediatos en la estrategia o reducir presupuesto."
        
        # CPA mucho más bajo (buen desempeño)
        if fila['CPA (USD)_Real'] < fila['CPA (USD)_Proyectado'] * 0.7:
            return f"OPORTUNIDAD: El CPA de {marca} en {canal} está significativamente por debajo de lo proyectado. Considerar aumentar presupuesto para maximizar resultados."
    
    # Casos de tasa de conversión
    if 'Tasa de Conversión (%)_Real' in fila and 'Tasa de Conversión (%)_Proyectado' in fila:
        # Conversión muy por debajo de lo esperado
        if fila['Tasa de Conversión (%)_Real'] < fila['Tasa de Conversión (%)_Proyectado'] * 0.7:
            return f"ALERTA: La tasa de conversión de {marca} en {canal} está muy por debajo de lo esperado. Revisar calidad de leads y proceso de seguimiento."
    
    # Recomendaciones generales según nivel de desempeño
    if nivel == 'Excelente':
        return f"MANTENER: {marca} en {canal} muestra un rendimiento excelente. Mantener estrategia actual y considerar aumentar la inversión."
    
    elif nivel == 'Bueno':
        return f"OPTIMIZAR: {marca} en {canal} muestra buen rendimiento. Revisar oportunidades de mejora en KPIs específicos para maximizar resultados."
    
    elif nivel == 'Regular':
        return f"AJUSTAR: {marca} en {canal} necesita ajustes. Revisar estrategia y considerar optimizaciones en segmentación o creatividades."
    
    elif nivel == 'Deficiente':
        return f"REEVALUAR: {marca} en {canal} no está cumpliendo los objetivos. Considerar rediseñar estrategia o reasignar presupuesto a canales con mejor desempeño."
    
    return "Revisar manualmente para determinar acciones específicas."


def generar_visualizaciones_comparativas(df_comparativo):
    """
    Genera visualizaciones comparativas entre resultados reales y proyecciones.
    
    Args:
        df_comparativo (pandas.DataFrame): DataFrame con datos de comparación.
        
    Returns:
        dict: Diccionario con figuras generadas.
    """
    figuras = {}
    
    # Configurar tema de visualización
    sns.set_style("whitegrid")
    sns.set_palette("Set2")
    
    # 1. Gráfico de barras comparativo de leads y matrículas
    if all(col in df_comparativo.columns for col in ['Leads_Real', 'Leads_Proyectado', 'Matrículas_Real', 'Matrículas_Proyectado']):
        fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Ordenar por marca y canal
        df_plot = df_comparativo.sort_values(['Marca', 'Canal'])
        
        # Crear etiquetas
        df_plot['Etiqueta'] = df_plot['Canal'] + ' - ' + df_plot['Marca']
        
        # Gráfico para leads
        x = np.arange(len(df_plot))
        width = 0.35
        
        ax1.bar(x - width/2, df_plot['Leads_Real'], width, label='Real', color='steelblue')
        ax1.bar(x + width/2, df_plot['Leads_Proyectado'], width, label='Proyectado', color='lightgreen')
        
        ax1.set_ylabel('Número de Leads')
        ax1.set_title('Leads: Real vs. Proyectado')
        ax1.set_xticks(x)
        ax1.set_xticklabels(df_plot['Etiqueta'], rotation=45, ha='right')
        ax1.legend()
        
        # Agregar valores encima de las barras
        for i, v in enumerate(df_plot['Leads_Real']):
            ax1.text(i - width/2, v + 5, f"{int(v)}", ha='center', va='bottom', fontsize=8)
        
        for i, v in enumerate(df_plot['Leads_Proyectado']):
            ax1.text(i + width/2, v + 5, f"{int(v)}", ha='center', va='bottom', fontsize=8)
        
        # Gráfico para matrículas
        ax2.bar(x - width/2, df_plot['Matrículas_Real'], width, label='Real', color='darkblue')
        ax2.bar(x + width/2, df_plot['Matrículas_Proyectado'], width, label='Proyectado', color='forestgreen')
        
        ax2.set_ylabel('Número de Matrículas')
        ax2.set_title('Matrículas: Real vs. Proyectado')
        ax2.set_xticks(x)
        ax2.set_xticklabels(df_plot['Etiqueta'], rotation=45, ha='right')
        ax2.legend()
        
        # Agregar valores encima de las barras
        for i, v in enumerate(df_plot['Matrículas_Real']):
            ax2.text(i - width/2, v + 1, f"{int(v)}", ha='center', va='bottom', fontsize=8)
        
        for i, v in enumerate(df_plot['Matrículas_Proyectado']):
            ax2.text(i + width/2, v + 1, f"{int(v)}", ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        figuras['leads_matriculas'] = fig1
    
    # 2. Gráfico de barras comparativo de CPL y CPA
    if all(col in df_comparativo.columns for col in ['CPL (USD)_Real', 'CPL (USD)_Proyectado', 'CPA (USD)_Real', 'CPA (USD)_Proyectado']):
        fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Ordenar por CPL real
        df_plot = df_comparativo.sort_values('CPL (USD)_Real', ascending=False)
        
        # Crear etiquetas
        df_plot['Etiqueta'] = df_plot['Canal'] + ' - ' + df_plot['Marca']
        
        # Gráfico para CPL
        x = np.arange(len(df_plot))
        width = 0.35
        
        ax1.bar(x - width/2, df_plot['CPL (USD)_Real'], width, label='Real', color='salmon')
        ax1.bar(x + width/2, df_plot['CPL (USD)_Proyectado'], width, label='Proyectado', color='lightsalmon')
        
        ax1.set_ylabel('CPL (USD)')
        ax1.set_title('Costo por Lead: Real vs. Proyectado')
        ax1.set_xticks(x)
        ax1.set_xticklabels(df_plot['Etiqueta'], rotation=45, ha='right')
        ax1.legend()
        
        # Agregar valores encima de las barras
        for i, v in enumerate(df_plot['CPL (USD)_Real']):
            ax1.text(i - width/2, v + 2, f"${v:.1f}", ha='center', va='bottom', fontsize=8)
        
        for i, v in enumerate(df_plot['CPL (USD)_Proyectado']):
            ax1.text(i + width/2, v + 2, f"${v:.1f}", ha='center', va='bottom', fontsize=8)
        
        # Gráfico para CPA
        df_plot = df_comparativo.sort_values('CPA (USD)_Real', ascending=False)
        
        ax2.bar(x - width/2, df_plot['CPA (USD)_Real'], width, label='Real', color='crimson')
        ax2.bar(x + width/2, df_plot['CPA (USD)_Proyectado'], width, label='Proyectado', color='lightcoral')
        
        ax2.set_ylabel('CPA (USD)')
        ax2.set_title('Costo por Adquisición: Real vs. Proyectado')
        ax2.set_xticks(x)
        ax2.set_xticklabels(df_plot['Etiqueta'], rotation=45, ha='right')
        ax2.legend()
        
        # Agregar valores encima de las barras
        for i, v in enumerate(df_plot['CPA (USD)_Real']):
            ax2.text(i - width/2, v + 5, f"${v:.1f}", ha='center', va='bottom', fontsize=8)
        
        for i, v in enumerate(df_plot['CPA (USD)_Proyectado']):
            ax2.text(i + width/2, v + 5, f"${v:.1f}", ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        figuras['cpl_cpa'] = fig2
    
    # 3. Heatmap de desviaciones porcentuales
    if any('Dif_' in col and '(%)' in col for col in df_comparativo.columns):
        fig3, ax = plt.subplots(figsize=(12, 8))
        
        # Seleccionar columnas de desviación porcentual
        cols_desviacion = [col for col in df_comparativo.columns if 'Dif_' in col and '(%)' in col]
        
        # Crear matriz para heatmap
        df_heat = df_comparativo.pivot_table(
            index=['Marca', 'Canal'],
            values=cols_desviacion,
            aggfunc='mean'
        )
        
        # Limpiar nombres de columnas
        df_heat.columns = [col.replace('Dif_', '').replace(' (%)', '') for col in df_heat.columns]
        
        # Crear heatmap
        sns.heatmap(
            df_heat, 
            annot=True, 
            fmt=".1f", 
            cmap="RdYlGn", 
            center=0,
            linewidths=.5,
            cbar_kws={"label": "Desviación (%)"}
        )
        
        ax.set_title('Desviación Porcentual de KPIs (Real vs. Proyectado)')
        plt.tight_layout()
        figuras['desviaciones'] = fig3
    
    # 4. Gráfico de puntuación de desempeño
    if 'Puntaje_Desempeño' in df_comparativo.columns:
        fig4, ax = plt.subplots(figsize=(12, 8))
        
        # Ordenar por puntaje
        df_plot = df_comparativo.sort_values('Puntaje_Desempeño', ascending=False)
        
        # Crear etiquetas
        df_plot['Etiqueta'] = df_plot['Canal'] + ' - ' + df_plot['Marca']
        
        # Definir colores según puntaje
        colores = df_plot['Puntaje_Desempeño'].map(
            lambda x: 'green' if x >= 85 else
                      'yellowgreen' if x >= 70 else
                      'orange' if x >= 50 else
                      'red'
        )
        
        # Crear barras
        barras = ax.barh(df_plot['Etiqueta'], df_plot['Puntaje_Desempeño'], color=colores)
        
        # Añadir etiquetas
        for i, bar in enumerate(barras):
            width = bar.get_width()
            ax.text(
                width + 1,
                bar.get_y() + bar.get_height()/2,
                f"{width:.1f} - {df_plot.iloc[i]['Nivel_Desempeño']}",
                ha='left',
                va='center'
            )
        
        # Configurar gráfico
        ax.set_xlabel('Puntaje de Desempeño (0-100)')
        ax.set_title('Evaluación de Desempeño por Canal')
        ax.set_xlim(0, 105)
        ax.axvline(x=85, color='green', linestyle='--', alpha=0.5)
        ax.axvline(x=70, color='yellowgreen', linestyle='--', alpha=0.5)
        ax.axvline(x=50, color='orange', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        figuras['desempeno'] = fig4
    
    return figuras


def exportar_reporte_pdf(df_comparativo, figuras, ruta_salida, titulo=None):
    """
    Exporta un reporte comparativo en formato PDF.
    
    Args:
        df_comparativo (pandas.DataFrame): DataFrame con datos de comparación.
        figuras (dict): Diccionario con figuras para incluir en el reporte.
        ruta_salida (str): Ruta donde guardar el archivo PDF.
        titulo (str, optional): Título del reporte.
        
    Returns:
        str: Ruta del archivo PDF generado.
    """
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    
    # Fecha para el título
    fecha_str = datetime.now().strftime('%d/%m/%Y')
    if titulo is None:
        titulo = f"Reporte Comparativo de Campañas - {fecha_str}"
    
    # Crear documento PDF
    with PdfPages(ruta_salida) as pdf:
        # Página de portada
        plt.figure(figsize=(12, 8))
        plt.axis('off')
        plt.text(0.5, 0.7, titulo, fontsize=24, ha='center')
        plt.text(0.5, 0.5, f"Generado el {fecha_str}", fontsize=16, ha='center')
        plt.text(0.5, 0.4, "Sistema de Predicción y Optimización de Matrículas", fontsize=14, ha='center')
        plt.tight_layout()
        pdf.savefig()
        plt.close()
        
        # Agregar figuras
        for nombre, fig in figuras.items():
            pdf.savefig(fig)
        
        # Crear tabla resumen
        plt.figure(figsize=(12, 9))
        plt.axis('off')
        plt.title("Resumen Comparativo por Canal", fontsize=16)
        
        # Seleccionar columnas para la tabla
        columnas_tabla = [
            'Marca', 'Canal', 
            'Leads_Real', 'Leads_Proyectado', 'Dif_Leads (%)',
            'Matrículas_Real', 'Matrículas_Proyectado', 'Dif_Matrículas (%)',
            'CPA (USD)_Real', 'CPA (USD)_Proyectado', 'Dif_CPA (USD) (%)',
            'Nivel_Desempeño'
        ]
        
        # Filtrar sólo columnas disponibles
        columnas_tabla = [col for col in columnas_tabla if col in df_comparativo.columns]
        
        # Crear tabla
        if columnas_tabla:
            df_tabla = df_comparativo[columnas_tabla].copy()
            
            # Renombrar columnas para mejor visualización
            renombres = {
                'Dif_Leads (%)': 'Δ Leads (%)',
                'Dif_Matrículas (%)': 'Δ Matrículas (%)',
                'Dif_CPA (USD) (%)': 'Δ CPA (%)'
            }
            
            df_tabla = df_tabla.rename(columns=renombres)
            
            # Ordenar por nivel de desempeño
            if 'Nivel_Desempeño' in df_tabla.columns:
                orden_niveles = {
                    'Excelente': 0,
                    'Bueno': 1,
                    'Regular': 2,
                    'Deficiente': 3,
                    'No Evaluado': 4
                }
                
                df_tabla['orden'] = df_tabla['Nivel_Desempeño'].map(orden_niveles)
                df_tabla = df_tabla.sort_values('orden').drop(columns=['orden'])
            
            # Crear tabla
            tabla = plt.table(
                cellText=df_tabla.values.round(1),
                colLabels=df_tabla.columns,
                loc='center',
                cellLoc='center',
                colColours=['lightgray'] * len(df_tabla.columns)
            )
            
            # Ajustar tamaño de tabla
            tabla.auto_set_font_size(False)
            tabla.set_fontsize(8)
            tabla.scale(1, 1.5)
            
            plt.tight_layout()
            pdf.savefig()
            plt.close()
        
        # Página de recomendaciones
        if 'Recomendación' in df_comparativo.columns:
            plt.figure(figsize=(12, 9))
            plt.axis('off')
            plt.title("Recomendaciones por Canal", fontsize=16)
            
            # Crear tabla de recomendaciones
            df_recom = df_comparativo[['Marca', 'Canal', 'Nivel_Desempeño', 'Recomendación']].copy()
            
            # Ordenar por nivel de desempeño
            orden_niveles = {
                'Excelente': 0,
                'Bueno': 1,
                'Regular': 2,
                'Deficiente': 3,
                'No Evaluado': 4
            }
            
            df_recom['orden'] = df_recom['Nivel_Desempeño'].map(orden_niveles)
            df_recom = df_recom.sort_values('orden').drop(columns=['orden'])
            
            # Crear tabla
            tabla = plt.table(
                cellText=df_recom.values,
                colLabels=df_recom.columns,
                loc='center',
                cellLoc='left',
                colColours=['lightgray'] * len(df_recom.columns)
            )
            
            # Ajustar tamaño de tabla
            tabla.auto_set_font_size(False)
            tabla.set_fontsize(8)
            tabla.scale(1, 1.5)
            
            # Ajustar ancho de columnas
            tabla.auto_set_column_width([0, 1, 2])
            
            plt.tight_layout()
            pdf.savefig()
            plt.close()
    
    return ruta_salida


def exportar_datos_powerbi(df_comparativo, ruta_salida):
    """
    Exporta datos para su uso en Power BI.
    
    Args:
        df_comparativo (pandas.DataFrame): DataFrame con datos de comparación.
        ruta_salida (str): Ruta donde guardar el archivo Excel.
        
    Returns:
        str: Ruta del archivo Excel generado.
    """
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    
    # Crear libro Excel
    writer = pd.ExcelWriter(
        ruta_salida,
        engine='xlsxwriter',
        engine_kwargs={'options': {'nan_inf_to_errors': True}}
    )
    
    # Guardar datos principales
    df_comparativo.to_excel(writer, sheet_name='Datos_Comparativos', index=False)
    
    # Crear pivotes útiles para Power BI
    
    # 1. Pivot de KPIs por Marca y Canal
    if all(col in df_comparativo.columns for col in ['Marca', 'Canal']):
        kpis_pivot = []
        
        for kpi in ['Leads', 'Matrículas', 'CPL (USD)', 'CPA (USD)', 'Tasa de Conversión (%)']:
            if f'{kpi}_Real' in df_comparativo.columns and f'{kpi}_Proyectado' in df_comparativo.columns:
                # Pivot para este KPI
                pivot_df = df_comparativo.pivot_table(
                    index=['Marca', 'Canal'],
                    values=[f'{kpi}_Real', f'{kpi}_Proyectado', f'Dif_{kpi}', f'Dif_{kpi} (%)'],
                    aggfunc='sum'
                ).reset_index()
                
                # Renombrar para evitar confusión
                pivot_df.columns = [
                    col[0] if col[1] == '' else f"{col[0]}_{col[1]}"
                    for col in pivot_df.columns.values
                ]
                
                pivot_df['KPI'] = kpi
                kpis_pivot.append(pivot_df)
        
        if kpis_pivot:
            # Unir todos los pivotes
            df_kpis = pd.concat(kpis_pivot, ignore_index=True)
            df_kpis.to_excel(writer, sheet_name='KPIs_por_Canal', index=False)
    
    # 2. Tabla para mapa de calor de desempeño
    if 'Nivel_Desempeño' in df_comparativo.columns:
        df_heat = df_comparativo.pivot_table(
            index=['Marca'],
            columns=['Canal'],
            values=['Puntaje_Desempeño'],
            aggfunc='mean'
        )
        
        # Aplanar multi-índice
        df_heat.columns = [col[1] for col in df_heat.columns]
        df_heat = df_heat.reset_index()
        
        df_heat.to_excel(writer, sheet_name='Mapa_Desempeño', index=False)
    
    # 3. Datos para métricas ejecutivas (KPIs generales)
    kpis_ejecutivos = {}
    
    for kpi in ['Leads', 'Matrículas', 'CPA (USD)']:
        if f'{kpi}_Real' in df_comparativo.columns and f'{kpi}_Proyectado' in df_comparativo.columns:
            total_real = df_comparativo[f'{kpi}_Real'].sum()
            total_proyectado = df_comparativo[f'{kpi}_Proyectado'].sum()
            
            if kpi in ['Leads', 'Matrículas']:
                # Para leads y matrículas, comparamos valor absoluto
                kpis_ejecutivos[f'Total {kpi} Real'] = total_real
                kpis_ejecutivos[f'Total {kpi} Proyectado'] = total_proyectado
                kpis_ejecutivos[f'Cumplimiento {kpi} (%)'] = (total_real / total_proyectado * 100) if total_proyectado > 0 else 0
            else:
                # Para CPA, calculamos promedio ponderado por matrículas
                if 'Matrículas_Real' in df_comparativo.columns and df_comparativo['Matrículas_Real'].sum() > 0:
                    cpa_ponderado = (df_comparativo[f'{kpi}_Real'] * df_comparativo['Matrículas_Real']).sum() / df_comparativo['Matrículas_Real'].sum()
                    kpis_ejecutivos[f'{kpi} Promedio Ponderado'] = cpa_ponderado
    
    # Calcular tasa de conversión general
    if 'Leads_Real' in df_comparativo.columns and 'Matrículas_Real' in df_comparativo.columns:
        leads_total = df_comparativo['Leads_Real'].sum()
        matriculas_total = df_comparativo['Matrículas_Real'].sum()
        
        if leads_total > 0:
            kpis_ejecutivos['Tasa Conversión General (%)'] = (matriculas_total / leads_total) * 100
    
    # Guardar métricas ejecutivas
    df_ejecutivo = pd.DataFrame([kpis_ejecutivos])
    df_ejecutivo.to_excel(writer, sheet_name='Métricas_Ejecutivas', index=False)
    
    # Guardar archivo
    writer.close()
    
    return ruta_salida


def generar_reporte_completo(datos_reales, datos_proyeccion, directorio_salida=None, formato='pdf'):
    """
    Genera un reporte completo con comparativas, visualizaciones y archivos para Power BI.
    
    Args:
        datos_reales (pandas.DataFrame): DataFrame con datos reales.
        datos_proyeccion (pandas.DataFrame): DataFrame con proyecciones.
        directorio_salida (str, optional): Directorio donde guardar los archivos generados.
        formato (str): Formato del reporte ('pdf', 'excel', 'ambos').
        
    Returns:
        dict: Diccionario con rutas de archivos generados.
    """
    # Configurar directorio de salida
    if directorio_salida is None:
        fecha_str = datetime.now().strftime('%Y-%m-%d')
        directorio_salida = f'../salidas/reportes/{fecha_str}'
    
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Generar análisis comparativo
    reporte_comparativo = generar_reporte_comparativo(datos_reales, datos_proyeccion)
    
    # Generar visualizaciones
    visualizaciones = generar_visualizaciones_comparativas(reporte_comparativo)
    
    # Rutas de archivos a generar
    archivos_generados = {}
    
    # Exportar a PDF
    if formato in ['pdf', 'ambos']:
        ruta_pdf = os.path.join(directorio_salida, f'reporte_comparativo_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf')
        archivos_generados['pdf'] = exportar_reporte_pdf(reporte_comparativo, visualizaciones, ruta_pdf)
    
    # Exportar para Power BI
    if formato in ['excel', 'ambos']:
        ruta_excel = os.path.join(directorio_salida, f'datos_powerbi_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx')
        archivos_generados['excel'] = exportar_datos_powerbi(reporte_comparativo, ruta_excel)
    
    # Guardar visualizaciones individuales
    for nombre, figura in visualizaciones.items():
        ruta_imagen = os.path.join(directorio_salida, f'{nombre}_{datetime.now().strftime("%Y%m%d_%H%M")}.png')
        figura.savefig(ruta_imagen, dpi=300, bbox_inches='tight')
        plt.close(figura)
        archivos_generados[f'imagen_{nombre}'] = ruta_imagen
    
    # Guardar datos del reporte
    ruta_datos = os.path.join(directorio_salida, f'datos_reporte_{datetime.now().strftime("%Y%m%d_%H%M")}.csv')
    reporte_comparativo.to_csv(ruta_datos, index=False)
    archivos_generados['datos'] = ruta_datos
    
    return archivos_generados


if __name__ == "__main__":
    # Ejemplo de uso
    from cargar_datos import cargar_datos_crm, cargar_datos_planificacion
    from analizar_rendimiento import calcular_metricas_rendimiento, calcular_tendencias, identificar_oportunidades_mejora
    
    try:
        print("Cargando datos...")
        datos_crm = cargar_datos_crm("../datos/leads_matriculas_reales.csv")
        datos_planificacion = cargar_datos_planificacion("../datos/planificacion_quincenal.csv")
        
        # Intentar cargar datos históricos (opcional)
        datos_historicos = None
        try:
            datos_historicos = cargar_datos_crm("../datos/leads_matriculas_historicos.csv")
        except:
            print("No se pudieron cargar datos históricos. Algunas funcionalidades avanzadas no estarán disponibles.")
        
        print("Calculando métricas...")
        metricas = calcular_metricas_rendimiento(datos_crm, datos_planificacion)
        tendencias = calcular_tendencias(metricas, periodo='mensual')
        oportunidades = identificar_oportunidades_mejora(metricas)
        
        print("Generando dashboard completo...")
        resultado = generar_dashboard_completo(
            metricas, 
            tendencias, 
            oportunidades,
            datos_historicos,
            datos_planificacion
        )
        
        directorio = os.path.dirname(resultado['archivos']['excel'])
        numero_archivos = sum(len(archivos) if isinstance(archivos, list) else 
                            len(archivos) if isinstance(archivos, dict) else 1 
                            for archivos in resultado['archivos'].values())
        
        print(f"Dashboard generado en: {directorio}")
        print(f"Archivos generados: {numero_archivos}")
        print(f"Reportes adicionales: {', '.join(resultado['reportes_adicionales'].keys())}")
        
    except Exception as e:
        print(f"Error: {e}") 