"""
Módulo para analizar la estacionalidad de leads y matrículas usando datos históricos.
Implementa modelos de machine learning para predicción basada en patrones temporales.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def preparar_datos_temporales(datos_historicos, freq='Q', columna_fecha='Fecha'):
    """
    Prepara los datos históricos para análisis de series temporales.
    
    Args:
        datos_historicos (pandas.DataFrame): DataFrame con datos históricos.
        freq (str): Frecuencia para agregación ('D'=diaria, 'W'=semanal, 
                   'M'=mensual, 'Q'=quincenal, 'SM'=semimensual).
        columna_fecha (str): Nombre de la columna que contiene las fechas.
        
    Returns:
        pandas.DataFrame: DataFrame con datos agregados por periodo.
    """
    # Verificar columnas necesarias
    columnas_requeridas = [columna_fecha, 'Tipo']
    for col in columnas_requeridas:
        if col not in datos_historicos.columns:
            raise ValueError(f"El DataFrame debe contener la columna '{col}'")
    
    # Asegurar que la columna de fecha sea datetime
    df = datos_historicos.copy()
    df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    
    # Crear columna de periodo según la frecuencia solicitada
    if freq == 'D':  # Diario
        df['Periodo'] = df[columna_fecha].dt.date
    elif freq == 'W':  # Semanal
        df['Periodo'] = df[columna_fecha].dt.to_period('W').dt.start_time
    elif freq == 'M':  # Mensual
        df['Periodo'] = df[columna_fecha].dt.to_period('M').dt.start_time
    elif freq == 'Q':  # Quincenal
        # Para quincenal, determinamos si es primera o segunda quincena
        df['Quincena'] = (df[columna_fecha].dt.day > 15).astype(int) + 1
        df['Periodo'] = df[columna_fecha].dt.to_period('M').dt.start_time
        # Combinar año-mes-quincena
        df['Periodo'] = df.apply(
            lambda row: row['Periodo'].replace(day=1) if row['Quincena'] == 1 
            else row['Periodo'].replace(day=16), axis=1
        )
    elif freq == 'SM':  # Semimensual (cada 6 meses)
        df['Semestre'] = (df[columna_fecha].dt.month > 6).astype(int) + 1
        df['Periodo'] = df[columna_fecha].dt.year.astype(str) + "-S" + df['Semestre'].astype(str)
    else:
        raise ValueError(f"Frecuencia '{freq}' no soportada")
    
    # Contar leads y matrículas por periodo
    leads_por_periodo = df[df['Tipo'] == 'Lead'].groupby('Periodo').size()
    matriculas_por_periodo = df[df['Tipo'] == 'Matrícula'].groupby('Periodo').size()
    
    # Crear DataFrame con ambas métricas
    df_temporal = pd.DataFrame({
        'Leads': leads_por_periodo,
        'Matrículas': matriculas_por_periodo
    }).fillna(0)
    
    # Calcular tasa de conversión
    df_temporal['Tasa Conversión (%)'] = (df_temporal['Matrículas'] / df_temporal['Leads']) * 100
    df_temporal['Tasa Conversión (%)'] = df_temporal['Tasa Conversión (%)'].fillna(0)
    
    # Ordenar por periodo
    df_temporal = df_temporal.sort_index()
    
    return df_temporal


def analizar_estacionalidad(df_temporal, metrica='Leads', periodo=12):
    """
    Realiza un análisis de estacionalidad sobre una métrica.
    
    Args:
        df_temporal (pandas.DataFrame): DataFrame con datos temporales.
        metrica (str): Métrica a analizar ('Leads', 'Matrículas', 'Tasa Conversión (%)').
        periodo (int): Periodo para detectar estacionalidad (12 para patrón anual con datos mensuales).
        
    Returns:
        dict: Resultados del análisis de estacionalidad y figura generada.
    """
    # Verificar que la métrica existe
    if metrica not in df_temporal.columns:
        raise ValueError(f"La métrica '{metrica}' no existe en el DataFrame")
    
    # Verificar que hay suficientes datos para el análisis
    if len(df_temporal) < periodo * 2:
        raise ValueError(f"Se necesitan al menos {periodo * 2} periodos para el análisis de estacionalidad")
    
    try:
        # Realizar descomposición estacional
        descomposicion = seasonal_decompose(
            df_temporal[metrica],
            model='additive',
            period=periodo
        )
        
        # Crear figura para visualización
        fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
        
        # Graficar componentes
        descomposicion.observed.plot(ax=axes[0], color='blue')
        axes[0].set_ylabel('Observado')
        axes[0].set_title(f'Descomposición Estacional de {metrica}')
        
        descomposicion.trend.plot(ax=axes[1], color='green')
        axes[1].set_ylabel('Tendencia')
        
        descomposicion.seasonal.plot(ax=axes[2], color='red')
        axes[2].set_ylabel('Estacionalidad')
        
        descomposicion.resid.plot(ax=axes[3], color='purple')
        axes[3].set_ylabel('Residual')
        
        plt.tight_layout()
        
        # Calcular índices de estacionalidad
        indices_estacionalidad = pd.DataFrame(descomposicion.seasonal)
        indices_estacionalidad.columns = ['Índice']
        
        # Para facilitar la interpretación, normalizar los índices
        valor_base = indices_estacionalidad['Índice'].mean()
        indices_estacionalidad['Índice Normalizado'] = indices_estacionalidad['Índice'] / valor_base
        
        # Extraer periodos de mayor y menor actividad
        periodos_max = indices_estacionalidad.nlargest(3, 'Índice')
        periodos_min = indices_estacionalidad.nsmallest(3, 'Índice')
        
        return {
            'figura': fig,
            'descomposicion': descomposicion,
            'indices_estacionalidad': indices_estacionalidad,
            'periodos_max': periodos_max,
            'periodos_min': periodos_min
        }
    
    except Exception as e:
        raise ValueError(f"Error en el análisis de estacionalidad: {str(e)}")


def entrenar_modelo_prediccion(df_temporal, variables_adicionales=None):
    """
    Entrena un modelo de predicción basado en patrones históricos.
    
    Args:
        df_temporal (pandas.DataFrame): DataFrame con datos temporales.
        variables_adicionales (pandas.DataFrame, optional): Variables externas para el modelo.
        
    Returns:
        dict: Modelo entrenado y métricas de evaluación.
    """
    # Preparar datos para entrenamiento
    df_modelo = df_temporal.copy().reset_index()
    
    # Extraer características temporales
    if isinstance(df_modelo['Periodo'].iloc[0], pd.Timestamp):
        # Para fechas tipo timestamp
        df_modelo['Año'] = df_modelo['Periodo'].dt.year
        df_modelo['Mes'] = df_modelo['Periodo'].dt.month
        df_modelo['Día'] = df_modelo['Periodo'].dt.day
        df_modelo['DiaSemana'] = df_modelo['Periodo'].dt.dayofweek
        df_modelo['Quincena'] = (df_modelo['Día'] > 15).astype(int) + 1
        
        # Crear variables cíclicas para capturar estacionalidad
        df_modelo['Mes_seno'] = np.sin(2 * np.pi * df_modelo['Mes'] / 12)
        df_modelo['Mes_coseno'] = np.cos(2 * np.pi * df_modelo['Mes'] / 12)
    
    # Incorporar variables adicionales si se proporcionan
    if variables_adicionales is not None:
        df_modelo = pd.merge(
            df_modelo,
            variables_adicionales,
            how='left',
            left_on='Periodo',
            right_index=True
        )
    
    # Crear características de rezago (lag)
    for i in range(1, 4):  # Crear rezagos de 1, 2 y 3 periodos
        df_modelo[f'Leads_lag{i}'] = df_modelo['Leads'].shift(i)
        df_modelo[f'Matriculas_lag{i}'] = df_modelo['Matrículas'].shift(i)
    
    # Eliminar filas con NaN debido a los rezagos
    df_modelo = df_modelo.dropna()
    
    # Preparar variables predictoras y objetivo
    features = [col for col in df_modelo.columns if col not in ['Periodo', 'Leads', 'Matrículas', 'Tasa Conversión (%)']]
    
    # Entrenar modelo para predecir leads
    X = df_modelo[features]
    y_leads = df_modelo['Leads']
    
    # Dividir en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y_leads, test_size=0.2, random_state=42)
    
    # Escalar características
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Entrenar modelo Random Forest
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluar modelo
    y_pred = model.predict(X_test_scaled)
    
    # Calcular métricas
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # Importancia de características
    feature_importance = pd.DataFrame({
        'Feature': features,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    # Crear visualización de importancia de características
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='Importance', y='Feature', data=feature_importance.head(10), palette='viridis')
    ax.set_title('Top 10 Características más Importantes para Predicción de Leads')
    plt.tight_layout()
    
    return {
        'modelo': model,
        'scaler': scaler,
        'features': features,
        'metricas': {
            'MAE': mae,
            'RMSE': rmse,
            'R2': r2
        },
        'importancia_caracteristicas': feature_importance,
        'figura_importancia': fig
    }


def generar_prediccion_futura(modelo_entrenado, df_temporal, periodos_futuros=6, variables_adicionales=None):
    """
    Genera predicciones para periodos futuros.
    
    Args:
        modelo_entrenado (dict): Modelo entrenado por la función entrenar_modelo_prediccion.
        df_temporal (pandas.DataFrame): DataFrame con datos temporales históricos.
        periodos_futuros (int): Número de periodos a predecir.
        variables_adicionales (pandas.DataFrame, optional): Variables externas para periodos futuros.
        
    Returns:
        pandas.DataFrame: DataFrame con predicciones y figura de visualización.
    """
    # Extraer componentes del modelo
    model = modelo_entrenado['modelo']
    scaler = modelo_entrenado['scaler']
    features = modelo_entrenado['features']
    
    # Obtener el último periodo conocido
    ultimo_periodo = df_temporal.index[-1]
    
    # Crear DataFrame para almacenar predicciones
    df_prediccion = pd.DataFrame()
    df_actual = df_temporal.copy().reset_index()
    
    # Generar periodos futuros
    periodos = []
    if isinstance(ultimo_periodo, pd.Timestamp):
        # Para fechas tipo timestamp
        if 'Mes' in str(ultimo_periodo):
            # Mensual
            for i in range(1, periodos_futuros + 1):
                periodos.append(ultimo_periodo + pd.DateOffset(months=i))
        elif ultimo_periodo.day in [1, 16]:
            # Quincenal
            for i in range(1, periodos_futuros + 1):
                if ultimo_periodo.day == 1:
                    # Primera quincena, siguiente es día 16 del mismo mes
                    if i % 2 == 1:
                        periodos.append(ultimo_periodo.replace(day=16))
                    else:
                        periodos.append((ultimo_periodo + pd.DateOffset(months=i//2)).replace(day=1))
                else:
                    # Segunda quincena, siguiente es día 1 del mes siguiente
                    if i % 2 == 1:
                        periodos.append((ultimo_periodo + pd.DateOffset(months=1)).replace(day=1))
                    else:
                        periodos.append((ultimo_periodo + pd.DateOffset(months=i//2)).replace(day=16))
        else:
            # Semanal o diario
            for i in range(1, periodos_futuros + 1):
                periodos.append(ultimo_periodo + pd.DateOffset(days=i*7))
    else:
        # Para índices no timestamp
        for i in range(1, periodos_futuros + 1):
            periodos.append(f"{ultimo_periodo}+{i}")
    
    # Crear DataFrame con periodos futuros
    df_prediccion['Periodo'] = periodos
    
    # Extraer características temporales
    if isinstance(df_prediccion['Periodo'].iloc[0], pd.Timestamp):
        df_prediccion['Año'] = df_prediccion['Periodo'].dt.year
        df_prediccion['Mes'] = df_prediccion['Periodo'].dt.month
        df_prediccion['Día'] = df_prediccion['Periodo'].dt.day
        df_prediccion['DiaSemana'] = df_prediccion['Periodo'].dt.dayofweek
        df_prediccion['Quincena'] = (df_prediccion['Día'] > 15).astype(int) + 1
        
        # Crear variables cíclicas
        df_prediccion['Mes_seno'] = np.sin(2 * np.pi * df_prediccion['Mes'] / 12)
        df_prediccion['Mes_coseno'] = np.cos(2 * np.pi * df_prediccion['Mes'] / 12)
    
    # Incorporar variables adicionales si se proporcionan
    if variables_adicionales is not None:
        df_prediccion = pd.merge(
            df_prediccion,
            variables_adicionales,
            how='left',
            left_on='Periodo',
            right_index=True
        )
    
    # Iterar para crear predicciones incrementales
    leads_pred = []
    matriculas_pred = []
    
    # Valores iniciales para lags (últimos valores conocidos)
    valores_leads = df_actual['Leads'].tail(3).tolist()
    valores_matriculas = df_actual['Matrículas'].tail(3).tolist()
    
    for i in range(periodos_futuros):
        # Crear fila para predecir
        fila_predecir = df_prediccion.iloc[i:i+1].copy()
        
        # Añadir valores de lag
        for j in range(1, 4):
            if j <= len(valores_leads):
                fila_predecir[f'Leads_lag{j}'] = valores_leads[-j]
                fila_predecir[f'Matriculas_lag{j}'] = valores_matriculas[-j]
            else:
                fila_predecir[f'Leads_lag{j}'] = 0
                fila_predecir[f'Matriculas_lag{j}'] = 0
        
        # Asegurar que todas las características requeridas estén presentes
        for feat in features:
            if feat not in fila_predecir.columns:
                fila_predecir[feat] = 0
        
        # Predecir leads
        X_pred = fila_predecir[features]
        X_pred_scaled = scaler.transform(X_pred)
        leads_prediccion = max(0, round(model.predict(X_pred_scaled)[0]))
        
        # Estimar matrículas basado en tasa de conversión histórica
        tasa_conversion_media = df_temporal['Tasa Conversión (%)'].mean() / 100
        matriculas_prediccion = max(0, round(leads_prediccion * tasa_conversion_media))
        
        # Almacenar predicciones
        leads_pred.append(leads_prediccion)
        matriculas_pred.append(matriculas_prediccion)
        
        # Actualizar valores para próxima iteración
        valores_leads.append(leads_prediccion)
        valores_matriculas.append(matriculas_prediccion)
    
    # Añadir predicciones al DataFrame
    df_prediccion['Leads_Pred'] = leads_pred
    df_prediccion['Matrículas_Pred'] = matriculas_pred
    df_prediccion['Tasa Conversión (%)'] = (df_prediccion['Matrículas_Pred'] / df_prediccion['Leads_Pred'] * 100).fillna(0)
    
    # Generar visualización
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # Histórico + Predicción de leads
    ax1.plot(df_actual['Periodo'], df_actual['Leads'], 'o-', color='blue', label='Leads Históricos')
    ax1.plot(df_prediccion['Periodo'], df_prediccion['Leads_Pred'], 'o--', color='red', label='Leads Predicción')
    ax1.set_title('Predicción de Leads')
    ax1.set_ylabel('Número de Leads')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Histórico + Predicción de matrículas
    ax2.plot(df_actual['Periodo'], df_actual['Matrículas'], 'o-', color='green', label='Matrículas Históricas')
    ax2.plot(df_prediccion['Periodo'], df_prediccion['Matrículas_Pred'], 'o--', color='purple', label='Matrículas Predicción')
    ax2.set_title('Predicción de Matrículas')
    ax2.set_ylabel('Número de Matrículas')
    ax2.set_xlabel('Periodo')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Formatear eje X si son fechas
    if isinstance(df_prediccion['Periodo'].iloc[0], pd.Timestamp):
        fig.autofmt_xdate()
    
    plt.tight_layout()
    
    return {
        'predicciones': df_prediccion,
        'figura': fig
    }


def generar_reporte_estacionalidad(datos_historicos, freq='Q', ruta_salida=None):
    """
    Genera un reporte completo de análisis de estacionalidad y predicción.
    
    Args:
        datos_historicos (pandas.DataFrame): DataFrame con datos históricos.
        freq (str): Frecuencia para análisis ('D'=diaria, 'W'=semanal, 
                   'M'=mensual, 'Q'=quincenal, 'SM'=semimensual).
        ruta_salida (str, optional): Ruta donde guardar el reporte.
        
    Returns:
        dict: Diccionario con resultados y rutas de archivos generados.
    """
    # Crear directorio si no existe
    if ruta_salida is None:
        fecha_str = datetime.now().strftime('%Y-%m-%d')
        ruta_salida = f'../salidas/analisis_estacionalidad/{fecha_str}'
    
    os.makedirs(ruta_salida, exist_ok=True)
    
    # Preparar datos temporales
    try:
        df_temporal = preparar_datos_temporales(datos_historicos, freq=freq)
        
        # Guardar datos temporales
        ruta_datos = os.path.join(ruta_salida, 'datos_temporales.csv')
        df_temporal.to_csv(ruta_datos)
        
        resultados = {
            'datos_temporales': df_temporal,
            'archivos': {'datos_temporales': ruta_datos}
        }
        
        # Determinar periodo para análisis estacional
        if freq == 'M':  # Mensual
            periodo_estacional = 12  # 12 meses en un año
        elif freq == 'Q':  # Quincenal
            periodo_estacional = 24  # 24 quincenas en un año
        elif freq == 'W':  # Semanal
            periodo_estacional = 52  # 52 semanas en un año
        elif freq == 'D':  # Diario
            periodo_estacional = 30  # Patrón mensual para datos diarios
        else:
            periodo_estacional = 12  # Valor predeterminado
        
        # Análisis de estacionalidad para leads
        if len(df_temporal) >= periodo_estacional * 2:
            try:
                estacionalidad_leads = analizar_estacionalidad(
                    df_temporal, 
                    metrica='Leads', 
                    periodo=periodo_estacional
                )
                
                # Guardar figura
                ruta_figura_leads = os.path.join(ruta_salida, 'estacionalidad_leads.png')
                estacionalidad_leads['figura'].savefig(ruta_figura_leads, dpi=300, bbox_inches='tight')
                plt.close(estacionalidad_leads['figura'])
                
                # Guardar índices de estacionalidad
                ruta_indices_leads = os.path.join(ruta_salida, 'indices_estacionalidad_leads.csv')
                estacionalidad_leads['indices_estacionalidad'].to_csv(ruta_indices_leads)
                
                resultados['estacionalidad_leads'] = estacionalidad_leads
                resultados['archivos']['estacionalidad_leads'] = ruta_figura_leads
                resultados['archivos']['indices_leads'] = ruta_indices_leads
            except Exception as e:
                print(f"Error en análisis de estacionalidad de leads: {e}")
        
        # Análisis de estacionalidad para matrículas
        if len(df_temporal) >= periodo_estacional * 2:
            try:
                estacionalidad_matriculas = analizar_estacionalidad(
                    df_temporal, 
                    metrica='Matrículas', 
                    periodo=periodo_estacional
                )
                
                # Guardar figura
                ruta_figura_matriculas = os.path.join(ruta_salida, 'estacionalidad_matriculas.png')
                estacionalidad_matriculas['figura'].savefig(ruta_figura_matriculas, dpi=300, bbox_inches='tight')
                plt.close(estacionalidad_matriculas['figura'])
                
                # Guardar índices de estacionalidad
                ruta_indices_matriculas = os.path.join(ruta_salida, 'indices_estacionalidad_matriculas.csv')
                estacionalidad_matriculas['indices_estacionalidad'].to_csv(ruta_indices_matriculas)
                
                resultados['estacionalidad_matriculas'] = estacionalidad_matriculas
                resultados['archivos']['estacionalidad_matriculas'] = ruta_figura_matriculas
                resultados['archivos']['indices_matriculas'] = ruta_indices_matriculas
            except Exception as e:
                print(f"Error en análisis de estacionalidad de matrículas: {e}")
        
        # Entrenar modelo de predicción
        try:
            modelo_prediccion = entrenar_modelo_prediccion(df_temporal)
            
            # Guardar figura de importancia de características
            ruta_importancia = os.path.join(ruta_salida, 'importancia_caracteristicas.png')
            modelo_prediccion['figura_importancia'].savefig(ruta_importancia, dpi=300, bbox_inches='tight')
            plt.close(modelo_prediccion['figura_importancia'])
            
            # Guardar métricas del modelo
            ruta_metricas = os.path.join(ruta_salida, 'metricas_modelo.json')
            with open(ruta_metricas, 'w') as f:
                import json
                json.dump(modelo_prediccion['metricas'], f, indent=4)
            
            resultados['modelo_prediccion'] = modelo_prediccion
            resultados['archivos']['importancia_caracteristicas'] = ruta_importancia
            resultados['archivos']['metricas_modelo'] = ruta_metricas
            
            # Generar predicciones para próximos periodos
            predicciones = generar_prediccion_futura(modelo_prediccion, df_temporal, periodos_futuros=6)
            
            # Guardar predicciones
            ruta_predicciones = os.path.join(ruta_salida, 'predicciones.csv')
            predicciones['predicciones'].to_csv(ruta_predicciones)
            
            # Guardar figura de predicciones
            ruta_figura_predicciones = os.path.join(ruta_salida, 'prediccion_futura.png')
            predicciones['figura'].savefig(ruta_figura_predicciones, dpi=300, bbox_inches='tight')
            plt.close(predicciones['figura'])
            
            resultados['predicciones'] = predicciones
            resultados['archivos']['predicciones'] = ruta_predicciones
            resultados['archivos']['figura_predicciones'] = ruta_figura_predicciones
        except Exception as e:
            print(f"Error en modelo de predicción: {e}")
        
        # Generar resumen HTML
        try:
            ruta_html = os.path.join(ruta_salida, 'reporte_estacionalidad.html')
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Análisis de Estacionalidad y Predicción</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                    h1, h2, h3 {{ color: #333; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; margin-bottom: 20px; }}
                    .section {{ background-color: white; margin-bottom: 30px; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                    .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
                    .image-container {{ margin: 15px 0; text-align: center; }}
                    img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                    th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    tr:hover {{ background-color: #f5f5f5; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Análisis de Estacionalidad y Predicción</h1>
                        <p>Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>
                    
                    <div class="section">
                        <h2>Resumen de Datos Temporales</h2>
                        <p>Frecuencia de análisis: {freq}</p>
                        <p>Periodo de análisis: {df_temporal.index[0]} a {df_temporal.index[-1]}</p>
                        <p>Total de periodos analizados: {len(df_temporal)}</p>
                        
                        <h3>Estadísticas Descriptivas</h3>
                        <table>
                            <tr>
                                <th>Métrica</th>
                                <th>Leads</th>
                                <th>Matrículas</th>
                                <th>Tasa Conversión (%)</th>
                            </tr>
                            <tr>
                                <td>Promedio</td>
                                <td>{df_temporal['Leads'].mean():.1f}</td>
                                <td>{df_temporal['Matrículas'].mean():.1f}</td>
                                <td>{df_temporal['Tasa Conversión (%)'].mean():.1f}%</td>
                            </tr>
                            <tr>
                                <td>Mínimo</td>
                                <td>{df_temporal['Leads'].min():.0f}</td>
                                <td>{df_temporal['Matrículas'].min():.0f}</td>
                                <td>{df_temporal['Tasa Conversión (%)'].min():.1f}%</td>
                            </tr>
                            <tr>
                                <td>Máximo</td>
                                <td>{df_temporal['Leads'].max():.0f}</td>
                                <td>{df_temporal['Matrículas'].max():.0f}</td>
                                <td>{df_temporal['Tasa Conversión (%)'].max():.1f}%</td>
                            </tr>
                        </table>
                    </div>
            """
            
            # Sección de estacionalidad de leads
            if 'estacionalidad_leads' in resultados:
                html_content += """
                    <div class="section">
                        <h2>Análisis de Estacionalidad - Leads</h2>
                        <div class="image-container">
                            <img src="estacionalidad_leads.png" alt="Estacionalidad de Leads">
                        </div>
                        
                        <h3>Interpretación</h3>
                """
                
                # Añadir información sobre periodos de máxima y mínima actividad
                if 'periodos_max' in resultados['estacionalidad_leads']:
                    periodos_max = resultados['estacionalidad_leads']['periodos_max']
                    html_content += "<p><strong>Periodos de mayor actividad:</strong></p><ul>"
                    
                    for idx, row in periodos_max.iterrows():
                        html_content += f"<li>Periodo {idx}: Índice {row['Índice']:.2f}</li>"
                    
                    html_content += "</ul>"
                
                if 'periodos_min' in resultados['estacionalidad_leads']:
                    periodos_min = resultados['estacionalidad_leads']['periodos_min']
                    html_content += "<p><strong>Periodos de menor actividad:</strong></p><ul>"
                    
                    for idx, row in periodos_min.iterrows():
                        html_content += f"<li>Periodo {idx}: Índice {row['Índice']:.2f}</li>"
                    
                    html_content += "</ul>"
                
                html_content += """
                    </div>
                """
            
            # Sección de estacionalidad de matrículas
            if 'estacionalidad_matriculas' in resultados:
                html_content += """
                    <div class="section">
                        <h2>Análisis de Estacionalidad - Matrículas</h2>
                        <div class="image-container">
                            <img src="estacionalidad_matriculas.png" alt="Estacionalidad de Matrículas">
                        </div>
                        
                        <h3>Interpretación</h3>
                """
                
                # Añadir información sobre periodos de máxima y mínima actividad
                if 'periodos_max' in resultados['estacionalidad_matriculas']:
                    periodos_max = resultados['estacionalidad_matriculas']['periodos_max']
                    html_content += "<p><strong>Periodos de mayor actividad:</strong></p><ul>"
                    
                    for idx, row in periodos_max.iterrows():
                        html_content += f"<li>Periodo {idx}: Índice {row['Índice']:.2f}</li>"
                    
                    html_content += "</ul>"
                
                if 'periodos_min' in resultados['estacionalidad_matriculas']:
                    periodos_min = resultados['estacionalidad_matriculas']['periodos_min']
                    html_content += "<p><strong>Periodos de menor actividad:</strong></p><ul>"
                    
                    for idx, row in periodos_min.iterrows():
                        html_content += f"<li>Periodo {idx}: Índice {row['Índice']:.2f}</li>"
                    
                    html_content += "</ul>"
                
                html_content += """
                    </div>
                """
            
            # Sección de modelo predictivo
            if 'modelo_prediccion' in resultados:
                html_content += """
                    <div class="section">
                        <h2>Modelo Predictivo</h2>
                """
                
                # Métricas del modelo
                metricas = resultados['modelo_prediccion']['metricas']
                html_content += """
                        <h3>Métricas de Evaluación</h3>
                        <table>
                            <tr>
                                <th>Métrica</th>
                                <th>Valor</th>
                                <th>Interpretación</th>
                            </tr>
                """
                
                html_content += f"""
                            <tr>
                                <td>MAE (Error Absoluto Medio)</td>
                                <td>{metricas['MAE']:.2f}</td>
                                <td>En promedio, las predicciones se desvían en {metricas['MAE']:.2f} leads de los valores reales.</td>
                            </tr>
                            <tr>
                                <td>RMSE (Raíz del Error Cuadrático Medio)</td>
                                <td>{metricas['RMSE']:.2f}</td>
                                <td>Medida de error que penaliza desviaciones grandes. Un valor de {metricas['RMSE']:.2f} indica la magnitud típica de error.</td>
                            </tr>
                            <tr>
                                <td>R² (Coeficiente de Determinación)</td>
                                <td>{metricas['R2']:.2f}</td>
                                <td>El modelo explica aproximadamente el {metricas['R2']*100:.1f}% de la variabilidad en los datos.</td>
                            </tr>
                """
                
                html_content += """
                        </table>
                        
                        <h3>Importancia de Características</h3>
                        <div class="image-container">
                            <img src="importancia_caracteristicas.png" alt="Importancia de Características">
                        </div>
                """
                
                html_content += """
                    </div>
                """
            
            # Sección de predicciones
            if 'predicciones' in resultados:
                html_content += """
                    <div class="section">
                        <h2>Predicciones Futuras</h2>
                        <div class="image-container">
                            <img src="prediccion_futura.png" alt="Predicciones Futuras">
                        </div>
                        
                        <h3>Valores Predichos</h3>
                        <table>
                            <tr>
                                <th>Periodo</th>
                                <th>Leads</th>
                                <th>Matrículas</th>
                                <th>Tasa Conversión (%)</th>
                            </tr>
                """
                
                for idx, row in resultados['predicciones']['predicciones'].iterrows():
                    periodo = row['Periodo']
                    if isinstance(periodo, pd.Timestamp):
                        periodo = periodo.strftime('%Y-%m-%d')
                    
                    html_content += f"""
                            <tr>
                                <td>{periodo}</td>
                                <td>{int(row['Leads_Pred'])}</td>
                                <td>{int(row['Matrículas_Pred'])}</td>
                                <td>{row['Tasa Conversión (%)']:.1f}%</td>
                            </tr>
                    """
                
                html_content += """
                        </table>
                    </div>
                """
            
            # Cerrar HTML
            html_content += """
                    <div class="footer">
                        <p>Generado por el Sistema Predictor de Matrículas</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            with open(ruta_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            resultados['archivos']['html'] = ruta_html
        except Exception as e:
            print(f"Error al generar reporte HTML: {e}")
        
        return resultados
    
    except Exception as e:
        print(f"Error al generar reporte de estacionalidad: {e}")
        return {'error': str(e)}


if __name__ == "__main__":
    # Ejemplo de uso
    from cargar_datos import cargar_datos_crm
    
    try:
        # Cargar datos históricos
        datos_historicos = cargar_datos_crm("../datos/historico/leads_matriculas_historicos.csv")
        
        # Generar reporte de estacionalidad
        reporte = generar_reporte_estacionalidad(datos_historicos, freq='Q')
        
        print("Reporte de estacionalidad generado correctamente.")
        print(f"Archivos generados en: {os.path.dirname(reporte['archivos']['html'])}")
        
    except Exception as e:
        print(f"Error: {e}") 