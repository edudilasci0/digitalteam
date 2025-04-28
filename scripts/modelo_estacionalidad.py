"""
Módulo para analizar patrones estacionales en datos de marketing y comparar
el avance actual con datos históricos por quincena.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime, timedelta


def calcular_patrones_estacionales(datos_historicos, agrupacion='quincena'):
    """
    Calcula patrones estacionales de leads, matrículas y tasa de conversión.
    
    Args:
        datos_historicos (pandas.DataFrame): DataFrame con datos históricos de conversiones.
        agrupacion (str): Tipo de agrupación temporal ('quincena', 'mes', 'semana').
        
    Returns:
        pandas.DataFrame: DataFrame con patrones estacionales calculados.
    """
    # Verificar columnas necesarias
    columnas_requeridas = ['Fecha', 'Marca', 'Canal', 'Leads', 'Matrículas']
    for col in columnas_requeridas:
        if col not in datos_historicos.columns:
            raise ValueError(f"El DataFrame debe contener la columna '{col}'")
    
    # Convertir fecha a datetime si no lo es
    datos_historicos['Fecha'] = pd.to_datetime(datos_historicos['Fecha'])
    
    # Crear columnas de agrupación temporal
    if agrupacion == 'quincena':
        # Determinar quincena (1-24, dos por mes)
        datos_historicos['Mes'] = datos_historicos['Fecha'].dt.month
        datos_historicos['Quincena'] = ((datos_historicos['Mes'] - 1) * 2 + 
                                      (datos_historicos['Fecha'].dt.day > 15).astype(int) + 1)
        grupo_temporal = 'Quincena'
    elif agrupacion == 'mes':
        datos_historicos['Mes'] = datos_historicos['Fecha'].dt.month
        grupo_temporal = 'Mes'
    elif agrupacion == 'semana':
        datos_historicos['Semana'] = datos_historicos['Fecha'].dt.isocalendar().week
        grupo_temporal = 'Semana'
    else:
        raise ValueError("Tipo de agrupación no válido. Use 'quincena', 'mes' o 'semana'.")
    
    # Calcular métricas estacionales
    patrones = datos_historicos.groupby(['Marca', 'Canal', grupo_temporal]).agg({
        'Leads': 'sum',
        'Matrículas': 'sum'
    }).reset_index()
    
    # Calcular tasa de conversión
    patrones['Tasa Conversión'] = np.where(
        patrones['Leads'] > 0,
        patrones['Matrículas'] / patrones['Leads'],
        0
    )
    
    # Calcular promedios globales por marca y canal
    promedios_globales = datos_historicos.groupby(['Marca', 'Canal']).agg({
        'Leads': 'sum',
        'Matrículas': 'sum'
    }).reset_index()
    
    promedios_globales['Tasa Conversión Global'] = np.where(
        promedios_globales['Leads'] > 0,
        promedios_globales['Matrículas'] / promedios_globales['Leads'],
        0
    )
    
    # Unir patrones con promedios globales
    patrones = pd.merge(patrones, promedios_globales[['Marca', 'Canal', 'Tasa Conversión Global']], 
                        on=['Marca', 'Canal'], how='left')
    
    # Calcular índices estacionales (relación entre valor de periodo y promedio global)
    total_periodos = datos_historicos[grupo_temporal].nunique()
    
    patrones['Índice Estacional Leads'] = patrones['Leads'] / (promedios_globales['Leads'] / total_periodos)
    patrones['Índice Estacional Matrículas'] = patrones['Matrículas'] / (promedios_globales['Matrículas'] / total_periodos)
    patrones['Índice Estacional Conversión'] = patrones['Tasa Conversión'] / patrones['Tasa Conversión Global']
    
    return patrones


def comparar_avance_estacional(datos_actuales, patrones_estacionales, periodo_actual):
    """
    Compara el avance actual con los patrones estacionales históricos.
    
    Args:
        datos_actuales (pandas.DataFrame): DataFrame con datos actuales.
        patrones_estacionales (pandas.DataFrame): DataFrame con patrones estacionales.
        periodo_actual (int): Período actual (quincena, mes o semana).
        
    Returns:
        pandas.DataFrame: DataFrame con comparación de avance actual vs histórico.
    """
    # Verificar columnas necesarias
    columnas_actuales = ['Marca', 'Canal', 'Leads', 'Matrículas']
    for col in columnas_actuales:
        if col not in datos_actuales.columns:
            raise ValueError(f"El DataFrame de datos actuales debe contener la columna '{col}'")
    
    # Agrupar datos actuales por marca y canal
    actual_agrupado = datos_actuales.groupby(['Marca', 'Canal']).agg({
        'Leads': 'sum',
        'Matrículas': 'sum'
    }).reset_index()
    
    # Calcular tasa de conversión actual
    actual_agrupado['Tasa Conversión Actual'] = np.where(
        actual_agrupado['Leads'] > 0,
        actual_agrupado['Matrículas'] / actual_agrupado['Leads'],
        0
    )
    
    # Detectar el grupo temporal usado en patrones
    if 'Quincena' in patrones_estacionales.columns:
        grupo_temporal = 'Quincena'
    elif 'Mes' in patrones_estacionales.columns:
        grupo_temporal = 'Mes'
    elif 'Semana' in patrones_estacionales.columns:
        grupo_temporal = 'Semana'
    else:
        raise ValueError("No se detectó un grupo temporal válido en los patrones estacionales")
    
    # Filtrar patrones estacionales para el periodo actual
    patrones_periodo = patrones_estacionales[patrones_estacionales[grupo_temporal] == periodo_actual]
    
    # Unir datos actuales con patrones estacionales
    comparacion = pd.merge(
        actual_agrupado,
        patrones_periodo[['Marca', 'Canal', 'Leads', 'Matrículas', 'Tasa Conversión', 
                         'Índice Estacional Leads', 'Índice Estacional Matrículas',
                         'Índice Estacional Conversión']],
        on=['Marca', 'Canal'],
        how='left',
        suffixes=('_Actual', '_Esperado')
    )
    
    # Calcular diferencias
    comparacion['Diferencia Leads (%)'] = np.where(
        comparacion['Leads_Esperado'] > 0,
        (comparacion['Leads_Actual'] - comparacion['Leads_Esperado']) / comparacion['Leads_Esperado'] * 100,
        0
    )
    
    comparacion['Diferencia Matrículas (%)'] = np.where(
        comparacion['Matrículas_Esperado'] > 0,
        (comparacion['Matrículas_Actual'] - comparacion['Matrículas_Esperado']) / comparacion['Matrículas_Esperado'] * 100,
        0
    )
    
    comparacion['Diferencia Conversión (pp)'] = comparacion['Tasa Conversión Actual'] - comparacion['Tasa Conversión']
    
    return comparacion


def visualizar_patrones_estacionales(patrones_estacionales, directorio=None):
    """
    Genera visualizaciones de patrones estacionales.
    
    Args:
        patrones_estacionales (pandas.DataFrame): DataFrame con patrones estacionales.
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
    
    # Detectar el grupo temporal usado
    if 'Quincena' in patrones_estacionales.columns:
        grupo_temporal = 'Quincena'
    elif 'Mes' in patrones_estacionales.columns:
        grupo_temporal = 'Mes'
    elif 'Semana' in patrones_estacionales.columns:
        grupo_temporal = 'Semana'
    else:
        raise ValueError("No se detectó un grupo temporal válido en los patrones estacionales")
    
    # 1. Gráfico de líneas: Índice estacional de leads por periodo
    plt.figure(figsize=(14, 10))
    
    # Obtener marcas únicas
    marcas = patrones_estacionales['Marca'].unique()
    
    for i, marca in enumerate(marcas):
        # Filtrar datos por marca
        df_marca = patrones_estacionales[patrones_estacionales['Marca'] == marca]
        
        # Crear subgráfico
        ax = plt.subplot(len(marcas), 1, i+1)
        
        # Crear gráfico de líneas
        sns.lineplot(
            data=df_marca,
            x=grupo_temporal,
            y='Índice Estacional Leads',
            hue='Canal',
            marker='o',
            ax=ax
        )
        
        # Configurar títulos y etiquetas
        plt.title(f'Índice Estacional de Leads por {grupo_temporal} - {marca}', fontsize=12)
        plt.xlabel(grupo_temporal, fontsize=10)
        plt.ylabel('Índice Estacional', fontsize=10)
        
        # Agregar línea de referencia (índice = 1)
        plt.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
        
        # Ajustar leyenda
        if i == 0:
            plt.legend(title='Canal', bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            plt.legend([],[], frameon=False)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    ruta_archivo = os.path.join(directorio, f'indice_estacional_leads_por_{grupo_temporal.lower()}.png')
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos_generados['leads'] = ruta_archivo
    
    # 2. Gráfico de líneas: Índice estacional de conversión por periodo
    plt.figure(figsize=(14, 10))
    
    for i, marca in enumerate(marcas):
        # Filtrar datos por marca
        df_marca = patrones_estacionales[patrones_estacionales['Marca'] == marca]
        
        # Crear subgráfico
        ax = plt.subplot(len(marcas), 1, i+1)
        
        # Crear gráfico de líneas
        sns.lineplot(
            data=df_marca,
            x=grupo_temporal,
            y='Índice Estacional Conversión',
            hue='Canal',
            marker='o',
            ax=ax
        )
        
        # Configurar títulos y etiquetas
        plt.title(f'Índice Estacional de Conversión por {grupo_temporal} - {marca}', fontsize=12)
        plt.xlabel(grupo_temporal, fontsize=10)
        plt.ylabel('Índice Estacional', fontsize=10)
        
        # Agregar línea de referencia (índice = 1)
        plt.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
        
        # Ajustar leyenda
        if i == 0:
            plt.legend(title='Canal', bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            plt.legend([],[], frameon=False)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    ruta_archivo = os.path.join(directorio, f'indice_estacional_conversion_por_{grupo_temporal.lower()}.png')
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos_generados['conversion'] = ruta_archivo
    
    # 3. Gráfico de calor: Mapa de estacionalidad por canal y periodo
    plt.figure(figsize=(16, 10))
    
    for i, metrica in enumerate(['Índice Estacional Leads', 'Índice Estacional Conversión']):
        # Por cada marca
        for j, marca in enumerate(marcas):
            # Calcular posición del subgráfico
            idx = i * len(marcas) + j + 1
            
            # Crear subgráfico
            ax = plt.subplot(2, len(marcas), idx)
            
            # Filtrar datos por marca
            df_marca = patrones_estacionales[patrones_estacionales['Marca'] == marca]
            
            # Pivotar datos para gráfico de calor
            pivot = df_marca.pivot(index='Canal', columns=grupo_temporal, values=metrica)
            
            # Crear gráfico de calor
            sns.heatmap(
                pivot,
                cmap='YlGnBu',
                cbar=True,
                annot=True,
                fmt='.2f',
                center=1.0,
                ax=ax
            )
            
            # Configurar títulos y etiquetas
            if i == 0:
                title = f'Estacionalidad de Leads - {marca}'
            else:
                title = f'Estacionalidad de Conversión - {marca}'
                
            plt.title(title, fontsize=11)
            plt.xlabel(grupo_temporal, fontsize=9)
            plt.ylabel('Canal', fontsize=9)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    ruta_archivo = os.path.join(directorio, f'mapa_calor_estacionalidad_{grupo_temporal.lower()}.png')
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos_generados['mapa_calor'] = ruta_archivo
    
    return archivos_generados


def visualizar_comparacion_avance(comparacion_avance, directorio=None):
    """
    Genera visualizaciones de la comparación de avance actual vs histórico.
    
    Args:
        comparacion_avance (pandas.DataFrame): DataFrame con comparación de avance.
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
    
    # 1. Gráfico de barras: Comparación de leads actual vs esperado
    plt.figure(figsize=(14, 8))
    
    # Preparar datos para visualización
    df_plot = comparacion_avance.melt(
        id_vars=['Marca', 'Canal'],
        value_vars=['Leads_Actual', 'Leads_Esperado'],
        var_name='Tipo',
        value_name='Leads'
    )
    
    # Ajustar etiquetas para mejor visualización
    df_plot['Tipo'] = df_plot['Tipo'].map({
        'Leads_Actual': 'Actual',
        'Leads_Esperado': 'Esperado'
    })
    
    # Obtener marcas únicas
    marcas = comparacion_avance['Marca'].unique()
    
    for i, marca in enumerate(marcas):
        # Filtrar datos por marca
        df_marca = df_plot[df_plot['Marca'] == marca]
        
        # Crear subgráfico
        ax = plt.subplot(len(marcas), 1, i+1)
        
        # Crear gráfico de barras
        sns.barplot(
            data=df_marca,
            x='Canal',
            y='Leads',
            hue='Tipo',
            ax=ax
        )
        
        # Configurar títulos y etiquetas
        plt.title(f'Leads Actuales vs Esperados - {marca}', fontsize=12)
        plt.xlabel('Canal', fontsize=10)
        plt.ylabel('Leads', fontsize=10)
        plt.xticks(rotation=45, ha='right')
        
        # Añadir etiquetas de porcentaje de diferencia
        canales = comparacion_avance[comparacion_avance['Marca'] == marca]['Canal'].unique()
        for j, canal in enumerate(canales):
            datos_canal = comparacion_avance[(comparacion_avance['Marca'] == marca) & 
                                           (comparacion_avance['Canal'] == canal)]
            if not datos_canal.empty:
                dif_porcentaje = datos_canal['Diferencia Leads (%)'].values[0]
                y_pos = max(datos_canal['Leads_Actual'].values[0], datos_canal['Leads_Esperado'].values[0])
                
                # Formato y color según si es positivo o negativo
                if dif_porcentaje >= 0:
                    texto = f"+{dif_porcentaje:.1f}%"
                    color = 'green'
                else:
                    texto = f"{dif_porcentaje:.1f}%"
                    color = 'red'
                
                ax.text(j, y_pos + 5, texto, ha='center', color=color, fontweight='bold', fontsize=9)
        
        # Ajustar leyenda
        if i == 0:
            plt.legend(title='', bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            plt.legend([],[], frameon=False)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    ruta_archivo = os.path.join(directorio, 'comparacion_leads_actual_vs_esperado.png')
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos_generados['comparacion_leads'] = ruta_archivo
    
    # 2. Gráfico de barras: Comparación de matrículas actual vs esperado
    plt.figure(figsize=(14, 8))
    
    # Preparar datos para visualización
    df_plot = comparacion_avance.melt(
        id_vars=['Marca', 'Canal'],
        value_vars=['Matrículas_Actual', 'Matrículas_Esperado'],
        var_name='Tipo',
        value_name='Matrículas'
    )
    
    # Ajustar etiquetas para mejor visualización
    df_plot['Tipo'] = df_plot['Tipo'].map({
        'Matrículas_Actual': 'Actual',
        'Matrículas_Esperado': 'Esperado'
    })
    
    for i, marca in enumerate(marcas):
        # Filtrar datos por marca
        df_marca = df_plot[df_plot['Marca'] == marca]
        
        # Crear subgráfico
        ax = plt.subplot(len(marcas), 1, i+1)
        
        # Crear gráfico de barras
        sns.barplot(
            data=df_marca,
            x='Canal',
            y='Matrículas',
            hue='Tipo',
            ax=ax
        )
        
        # Configurar títulos y etiquetas
        plt.title(f'Matrículas Actuales vs Esperadas - {marca}', fontsize=12)
        plt.xlabel('Canal', fontsize=10)
        plt.ylabel('Matrículas', fontsize=10)
        plt.xticks(rotation=45, ha='right')
        
        # Añadir etiquetas de porcentaje de diferencia
        canales = comparacion_avance[comparacion_avance['Marca'] == marca]['Canal'].unique()
        for j, canal in enumerate(canales):
            datos_canal = comparacion_avance[(comparacion_avance['Marca'] == marca) & 
                                           (comparacion_avance['Canal'] == canal)]
            if not datos_canal.empty:
                dif_porcentaje = datos_canal['Diferencia Matrículas (%)'].values[0]
                y_pos = max(datos_canal['Matrículas_Actual'].values[0], datos_canal['Matrículas_Esperado'].values[0])
                
                # Formato y color según si es positivo o negativo
                if dif_porcentaje >= 0:
                    texto = f"+{dif_porcentaje:.1f}%"
                    color = 'green'
                else:
                    texto = f"{dif_porcentaje:.1f}%"
                    color = 'red'
                
                ax.text(j, y_pos + 0.5, texto, ha='center', color=color, fontweight='bold', fontsize=9)
        
        # Ajustar leyenda
        if i == 0:
            plt.legend(title='', bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            plt.legend([],[], frameon=False)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    ruta_archivo = os.path.join(directorio, 'comparacion_matriculas_actual_vs_esperado.png')
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos_generados['comparacion_matriculas'] = ruta_archivo
    
    # 3. Gráfico de barras: Diferencia porcentual por canal
    plt.figure(figsize=(14, 10))
    
    # Crear subgráficos para leads y matrículas
    ax1 = plt.subplot(2, 1, 1)
    ax2 = plt.subplot(2, 1, 2)
    
    # Colores según diferencia (verde para positivo, rojo para negativo)
    def asignar_color(valor):
        return 'green' if valor >= 0 else 'red'
    
    for i, marca in enumerate(marcas):
        # Filtrar datos por marca
        df_marca = comparacion_avance[comparacion_avance['Marca'] == marca]
        
        # Crear gráfico para diferencia en leads
        sns.barplot(
            data=df_marca,
            x='Canal',
            y='Diferencia Leads (%)',
            hue='Marca',
            palette=[sns.color_palette("Set2")[i]],
            ax=ax1,
            dodge=False,
            alpha=0.7
        )
        
        # Crear gráfico para diferencia en matrículas
        sns.barplot(
            data=df_marca,
            x='Canal',
            y='Diferencia Matrículas (%)',
            hue='Marca',
            palette=[sns.color_palette("Set2")[i]],
            ax=ax2,
            dodge=False,
            alpha=0.7
        )
    
    # Configurar títulos y etiquetas para leads
    ax1.set_title('Diferencia Porcentual en Leads (Actual vs Esperado)', fontsize=12)
    ax1.set_xlabel('')
    ax1.set_ylabel('Diferencia (%)', fontsize=10)
    ax1.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
    
    # Configurar títulos y etiquetas para matrículas
    ax2.set_title('Diferencia Porcentual en Matrículas (Actual vs Esperado)', fontsize=12)
    ax2.set_xlabel('Canal', fontsize=10)
    ax2.set_ylabel('Diferencia (%)', fontsize=10)
    ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
    
    # Eliminar leyendas duplicadas
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles, labels, title='Marca', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.legend([], [], frameon=False)
    
    # Añadir coloración y etiquetas a las barras
    for ax, col in [(ax1, 'Diferencia Leads (%)'), (ax2, 'Diferencia Matrículas (%)')]:
        # Colorear barras según valor
        for i, patch in enumerate(ax.patches):
            # Calcular índice para acceder a los datos correctos
            idx = i % len(comparacion_avance)
            if idx < len(comparacion_avance):
                valor = comparacion_avance.iloc[idx][col]
                patch.set_facecolor(asignar_color(valor))
                
                # Añadir etiqueta de valor
                ax.text(
                    patch.get_x() + patch.get_width() / 2,
                    patch.get_height() + (5 if valor >= 0 else -10),
                    f"{valor:.1f}%",
                    ha='center',
                    color=asignar_color(valor),
                    fontweight='bold',
                    fontsize=8
                )
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar figura
    ruta_archivo = os.path.join(directorio, 'diferencia_porcentual_actual_vs_esperado.png')
    plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    
    archivos_generados['diferencia_porcentual'] = ruta_archivo
    
    return archivos_generados


def generar_reporte_estacionalidad(datos_historicos, datos_actuales, periodo_actual, 
                                  agrupacion='quincena', directorio=None):
    """
    Genera un reporte completo de análisis estacional y comparación de avance.
    
    Args:
        datos_historicos (pandas.DataFrame): DataFrame con datos históricos.
        datos_actuales (pandas.DataFrame): DataFrame con datos actuales.
        periodo_actual (int): Período actual (quincena, mes o semana).
        agrupacion (str): Tipo de agrupación temporal ('quincena', 'mes', 'semana').
        directorio (str, opcional): Directorio donde guardar el reporte.
        
    Returns:
        dict: Diccionario con resultados y rutas de archivos generados.
    """
    # Crear directorio si no existe
    if directorio is None:
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        directorio = os.path.join('../reportes', fecha_actual)
        if not os.path.exists(directorio):
            os.makedirs(directorio)
    
    # Calcular patrones estacionales
    patrones = calcular_patrones_estacionales(datos_historicos, agrupacion)
    
    # Comparar avance actual con histórico
    comparacion = comparar_avance_estacional(datos_actuales, patrones, periodo_actual)
    
    # Generar visualizaciones
    archivos_patrones = visualizar_patrones_estacionales(patrones, directorio)
    archivos_comparacion = visualizar_comparacion_avance(comparacion, directorio)
    
    # Generar reporte Excel
    ruta_excel = os.path.join(directorio, 'analisis_estacionalidad.xlsx')
    
    # Crear libro Excel
    writer = pd.ExcelWriter(ruta_excel, engine='xlsxwriter')
    
    # Guardar patrones estacionales en Excel
    patrones.to_excel(writer, sheet_name='Patrones Estacionales', index=False)
    
    # Guardar comparación en Excel
    comparacion.to_excel(writer, sheet_name='Comparación Avance', index=False)
    
    # Crear resumen de diferencias
    resumen_diferencias = comparacion.groupby('Marca').agg({
        'Diferencia Leads (%)': 'mean',
        'Diferencia Matrículas (%)': 'mean',
        'Diferencia Conversión (pp)': 'mean'
    }).reset_index()
    
    # Guardar resumen en Excel
    resumen_diferencias.to_excel(writer, sheet_name='Resumen Diferencias', index=False)
    
    # Guardar Excel
    writer.close()
    
    # Combinar archivos generados
    archivos_generados = {**archivos_patrones, **archivos_comparacion, 'excel': ruta_excel}
    
    return {
        'patrones': patrones,
        'comparacion': comparacion,
        'resumen': resumen_diferencias,
        'archivos': archivos_generados
    }


if __name__ == "__main__":
    # Ejemplo de uso
    from cargar_datos import cargar_datos_crm
    
    try:
        print("Cargando datos históricos...")
        datos_historicos = cargar_datos_crm("../datos/leads_matriculas_historicos.csv")
        
        print("Cargando datos actuales...")
        datos_actuales = cargar_datos_crm("../datos/leads_matriculas_reales.csv")
        
        # Determinar quincena actual (ejemplo: quincena 12 = segunda quincena de junio)
        mes_actual = datetime.now().month
        dia_actual = datetime.now().day
        quincena_actual = (mes_actual - 1) * 2 + (2 if dia_actual > 15 else 1)
        
        print(f"Generando reporte de estacionalidad para quincena {quincena_actual}...")
        resultado = generar_reporte_estacionalidad(
            datos_historicos,
            datos_actuales,
            quincena_actual,
            agrupacion='quincena'
        )
        
        print(f"Reporte generado en: {resultado['archivos']['excel']}")
        print("\nResumen de diferencias por marca:")
        print(resultado['resumen'])
        
    except Exception as e:
        print(f"Error: {e}") 