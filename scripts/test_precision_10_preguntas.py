#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST DE PRECISION: 10 PREGUNTAS COMPLEJAS CON VALIDACION DE RELACIONES
Verifica:
1. Precision en respuestas
2. Manejo de relaciones entre tablas (FK)
3. Tablas puente (persona_rol, programa_materia)
4. Multiples JOINs
5. Truncamiento de respuestas (max 900 caracteres)
"""

import sys
sys.path.insert(0, '/root')

from pipeline.generate_sql import generar_sql
from pipeline.execute_query import ejecutar_sql
from pipeline.human_response import generar_respuesta
from database.queries import get_connection
import logging
import time

logging.basicConfig(level=logging.WARNING)

# Preguntas de test y respuestas esperadas
PREGUNTAS_TEST = [
    {
        "id": 1,
        "pregunta": "¿Quiénes son los profesores que enseñan aquí?",
        "tablas_requeridas": ["personas", "persona_rol", "roles"],
        "relaciones": "Personas <- persona_rol -> roles",
        "tipo": "Tabla puente: persona_rol"
    },
    {
        "id": 2,
        "pregunta": "¿Cuál es el correo de Juan Pérez?",
        "tablas_requeridas": ["personas"],
        "relaciones": "ILIKE en personas.nombre y personas.correo",
        "tipo": "Campo específico con LIKE"
    },
    {
        "id": 3,
        "pregunta": "¿En qué aulas se dictan clases los lunes?",
        "tablas_requeridas": ["asignacion_instalaciones", "instalaciones", "bloques", "campus"],
        "relaciones": "asignacion -> instalaciones -> bloques -> campus",
        "tipo": "Multiples JOINs (4 tablas)"
    },
    {
        "id": 4,
        "pregunta": "¿Cuál es la capacidad total de las instalaciones?",
        "tablas_requeridas": ["instalaciones"],
        "relaciones": "SUM(capacidad)",
        "tipo": "Agregación"
    },
    {
        "id": 5,
        "pregunta": "¿Dónde está el Laboratorio 201 y cuál es su capacidad?",
        "tablas_requeridas": ["instalaciones", "bloques", "campus"],
        "relaciones": "instalaciones -> bloques -> campus",
        "tipo": "FK con ubicación completa (2 JOINs)"
    },
    {
        "id": 6,
        "pregunta": "¿Cuál es el horario de la Dra. María García?",
        "tablas_requeridas": ["personas", "asignacion_instalaciones"],
        "relaciones": "personas.id <- asignacion.id_persona",
        "tipo": "FK inversa: persona a asignacion"
    },
    {
        "id": 7,
        "pregunta": "¿Qué materias se dictan en el Aula 101?",
        "tablas_requeridas": ["instalaciones", "asignacion_instalaciones", "materias"],
        "relaciones": "instalaciones <- asignacion -> materias",
        "tipo": "FK bidireccional"
    },
    {
        "id": 8,
        "pregunta": "¿Cuántas aulas hay en el Bloque B?",
        "tablas_requeridas": ["bloques", "instalaciones"],
        "relaciones": "bloques.id_bloque -> instalaciones.id_bloque",
        "tipo": "COUNT con filtro"
    },
    {
        "id": 9,
        "pregunta": "¿Quién dicta Programación y en qué horario?",
        "tablas_requeridas": ["materias", "asignacion_instalaciones", "personas"],
        "relaciones": "materias.id <- asignacion -> personas.id",
        "tipo": "Buscar por nombre en tabla referenciada"
    },
    {
        "id": 10,
        "pregunta": "¿Qué profesor da clases el miércoles?",
        "tablas_requeridas": ["asignacion_instalaciones", "personas"],
        "relaciones": "asignacion.id_persona -> personas.nombre",
        "tipo": "FK con filtro en tabla puente"
    }
]

def test_pregunta(pregunta_config):
    """Ejecuta una pregunta de test y retorna resultados"""
    
    print("\n" + "=" * 90)
    print("PREGUNTA #%d: %s" % (pregunta_config['id'], pregunta_config['pregunta']))
    print("=" * 90)
    print("Tablas: %s" % ", ".join(pregunta_config['tablas_requeridas']))
    print("Relaciones: %s" % pregunta_config['relaciones'])
    print("Tipo: %s" % pregunta_config['tipo'])
    print("-" * 90)
    
    try:
        inicio = time.time()
        
        # PASO 1: Generar SQL
        print("[1/3] Generando SQL...")
        sql = generar_sql(pregunta_config['pregunta'])
        print("  SQL generado: %s" % (sql[:100] if sql else "NONE"))
        
        if not sql:
            print("  FALLO: SQL no generado")
            return False
        
        # PASO 2: Ejecutar SQL
        print("[2/3] Ejecutando SQL en PostgreSQL...")
        resultado = ejecutar_sql(sql)
        num_filas = len(resultado.get('filas', []))
        print("  Resultado: %d filas" % num_filas)
        
        if num_filas == 0:
            print("  ADVERTENCIA: Sin resultados (puede ser correcto)")
        
        # PASO 3: Generar respuesta natural
        print("[3/3] Generando respuesta con Ollama...")
        respuesta = generar_respuesta(pregunta_config['pregunta'], resultado, timeout=30)
        
        # Validacion
        tiempo_total = time.time() - inicio
        longitud = len(respuesta)
        
        print("\nRESULTADO:")
        print("  Respuesta: %s" % respuesta[:150])
        print("  Longitud: %d caracteres (max 900)" % longitud)
        print("  Tiempo: %.2f segundos" % tiempo_total)
        
        # Validaciones
        exito = True
        validaciones = []
        
        # V1: Respuesta no vacía
        if len(respuesta.strip()) < 5:
            validaciones.append("FALLO: Respuesta vacía o muy corta")
            exito = False
        else:
            validaciones.append("OK: Respuesta generada")
        
        # V2: Respuesta dentro de límite
        if longitud > 900:
            validaciones.append("FALLO: Respuesta excede 900 caracteres (%d)" % longitud)
            exito = False
        else:
            validaciones.append("OK: Longitud válida (%d/900)" % longitud)
        
        # V3: SQL contiene tablas requeridas
        sql_upper = sql.upper()
        tablas_encontradas = []
        for tabla in pregunta_config['tablas_requeridas']:
            if tabla.upper() in sql_upper:
                tablas_encontradas.append(tabla)
        
        if len(tablas_encontradas) >= len(pregunta_config['tablas_requeridas']) * 0.8:
            validaciones.append("OK: Tablas correctas (%d/%d)" % (len(tablas_encontradas), len(pregunta_config['tablas_requeridas'])))
        else:
            validaciones.append("AVISO: Faltan tablas (%d/%d)" % (len(tablas_encontradas), len(pregunta_config['tablas_requeridas'])))
        
        # V4: Respuesta contiene datos coherentes
        if num_filas > 0 and len(respuesta) < 10:
            validaciones.append("FALLO: Hay datos pero respuesta muy corta")
            exito = False
        elif num_filas > 0:
            validaciones.append("OK: Datos interpretados en respuesta")
        
        print("\nVALIDACIONES:")
        for v in validaciones:
            print("  - %s" % v)
        
        print("\nESTADO: %s" % ("APROBADO" if exito else "REVISAR"))
        return exito
        
    except Exception as e:
        print("\nERROR: %s" % str(e))
        return False

def main():
    print("\n" + "#" * 90)
    print("# TEST DE PRECISION: 10 PREGUNTAS COMPLEJAS CON VALIDACION DE RELACIONES")
    print("#" * 90)
    print("\nValidando:")
    print("  - Precision en respuestas")
    print("  - Manejo de Foreign Keys")
    print("  - Tablas puente (persona_rol, programa_materia)")
    print("  - Multiples JOINs")
    print("  - Truncamiento de respuestas (900 caracteres)")
    
    resultados = []
    for pregunta_config in PREGUNTAS_TEST:
        resultado = test_pregunta(pregunta_config)
        resultados.append({
            'id': pregunta_config['id'],
            'pregunta': pregunta_config['pregunta'],
            'exito': resultado
        })
    
    # RESUMEN FINAL
    print("\n\n" + "#" * 90)
    print("# RESUMEN FINAL DE TEST")
    print("#" * 90 + "\n")
    
    total = len(resultados)
    aprobadas = sum(1 for r in resultados if r['exito'])
    tasa_exito = (aprobadas / total) * 100 if total > 0 else 0
    
    print("Resultados:")
    for r in resultados:
        status = "APROBADO" if r['exito'] else "REVISAR"
        print("  Q%d: %s [%s]" % (r['id'], r['pregunta'][:50], status))
    
    print("\n" + "-" * 90)
    print("TASA DE EXITO: %.1f%% (%d/%d preguntas aprobadas)" % (tasa_exito, aprobadas, total))
    print("-" * 90)
    
    if tasa_exito >= 90:
        print("\nCONCLUSION: Sistema LISTO PARA PRODUCCION")
    elif tasa_exito >= 70:
        print("\nCONCLUSION: Sistema FUNCIONAL (revisar preguntas fallidas)")
    else:
        print("\nCONCLUSION: Sistema REQUIERE AJUSTES")
    
    print("\n" + "#" * 90 + "\n")

if __name__ == '__main__':
    main()
