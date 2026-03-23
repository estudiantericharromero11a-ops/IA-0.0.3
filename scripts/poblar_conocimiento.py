#!/usr/bin/env python3
"""
Script inteligente para poblar la tabla conocimiento.
Mapea conceptos naturales → tablas → columnas.
Esto permite que la THANIA entienda qué buscar en la BD.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer
from database.queries import get_connection
from ai.schema_discovery import obtener_esquema_completo, obtener_relaciones

def poblar_conocimiento_completo():
    """Pobla conocimiento con mapeos inteligentes concepto → tabla → columna."""

    modelo = SentenceTransformer('all-MiniLM-L6-v2')

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM conocimiento")

                # Descubrir esquema automáticamente
                esquema = obtener_esquema_completo()
                relaciones = obtener_relaciones()

                # Obtener datos reales
                cursor.execute("SELECT nombre FROM materias ORDER BY nombre;")
                materias = [row['nombre'] for row in cursor.fetchall()]

                # Get all personas (we don't have a 'rol' column directly in personas)
                cursor.execute("SELECT DISTINCT p.nombre FROM personas p ORDER BY p.nombre;")
                profesores = [row['nombre'] for row in cursor.fetchall()]

                cursor.execute("""
                    SELECT DISTINCT p.nombre, m.nombre, Sistema.dia_semana, Sistema.hora_inicio, Sistema.hora_fin
                    FROM asignacion_instalaciones Sistema
                    JOIN personas p ON Sistema.id_persona = p.id_persona
                    JOIN materias m ON Sistema.id_materia = m.id_materia
                    ORDER BY p.nombre, m.nombre;
                """)
                asignaciones = [(row['nombre'], row['nombre'], row['dia_semana'], row['hora_inicio'], row['hora_fin']) for row in cursor.fetchall()]

                # === ESQUEMA COMPLETO CON RELACIONES FK ===
                esquema_completo = [
                    # MÓDULO ESTRUCTURA FÍSICA
                    "[ESQUEMA] campus: id_campus(PK), nombre, direccion, descripcion",
                    "[RELACION] campus → bloques: bloques.id_campus → campus.id_campus (Un campus tiene muchos bloques)",
                    "[ESQUEMA] bloques: id_bloque(PK), nombre, descripcion, id_campus(FK→campus)",
                    "[RELACION] bloques → instalaciones: instalaciones.id_bloque → bloques.id_bloque (Un bloque contiene muchas instalaciones)",
                    "[ESQUEMA] instalaciones: id_instalacion(PK), nombre, tipo_instalacion, piso, capacidad, id_bloque(FK→bloques), id_area(FK→areas_funcionales), id_estado(FK→estado_instalacion)",
                    "[RELACION] areas_funcionales → instalaciones: instalaciones.id_area → areas_funcionales.id_area (Cada instalación pertenece a un área funcional)",
                    "[RELACION] estado_instalacion → instalaciones: instalaciones.id_estado → estado_instalacion.id_estado (Define estado de la instalación)",
                    "[ESQUEMA] areas_funcionales: id_area(PK), nombre_area, descripcion",
                    "[ESQUEMA] estado_instalacion: id_estado(PK), nombre_estado, descripcion",
                    "[RELACION] instalaciones → horario_instalacion: horario_instalacion.id_instalacion → instalaciones.id_instalacion (Una instalación puede tener varios horarios)",
                    "[ESQUEMA] horario_instalacion: id_horario(PK), id_instalacion(FK→instalaciones), dia_semana, hora_apertura, hora_cierre",
                    
                    # MÓDULO GESTIÓN ACADÉMICA
                    "[ESQUEMA] personas: id_persona(PK), nombre, documento, correo, telefono",
                    "[ESQUEMA] roles: id_rol(PK), nombre_rol, descripcion",
                    "[RELACION] personas ↔ roles: persona_rol.id_persona → personas.id_persona, persona_rol.id_rol → roles.id_rol (Una persona puede tener varios roles)",
                    "[ESQUEMA] persona_rol: id_persona(FK→personas), id_rol(FK→roles)",
                    "[RELACION] persona_rol une personas y roles: identifica roles de cada persona (Prof, Estud, Admin)",
                    "[ESQUEMA] materias: id_materia(PK), nombre, creditos, descripcion",
                    "[ESQUEMA] programas: id_programa(PK), nombre, tipo_programa, duracion_semestres",
                    "[RELACION] programas ↔ materias: programa_materia.id_programa → programas.id_programa, programa_materia.id_materia → materias.id_materia (Un programa tiene muchas materias)",
                    "[ESQUEMA] programa_materia: id_programa(FK→programas), id_materia(FK→materias)",
                    
                    # MÓDULO OPERACIÓN (NÚCLEO)
                    "[ESQUEMA] asignacion_instalaciones: id_asignacion(PK), id_instalacion(FK→instalaciones), id_materia(FK→materias), dia_semana, hora_inicio, hora_fin, id_persona(FK→personas)",
                    "[RELACION] asignacion_instalaciones.id_persona → personas.id_persona (Quién da la clase)",
                    "[RELACION] asignacion_instalaciones.id_materia → materias.id_materia (Qué materia se enseña)",
                    "[RELACION] asignacion_instalaciones.id_instalacion → instalaciones.id_instalacion (Dónde se da la clase)",
                    "[RELACION] asignacion_instalaciones conecta TODO: profesor + materia + instalación + horario",
                    
                    # MÓDULO THANIA
                    "[ESQUEMA] conocimiento: id(PK), contenido, embedding(vector)",
                ]

                # === FLUJO DE DATOS ===
                flujo_datos = [
                    "[FLUJO] campus → bloques → instalaciones → asignacion_instalaciones ← personas, ← materias, ← instalaciones",
                    "[FLUJO] Para responder preguntas, SIEMPRE buscar en asignacion_instalaciones primero",
                    "[FLUJO] asignacion_instalaciones contiene TODA la verdad sobre horarios reales",
                    "[FLUJO] Para 'profesor + materia': JOIN asignacion_instalaciones con personas y materias",
                    "[FLUJO] Para 'dónde + cuándo': JOIN asignacion_instalaciones con instalaciones y horarios",
                    "[FLUJO] Para 'qué enseña profesor': JOIN asignacion_instalaciones con materias WHERE id_persona",
                    "[FLUJO] Para 'dónde está clase': JOIN asignacion_instalaciones con instalaciones WHERE id_materia",
                ]

                # === EJEMPLOS ESPECÍFICOS CON FK ===
                ejemplos_fk = [
                    "PREGUNTA: 'qué profesor da matemáticas' → SQL: SELECT p.nombre FROM personas p JOIN asignacion_instalaciones Sistema ON p.id_persona=Sistema.id_persona JOIN materias m ON m.id_materia=Sistema.id_materia WHERE m.nombre LIKE '%Matemática%'",
                    "PREGUNTA: 'dónde está la clase de física' → SQL: SELECT i.nombre, b.nombre FROM instalaciones i JOIN asignacion_instalaciones Sistema ON i.id_instalacion=Sistema.id_instalacion JOIN bloques b ON i.id_bloque=b.id_bloque JOIN materias m ON Sistema.id_materia=m.id_materia WHERE m.nombre LIKE '%Física%'",
                    "PREGUNTA: 'qué se enseña los lunes' → SQL: SELECT DISTINCT m.nombre FROM materias m JOIN asignacion_instalaciones Sistema ON m.id_materia=Sistema.id_materia WHERE Sistema.dia_semana='Lunes'",
                    "PREGUNTA: 'quién da clase en aula 101' → SQL: SELECT p.nombre FROM personas p JOIN asignacion_instalaciones Sistema ON p.id_persona=Sistema.id_persona JOIN instalaciones i ON i.id_instalacion=Sistema.id_instalacion WHERE i.nombre LIKE '%101%'",
                    "PREGUNTA: 'qué aulas están disponibles' → SQL: SELECT i.nombre FROM instalaciones i JOIN estado_instalacion e ON i.id_estado=e.id_estado WHERE e.nombre_estado='Disponible'",
                    "PREGUNTA: 'quién tiene rol de administrador' → SQL: SELECT p.nombre FROM personas p JOIN persona_rol pr ON p.id_persona=pr.id_persona JOIN roles r ON pr.id_rol=r.id_rol WHERE LOWER(r.nombre_rol) LIKE '%administrador%'",
                ]

                # === CONTEXTO COMPLETO ===
                contexto_textos = []

                # 1. Esquema completo con FK
                contexto_textos.extend(esquema_completo)

                # 2. Flujo de datos
                contexto_textos.extend(flujo_datos)

                # 3. Ejemplos específicos
                contexto_textos.extend(ejemplos_fk)

                # 4. Descripciones extendidas basadas en información del usuario
                contexto_detallado = [
                    "MÓDULO: ESTRUCTURA FÍSICA -> Tablas: campus, bloques, instalaciones, areas_funcionales, estado_instalacion.",
                    "campus: id_campus (PK), nombre (CUL/CUC), direccion, descripcion; distingue universidades en una estructura común.",
                    "bloques: id_bloque (PK), nombre, descripcion, id_campus (FK). Asocia bloques físicos a un campus.",
                    "instalaciones: id_instalacion (PK), nombre, tipo_instalacion (aula, laboratorio, oficina, biblioteca), piso, capacidad, id_bloque (FK), id_area (FK), id_estado (FK).",
                    "areas_funcionales: id_area (PK), nombre_area, descripcion; define el propósito funcional de instalaciones.",
                    "estado_instalacion: id_estado (PK), nombre_estado (Disponible, Ocupado, Mantenimiento), descripcion; indica disponibilidad de instalaciones.",
                    "horario_instalacion: id_horario (PK), id_instalacion (FK), dia_semana, hora_apertura, hora_cierre; define ventanas de uso físico.",
                    "MÓDULO: GESTIÓN ACADÉMICA -> Tablas: personas, roles, persona_rol, materias, programas, programa_materia, horario_instalacion.",
                    "personas: id_persona (PK), nombre, documento (sensible), correo, telefono; usuarios del sistema (profesores, estudiantes, administrativos).",
                    "roles: id_rol (PK), nombre_rol (Estudiante, Profesor, Administrativo), descripcion; define categoria de rol por persona.",
                    "persona_rol: tabla puente entre personas y roles; permite múltiples roles por persona.",
                    "materias: id_materia (PK), nombre, creditos, descripcion; asignaturas del catálogo.",
                    "programas: id_programa (PK), nombre, tipo_programa (pregrado, postgrado, tecnologo, tecnico), duracion_semestres.",
                    "programa_materia: tabla puente entre programas y materias; organiza planes de estudio.",
                    "MÓDULO: OPERACIÓN (NÚCLEO DEL SISTEMA) -> tabla asignacion_instalaciones.",
                    "asignacion_instalaciones: id_asignacion (PK), id_instalacion (FK), id_materia (FK), dia_semana, hora_inicio, hora_fin, id_persona (FK); conecta profesor, materia, instalación y horario.",
                    "Responde preguntas clave: ¿qué profesor da clase?, ¿dónde?, ¿cuándo?, ¿qué materia? con datos reales.",
                    "MÓDULO: INTELIGENCIA ARTIFICIAL -> tabla conocimiento (id PK, contenido texto, embedding vector).",
                    "conocimiento: vía RAG para entender lenguaje natural, búsquedas semánticas y contexto adicional de este dominio universitario.",
                    "Recomendación: si la base de conocimiento es insuficiente, esta tabla debe reforzarse con descripciones de tabla, relación y casos con ejemplos.",
                ]
                contexto_textos.extend(contexto_detallado)

                # Insertar todos los contextos
                for i, texto in enumerate(contexto_textos, 1):
                    try:
                        embedding = modelo.encode(texto).tolist()
                        cursor.execute("""
                            INSERT INTO conocimiento (contenido, embedding)
                            VALUES (%s, %s::vector)
                        """, (texto, embedding))
                    except Exception as e:
                        print(f"Error insertando contexto {i}: {e}")

                conn.commit()
                print(f"✅ Insertados {len(contexto_textos)} registros de contexto inteligente")
                print(f"   - Esquema con FK: {len(esquema_completo)}")
                print(f"   - Flujo de datos: {len(flujo_datos)}")
                print(f"   - Ejemplos FK: {len(ejemplos_fk)}")
                print(f"   - Tablas descubiertas: {len(esquema)}")
                print(f"   - Datos reales: {len(asignaciones)} asignaciones")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True

if __name__ == "__main__":
    print("[*] Poblando conocimiento con mapeos inteligentes...")
    if poblar_conocimiento_completo():
        print("[OK] Sistema RAG listo - La THANIA ahora entiende tabla -> concepto")
    else:
        print("[ERROR] Error en el proceso")
        sys.exit(1)