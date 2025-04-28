"""
Módulo para visualización de datos y resultados de análisis.
Proporciona funciones para generar gráficos y visualizaciones para reportes.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional
import logging
from datetime import datetime

from src.utils.config import get_config
from src.utils.logging import get_module_logger

logger = get_module_logger(__name__)

# Configurar estilo de matplotlib
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

class Visualizador:
    """
    Clase para generar visualizaciones y gráficos de datos.
    """
    
    def __init__(self):
        """
        Inicializa el visualizador.
        """
        self.config = get_config()
        
        # Configurar directorio para guardar gráficos
        output_dir = Path(self.config['paths']['output'])
        self.graficos_dir = output_dir / 'graficos'
        self.graficos_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar paleta de colores predeterminada
        self.paleta_colores = sns.color_palette("viridis", 10)
    
    def graficar_serie_temporal(self,
                               datos: pd.DataFrame,
                               columna_fecha: str,
                               columna_valor: str,
                               titulo: str = None,
                               etiqueta_x: str = None,
                               etiqueta_y: str = None,
                               color: str = 'blue',
                               guardar: bool = True,
                               nombre_archivo: str = None) -> plt.Figure:
        """
        Genera un gráfico de serie temporal.
        
        Args:
            datos (pd.DataFrame): DataFrame con los datos
            columna_fecha (str): Nombre de la columna con fechas
            columna_valor (str): Nombre de la columna con valores
            titulo (str): Título del gráfico
            etiqueta_x (str): Etiqueta para el eje X
            etiqueta_y (str): Etiqueta para el eje Y
            color (str): Color para la línea
            guardar (bool): Si se debe guardar el gráfico en disco
            nombre_archivo (str): Nombre de archivo para guardar
            
        Returns:
            plt.Figure: Figura generada
        """
        # Verificar columnas
        if columna_fecha not in datos.columns:
            mensaje = f"La columna de fecha '{columna_fecha}' no existe en los datos"
            logger.error(mensaje)
            raise ValueError(mensaje)
            
        if columna_valor not in datos.columns:
            mensaje = f"La columna de valor '{columna_valor}' no existe en los datos"
            logger.error(mensaje)
            raise ValueError(mensaje)
        
        # Asegurar que la columna de fecha sea de tipo datetime
        datos_temp = datos.copy()
        if not pd.api.types.is_datetime64_any_dtype(datos_temp[columna_fecha]):
            datos_temp[columna_fecha] = pd.to_datetime(datos_temp[columna_fecha], errors='coerce')
            logger.info(f"Columna '{columna_fecha}' convertida a tipo datetime")
        
        # Ordenar datos por fecha
        datos_temp = datos_temp.sort_values(by=columna_fecha)
        
        # Crear gráfico
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Graficar línea principal
        ax.plot(datos_temp[columna_fecha], datos_temp[columna_valor], 
               color=color, linewidth=2, marker='o', markersize=4, alpha=0.7)
        
        # Añadir línea de tendencia
        try:
            z = np.polyfit(np.arange(len(datos_temp)), datos_temp[columna_valor], 1)
            p = np.poly1d(z)
            ax.plot(datos_temp[columna_fecha], p(np.arange(len(datos_temp))), 
                   'r--', linewidth=1, alpha=0.8, label='Tendencia')
            logger.debug("Línea de tendencia añadida al gráfico")
        except Exception as e:
            logger.warning(f"No se pudo añadir línea de tendencia: {str(e)}")
        
        # Configurar etiquetas
        if titulo is None:
            titulo = f"Evolución temporal de {columna_valor}"
        ax.set_title(titulo)
        
        if etiqueta_x is None:
            etiqueta_x = columna_fecha
        ax.set_xlabel(etiqueta_x)
        
        if etiqueta_y is None:
            etiqueta_y = columna_valor
        ax.set_ylabel(etiqueta_y)
        
        # Formatear eje X
        plt.xticks(rotation=45)
        fig.tight_layout()
        
        # Añadir grid
        ax.grid(True, alpha=0.3)
        
        # Añadir leyenda si hay
        if len(ax.get_legend_handles_labels()[0]) > 0:
            ax.legend()
        
        # Guardar gráfico si se solicita
        if guardar:
            if nombre_archivo is None:
                fecha_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_archivo = f"serie_temporal_{columna_valor}_{fecha_hora}.png"
            
            ruta_archivo = self.graficos_dir / nombre_archivo
            plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico guardado en {ruta_archivo}")
        
        return fig
    
    def graficar_distribucion(self,
                             datos: pd.DataFrame,
                             columna: str,
                             titulo: str = None,
                             color: str = 'blue',
                             kde: bool = True,
                             guardar: bool = True,
                             nombre_archivo: str = None) -> plt.Figure:
        """
        Genera un histograma para visualizar la distribución de una variable.
        
        Args:
            datos (pd.DataFrame): DataFrame con los datos
            columna (str): Nombre de la columna a visualizar
            titulo (str): Título del gráfico
            color (str): Color para el histograma
            kde (bool): Si se debe incluir la estimación de densidad kernel
            guardar (bool): Si se debe guardar el gráfico en disco
            nombre_archivo (str): Nombre de archivo para guardar
            
        Returns:
            plt.Figure: Figura generada
        """
        # Verificar columna
        if columna not in datos.columns:
            mensaje = f"La columna '{columna}' no existe en los datos"
            logger.error(mensaje)
            raise ValueError(mensaje)
        
        # Crear gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generar histograma con seaborn
        sns.histplot(data=datos, x=columna, kde=kde, color=color, ax=ax)
        
        # Configurar etiquetas
        if titulo is None:
            titulo = f"Distribución de {columna}"
        ax.set_title(titulo)
        
        ax.set_xlabel(columna)
        ax.set_ylabel('Frecuencia')
        
        # Añadir estadísticas
        media = datos[columna].mean()
        mediana = datos[columna].median()
        
        ax.axvline(media, color='r', linestyle='--', linewidth=1.5, 
                  label=f'Media: {media:.2f}')
        ax.axvline(mediana, color='g', linestyle='-.', linewidth=1.5, 
                  label=f'Mediana: {mediana:.2f}')
        
        ax.legend()
        
        # Guardar gráfico si se solicita
        if guardar:
            if nombre_archivo is None:
                fecha_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_archivo = f"distribucion_{columna}_{fecha_hora}.png"
            
            ruta_archivo = self.graficos_dir / nombre_archivo
            plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico guardado en {ruta_archivo}")
        
        return fig
    
    def graficar_barras(self,
                       datos: pd.DataFrame,
                       columna_categoria: str,
                       columna_valor: str = None,
                       titulo: str = None,
                       limite_categorias: int = 10,
                       orientacion: str = 'vertical',
                       ordenar: bool = True,
                       ascendente: bool = False,
                       guardar: bool = True,
                       nombre_archivo: str = None) -> plt.Figure:
        """
        Genera un gráfico de barras para visualizar valores por categoría.
        
        Args:
            datos (pd.DataFrame): DataFrame con los datos
            columna_categoria (str): Nombre de la columna con categorías
            columna_valor (str): Nombre de la columna con valores (si None, cuenta frecuencias)
            titulo (str): Título del gráfico
            limite_categorias (int): Número máximo de categorías a mostrar
            orientacion (str): 'vertical' u 'horizontal'
            ordenar (bool): Si se deben ordenar las barras por valor
            ascendente (bool): Si el orden debe ser ascendente
            guardar (bool): Si se debe guardar el gráfico en disco
            nombre_archivo (str): Nombre de archivo para guardar
            
        Returns:
            plt.Figure: Figura generada
        """
        # Verificar columnas
        if columna_categoria not in datos.columns:
            mensaje = f"La columna de categoría '{columna_categoria}' no existe en los datos"
            logger.error(mensaje)
            raise ValueError(mensaje)
            
        if columna_valor is not None and columna_valor not in datos.columns:
            mensaje = f"La columna de valor '{columna_valor}' no existe en los datos"
            logger.error(mensaje)
            raise ValueError(mensaje)
        
        # Preparar datos
        if columna_valor is None:
            # Contar frecuencias
            df_plot = datos[columna_categoria].value_counts().reset_index()
            df_plot.columns = [columna_categoria, 'frecuencia']
            columna_valor = 'frecuencia'
        else:
            # Agregar por categoría
            df_plot = datos.groupby(columna_categoria)[columna_valor].sum().reset_index()
        
        # Ordenar si se solicita
        if ordenar:
            df_plot = df_plot.sort_values(by=columna_valor, ascending=ascendente)
        
        # Limitar el número de categorías
        if len(df_plot) > limite_categorias:
            if ordenar and not ascendente:
                df_plot = df_plot.head(limite_categorias)
            elif ordenar and ascendente:
                df_plot = df_plot.tail(limite_categorias)
            else:
                df_plot = df_plot.head(limite_categorias)
                
            logger.info(f"Mostrando solo las primeras {limite_categorias} categorías")
        
        # Crear figura
        if orientacion == 'horizontal':
            figsize = (10, max(6, len(df_plot) * 0.4))
        else:
            figsize = (max(8, len(df_plot) * 0.6), 6)
            
        fig, ax = plt.subplots(figsize=figsize)
        
        # Crear paleta de colores
        colores = self.paleta_colores[:len(df_plot)]
        
        # Graficar barras
        if orientacion == 'horizontal':
            barras = ax.barh(df_plot[columna_categoria], df_plot[columna_valor], color=colores)
            
            # Añadir valores al final de las barras
            for i, barra in enumerate(barras):
                ancho = barra.get_width()
                ax.text(ancho + ancho*0.01, barra.get_y() + barra.get_height()/2, 
                       f'{ancho:,.0f}', va='center')
                
            ax.set_xlabel(columna_valor)
            ax.set_ylabel(columna_categoria)
            
        else:  # vertical
            barras = ax.bar(df_plot[columna_categoria], df_plot[columna_valor], color=colores)
            
            # Añadir valores encima de las barras
            for i, barra in enumerate(barras):
                altura = barra.get_height()
                ax.text(barra.get_x() + barra.get_width()/2, altura + altura*0.01, 
                       f'{altura:,.0f}', ha='center')
                
            ax.set_xlabel(columna_categoria)
            ax.set_ylabel(columna_valor)
            plt.xticks(rotation=45, ha='right')
        
        # Configurar título
        if titulo is None:
            if columna_valor == 'frecuencia':
                titulo = f"Frecuencia por {columna_categoria}"
            else:
                titulo = f"{columna_valor} por {columna_categoria}"
                
        ax.set_title(titulo)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar gráfico si se solicita
        if guardar:
            if nombre_archivo is None:
                fecha_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_archivo = f"barras_{columna_categoria}_{fecha_hora}.png"
            
            ruta_archivo = self.graficos_dir / nombre_archivo
            plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico guardado en {ruta_archivo}")
        
        return fig
    
    def graficar_dispersion(self,
                           datos: pd.DataFrame,
                           columna_x: str,
                           columna_y: str,
                           columna_color: str = None,
                           columna_tamaño: str = None,
                           titulo: str = None,
                           mostrar_regresion: bool = True,
                           guardar: bool = True,
                           nombre_archivo: str = None) -> plt.Figure:
        """
        Genera un gráfico de dispersión entre dos variables.
        
        Args:
            datos (pd.DataFrame): DataFrame con los datos
            columna_x (str): Nombre de la columna para el eje X
            columna_y (str): Nombre de la columna para el eje Y
            columna_color (str): Nombre de la columna para el color de los puntos
            columna_tamaño (str): Nombre de la columna para el tamaño de los puntos
            titulo (str): Título del gráfico
            mostrar_regresion (bool): Si se debe mostrar la línea de regresión
            guardar (bool): Si se debe guardar el gráfico en disco
            nombre_archivo (str): Nombre de archivo para guardar
            
        Returns:
            plt.Figure: Figura generada
        """
        # Verificar columnas
        for col, desc in [(columna_x, 'X'), (columna_y, 'Y')]:
            if col not in datos.columns:
                mensaje = f"La columna para el eje {desc} '{col}' no existe en los datos"
                logger.error(mensaje)
                raise ValueError(mensaje)
        
        if columna_color is not None and columna_color not in datos.columns:
            mensaje = f"La columna para color '{columna_color}' no existe en los datos"
            logger.warning(mensaje)
            columna_color = None
            
        if columna_tamaño is not None and columna_tamaño not in datos.columns:
            mensaje = f"La columna para tamaño '{columna_tamaño}' no existe en los datos"
            logger.warning(mensaje)
            columna_tamaño = None
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Opciones para el gráfico
        scatter_kwargs = {'alpha': 0.7}
        
        if columna_tamaño is not None:
            # Normalizar tamaños
            tamaño_min, tamaño_max = 20, 200
            tamaños = datos[columna_tamaño]
            tamaños_norm = ((tamaños - tamaños.min()) / 
                           (tamaños.max() - tamaños.min())) * (tamaño_max - tamaño_min) + tamaño_min
            scatter_kwargs['s'] = tamaños_norm
        
        # Crear scatter plot
        if columna_color is not None:
            scatter = ax.scatter(datos[columna_x], datos[columna_y], 
                                c=datos[columna_color], cmap='viridis', **scatter_kwargs)
            
            # Añadir barra de color
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label(columna_color)
        else:
            ax.scatter(datos[columna_x], datos[columna_y], **scatter_kwargs)
        
        # Añadir línea de regresión si se solicita
        if mostrar_regresion:
            sns.regplot(x=columna_x, y=columna_y, data=datos, scatter=False, 
                       ax=ax, line_kws={'color': 'red', 'linestyle': '--'})
            
            # Calcular y mostrar correlación
            corr = datos[columna_x].corr(datos[columna_y])
            ax.annotate(f'Correlación: {corr:.2f}', xy=(0.05, 0.95), xycoords='axes fraction', 
                       fontsize=10, backgroundcolor='white', ha='left', va='top')
        
        # Configurar etiquetas
        ax.set_xlabel(columna_x)
        ax.set_ylabel(columna_y)
        
        if titulo is None:
            titulo = f"Relación entre {columna_y} y {columna_x}"
        ax.set_title(titulo)
        
        # Añadir grid
        ax.grid(True, alpha=0.3)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar gráfico si se solicita
        if guardar:
            if nombre_archivo is None:
                fecha_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_archivo = f"dispersion_{columna_x}_vs_{columna_y}_{fecha_hora}.png"
            
            ruta_archivo = self.graficos_dir / nombre_archivo
            plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico guardado en {ruta_archivo}")
        
        return fig
    
    def graficar_matriz_correlacion(self,
                                  datos: pd.DataFrame,
                                  columnas: List[str] = None,
                                  titulo: str = None,
                                  metodo: str = 'pearson',
                                  mostrar_valores: bool = True,
                                  guardar: bool = True,
                                  nombre_archivo: str = None) -> plt.Figure:
        """
        Genera una matriz de correlación entre variables numéricas.
        
        Args:
            datos (pd.DataFrame): DataFrame con los datos
            columnas (List[str]): Lista de columnas a incluir (None para todas numéricas)
            titulo (str): Título del gráfico
            metodo (str): Método de correlación ('pearson', 'kendall', 'spearman')
            mostrar_valores (bool): Si se deben mostrar los valores de correlación
            guardar (bool): Si se debe guardar el gráfico en disco
            nombre_archivo (str): Nombre de archivo para guardar
            
        Returns:
            plt.Figure: Figura generada
        """
        # Si no se especifican columnas, usar todas las numéricas
        if columnas is None:
            columnas = datos.select_dtypes(include=['number']).columns.tolist()
        else:
            # Verificar que las columnas existen y son numéricas
            for col in columnas:
                if col not in datos.columns:
                    mensaje = f"La columna '{col}' no existe en los datos"
                    logger.error(mensaje)
                    raise ValueError(mensaje)
                
                if not pd.api.types.is_numeric_dtype(datos[col]):
                    mensaje = f"La columna '{col}' no es numérica"
                    logger.warning(mensaje)
        
        # Calcular matriz de correlación
        corr_matrix = datos[columnas].corr(method=metodo)
        
        # Crear figura con tamaño proporcional a la cantidad de variables
        n_vars = len(columnas)
        figsize = (max(8, n_vars * 0.7), max(6, n_vars * 0.7))
        fig, ax = plt.subplots(figsize=figsize)
        
        # Crear heatmap
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))  # Máscara para triángulo superior
        cmap = sns.diverging_palette(230, 20, as_cmap=True)
        
        sns.heatmap(corr_matrix, mask=mask, cmap=cmap, vmax=1, vmin=-1, center=0,
                   annot=mostrar_valores, fmt='.2f', square=True, linewidths=.5, 
                   cbar_kws={"shrink": .5}, ax=ax)
        
        # Configurar título
        if titulo is None:
            titulo = f"Matriz de Correlación ({metodo.capitalize()})"
        ax.set_title(titulo)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar gráfico si se solicita
        if guardar:
            if nombre_archivo is None:
                fecha_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_archivo = f"matriz_correlacion_{fecha_hora}.png"
            
            ruta_archivo = self.graficos_dir / nombre_archivo
            plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico guardado en {ruta_archivo}")
        
        return fig
    
    def graficar_multilinea(self,
                          datos: pd.DataFrame,
                          columna_x: str,
                          columnas_y: List[str],
                          titulo: str = None,
                          etiqueta_x: str = None,
                          etiqueta_y: str = None,
                          mostrar_leyenda: bool = True,
                          guardar: bool = True,
                          nombre_archivo: str = None) -> plt.Figure:
        """
        Genera un gráfico con múltiples líneas para comparar varias series temporales.
        
        Args:
            datos (pd.DataFrame): DataFrame con los datos
            columna_x (str): Nombre de la columna para el eje X
            columnas_y (List[str]): Lista de columnas a graficar en el eje Y
            titulo (str): Título del gráfico
            etiqueta_x (str): Etiqueta para el eje X
            etiqueta_y (str): Etiqueta para el eje Y
            mostrar_leyenda (bool): Si se debe mostrar la leyenda
            guardar (bool): Si se debe guardar el gráfico en disco
            nombre_archivo (str): Nombre de archivo para guardar
            
        Returns:
            plt.Figure: Figura generada
        """
        # Verificar columnas
        if columna_x not in datos.columns:
            mensaje = f"La columna para el eje X '{columna_x}' no existe en los datos"
            logger.error(mensaje)
            raise ValueError(mensaje)
            
        # Verificar columnas Y
        columnas_y_validas = []
        for col in columnas_y:
            if col not in datos.columns:
                mensaje = f"La columna '{col}' no existe en los datos"
                logger.warning(mensaje)
            else:
                columnas_y_validas.append(col)
        
        if not columnas_y_validas:
            mensaje = "No hay columnas válidas para graficar"
            logger.error(mensaje)
            raise ValueError(mensaje)
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Preparar datos
        datos_ordenados = datos.sort_values(by=columna_x)
        
        # Graficar cada línea
        for i, col in enumerate(columnas_y_validas):
            color = self.paleta_colores[i % len(self.paleta_colores)]
            ax.plot(datos_ordenados[columna_x], datos_ordenados[col], 
                   label=col, color=color, linewidth=2, marker='o', markersize=4, alpha=0.7)
        
        # Configurar etiquetas
        if titulo is None:
            titulo = f"Comparación de series"
        ax.set_title(titulo)
        
        if etiqueta_x is None:
            etiqueta_x = columna_x
        ax.set_xlabel(etiqueta_x)
        
        if etiqueta_y is None:
            etiqueta_y = "Valores"
        ax.set_ylabel(etiqueta_y)
        
        # Mostrar leyenda si se solicita
        if mostrar_leyenda:
            ax.legend(loc='best')
        
        # Formatear eje X si es fecha
        if pd.api.types.is_datetime64_any_dtype(datos[columna_x]):
            plt.xticks(rotation=45)
            
        # Añadir grid
        ax.grid(True, alpha=0.3)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Guardar gráfico si se solicita
        if guardar:
            if nombre_archivo is None:
                fecha_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_archivo = f"multilinea_{fecha_hora}.png"
            
            ruta_archivo = self.graficos_dir / nombre_archivo
            plt.savefig(ruta_archivo, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico guardado en {ruta_archivo}")
        
        return fig 