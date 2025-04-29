#!/usr/bin/env python3
"""
Script para ejecutar todas las pruebas unitarias del proyecto Motor de Decisión.
Utiliza pytest y genera reportes de cobertura.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_tests(args):
    """
    Ejecuta las pruebas unitarias con pytest.
    
    Args:
        args: Argumentos de línea de comandos parseados
    
    Returns:
        int: Código de salida de pytest
    """
    # Construir comando base
    cmd = ["pytest"]
    
    # Añadir paths de pruebas
    if args.module:
        cmd.append(f"tests/{args.module}")
    else:
        cmd.append("tests/")
    
    # Añadir opciones
    if args.verbose:
        cmd.append("-v")
    
    if args.quiet:
        cmd.append("-q")
    
    # Generar reporte de cobertura si se solicita
    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=term", "--cov-report=html:coverage_report"])
    
    # Capturar solo últimas líneas de salida si se solicita
    if args.last_failures:
        cmd.append("--last-failed")
    
    # Depuración
    if args.debug:
        print(f"Comando a ejecutar: {' '.join(cmd)}")
    
    # Ejecutar comando
    return subprocess.call(cmd)

def setup_environment():
    """
    Configura el entorno para las pruebas.
    """
    # Asegurar que el directorio raíz está en el path
    root_dir = str(Path(__file__).resolve().parent)
    sys.path.insert(0, root_dir)
    
    # Configurar variable de entorno para pruebas
    os.environ["MOTOR_DECISION_ENV"] = "test"
    
    # Crear directorio para reportes de cobertura si no existe
    Path("coverage_report").mkdir(exist_ok=True)

def parse_args():
    """
    Parsea los argumentos de línea de comandos.
    
    Returns:
        argparse.Namespace: Argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description="Ejecuta pruebas unitarias para el Motor de Decisión"
    )
    
    parser.add_argument(
        "-m", "--module",
        help="Módulo específico a probar (data, models, etc.)",
        default=None
    )
    
    parser.add_argument(
        "-v", "--verbose",
        help="Mostrar detalles completos de las pruebas",
        action="store_true"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        help="Mostrar información mínima de las pruebas",
        action="store_true"
    )
    
    parser.add_argument(
        "-c", "--coverage",
        help="Generar reporte de cobertura de código",
        action="store_true"
    )
    
    parser.add_argument(
        "-l", "--last-failures",
        help="Ejecutar solo pruebas que fallaron la última vez",
        action="store_true"
    )
    
    parser.add_argument(
        "-d", "--debug",
        help="Mostrar información de depuración",
        action="store_true"
    )
    
    return parser.parse_args()

def main():
    """
    Función principal del script.
    """
    # Configurar entorno
    setup_environment()
    
    # Parsear argumentos
    args = parse_args()
    
    # Imprimir mensaje de inicio
    print("=" * 80)
    print(f" Ejecutando pruebas unitarias para el Motor de Decisión ")
    print("=" * 80)
    
    if args.module:
        print(f"Módulo: {args.module}")
    
    # Ejecutar pruebas
    return run_tests(args)

if __name__ == "__main__":
    # Ejecutar y obtener código de salida
    exit_code = main()
    
    # Salir con el código correspondiente
    sys.exit(exit_code) 