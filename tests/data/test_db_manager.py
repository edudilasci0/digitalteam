"""
Tests para el gestor de base de datos SQLite.
"""

import os
import sys
import tempfile
import unittest
import pandas as pd
import sqlite3
from pathlib import Path

# Asegurar que el directorio raíz está en el path para importar src.data.db_manager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.db_manager import DBManager

class TestDBManager(unittest.TestCase):
    """Pruebas para el gestor de base de datos SQLite."""
    
    def setUp(self):
        """Configuración para cada test."""
        # Crear archivo temporal para la base de datos de prueba
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_manager = DBManager(self.db_path)
        
        # Datos de prueba para leads
        self.test_leads = pd.DataFrame({
            'id': ['lead1', 'lead2', 'lead3'],
            'fecha_creacion': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'programa': ['MBA', 'Marketing', 'Finanzas'],
            'origen': ['Facebook', 'Google', 'LinkedIn'],
            'marca': ['Marca1', 'Marca2', 'Marca1'],
            'costo': [100.0, 200.0, 150.0],
            'utm_source': ['fb', 'google', 'linkedin'],
            'utm_medium': ['cpc', 'cpc', 'social'],
            'utm_campaign': ['camp1', 'camp2', 'camp3']
        })
        
        # Datos de prueba para matrículas
        self.test_matriculas = pd.DataFrame({
            'id': ['mat1', 'mat2'],
            'id_lead': ['lead1', 'lead3'],
            'fecha_matricula': ['2023-01-15', '2023-01-20'],
            'programa': ['MBA', 'Finanzas'],
            'valor_matricula': [1500.0, 2000.0],
            'modalidad': ['Online', 'Presencial'],
            'sede': ['Sede1', 'Sede2']
        })
    
    def tearDown(self):
        """Limpieza después de cada test."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_crear_tablas(self):
        """Prueba que las tablas se creen correctamente."""
        # Conectar directamente a la base de datos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar si existen las tablas esperadas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        nombres_tablas = [tabla[0] for tabla in tablas]
        
        # Verificar que existan las tablas principales
        self.assertIn('leads', nombres_tablas)
        self.assertIn('matriculas', nombres_tablas)
        self.assertIn('historial_cargas', nombres_tablas)
        self.assertIn('configuracion', nombres_tablas)
        
        conn.close()
    
    def test_guardar_leads(self):
        """Prueba la inserción de leads en la base de datos."""
        # Guardar leads
        registros_insertados = self.db_manager.guardar_leads(self.test_leads)
        
        # Verificar que se insertaron todos los registros
        self.assertEqual(registros_insertados, len(self.test_leads))
        
        # Verificar que los datos se pueden recuperar
        leads_recuperados = self.db_manager.obtener_leads()
        
        # Verificar el número de registros
        self.assertEqual(len(leads_recuperados), len(self.test_leads))
        
        # Verificar que los IDs coinciden
        ids_recuperados = set(leads_recuperados['id'])
        ids_originales = set(self.test_leads['id'])
        self.assertEqual(ids_recuperados, ids_originales)
    
    def test_guardar_matriculas(self):
        """Prueba la inserción de matrículas en la base de datos."""
        # Primero guardar leads para mantener integridad referencial
        self.db_manager.guardar_leads(self.test_leads)
        
        # Guardar matrículas
        registros_insertados = self.db_manager.guardar_matriculas(self.test_matriculas)
        
        # Verificar que se insertaron todos los registros
        self.assertEqual(registros_insertados, len(self.test_matriculas))
        
        # Verificar que los datos se pueden recuperar
        matriculas_recuperadas = self.db_manager.obtener_matriculas()
        
        # Verificar el número de registros
        self.assertEqual(len(matriculas_recuperadas), len(self.test_matriculas))
        
        # Verificar que los IDs coinciden
        ids_recuperados = set(matriculas_recuperadas['id'])
        ids_originales = set(self.test_matriculas['id'])
        self.assertEqual(ids_recuperados, ids_originales)
    
    def test_obtener_leads_con_filtro(self):
        """Prueba la obtención de leads con filtros."""
        # Guardar leads
        self.db_manager.guardar_leads(self.test_leads)
        
        # Filtrar por origen
        filtro = {'origen': 'Facebook'}
        leads_filtrados = self.db_manager.obtener_leads(filtro)
        
        # Verificar que solo se obtienen los leads de Facebook
        self.assertEqual(len(leads_filtrados), 1)
        self.assertEqual(leads_filtrados.iloc[0]['origen'], 'Facebook')
        
        # Filtrar por marca
        filtro = {'marca': 'Marca1'}
        leads_filtrados = self.db_manager.obtener_leads(filtro)
        
        # Verificar que solo se obtienen los leads de Marca1
        self.assertEqual(len(leads_filtrados), 2)
        self.assertTrue(all(lead == 'Marca1' for lead in leads_filtrados['marca']))
    
    def test_obtener_leads_con_matriculas(self):
        """Prueba la obtención de leads con sus matrículas correspondientes."""
        # Guardar leads y matrículas
        self.db_manager.guardar_leads(self.test_leads)
        self.db_manager.guardar_matriculas(self.test_matriculas)
        
        # Obtener leads con matrículas
        leads_con_matriculas = self.db_manager.obtener_leads_con_matriculas()
        
        # Verificar que se obtienen todos los leads
        self.assertEqual(len(leads_con_matriculas), 3)
        
        # Verificar que los leads convertidos tienen True en la columna 'convertido'
        leads_convertidos = leads_con_matriculas[leads_con_matriculas['convertido'] == True]
        self.assertEqual(len(leads_convertidos), 2)
        
        # Verificar que los leads no convertidos tienen False en la columna 'convertido'
        leads_no_convertidos = leads_con_matriculas[leads_con_matriculas['convertido'] == False]
        self.assertEqual(len(leads_no_convertidos), 1)
        self.assertEqual(leads_no_convertidos.iloc[0]['id'], 'lead2')
    
    def test_historial_cargas(self):
        """Prueba el registro y recuperación del historial de cargas."""
        # Registrar cargas
        id_registro1 = self.db_manager.registrar_carga('leads', 'test_leads.csv', 3, 'completado')
        id_registro2 = self.db_manager.registrar_carga('matriculas', 'test_matriculas.csv', 2, 'completado')
        
        # Verificar que se crearon los registros
        self.assertIsNotNone(id_registro1)
        self.assertIsNotNone(id_registro2)
        
        # Obtener historial
        historial = self.db_manager.obtener_historial_cargas()
        
        # Verificar que hay dos registros
        self.assertEqual(len(historial), 2)
        
        # Verificar que los tipos de datos son correctos
        tipos_datos = set(historial['tipo_datos'])
        self.assertEqual(tipos_datos, {'leads', 'matriculas'})
        
        # Verificar que el estado es correcto
        estados = set(historial['estado'])
        self.assertEqual(estados, {'completado'})
    
    def test_configuracion(self):
        """Prueba el almacenamiento y recuperación de configuración."""
        # Guardar diferentes tipos de configuración
        self.db_manager.guardar_configuracion('string_config', 'valor_texto')
        self.db_manager.guardar_configuracion('int_config', 123)
        self.db_manager.guardar_configuracion('bool_config', True)
        self.db_manager.guardar_configuracion('dict_config', {'clave': 'valor', 'numero': 42})
        self.db_manager.guardar_configuracion('list_config', [1, 2, 3, 4])
        
        # Recuperar configuraciones
        string_value = self.db_manager.obtener_configuracion('string_config')
        int_value = self.db_manager.obtener_configuracion('int_config')
        bool_value = self.db_manager.obtener_configuracion('bool_config')
        dict_value = self.db_manager.obtener_configuracion('dict_config')
        list_value = self.db_manager.obtener_configuracion('list_config')
        
        # Verificar valores
        self.assertEqual(string_value, 'valor_texto')
        self.assertEqual(int_value, 123)
        self.assertEqual(bool_value, True)
        self.assertEqual(dict_value['clave'], 'valor')
        self.assertEqual(dict_value['numero'], 42)
        self.assertEqual(list_value, [1, 2, 3, 4])
        
        # Verificar valor por defecto para clave inexistente
        default_value = self.db_manager.obtener_configuracion('clave_inexistente', 'valor_default')
        self.assertEqual(default_value, 'valor_default')
    
    def test_realizar_backup(self):
        """Prueba la creación de backup de la base de datos."""
        # Guardar algunos datos
        self.db_manager.guardar_leads(self.test_leads)
        self.db_manager.guardar_matriculas(self.test_matriculas)
        
        # Crear backup en archivo temporal
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            backup_path = temp_file.name
        
        # Realizar backup
        backup_file = self.db_manager.realizar_backup(backup_path)
        
        # Verificar que se creó el archivo
        self.assertTrue(os.path.exists(backup_file))
        
        # Verificar que el backup contiene los datos
        conn_backup = sqlite3.connect(backup_file)
        cursor = conn_backup.cursor()
        
        # Verificar leads
        cursor.execute("SELECT COUNT(*) FROM leads")
        count_leads = cursor.fetchone()[0]
        self.assertEqual(count_leads, 3)
        
        # Verificar matrículas
        cursor.execute("SELECT COUNT(*) FROM matriculas")
        count_matriculas = cursor.fetchone()[0]
        self.assertEqual(count_matriculas, 2)
        
        conn_backup.close()
        
        # Limpiar archivo temporal
        os.unlink(backup_file)

if __name__ == '__main__':
    unittest.main() 