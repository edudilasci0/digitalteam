"""
Módulo para simular el impacto de mejoras en la tasa de conversión en campañas de marketing.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime


def simular_mejora_conversion(datos_metricas, incrementos=[0.02, 0.05, 0.10]):
    """
    Simula el impacto de mejorar la tasa de conversión en diferentes porcentajes.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas de rendimiento actuales.
        incrementos (list): Lista de incrementos porcentuales a simular (en decimales).
        
    Returns:
        pandas.DataFrame: DataFrame con resultados de la simulación para diferentes escenarios.
    """
    # Verificar columnas necesarias
    columnas_requeridas = ['Marca', 'Canal', 'Leads', 'Matrículas', 'Tasa Conversión', 'Presupuesto Asignado (USD)']
    for col in columnas_requeridas:
        if col not in datos_metricas.columns:
            raise ValueError(f"El DataFrame debe contener la columna '{col}'")
    
    # Agrupar datos por marca y canal
    df_agrupado = datos_metricas.groupby(['Marca', 'Canal']).agg({
        'Leads': 'sum',
        'Matrículas': 'sum',
        'Tasa Conversión': 'mean',
        'Presupuesto Asignado (USD)': 'sum'
    }).reset_index()
    
    # Calcular CPA actual
    df_agrupado['CPA Actual'] = np.where(
        df_agrupado['Matrículas'] > 0,
        df_agrupado['Presupuesto Asignado (USD)'] / df_agrupado['Matrículas'],
        float('inf')
    )
    
    # Crear DataFrame para almacenar resultados
    resultados = []
    
    # Simular mejoras para cada incremento
    for incremento in incrementos:
        for _, row in df_agrupado.iterrows():
            # Calcular nueva tasa de conversión
            nueva_tasa = row['Tasa Conversión'] + incremento
            
            # Calcular nuevas matrículas proyectadas (manteniendo leads constantes)
            nuevas_matriculas = row['Leads'] * nueva_tasa
            
            # Calcular nuevo CPA proyectado (manteniendo presupuesto constante)
            nuevo_cpa = np.where(
                nuevas_matriculas > 0,
                row['Presupuesto Asignado (USD)'] / nuevas_matriculas,
                float('inf')
            )
            
            # Calcular incremento de matrículas
            incremento_matriculas = nuevas_matriculas - row['Matrículas']
            
            # Calcular porcentaje de mejora en CPA
            mejora_cpa_porcentual = np.where(
                row['CPA Actual'] > 0 and row['CPA Actual'] != float('inf'),
                (row['CPA Actual'] - nuevo_cpa) / row['CPA Actual'] * 100,
                0
            )
            
            # Almacenar resultados
            resultados.append({
                'Marca': row['Marca'],
                'Canal': row['Canal'],
                'Escenario': f'Incremento {incremento*100:.0f}%',
                'Leads': row['Leads'],
                'Tasa Conversión Actual': row['Tasa Conversión'],
                'Tasa Conversión Nueva': nueva_tasa,
                'Matrículas Actuales': row['Matrículas'],
                'Matrículas Proyectadas': nuevas_matriculas,
                'Incremento Matrículas': incremento_matriculas,
                'Presupuesto (USD)': row['Presupuesto Asignado (USD)'],
                'CPA Actual (USD)': row['CPA Actual'],
                'CPA Proyectado (USD)': nuevo_cpa,
                'Mejora CPA (%)': mejora_cpa_porcentual
            })
    
    # Convertir a DataFrame
    df_resultados = pd.DataFrame(resultados)
    
    # Redondear valores numéricos
    columnas_redondeo = ['Tasa Conversión Actual', 'Tasa Conversión Nueva', 
                         'Matrículas Proyectadas', 'Incremento Matrículas',
                         'CPA Proyectado (USD)', 'Mejora CPA (%)']
    
    for col in columnas_redondeo:
        if col in df_resultados.columns:
            df_resultados[col] = df_resultados[col].round(2)
    
    return df_resultados


def visualizar_mejora_conversion(df_simulacion, directorio=None):
    """
    Genera visualizaciones de los resultados de la simulación de mejora de conversión.
    
    Args:
        df_simulacion (pandas.DataFrame): DataFrame con resultados de la simulación.
        directorio (str, opcional): Directorio donde guardar las visualizaciones.
        
    Returns:
        dict: Diccionario con rutas de los archivos generados.
    """
    # Configurar estilo de visualización
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("Set2")
    
    # Crear directorio si no existe
    if directorio is None:
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        directorio = os.path.join('../reportes', fecha_actual)
        if not os.path.exists(directorio):
            os.makedirs(directorio)
    
    archivos_generados = {}
    
    # 1. Gráfico de barras: Incremento de matrículas por canal y escenario
    plt.figure(figsize=(14, 8))
    
    # Pivotar datos para gráfico
    pivot_matriculas = df_simulacion.pivot_table(
        index=['Marca', 'Canal'],
        columns='Escenario',
        values='Matrículas Proyectadas'
    ).reset_index()
    
    # Preparar datos para visualización
    marcas = pivot_matriculas['Marca'].unique()
    
    for i, marca in enumerate(marcas):
        # Filtrar por marca
        df_marca = pivot_matriculas[pivot_matriculas['Marca'] == marca]
        
        # Crear subgráfico
        ax = plt.subplot(len(marcas), 1, i+1)
        
        # Crear gráfico de barras
        df_plot = df_marca.melt(
            id_vars=['Marca', 'Canal'],
            var_name='Escenario',
            value_name='Matrículas Proyectadas'
        )
        
        sns.barplot(
            data=df_plot,
            x='Canal',
            y='Matrículas Proyectadas',
            hue='Escenario',
            ax=ax
        )
        
        # Configurar títulos y etiquetas
        plt.title(f'Matrículas Proyectadas por Escenario - {marca}', fontsize=12)
        plt.xlabel('Canal', fontsize=10)
        plt.ylabel('Matrículas', fontsize=10)
        plt.xticks(rotation=45, ha='right')
        
        # Ajustar leyenda
        if i == 0:
            plt.legend(title='Escenario', bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            plt.legend([],[], frameon=False)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    ruta_archivo = os.path.join(directorio, 'simulacion_matriculas_por_escenario.png')
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos_generados['matriculas'] = ruta_archivo
    
    # 2. Gráfico de barras: Mejora de CPA por canal y escenario
    plt.figure(figsize=(14, 8))
    
    # Pivotar datos para gráfico
    pivot_cpa = df_simulacion.pivot_table(
        index=['Marca', 'Canal'],
        columns='Escenario',
        values='CPA Proyectado (USD)'
    ).reset_index()
    
    # Preparar datos para visualización
    for i, marca in enumerate(marcas):
        # Filtrar por marca
        df_marca = pivot_cpa[pivot_cpa['Marca'] == marca]
        
        # Crear subgráfico
        ax = plt.subplot(len(marcas), 1, i+1)
        
        # Crear gráfico de barras
        df_plot = df_marca.melt(
            id_vars=['Marca', 'Canal'],
            var_name='Escenario',
            value_name='CPA Proyectado (USD)'
        )
        
        sns.barplot(
            data=df_plot,
            x='Canal',
            y='CPA Proyectado (USD)',
            hue='Escenario',
            ax=ax
        )
        
        # Configurar títulos y etiquetas
        plt.title(f'CPA Proyectado por Escenario - {marca}', fontsize=12)
        plt.xlabel('Canal', fontsize=10)
        plt.ylabel('CPA (USD)', fontsize=10)
        plt.xticks(rotation=45, ha='right')
        
        # Ajustar leyenda
        if i == 0:
            plt.legend(title='Escenario', bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            plt.legend([],[], frameon=False)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    ruta_archivo = os.path.join(directorio, 'simulacion_cpa_por_escenario.png')
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos_generados['cpa'] = ruta_archivo
    
    # 3. Resumen de impacto global por escenario
    plt.figure(figsize=(12, 6))
    
    # Agrupar datos por escenario
    resumen_global = df_simulacion.groupby('Escenario').agg({
        'Matrículas Actuales': 'sum',
        'Matrículas Proyectadas': 'sum',
        'Incremento Matrículas': 'sum',
        'Presupuesto (USD)': 'sum'
    }).reset_index()
    
    # Calcular CPA global
    resumen_global['CPA Global Actual (USD)'] = resumen_global['Presupuesto (USD)'] / resumen_global['Matrículas Actuales']
    resumen_global['CPA Global Proyectado (USD)'] = resumen_global['Presupuesto (USD)'] / resumen_global['Matrículas Proyectadas']
    resumen_global['Mejora CPA Global (%)'] = (resumen_global['CPA Global Actual (USD)'] - resumen_global['CPA Global Proyectado (USD)']) / resumen_global['CPA Global Actual (USD)'] * 100
    
    # Crear gráfico de barras para incremento de matrículas
    ax1 = plt.subplot(1, 2, 1)
    sns.barplot(
        data=resumen_global,
        x='Escenario',
        y='Incremento Matrículas',
        ax=ax1
    )
    
    # Configurar títulos y etiquetas
    plt.title('Incremento Total de Matrículas por Escenario', fontsize=12)
    plt.xlabel('Escenario', fontsize=10)
    plt.ylabel('Incremento de Matrículas', fontsize=10)
    
    # Añadir etiquetas de valor
    for i, v in enumerate(resumen_global['Incremento Matrículas']):
        ax1.text(i, v + 1, f"{v:.0f}", ha='center', fontsize=9)
    
    # Crear gráfico de barras para mejora de CPA
    ax2 = plt.subplot(1, 2, 2)
    sns.barplot(
        data=resumen_global,
        x='Escenario',
        y='Mejora CPA Global (%)',
        ax=ax2
    )
    
    # Configurar títulos y etiquetas
    plt.title('Mejora de CPA Global por Escenario', fontsize=12)
    plt.xlabel('Escenario', fontsize=10)
    plt.ylabel('Mejora de CPA (%)', fontsize=10)
    
    # Añadir etiquetas de valor
    for i, v in enumerate(resumen_global['Mejora CPA Global (%)']):
        ax2.text(i, v + 0.5, f"{v:.1f}%", ha='center', fontsize=9)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    ruta_archivo = os.path.join(directorio, 'resumen_impacto_global_conversion.png')
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos_generados['resumen'] = ruta_archivo
    
    return archivos_generados


def generar_reporte_mejora_conversion(datos_metricas, directorio=None):
    """
    Genera un reporte completo de simulación de mejora de conversión.
    
    Args:
        datos_metricas (pandas.DataFrame): DataFrame con métricas de rendimiento actuales.
        directorio (str, opcional): Directorio donde guardar el reporte.
        
    Returns:
        dict: Diccionario con rutas de los archivos generados y DataFrame con resultados.
    """
    # Simular mejoras de conversión
    df_simulacion = simular_mejora_conversion(datos_metricas)
    
    # Generar visualizaciones
    archivos_generados = visualizar_mejora_conversion(df_simulacion, directorio)
    
    # Generar reporte Excel
    if directorio is None:
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        directorio = os.path.join('../reportes', fecha_actual)
        if not os.path.exists(directorio):
            os.makedirs(directorio)
    
    # Guardar resultados en Excel
    ruta_excel = os.path.join(directorio, 'simulacion_mejora_conversion.xlsx')
    
    # Crear libro Excel
    writer = pd.ExcelWriter(ruta_excel, engine='xlsxwriter')
    
    # Guardar datos en Excel
    df_simulacion.to_excel(writer, sheet_name='Simulación Detallada', index=False)
    
    # Crear resumen por escenario
    resumen_escenario = df_simulacion.groupby(['Escenario']).agg({
        'Matrículas Actuales': 'sum',
        'Matrículas Proyectadas': 'sum',
        'Incremento Matrículas': 'sum',
        'Presupuesto (USD)': 'sum'
    }).reset_index()
    
    # Calcular CPA global
    resumen_escenario['CPA Global Actual (USD)'] = resumen_escenario['Presupuesto (USD)'] / resumen_escenario['Matrículas Actuales']
    resumen_escenario['CPA Global Proyectado (USD)'] = resumen_escenario['Presupuesto (USD)'] / resumen_escenario['Matrículas Proyectadas']
    resumen_escenario['Mejora CPA Global (%)'] = (resumen_escenario['CPA Global Actual (USD)'] - resumen_escenario['CPA Global Proyectado (USD)']) / resumen_escenario['CPA Global Actual (USD)'] * 100
    
    # Guardar resumen en Excel
    resumen_escenario.to_excel(writer, sheet_name='Resumen Global', index=False)
    
    # Crear resumen por marca y escenario
    resumen_marca = df_simulacion.groupby(['Marca', 'Escenario']).agg({
        'Matrículas Actuales': 'sum',
        'Matrículas Proyectadas': 'sum',
        'Incremento Matrículas': 'sum',
        'Presupuesto (USD)': 'sum'
    }).reset_index()
    
    # Calcular CPA por marca
    resumen_marca['CPA Actual (USD)'] = resumen_marca['Presupuesto (USD)'] / resumen_marca['Matrículas Actuales']
    resumen_marca['CPA Proyectado (USD)'] = resumen_marca['Presupuesto (USD)'] / resumen_marca['Matrículas Proyectadas']
    resumen_marca['Mejora CPA (%)'] = (resumen_marca['CPA Actual (USD)'] - resumen_marca['CPA Proyectado (USD)']) / resumen_marca['CPA Actual (USD)'] * 100
    
    # Guardar resumen por marca en Excel
    resumen_marca.to_excel(writer, sheet_name='Resumen por Marca', index=False)
    
    # Guardar Excel
    writer.close()
    
    archivos_generados['excel'] = ruta_excel
    
    return {
        'archivos': archivos_generados,
        'resultados': df_simulacion,
        'resumen_global': resumen_escenario,
        'resumen_marca': resumen_marca
    }


if __name__ == "__main__":
    # Ejemplo de uso
    from cargar_datos import cargar_datos_crm, cargar_datos_planificacion
    from analizar_rendimiento import calcular_metricas_rendimiento
    
    try:
        print("Cargando datos...")
        datos_crm = cargar_datos_crm("../datos/leads_matriculas_reales.csv")
        datos_planificacion = cargar_datos_planificacion("../datos/planificacion_quincenal.csv")
        
        print("Calculando métricas de rendimiento...")
        metricas = calcular_metricas_rendimiento(datos_crm, datos_planificacion)
        
        print("Generando simulación de mejora de conversión...")
        resultado_simulacion = generar_reporte_mejora_conversion(metricas)
        
        print(f"Reporte generado en: {resultado_simulacion['archivos']['excel']}")
        print("\nResumen de resultados:")
        print(resultado_simulacion['resumen_global'][['Escenario', 'Incremento Matrículas', 'Mejora CPA Global (%)']])
        
    except Exception as e:
        print(f"Error: {e}") 