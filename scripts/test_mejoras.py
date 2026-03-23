#!/usr/bin/env python3
"""
Test simple de las mejoras en el algoritmo THANIA IA
"""

from pipeline.generate_sql import generar_sql
from pipeline.execute_query import ejecutar_query

def test_sql_generation():
    """Test de generación de SQL mejorada"""

    preguntas = [
        "¿Dónde está el profesor Juan Pérez?",
        "¿Qué materias dicta el profesor María García?",
        "¿Dónde está el aula 101?",
        "¿Cuál es la capacidad del laboratorio de química?"
    ]

    for pregunta in preguntas:
        print(f"\nPregunta: {pregunta}")
        sql = generar_sql(pregunta)
        print(f"SQL generado: {sql}")

        if sql:
            try:
                resultado = ejecutar_query(sql)
                filas = resultado.get('filas', [])
                print(f"Registros encontrados: {len(filas)}")
                if filas:
                    print("Primer registro:", filas[0])
            except Exception as e:
                print(f"Error ejecutando SQL: {e}")
        print("-" * 50)

if __name__ == "__main__":
    test_sql_generation()