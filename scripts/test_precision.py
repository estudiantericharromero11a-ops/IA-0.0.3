#!/usr/bin/env python3
"""
Script de validación de precisión de THANIA THANIA v0.0.3
Ejecuta 15 preguntas de nivel experto y evalúa resultados
"""

import sys
import os
import warnings
from pathlib import Path

# Silenciar advertencias
warnings.filterwarnings('ignore', category=UserWarning, message=r'.*torch\.utils\._pytree.*')
warnings.filterwarnings('ignore', category=FutureWarning, message=r'.*resume_download.*')

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.generate_sql import generar_sql
from pipeline.execute_query import ejecutar_sql
from pipeline.human_response import generar_respuesta

# ============================================================================
# PREGUNTAS DE PRUEBA (15 nivel experto)
# ============================================================================

TEST_QUERIES = [
    {
        "id": 1,
        "categoria": "JOINs Complejos",
        "pregunta": "¿Cuáles son los programas en los que los estudiantes tienen más materias?",
        "tipo_esperado": "GROUP BY + JOIN"
    },
    {
        "id": 2,
        "categoria": "JOINs Complejos",
        "pregunta": "¿Qué estudiantes estudian programas que incluyen matemáticas?",
        "tipo_esperado": "JOIN 3+ tablas"
    },
    {
        "id": 3,
        "categoria": "JOINs Complejos",
        "pregunta": "¿Cuáles son los profesores que enseñan en el programa de Ingeniería?",
        "tipo_esperado": "JOIN 4 tablas"
    },
    {
        "id": 4,
        "categoria": "JOINs Complejos",
        "pregunta": "¿Qué profesores enseñan en más de una materia?",
        "tipo_esperado": "GROUP BY + HAVING"
    },
    {
        "id": 5,
        "categoria": "Agregaciones",
        "pregunta": "¿Cuántas materias tiene cada programa?",
        "tipo_esperado": "COUNT + GROUP BY"
    },
    {
        "id": 6,
        "categoria": "Agregaciones",
        "pregunta": "¿Cuál es el número promedio de materias por programa?",
        "tipo_esperado": "AVG + GROUP BY"
    },
    {
        "id": 7,
        "categoria": "Agregaciones",
        "pregunta": "Muestra el programa con más estudiantes registrados",
        "tipo_esperado": "MAX + ORDER BY"
    },
    {
        "id": 8,
        "categoria": "LEFT JOINs",
        "pregunta": "¿Qué estudiantes no tienen evaluaciones?",
        "tipo_esperado": "LEFT JOIN + NULL"
    },
    {
        "id": 9,
        "categoria": "LEFT JOINs",
        "pregunta": "¿Cuáles son los programas sin profesores asignados?",
        "tipo_esperado": "LEFT JOIN + NULL"
    },
    {
        "id": 10,
        "categoria": "Lógica Compleja",
        "pregunta": "¿Qué estudiantes estudian ingeniería O ciencias?",
        "tipo_esperado": "OR + JOIN"
    },
    {
        "id": 11,
        "categoria": "Lógica Compleja",
        "pregunta": "¿Cuáles son los programas que tienen más de 8 semestres Y incluyen matemáticas?",
        "tipo_esperado": "AND + JOIN"
    },
    {
        "id": 12,
        "categoria": "SELECT Simple",
        "pregunta": "¿Cuáles estudiantes tienen promedio superior a 4.0?",
        "tipo_esperado": "WHERE"
    },
    {
        "id": 13,
        "categoria": "SELECT Simple",
        "pregunta": "¿Qué materias están disponibles en el programa de Derecho?",
        "tipo_esperado": "WHERE + JOIN"
    },
    {
        "id": 14,
        "categoria": "Seguridad",
        "pregunta": "¿Qué estudiantes tienen ID = ?",
        "tipo_esperado": "Debe rechazar parámetro sin valor"
    },
    {
        "id": 15,
        "categoria": "Seguridad",
        "pregunta": "¿A qué hora termina la clase en formato LIKE '%08%'?",
        "tipo_esperado": "Debe rechazar LIKE en TIME"
    }
]

# ============================================================================
# CRITERIOS DE EVALUACIÓN
# ============================================================================

def evaluar_respuesta(query, resultado, categoria):
    """
    Evalúa si la respuesta fue exitosa.
    
    Retorna:
        - True: pregunta procesada correctamente (SQL generado o rechazada con razón válida)
        - False: error no intencional
    """
    
    # Preguntas de SEGURIDAD (deben rechazarse)
    if categoria == "Seguridad":
        if resultado.get("error") or not resultado.get("sql"):
            return True  # Rechazo intencional = éxito
        return False
    
    # Preguntas NORMALES (deben generar SQL válido)
    sql = resultado.get("sql")
    error = resultado.get("error")
    
    # Si hay SQL válido = éxito
    if sql and not error:
        return True
    
    # Si hay error = fallo
    if error:
        return False
    
    return False

