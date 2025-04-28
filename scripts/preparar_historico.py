#!/usr/bin/env python3
"""
Script para limpiar y preparar datos históricos para el Motor de Decisión.
Este script prepara archivos CSV históricos para su uso en modelos predictivos.
"""

import pandas as pd
import numpy as np
import os
import sys
import json
import argparse
from datetime import datetime
import re


def definir_parametros():
    """Define los parámetros del script."""
    parser = argparse.ArgumentParser(description='Prepara datos históricos para el Motor de Decisión.')
    parser.add_argument('--ano', type=int, required=True, help='Año de los datos (ej: 2022)')
    parser.add_argument('--trimestre', type=int, choices=[1, 2, 3, 4], help='Trimestre (1-4)')
    parser.add_argument('--tipo', type=str, choices=['leads', 'matriculas', 'planificacion'], 
                        required=True, help='Tipo de datos a procesar')
    parser.add_argument('--ruta-entrada', type=str, help='Ruta al archivo de entrada (opcional)')
    parser.add_argument('--ruta-salida', type=str, help='Ruta para guardar el archivo procesado (opcional)')
    parser.add_argument('--forzar', action='store_true', help='Sobrescribir archivos existentes')
    parser.add_argument('--estandarizar-canales', action='store_true', help='Estandarizar nombres de canales')
    parser.add_argument('--estandarizar-programas', action='store_true', help='Estandarizar nombres de programas')
    
    return parser.parse_args()


