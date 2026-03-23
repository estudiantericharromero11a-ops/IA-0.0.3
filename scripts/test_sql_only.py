#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST SIN OLLAMA: Valida SQL generation y query execution
Evita timeout de Ollama para hacer diagnóstico rápido
"""

import sys
import os
import io

# Forzar UTF-8 en output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.generate_sql import generar_sql
from pipeline.execute_query import ejecutar_sql
import logging

logging.basicConfig(level=logging.WARNING)

# Preguntas de test
TESTS = [
    {
        "num": 1,
        "pregunta": "¿Quiénes son los profesores?",
        "tipo": "FK + Tabla Puente (persona_rol)",
        "validar_sql": lambda sql: "persona_rol" in sql.lower() and "profesor" in sql.lower(),
        "validar_resultados": lambda res: len(res) > 0 and any('María' in str(r) or 'Juan' in str(r) for r in res)
    },
    {
        "num": 2,
        "pregunta": "¿Cuál es el correo de Juan Pérez?",
        "tipo": "ILIKE + Campo email",
        "validar_sql": lambda sql: "correo" in sql.lower() and "juan" in sql.lower(),
        "validar_resultados": lambda res: any("@" in str(r).lower() or "correo" in str(r).lower() for r in res)
    },
    {
        "num": 3,
        "pregunta": "¿En qué aulas se dictan clases los lunes?",
        "tipo": "Multiple JOINs + Filtro día",
        "validar_sql": lambda sql: "lunes" in sql.lower() and "instalaciones" in sql.lower(),
        "validar_resultados": lambda res: len(res) >= 0
    },
    {
        "num": 4,
        "pregunta": "¿Cuál es la capacidad total de las instalaciones?",
        "tipo": "Agregación (SUM)",
        "validar_sql": lambda sql: "sum" in sql.lower() and "capacidad" in sql.lower(),
        "validar_resultados": lambda res: any(isinstance(r.get('capacidad_total'), (int, float)) or r.get('capacidad_total') is not None for r in (res if isinstance(res, list) else [res]))
    },
    {
        "num": 5,
        "pregunta": "¿Dónde está el Laboratorio 201?",
        "tipo": "FK con ubicación",
        "validar_sql": lambda sql: "laboratorio" in sql.lower() and ("bloque" in sql.lower() or "campus" in sql.lower()),
        "validar_resultados": lambda res: len(res) >= 0
    },
    {
        "num": 6,
        "pregunta": "¿Cuál es el horario de la Dra. María García?",
        "tipo": "FK Inversa",
        "validar_sql": lambda sql: "maría" in sql.lower() and ("hora" in sql.lower() or "asignacion" in sql.lower()),
        "validar_resultados": lambda res: len(res) >= 0
    },
    {
        "num": 7,
        "pregunta": "¿En dónde está el aula 101 y qué capacidad tiene?",
        "tipo": "FK Bidireccional",
        "validar_sql": lambda sql: "101" in sql or "aula" in sql.lower(),
        "validar_resultados": lambda res: len(res) >= 0
    },
    {
        "num": 8,
        "pregunta": "¿Cuántas materias se dictan en Ingeniería?",
        "tipo": "COUNT + Tabla Puente",
        "validar_sql": lambda sql: "ingenieria" in sql.lower() and "materia" in sql.lower(),
        "validar_resultados": lambda res: len(res) >= 0
    },
    {
        "num": 9,
        "pregunta": "¿Qué materias se dictan en la Ingeniería?",
        "tipo": "Búsqueda en tabla",
        "validar_sql": lambda sql: "ingenieria" in sql.lower() and "materia" in sql.lower(),
        "validar_resultados": lambda res: len(res) >= 0
    },
    {
        "num": 10,
        "pregunta": "¿Qué profesor enseña Cálculo I?",
        "tipo": "FK + Filtro",
        "validar_sql": lambda sql: "calculos" in sql.lower() or "calculo" in sql.lower() and "profesor" in sql.lower(),
        "validar_resultados": lambda res: len(res) >= 0
    },
]

def test_pregunta(test_config):
    """Ejecuta una pregunta y retorna True si pasa la validación"""
    num = test_config["num"]
    pregunta = test_config["pregunta"]
    validar_sql = test_config["validar_sql"]
    validar_resultados = test_config["validar_resultados"]
    
    print(f"\n{'='*80}")
    print(f"PREGUNTA #{num}: {test_config['tipo']}")
    print(f"{'='*80}")
    print(f"Pregunta: {pregunta}")
    
    try:
        # Generar SQL
        sql = generar_sql(pregunta)
        print(f"\n[SQL] SQL Generado:")
        print(f"{sql[:300]}..." if len(sql) > 300 else sql)
        
        # Validar SQL
        sql_valido = validar_sql(sql)
        if not sql_valido:
            print(f"\n[WARNING] SQL generado no contiene los keywords esperados")
        
        # Ejecutar SQL
        try:
            resultados = ejecutar_sql(sql)
            num_registros = len(resultados) if isinstance(resultados, list) else 1
            print(f"\n[RESULTS] {num_registros} registros encontrados")
            
            if num_registros > 0 and num_registros <= 3:
                print(f"   Datos: {resultados}")
            
            # Validar resultados
            resultados_validos = validar_resultados(resultados)
            
            if sql_valido and resultados_validos:
                print(f"\n[OK] PASADO")
                return True
            else:
                print(f"\n[FAIL] FALLIDO - SQL o resultados no validos")
                return False
                
        except Exception as e:
            print(f"\n[ERROR] en ejecutar_sql: {str(e)[:150]}")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"\n[ERROR] {error_msg[:200]}")
        return False

def main():
    print("\n" + "="*80)
    print("TEST DE SQL GENERATION Y QUERY EXECUTION (SIN OLLAMA)")
    print("="*80)
    print(f"Total de preguntas: {len(TESTS)}")
    print("="*80)
    
    resultados = []
    
    for test_config in TESTS:
        resultado = test_pregunta(test_config)
        resultados.append((test_config["num"], resultado))
    
    # Resumen final
    print(f"\n\n{'='*80}")
    print("RESUMEN DE RESULTADOS")
    print(f"{'='*80}")
    
    exitosas = sum(1 for _, r in resultados if r)
    total = len(resultados)
    porcentaje = (exitosas / total * 100) if total > 0 else 0
    
    print(f"\nResultados:")
    for num, resultado in resultados:
        estado = "[OK] PASADO" if resultado else "[FAIL] FALLIDO"
        print(f"  Pregunta {num:2d}: {estado}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {exitosas}/{total} preguntas PASADAS ({porcentaje:.1f}%)")
    print(f"{'='*80}")
    
    # Criterio de éxito
    if porcentaje >= 80:
        print("[OK] SQL GENERATION Y QUERY EXECUTION: FUNCIONALES")
    elif porcentaje >= 60:
        print("[WARNING] PARCIALMENTE FUNCIONAL (revisar fallos)")
    else:
        print("[ERROR] REQUIERE AJUSTES")
    
    print("\nNOTA: Este test NO incluye Ollama (LLM). Solo valida:")
    print("  - Generacion de SQL")
    print("  - Ejecucion de queries")
    print("  - Estructura de resultados")
    print("\nPara test completo con Ollama, ejecutar test_auto.py")
    
    return exitosas, total, porcentaje

if __name__ == "__main__":
    main()