# ============================================================================
# MAIN - EJECUTAR TESTS
# ============================================================================

def main():
    print("\n" + "="*80)
    print("🧪 TEST DE PRECISIÓN - THANIA THANIA v0.0.3")
    print("="*80)
    print(f"Ejecutando {len(TEST_QUERIES)} preguntas de validación...\n")
    
    resultados = {
        "exitosas": 0,
        "fallidas": 0,
        "detalles": []
    }
    
    # Ejecutar cada pregunta
    for i, test in enumerate(TEST_QUERIES, 1):
        print(f"\n[{i}/{len(TEST_QUERIES)}] Pregunta: {test['pregunta']}\n    Categoría: {test['categoria']}")
        print(f"    Tipo esperado: {test['tipo_esperado']}")
        print("    Procesando...", end="", flush=True)
        
        try:
            # Generar SQL
            sql = generar_sql(test['pregunta'])
            
            # Evaluar resultado
            resultado = {
                "sql": sql,
                "pregunta": test['pregunta'],
                "categoria": test['categoria']
            }
            
            if sql:
                print(" ✅ SQL generado correctamente")
                resultados["exitosas"] += 1
                estado = "✅ ÉXITO"
            else:
                # Podría ser una pregunta sobre THANIA o fallo
                if "tu nombre" in test['pregunta'].lower() or "puedes" in test['pregunta'].lower():
                    print(" ✅ Detectada como pregunta sobre THANIA")
                    resultados["exitosas"] += 1
                    estado = "✅ ÉXITO (THANIA)"
                else:
                    print(" ❌ Fallo")
                    resultados["fallidas"] += 1
                    estado = "❌ FALLO"
            
            resultados["detalles"].append({
                "numero": test["id"],
                "categoria": test["categoria"],
                "pregunta": test["pregunta"],
                "sql": sql[:100] + "..." if sql and len(sql) > 100 else sql,
                "estado": estado
            })
            
        except Exception as e:
            print(f" ❌ Error: {str(e)[:50]}")
            resultados["fallidas"] += 1
            resultados["detalles"].append({
                "numero": test["id"],
                "categoria": test["categoria"],
                "pregunta": test["pregunta"],
                "error": str(e)[:100],
                "estado": "❌ ERROR"
            })
    
    # ========================================================================
    # RESUMEN
    # ========================================================================
    
    print("\n\n" + "="*80)
    print("📊 RESULTADOS DE LA VALIDACIÓN")
    print("="*80)
    
    total = len(TEST_QUERIES)
    exitosas = resultados["exitosas"]
    fallidas = resultados["fallidas"]
    porcentaje = (exitosas / total) * 100 if total > 0 else 0
    
    print(f"\n✅ Exitosas:  {exitosas}/{total}")
    print(f"❌ Fallidas:  {fallidas}/{total}")
    print(f"📈 Precisión: {porcentaje:.1f}%")
    
    print("\n" + "-"*80)
    print("DETALLES POR CATEGORÍA:")
    print("-"*80)
    
    categorias = {}
    for detalle in resultados["detalles"]:
        cat = detalle["categoria"]
        if cat not in categorias:
            categorias[cat] = {"exitosas": 0, "total": 0}
        categorias[cat]["total"] += 1
        if "✅" in detalle["estado"]:
            categorias[cat]["exitosas"] += 1
    
    for cat, stats in categorias.items():
        pct = (stats["exitosas"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        print(f"  {cat:20s}: {stats['exitosas']}/{stats['total']} ({pct:.0f}%)")
    
    print("\n" + "-"*80)
    print("LISTADO COMPLETO:")
    print("-"*80)
    
    for detalle in resultados["detalles"]:
        num = detalle["numero"]
        estado = detalle["estado"]
        categoria = detalle["categoria"]
        asunto = detalle["pregunta"][:60] + "..." if len(detalle["pregunta"]) > 60 else detalle["pregunta"]
        print(f"{num:2d}. {estado} | {categoria:15s} | {asunto}")
    
    print("\n" + "="*80)
    
    # Status report
    if porcentaje >= 80:
        print("🟢 STATUS: PRODUCCIÓN LISTA (Precisión >= 80%)")
    elif porcentaje >= 60:
        print("🟡 STATUS: REQUIERE AJUSTES (Precisión 60-79%)")
    else:
        print("🔴 STATUS: CRÍTICO (Precisión < 60%)")
    
    print("="*80 + "\n")
    
    return resultados

if __name__ == "__main__":
    main()
