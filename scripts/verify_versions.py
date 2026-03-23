#!/usr/bin/env python3
"""
THANIA THANIA - Script de Verificación Rápida

Ejecutar después de instalar requirements.txt para verificar que todo funciona.
"""

import sys
import subprocess

def check_versions():
    """Verifica versiones de paquetes críticos"""
    print("=" * 70)
    print("VERIFICACIÓN DE VERSIONES CRÍTICAS (v0.0.3)")
    print("=" * 70)
    
    packages_to_check = {
        'torch': '2.3.0',
        'transformers': '4.36.0',
        'sentence_transformers': '3.0.1',
        'psycopg': '3.1',
        'pgvector': '0.2',
    }
    
    all_ok = True
    
    for pkg, expected_version in packages_to_check.items():
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', pkg],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':')[1].strip()
                        status = "✅" if expected_version in version else "⚠️ "
                        print(f"{status} {pkg}: {version} (expected: {expected_version})")
                        break
            else:
                print(f"❌ {pkg}: NO INSTALADO")
                all_ok = False
        except Exception as e:
            print(f"❌ {pkg}: ERROR - {e}")
            all_ok = False
    
    print("\n" + "=" * 70)
    
    if all_ok:
        print("✅ TODAS LAS VERSIONES VERIFICADAS CORRECTAMENTE")
    else:
        print("❌ HAY PROBLEMAS DE VERSIÓN - Ejecuta: pip install -r requirements.txt")
    
    print("=" * 70)
    
    return all_ok

def main():
    check_versions()

if __name__ == '__main__':
    main()
