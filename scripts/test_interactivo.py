#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTERFAZ INTERACTIVA DE TEST
Prueba las 10 preguntas una por una con al presionar ENTER
"""

import sys
sys.path.insert(0, '/root')

# Importaciones
from pipeline.generate_sql import generar_sql
from pipeline.execute_query import ejecutar_sql
from pipeline.human_response import generar_respuesta
import logging

logging.basicConfig(level=logging.WARNING)

# Preguntas de test
TESTS = [
    {
        "num": 1,
        "pregunta": "¿Quiénes son los profesores?",
        "tipo": "FK + Tabla Puente (persona_rol)"
    },
    {
        "num": 2,
        "pregunta": "¿Cuál es el correo de Juan Pérez?",
        "tipo": "ILIKE + Campo específico"
    },
    {
        "num": 3,
        "pregunta": "¿En qué aulas se dictan clases los lunes?",
        "tipo": "4 JOINs (asignacion->instalaciones->bloques->campus)"
    },
    {
        "num": 4,
        "pregunta": "¿Cuál es la capacidad total de las instalaciones?",
        "tipo": "Agregación (SUM)"
    },
    {
        "num": 5,
        "pregunta": "¿Dónde está el Laboratorio 201?",
        "tipo": "FK con ubicación (2 JOINs)"
    },
    {
        "num": 6,
        "pregunta": "¿Cuál es el horario de la Dra. María García?",
        "tipo": "FK Inversa (persona -> asignacion)"
    },
    {
        "num": 7,
        "pregunta": "¿Qué materias se dictan en el Aula 101?",
        "tipo": "FK Bidireccional"
    },
    {
        "num": 8,
        "pregunta": "¿Cuántas aulas hay en el Bloque B?",
        "tipo": "COUNT con filtro"
    },
    {
        "num": 9,
        "pregunta": "¿Quién dicta Programación?",
        "tipo": "Buscar por nombre en tabla referenciada"
    },
    {
        "num": 10,
        "pregunta": "¿Qué profesor da clases el miércoles?",
        "tipo": "FK con filtro en tabla puente"
    }
]

def main():
    print("\n" + "="*90)
    print("TEST INTERACTIVO DE PRECISION: 10 PREGUNTAS COMPLEJAS")
    print("="*90)
    print("\nEste script te permite probar cada pregunta una a una.")
    print("Presiona ENTER para pasar a la siguiente pregunta.\n")
    
    resultados = []
    
    for test in TESTS:
        print("-" * 90)
        print("PREGUNTA #%d" % test['num'])
        print("-" * 90)
        print("Pregunta: %s" % test['pregunta'])
        print("Tipo de prueba: %s" % test['tipo'])
        print("\nPresiona ENTER para ejecutar la pregunta...", end="")
        input()
        
        try:
            print("\n[1/3] Generando SQL...")
            sql = generar_sql(test['pregunta'])
            
            if not sql:
                print("  [FALLO] SQL no generado")
                resultados.append(False)
                continue
            
            print("  SQL: %s" % sql[:100])
            
            print("[2/3] Ejecutando query...")
            resultado = ejecutar_sql(sql)
            filas = len(resultado.get('filas', []))
            print("  Resultados: %d filas" % filas)
            
            print("[3/3] Generando respuesta (timeout: 30s)...")
            respuesta = generar_respuesta(test['pregunta'], resultado, timeout=30)
            
            print("\nRESPUESTA:")
            print("  %s" % respuesta)
            print("  Longitud: %d caracteres (max 900)" % len(respuesta))
            
            # Validación
            exito = (len(respuesta) >= 20 and 
                    len(respuesta) <= 900 and 
                    "error" not in respuesta.lower())
            
            print("\nEVALUACION: %s" % ("APROBADA" if exito else "REVISAR"))
            resultados.append(exito)
            
        except Exception as e:
            print("\nERROR: %s" % str(e))
            resultados.append(False)
        
        print("\nPresiona ENTER para continuar...", end="")
        input()
    
    # RESUMEN FINAL
    print("\n\n" + "="*90)
    print("RESUMEN FINAL")
    print("="*90)
    
    exitos = sum(resultados)
    total = len(resultados)
    tasa = (exitos / total * 100) if total > 0 else 0
    
    print("\nResultados por pregunta:")
    for test, resultado in zip(TESTS, resultados):
        status = "APROBADA" if resultado else "REVISAR"
        print("  Q%d: %s [%s]" % (test['num'], test['pregunta'][:50], status))
    
    print("\n" + "-"*90)
    print("TASA DE EXITO: %.1f%% (%d/%d preguntas aprobadas)" % (tasa, exitos, total))
    print("-"*90)
    
    if tasa >= 90:
        print("\nCONCLUSION: Sistema LISTO PARA PRODUCCION")
    elif tasa >= 70:
        print("\nCONCLUSION: Sistema FUNCIONAL (revisar preguntas fallidas)")
    else:
        print("\nCONCLUSION: Sistema REQUIERE AJUSTES")
    
    print("\n" + "="*90 + "\n")

if __name__ == '__main__':
    main()