def determinar_rutas(args):
    """Determina las rutas de entrada y salida basadas en los argumentos."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Determinar ruta de entrada
    if args.ruta_entrada:
        ruta_entrada = args.ruta_entrada
    else:
        if args.trimestre:
            ruta_entrada = os.path.join(
                base_dir, 'datos', 'historico', args.tipo, 
                str(args.ano), f'{args.tipo}_{args.ano}_Q{args.trimestre}_raw.csv'
            )
        else:
            ruta_entrada = os.path.join(
                base_dir, 'datos', 'historico', args.tipo,
                f'{args.tipo}_{args.ano}_raw.csv'
            )
    
    # Determinar ruta de salida
    if args.ruta_salida:
        ruta_salida = args.ruta_salida
    else:
        if args.trimestre:
            ruta_salida = os.path.join(
                base_dir, 'datos', 'historico', args.tipo, 
                str(args.ano), f'{args.tipo}_{args.ano}_Q{args.trimestre}.csv'
            )
        else:
            ruta_salida = os.path.join(
                base_dir, 'datos', 'historico', args.tipo,
                f'{args.tipo}_{args.ano}.csv'
            )
    
    return ruta_entrada, ruta_salida


def verificar_archivos(ruta_entrada, ruta_salida, forzar=False):
    """Verifica existencia de archivos y directorios."""
    # Verificar que el archivo de entrada existe
    if not os.path.exists(ruta_entrada):
        print(f"Error: Archivo de entrada no encontrado: {ruta_entrada}")
        sys.exit(1)
    
    # Verificar que el directorio de salida existe
    dir_salida = os.path.dirname(ruta_salida)
    if not os.path.exists(dir_salida):
        os.makedirs(dir_salida, exist_ok=True)
        print(f"Creado directorio: {dir_salida}")
    
    # Verificar si el archivo de salida ya existe
    if os.path.exists(ruta_salida) and not forzar:
        print(f"Error: Archivo de salida ya existe: {ruta_salida}")
        print("Use --forzar para sobrescribir.")
        sys.exit(1)


def cargar_datos(ruta_archivo, tipo):
    """Carga datos desde un archivo CSV."""
    try:
        df = pd.read_csv(ruta_archivo)
        print(f"Cargados {len(df)} registros desde {ruta_archivo}")
        return df
    except Exception as e:
        print(f"Error al cargar archivo {ruta_archivo}: {e}")
        sys.exit(1)


def limpiar_leads(df):
    """Limpia y prepara datos de leads."""
    print("Limpiando datos de leads...")
    
    # Verificar columnas requeridas
    columnas_requeridas = ['id_lead', 'fecha_creacion', 'origen', 'programa', 'marca', 'estado']
    for col in columnas_requeridas:
        if col not in df.columns:
            print(f"Advertencia: Columna requerida '{col}' no encontrada.")
    
    # Convertir fechas
    if 'fecha_creacion' in df.columns:
        try:
            df['fecha_creacion'] = pd.to_datetime(df['fecha_creacion'])
            df['fecha_creacion'] = df['fecha_creacion'].dt.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Error al convertir fechas: {e}")
    
    # Estandarizar orígenes (canales)
    if 'origen' in df.columns:
        # Mapeo de canales alternativos a nombres estándar
        mapeo_canales = {
            'FB': 'Facebook',
            'facebook': 'Facebook',
            'face': 'Facebook',
            'ig': 'Instagram',
            'insta': 'Instagram',
            'google ads': 'Google',
            'adwords': 'Google',
            'ln': 'LinkedIn',
            'linkedin': 'LinkedIn',
            'tw': 'Twitter',
            'twitter': 'Twitter',
            'mail': 'Email',
            'correo': 'Email',
            'ref': 'Referido',
            'referral': 'Referido'
        }
        df['origen'] = df['origen'].str.lower().map(lambda x: mapeo_canales.get(x, x)).str.capitalize()
    
    # Eliminar duplicados
    if 'id_lead' in df.columns:
        antes = len(df)
        df = df.drop_duplicates(subset=['id_lead'])
        duplicados = antes - len(df)
        if duplicados > 0:
            print(f"Se eliminaron {duplicados} registros duplicados")
    
    # Tratar valores nulos
    for col in columnas_requeridas:
        if col in df.columns and df[col].isnull().sum() > 0:
            nulos = df[col].isnull().sum()
            if col in ['id_lead', 'fecha_creacion']:
                # Eliminar registros con valores críticos nulos
                df = df.dropna(subset=[col])
                print(f"Se eliminaron {nulos} registros con {col} nulo")
            elif col == 'origen':
                df[col] = df[col].fillna('Desconocido')
                print(f"Se completaron {nulos} valores nulos en {col} con 'Desconocido'")
            else:
                df[col] = df[col].fillna('No especificado')
                print(f"Se completaron {nulos} valores nulos en {col} con 'No especificado'")
    
    return df


def limpiar_matriculas(df):
    """Limpia y prepara datos de matrículas."""
    print("Limpiando datos de matrículas...")
    
    # Verificar columnas requeridas
    columnas_requeridas = ['id_matricula', 'id_lead', 'fecha_matricula', 'programa', 'marca']
    for col in columnas_requeridas:
        if col not in df.columns:
            print(f"Advertencia: Columna requerida '{col}' no encontrada.")
    
    # Convertir fechas
    if 'fecha_matricula' in df.columns:
        try:
            df['fecha_matricula'] = pd.to_datetime(df['fecha_matricula'])
            df['fecha_matricula'] = df['fecha_matricula'].dt.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Error al convertir fechas: {e}")
    
    # Eliminar duplicados
    if 'id_matricula' in df.columns:
        antes = len(df)
        df = df.drop_duplicates(subset=['id_matricula'])
        duplicados = antes - len(df)
        if duplicados > 0:
            print(f"Se eliminaron {duplicados} registros duplicados")
    
    # Tratar valores nulos
    for col in columnas_requeridas:
        if col in df.columns and df[col].isnull().sum() > 0:
            nulos = df[col].isnull().sum()
            if col in ['id_matricula', 'id_lead', 'fecha_matricula']:
                # Eliminar registros con valores críticos nulos
                df = df.dropna(subset=[col])
                print(f"Se eliminaron {nulos} registros con {col} nulo")
            else:
                df[col] = df[col].fillna('No especificado')
                print(f"Se completaron {nulos} valores nulos en {col} con 'No especificado'")
    
    return df


def limpiar_planificacion(df):
    """Limpia y prepara datos de planificación."""
    print("Limpiando datos de planificación...")
    
    # Verificar columnas requeridas
    columnas_requeridas = ['Fecha', 'ID_Campaña', 'Marca', 'Presupuesto_Total', 
                           'Objetivo_Matriculas_Total', 'Fecha_Inicio', 'Fecha_Fin']
    for col in columnas_requeridas:
        if col not in df.columns:
            print(f"Advertencia: Columna requerida '{col}' no encontrada.")
    
    # Convertir fechas
    for col in ['Fecha', 'Fecha_Inicio', 'Fecha_Fin']:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col])
                df[col] = df[col].dt.strftime('%Y-%m-%d')
            except Exception as e:
                print(f"Error al convertir fechas en columna {col}: {e}")
    
    # Convertir campos numéricos
    if 'Presupuesto_Total' in df.columns:
        try:
            df['Presupuesto_Total'] = pd.to_numeric(df['Presupuesto_Total'])
        except Exception as e:
            print(f"Error al convertir Presupuesto_Total a numérico: {e}")
    
    if 'Objetivo_Matriculas_Total' in df.columns:
        try:
            df['Objetivo_Matriculas_Total'] = pd.to_numeric(df['Objetivo_Matriculas_Total'])
            df['Objetivo_Matriculas_Total'] = df['Objetivo_Matriculas_Total'].round().astype(int)
        except Exception as e:
            print(f"Error al convertir Objetivo_Matriculas_Total a entero: {e}")
    
    # Asegurar formato correcto en campos de lista
    if 'Canales_Activos' in df.columns:
        # Asegurar que los canales están separados por pipe (|)
        df['Canales_Activos'] = df['Canales_Activos'].apply(
            lambda x: '|'.join([c.strip() for c in re.split(r'[|,;]', str(x))])
        )
    
    if 'Programas_Incluidos' in df.columns:
        # Asegurar que los programas están separados por pipe (|)
        df['Programas_Incluidos'] = df['Programas_Incluidos'].apply(
            lambda x: '|'.join([p.strip() for p in re.split(r'[|,;]', str(x))])
        )
    
    return df


def generar_metadatos(df, tipo, ruta_salida):
    """Genera un archivo de metadatos con información del dataset procesado."""
    metadatos = {
        'tipo_datos': tipo,
        'fecha_procesamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'registros_totales': len(df),
        'columnas': list(df.columns),
        'periodo': {
            'inicio': None,
            'fin': None
        },
        'estadisticas': {}
    }
    
    # Determinar período cubierto
    if tipo == 'leads' and 'fecha_creacion' in df.columns:
        metadatos['periodo']['inicio'] = str(df['fecha_creacion'].min())
        metadatos['periodo']['fin'] = str(df['fecha_creacion'].max())
    elif tipo == 'matriculas' and 'fecha_matricula' in df.columns:
        metadatos['periodo']['inicio'] = str(df['fecha_matricula'].min())
        metadatos['periodo']['fin'] = str(df['fecha_matricula'].max())
    elif tipo == 'planificacion' and 'Fecha_Inicio' in df.columns:
        metadatos['periodo']['inicio'] = str(df['Fecha_Inicio'].min())
        metadatos['periodo']['fin'] = str(df['Fecha_Fin'].max())
    
    # Generar estadísticas básicas para algunas columnas clave
    if tipo == 'leads':
        # Distribución por origen
        if 'origen' in df.columns:
            metadatos['estadisticas']['distribucion_origen'] = df['origen'].value_counts().to_dict()
        
        # Distribución por marca
        if 'marca' in df.columns:
            metadatos['estadisticas']['distribucion_marca'] = df['marca'].value_counts().to_dict()
        
        # Distribución por estado
        if 'estado' in df.columns:
            metadatos['estadisticas']['distribucion_estado'] = df['estado'].value_counts().to_dict()
    
    elif tipo == 'matriculas':
        # Distribución por marca
        if 'marca' in df.columns:
            metadatos['estadisticas']['distribucion_marca'] = df['marca'].value_counts().to_dict()
        
        # Distribución por programa
        if 'programa' in df.columns:
            metadatos['estadisticas']['distribucion_programa'] = df['programa'].value_counts().to_dict()
    
    elif tipo == 'planificacion':
        # Presupuesto total
        if 'Presupuesto_Total' in df.columns:
            metadatos['estadisticas']['presupuesto_total'] = float(df['Presupuesto_Total'].sum())
            metadatos['estadisticas']['presupuesto_promedio'] = float(df['Presupuesto_Total'].mean())
        
        # Objetivos totales
        if 'Objetivo_Matriculas_Total' in df.columns:
            metadatos['estadisticas']['objetivo_matriculas_total'] = int(df['Objetivo_Matriculas_Total'].sum())
    
    # Guardar metadatos
    ruta_metadatos = ruta_salida.replace('.csv', '_metadatos.json')
    with open(ruta_metadatos, 'w', encoding='utf-8') as f:
        json.dump(metadatos, f, indent=2, ensure_ascii=False)
    
    print(f"Metadatos generados en: {ruta_metadatos}")
    return metadatos


def main():
    """Función principal del script."""
    args = definir_parametros()
    
    # Determinar rutas
    ruta_entrada, ruta_salida = determinar_rutas(args)
    
    # Verificar archivos
    verificar_archivos(ruta_entrada, ruta_salida, args.forzar)
    
    # Cargar datos
    df = cargar_datos(ruta_entrada, args.tipo)
    
    # Limpiar datos según el tipo
    if args.tipo == 'leads':
        df_procesado = limpiar_leads(df)
    elif args.tipo == 'matriculas':
        df_procesado = limpiar_matriculas(df)
    elif args.tipo == 'planificacion':
        df_procesado = limpiar_planificacion(df)
    
    # Generar metadatos
    generar_metadatos(df_procesado, args.tipo, ruta_salida)
    
    # Guardar datos procesados
    df_procesado.to_csv(ruta_salida, index=False)
    print(f"Datos procesados guardados en: {ruta_salida}")
    print(f"Total de registros procesados: {len(df_procesado)}")


if __name__ == "__main__":
    main() 