#!/usr/bin/env python3
"""
Script mejorado para poblar tabla conocimiento con enfoque MODULE-AWARE.
Ahora prioriza asignacion_instalaciones como el NÚCLEO del sistema.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sentence_transformers import SentenceTransformer
from database.queries import get_connection

def poblar_conocimiento_module_aware():
    """Pobla conocimiento con información MODULE-AWARE del sistema."""
    
    modelo = SentenceTransformer('all-MiniLM-L6-v2')
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                print("[*] Limpiando tabla conocimiento...")
                cursor.execute("DELETE FROM conocimiento")
                
                # Documentación MODULE-AWARE
                contextos = [
                    # ========== MÓDULO 1: ESTRUCTURA FÍSICA ==========
                    "El sistema tiene CAMPUS (universidades): CUL y CUC son dos universidades diferentes",
                    "campus contiene: id_campus, nombre, direccion, descripcion - Diferencia entre CUL y CUC",
                    "BLOQUES son edificios dentro de cada campus - Ejemplo: Bloque A, Bloque B, Bloque C",
                    "Cada bloque pertenece a UN campus (relación 1:N)",
                    "INSTALACIONES son espacios físicos: aulas, laboratorios, oficinas, bibliotecas",
                    "Instalaciones contiene: nombre, tipo_instalacion, piso, capacidad, id_bloque, id_area, id_estado",
                    "Cada instalación está en UN bloque, el cual está en UN campus",
                    "ESTADO_INSTALACION define si un aula está: Disponible, Ocupada, Mantenimiento",
                    "AREAS_FUNCIONALES categoriza espacios: Académica, Administrativa, etc.",
                    "HORARIO_INSTALACION define cuándo está abierta cada instalación (lunes-viernes 8:00-18:00)",
                    
                    # ========== MÓDULO 2: GESTIÓN ACADÉMICA ==========
                    "PERSONAS son todos los usuarios: profesores, estudiantes, administrativos",
                    "ROLES define cargos: profesor, docente, estudiante, administrador, coordinador",
                    "PERSONA_ROL es una tabla puente: UNA persona PUEDE tener MÚLTIPLES roles",
                    "MATERIAS son asignaturas: Matemáticas, Física, Programación, Bases de Datos, etc.",
                    "Cada materia tiene: nombre, creditos (dificultad), descripcion",
                    "PROGRAMAS son carreras: Ingeniería, Administración, Derecho, etc.",
                    "Tipos de programa: pregrado, postgrado, tecnólogo, técnico",
                    "Duracion_semestres indica cuántos semestres dura la carrera (ej: 8 semestres)",
                    "PROGRAMA_MATERIA: una carrera TIENE muchas materias, una materia está en muchas carreras",
                    
                    # ========== MÓDULO 3: OPERACIÓN (EL NÚCLEO) ==========
                    "ASIGNACION_INSTALACIONES es LA TABLA MÁS IMPORTANTE - conecta TODO",
                    "Asignacion_instalaciones responde: ¿Quién? ¿Dónde? ¿Cuándo? ¿Qué materia?",
                    "Campos de asignacion_instalaciones: id_persona (profesor), id_materia, id_instalacion, dia_semana, hora_inicio, hora_fin",
                    "id_persona (FK) → ¿QUIÉN enseña? Conecta con tabla personas para saber el profesor",
                    "id_materia (FK) → ¿QUÉ MATERIA? Conecta con tabla materias",
                    "id_instalacion (FK) → ¿DÓNDE? Conecta con instalaciones, luego bloques, luego campus",
                    "dia_semana → ¿CUÁNDO? (lunes, martes, miércoles, jueves, viernes)",
                    "hora_inicio + hora_fin → ¿A QUÉ HORA? (ej: 08:00 a 10:00)",
                    "Más del 80% de respuestas sobre clases vienen de esta tabla",
                    
                    # ========== PATRONES DE BÚSQUEDA COMUNES ==========
                    "Pregunta ¿Qué profesor tiene más horas de clase? → Busca en asignacion_instalaciones, agrupa por profesor, suma horas",
                    "Pregunta ¿Dónde dan clases los lunes? → Busca asignacion_instalaciones con dia_semana=lunes, JOIN instalaciones→bloques→campus",
                    "Pregunta ¿Quiénes son profesores? → Busca en personas JOIN persona_rol JOIN roles donde rol=profesor",
                    "Pregunta ¿Qué materias se enseñan? → Busca DISTINCT en tabla materias o en asignacion_instalaciones",
                    "Pregunta ¿Qué aulas disponibles? → Busca instalaciones donde estado=Disponible",
                    "Pregunta ¿Capacidad total? → SUM de capacidad en tabla instalaciones",
                    "Pregunta ¿Cuántos campus? → COUNT DISTINCT id_campus de tabla campus",
                    
                    # ========== REGLAS DE JUNTURA CRÍTICAS ==========
                    "Para encontrar QUIÉN da clase: asignacion_instalaciones → personas (join id_persona)",
                    "Para encontrar QUÉ materia: asignacion_instalaciones → materias (join id_materia)",
                    "Para encontrar DÓNDE: asignacion_instalaciones → instalaciones → bloques → campus",
                    "Para roles de personas: personas → persona_rol → roles",
                    "Para materias de carrera: programas → programa_materia → materias",
                    "NO EXISTE id_campus en asignacion_instalaciones - siempre ir vía instalaciones→bloques→campus",
                    "UNA persona PUEDE ser profesor AND coordinador - revisar persona_rol",
                    
                    # ========== EJEMPLOS DE QUERIES REALES ==========
                    "Query: ¿Qué profesor tiene más horas? → SELECT p.nombre, SUM(EPOCH...) FROM asignacion_instalaciones a JOIN personas p ON a.id_persona=p.id_persona GROUP BY p.id_persona ORDER BY horas DESC LIMIT 1",
                    "Query: ¿Lunes dónde? → SELECT p.nombre, m.nombre, i.nombre, c.nombre FROM asignacion_instalaciones a ... WHERE dia_semana='lunes'",
                    "Query: ¿Profesores? → SELECT DISTINCT p.nombre FROM personas p JOIN persona_rol pr WHERE r.nombre_rol='profesor'",
                    "Query: ¿Capacidad total? → SELECT SUM(capacidad) FROM instalaciones",
                    
                    # ========== CONTEXTO CUL/CUC ==========
                    "La BD es para dos universidades en una misma: CUL y CUC",
                    "CUL y CUC tienen cada una sus bloques, instalaciones y asignaciones",
                    "Para diferencia CUL de CUC: filtra por campus.nombre o campus.id_campus",
                    "Bloque A puede existir en CUL y también en CUC - verifica campus.nombre",
                    
                    # ========== MÓDULO 4: IA Y EMBEDDINGS ==========
                    "Tabla CONOCIMIENTO tiene: id, contenido (texto), embedding (vector 384D)",
                    "Los embeddings permiten búsquedas semánticas - ¿Quién? ¿Dónde? ¿Cuándo?",
                    "RAG: Recuperar contexto relevante → Generar SQL → Ejecutar → Respuesta natural",
                ]
                
                print(f"[*] Insertando {len(contextos)} registros de contexto...")
                for i, texto in enumerate(contextos, 1):
                    try:
                        embedding = modelo.encode(texto).tolist()
                        cursor.execute("""
                            INSERT INTO conocimiento (contenido, embedding)
                            VALUES (%s, %s::vector)
                        """, (texto, embedding))
                        if i % 10 == 0:
                            print(f"    [{i}/{len(contextos)}] Insertados...")
                    except Exception as e:
                        print(f"    [ERROR] Registro {i}: {e}")
                
                conn.commit()
                print(f"\n[OK] {len(contextos)} registros insertados exitosamente")
                return True
                
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == '__main__':
    poblar_conocimiento_module_aware()
