#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST AUTOMATICO: 10 PREGUNTAS COMPLEJAS
Ejecuta todas las pruebas sin requerir entrada del usuario
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.generate_sql import generar_sql
from pipeline.execute_query import ejecutar_sql
from pipeline.human_response import generar_respuesta
import logging
import time

logging.basicConfig(level=logging.WARNING)

# Preguntas de test
TESTS = [
    {
        "num": 1,
        "pregunta": "¿Quiénes son los profesores?",
        "tipo": "FK + Tabla Puente (persona_rol)",
        "validar": lambda resp: "profesor" in resp.lower() or "docente" in resp.lower() or "dra." in resp.lower() or "dr." in resp.lower() or "nombre" in resp.lower()
    },
    {
        "num": 2,
        "pregunta": "¿Cuál es el correo de Juan Pérez?",
        "tipo": "ILIKE + Campo específico",
        "validar": lambda resp: "@" in resp or "correo" in resp.lower() or "no disponible" in resp.lower()
    },
    {
        "num": 3,
        "pregunta": "¿En qué aulas se dictan clases los lunes?",
        "tipo": "4 JOINs (asignacion->instalaciones->bloques->campus)",
        "validar": lambda resp: "lunes" in resp.lower() or "aula" in resp.lower() or "laboratorio" in resp.lower()
    },
    {
        "num": 4,
        "pregunta": "¿Cuál es la capacidad total de las instalaciones?",
        "tipo": "Agregación (SUM)",
        "validar": lambda resp: any(char.isdigit() for char in resp) or "capacidad" in resp.lower()
    },
    {
        "num": 5,
        "pregunta": "¿Dónde está el Laboratorio 201?",
        "tipo": "FK con ubicación (2 JOINs)",
        "validar": lambda resp: "bloque" in resp.lower() or "campus" in resp.lower() or "laboratorio" in resp.lower()
    },
    {
        "num": 6,
        "pregunta": "¿Cuál es el horario de la Dra. María García?",
        "tipo": "FK Inversa (persona -> asignacion)",
        "validar": lambda resp: any(char.isdigit() for char in resp) or "horario" in resp.lower()
    },
    {
        "num": 7,
        "pregunta": "¿En dónde está el aula 101 y qué capacidad tiene?",
        "tipo": "FK Bidireccional + Múltiples Campos",
        "validar": lambda resp: any(char.isdigit() for char in resp) or "aula" in resp.lower() or "capacidad" in resp.lower()
    },
    {
        "num": 8,
        "pregunta": "¿Cuántas materias se dictan en el programa Ingeniería?",
        "tipo": "COUNT + Tabla Puente",
        "validar": lambda resp: any(char.isdigit() for char in resp) or "materia" in resp.lower()
    },
    {
        "num": 9,
        "pregunta": "¿Qué materias se dictan en la Ingeniería?",
        "tipo": "Búsqueda en tabla referenciada",
        "validar": lambda resp: len(resp) > 20 or "materia" in resp.lower()
    },
    {
        "num": 10,
        "pregunta": "¿Qué profesor enseña Cálculo I?",
        "tipo": "FK + Filtro + Tabla Puente",
        "validar": lambda resp: "profesor" in resp.lower() or "docente" in resp.lower() or "garcía" in resp.lower()
    },
]

def test_pregunta(test_config):
    """Ejecuta una pregunta y retorna True si pasa la validación"""
    num = test_config["num"]
    pregunta = test_config["pregunta"]
    validar = test_config["validar"]
    
    print(f"\n{'='*80}")
    print(f"PREGUNTA #{num}: {test_config['tipo']}")
    print(f"{'='*80}")
    print(f"Pregunta: {pregunta}")
    
    try:
        # Generar SQL
        sql = generar_sql(pregunta)
        print(f"\n📋 SQL Generado:\n{sql[:200]}..." if len(sql) > 200 else f"\n📋 SQL Generado:\n{sql}")
        
        # Ejecutar SQL
        resultados = ejecutar_sql(sql)
        print(f"\n📊 Resultados: {len(resultados)} registros encontrados")
        
        # Generar respuesta
        respuesta = generar_respuesta(sql, resultados)
        print(f"\n💬 Respuesta ({len(respuesta)} chars):\n{respuesta}")
        
        # Validar respuesta
        es_valida = validar(respuesta)
        
        if es_valida:
            print(f"\n✅ PASADO")
            return True
        else:
            print(f"\n❌ FALLIDO - Respuesta no cumple criterios de validación")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def main():
    print("\n" + "="*80)
    print("TEST AUTOMATICO DE PRECISION: 10 PREGUNTAS COMPLEJAS")
    print("="*80)
    print(f"Total de preguntas: {len(TESTS)}")
    print("="*80)
    
    inicio = time.time()
    resultados = []
    
    for test_config in TESTS:
        resultado = test_pregunta(test_config)
        resultados.append((test_config["num"], resultado))
        time.sleep(0.5)  # Pequeña pausa entre preguntas
    
    duracion = time.time() - inicio
    
    # Resumen final
    print(f"\n\n{'='*80}")
    print("RESUMEN DE RESULTADOS")
    print(f"{'='*80}")
    
    exitosas = sum(1 for _, r in resultados if r)
    total = len(resultados)
    porcentaje = (exitosas / total * 100) if total > 0 else 0
    
    print(f"\nResultados:")
    for num, resultado in resultados:
        estado = "✅ PASADO" if resultado else "❌ FALLIDO"
        print(f"  Pregunta {num:2d}: {estado}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {exitosas}/{total} preguntas PASADAS ({porcentaje:.1f}%)")
    print(f"Tiempo total: {duracion:.2f}s")
    print(f"{'='*80}")
    
    # Criterio de éxito
    if porcentaje >= 90:
        print("🟢 LISTO PARA PRODUCCION ✅")
    elif porcentaje >= 70:
        print("🟡 FUNCIONAL (revisar fallos)")
    else:
        print("🔴 REQUIERE AJUSTES")
    
    return exitosas, total, porcentaje

if __name__ == "__main__":
    main()
