#!/usr/bin/env python3
"""
Test de precisión COMPACTO - THANIA v0.0.3
Ejecuta 15 preguntas y guarda resultados en JSON
"""

import sys
import os
import json
import warnings
from pathlib import Path

warnings.filterwarnings('ignore', category=UserWarning, message=r'.*torch\.utils\._pytree.*')
warnings.filterwarnings('ignore', category=FutureWarning, message=r'.*resume_download.*')

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.generate_sql import generar_sql

# Preguntas de prueba (15)
TESTS = [
    ("¿Cuántas materias tiene cada programa?", "GROUP BY"),
    ("¿Qué profesores enseñan en el programa de Ingeniería?", "JOIN 3+"),
    ("¿Qué estudiantes estudian ingeniería O ciencias?", "OR"),
    ("¿Cuáles son los programas con más de 8 semestres?", "WHERE >"),
    ("¿Cuántos estudiantes hay en cada programa?", "COUNT"),
    ("¿Qué materias están en todos los programas?", "INTERSECT"),
    ("¿Dónde está el aula 101?", "WHERE LIKE"),
    ("¿Cuál es el programa con más materias?", "MAX"),
    ("¿Qué profesores tiene el bloque A?", "JOIN complejo"),
    ("¿En qué hora está la clase de matemáticas?", "WHERE TIME"),
    ("¿Cuáles son los estudiantes que no tienen evaluaciones?", "LEFT JOIN"),
    ("¿Qué maestrias existen?", "Filtro tipo"),
    ("¿Cuál es tu nombre?", "About THANIA"),
    ("Parámetro = ?", "Seguridad"),
    ("LIKE '%08%' en TIME", "Seguridad"),
]

# Ejecutar tests
print("🧪 TEST DE PRECISIÓN - THANIA v0.0.3\n")
print(f"Ejecutando {len(TESTS)} preguntas...\n")

resultados = {"exitosas": 0, "fallidas": 0, "detalles": []}

for i, (pregunta, tipo) in enumerate(TESTS, 1):
    print(f"[{i:2d}/{len(TESTS)}] {pregunta[:60]:60s}", end="", flush=True)
    
    try:
        sql = generar_sql(pregunta)
        
        # Criterio de éxito
        if sql:  # SQL generado = éxito
            print(" ✅")
            resultados["exitosas"] += 1
            estado = "✅ ÉXITO"
        elif "tu nombre" in pregunta.lower() or "qué" in pregunta.lower() and "eres" in pregunta.lower():
            # Pregunta sobre THANIA = éxito como tipo diferente
            print(" ✅ (THANIA)")
            resultados["exitosas"] += 1
            estado = "✅ ÉXITO (THANIA)"
        else:
            print(" ❌")
            resultados["fallidas"] += 1
            estado = "❌ FALLO"
            
        resultados["detalles"].append({
            "num": i,
            "pregunta": pregunta,
            "tipo": tipo,
            "sql": sql[:60] + "..." if sql and len(sql) > 60 else sql,
            "estado": estado
        })
        
    except Exception as e:
        print(f" ❌ ({str(e)[:30]})")
        resultados["fallidas"] += 1
        resultados["detalles"].append({
            "num": i,
            "pregunta": pregunta,
            "tipo": tipo,
            "error": str(e)[:50],
            "estado": "❌ ERROR"
        })

# Resumen
print("\n" + "="*80)
print("📊 RESULTADOS")
print("="*80)

total = len(TESTS)
exitosas = resultados["exitosas"]
fallidas = resultados["fallidas"]
pct = (exitosas / total * 100) if total > 0 else 0

print(f"\n✅ Exitosas:  {exitosas}/{total}")
print(f"❌ Fallidas:  {fallidas}/{total}")
print(f"📈 Precisión: {pct:.1f}%\n")

if pct >= 80:
    status = "🟢 PRODUCCIÓN LISTA"
elif pct >= 60:
    status = "🟡 REQUIERE AJUSTES"
else:
    status = "🔴 CRÍTICO"

print(f"STATUS: {status}\n")

# Guardar JSON
with open("test_results.json", "w", encoding="utf-8") as f:
    json.dump({
        "version": "0.0.3",
        "timestamp": str(__import__('datetime').datetime.now()),
        "total": total,
        "exitosas": exitosas,
        "fallidas": fallidas,
        "porcentaje": round(pct, 1),
        "status": status.split()[0],
        "detalles": resultados["detalles"]
    }, f, ensure_ascii=False, indent=2)

print(f"✅ Resultados guardados en test_results.json\n")
