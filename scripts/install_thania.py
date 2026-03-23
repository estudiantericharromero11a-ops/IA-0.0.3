#!/usr/bin/env python3
"""
THANIA THANIA - Script de Instalación y Verificación Automatizada (v0.0.3)

Este script automatiza:
1. Verificación de requisitos previos
2. Instalación de dependencias
3. Configuración de base de datos
4. Tests funcionales
5. Status del sistema
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class ThaniInstaller:
    """Gestor de instalación de THANIA THANIA"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.env_file = self.base_dir / '.env'
        self.env_example = self.base_dir / '.env.example'
        self.results = {'success': [], 'errors': []}
    
    def print_header(self, title):
        """Imprime encabezado"""
        print(f"\n{BLUE}{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}{RESET}\n")
    
    def print_success(self, msg):
        """Imprime mensaje exitoso"""
        print(f"{GREEN}✅ {msg}{RESET}")
        self.results['success'].append(msg)
    
    def print_error(self, msg):
        """Imprime mensaje de error"""
        print(f"{RED}❌ {msg}{RESET}")
        self.results['errors'].append(msg)
    
    def print_warning(self, msg):
        """Imprime advertencia"""
        print(f"{YELLOW}⚠️  {msg}{RESET}")
    
    def print_info(self, msg):
        """Imprime información"""
        print(f"{BLUE}ℹ️  {msg}{RESET}")
    
    # ========== VERIFICACIONES ==========
    
    def check_python_version(self):
        """Verifica versión de Python"""
        self.print_header("1. Verificación de Python")
        
        version_info = sys.version_info
        version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
        
        if version_info >= (3, 12):
            self.print_success(f"Python {version_str} ✓")
            return True
        else:
            self.print_warning(f"Python {version_str} (recomendado: 3.12+)")
            return True  # Continuamos de todas formas
    
    def check_environment_file(self):
        """Verifica archivo .env"""
        self.print_header("2. Verificación de Configuración (.env)")
        
        if self.env_file.exists():
            self.print_success(".env encontrado")
            return True
        elif self.env_example.exists():
            self.print_warning(".env no encontrado, usando .env.example como template")
            self.print_info("Por favor edita .env con tus credenciales de BD")
            return False
        else:
            self.print_error("No se encontró .env ni .env.example")
            return False
    
    def check_pip_packages(self):
        """Verifica paquetes pip instalados"""
        self.print_header("3. Verificación de Dependencias Python")
        
        required_packages = {
            'torch': '2.3.0',
            'transformers': '4.36.0',
            'sentence_transformers': '3.0.1',
            'psycopg': '3.1',
            'pgvector': '0.2',
        }
        
        all_ok = True
        for pkg, version in required_packages.items():
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'show', pkg],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    # Extrae versión
                    for line in result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            installed_version = line.split(':')[1].strip()
                            self.print_success(f"{pkg}=={installed_version}")
                            break
                else:
                    self.print_error(f"{pkg} no instalado")
                    all_ok = False
            except Exception as e:
                self.print_error(f"Error verificando {pkg}: {e}")
                all_ok = False
        
        return all_ok
    
    def check_database_connection(self):
        """Verifica conexión a base de datos"""
        self.print_header("4. Verificación de Base de Datos")
        
        if not self.env_file.exists():
            self.print_warning("Salta verificación (no hay .env configurado)")
            return False
        
        try:
            from database.queries import get_connection
            conn = get_connection()
            conn.close()
            self.print_success("Conexión a PostgreSQL ✓")
            return True
        except Exception as e:
            self.print_error(f"No se puede conectar a PostgreSQL: {e}")
            self.print_info("Asegúrate que PostgreSQL esté ejecutándose y .env sea correcto")
            return False
    
    def check_ollama_connection(self):
        """Verifica conexión a Ollama"""
        self.print_header("5. Verificación de Ollama (THANIA)")
        
        try:
            import requests
            resp = requests.get('http://localhost:11434/api/tags', timeout=3)
            
            if resp.status_code == 200:
                models = resp.json().get('models', [])
                if models:
                    model_names = [m.get('name', 'unknown') for m in models]
                    self.print_success(f"Ollama conectado ✓ - Modelos: {', '.join(model_names)}")
                    return True
                else:
                    self.print_warning("Ollama conectado pero sin modelos. Ejecuta: ollama pull llama3")
                    return False
            else:
                self.print_error("Ollama responde pero con estado incorrecto")
                return False
        except Exception as e:
            self.print_error(f"Ollama no disponible: {e}")
            self.print_info("Ejecuta en otra terminal: ollama serve")
            return False
    
    def check_ai_modules(self):
        """Verifica módulos THANIA"""
        self.print_header("6. Verificación de Módulos THANIA")
        
        modules_to_check = [
            ('Sistema.retrieval', 'Retrieval semántico'),
            ('Sistema.llm', 'LLM Integration'),
            ('pipeline.generate_sql', 'Generación de SQL'),
            ('pipeline.execute_query', 'Ejecución de queries'),
            ('pipeline.human_response', 'Respuestas naturales'),
        ]
        
        all_ok = True
        for module, description in modules_to_check:
            try:
                __import__(module)
                self.print_success(f"{description} ✓")
            except ImportError as e:
                self.print_error(f"{description}: {e}")
                all_ok = False
        
        return all_ok
    
    # ========== INSTALACIÓN ==========
    
    def install_requirements(self):
        """Instala requirements.txt"""
        self.print_header("Instalando Dependencias")
        
        requirements_file = self.base_dir / 'requirements.txt'
        
        if not requirements_file.exists():
            self.print_error("No se encontró requirements.txt")
            return False
        
        try:
            self.print_info("Instalando paquetes (puede tomar algunos minutos)...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                self.print_success("Dependencias instaladas correctamente")
                return True
            else:
                self.print_error(f"Error: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.print_error("Instalación tardó demasiado (timeout)")
            return False
        except Exception as e:
            self.print_error(f"Error instalando: {e}")
            return False
    
    # ========== TEST FUNCIONAL ==========
    
    def test_basic_imports(self):
        """Test de importaciones básicas"""
        self.print_header("7. Test Funcional - Importaciones")
        
        test_code = """
import torch
import transformers
from sentence_transformers import SentenceTransformer
print(f'Torch: {torch.__version__}')
print(f'Transformers: {transformers.__version__}')
print('✓ Importaciones OK')
"""
        
        try:
            result = subprocess.run(
                [sys.executable, '-c', test_code],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.print_success("Importaciones básicas funcionan ✓")
                return True
            else:
                self.print_error(f"Error en importaciones: {result.stderr}")
                return False
        except Exception as e:
            self.print_error(f"Error en test: {e}")
            return False
    
    # ========== REPORTES ==========
    
    def print_summary(self):
        """Imprime resumen final"""
        self.print_header("RESUMEN DE VERIFICACIÓN")
        
        total_success = len(self.results['success'])
        total_errors = len(self.results['errors'])
        
        print(f"{GREEN}Exitosos:{RESET} {total_success}")
        print(f"{RED}Errores:{RESET} {total_errors}")
        
        if total_errors > 0:
            print(f"\n{RED}Errores encontrados:{RESET}")
            for i, error in enumerate(self.results['errors'], 1):
                print(f"  {i}. {error}")
        
        print(f"\n{BLUE}{'='*70}{RESET}")
        
        if total_errors == 0:
            print(f"{GREEN}✅ SISTEMA COMPLETAMENTE FUNCIONAL{RESET}")
            print(f"\n{BLUE}Próximo paso:{RESET}")
            print(f"  python app.py --local")
            return True
        else:
            print(f"{RED}❌ HAY ERRORES QUE CORREGIR{RESET}")
            return False
    
    def run_full_check(self):
        """Ejecuta todas las verificaciones"""
        self.print_header("🚀 THANIA THANIA - VERIFICACIÓN Y INSTALACIÓN (v0.0.3)")
        print("Este script verificará todas las dependencias y configuración.\n")
        
        # Verificaciones en orden
        checks = [
            self.check_python_version(),
            self.check_environment_file(),
            self.check_pip_packages(),
            self.check_ai_modules(),
        ]
        
        # Verificaciones que requieren servicios externos (opcional)
        try:
            self.check_database_connection()
        except:
            pass
        
        try:
            self.check_ollama_connection()
        except:
            pass
        
        # Test funcional
        self.test_basic_imports()
        
        # Resumen
        return self.print_summary()

def main():
    """Punto de entrada principal"""
    installer = ThaniInstaller()
    success = installer.run_full_check()
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
