#!/usr/bin/env python3
"""
Script exhaustivo para poblar la tabla conocimiento con documentación completa del esquema.
Este script ingresa toda la información de la base de datos de forma estructurada y vectorizada.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer
from database.queries import get_connection
from ai.schema_discovery import obtener_esquema_completo, obtener_relaciones

def poblar_conocimiento_exhaustivo():
    """Pobla conocimiento con documentación COMPLETA del esquema."""

    modelo = SentenceTransformer('all-MiniLM-L6-v2')

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                print("[*] Limpiando tabla conocimiento...")
                cursor.execute("DELETE FROM conocimiento")

                # ========================================================================
                # 1. DOCUMENTACIÓN DE MÓDULOS Y TABLAS
                # ========================================================================
                modulos = [
                    # MÓDULO 1: ESTRUCTURA FÍSICA
                    "[MODULO] ESTRUCTURA FÍSICA: Define la infraestructura física de la universidad (campus, bloques, instalaciones, estados, horarios)",
                    
                    "[TABLA] campus: Diferencia universidades (CUL, CUC). Columnas: id_campus(PK), nombre, direccion, descripcion",
                    "[RELACION] campus → bloques: Un campus tiene muchos bloques (1:N)",
                    
                    "[TABLA] bloques: Secciones/bloques dentro de campus (Bloque A, B, etc.). Columnas: id_bloque(PK), nombre, descripcion, id_campus(FK)",
                    "[RELACION] bloques → instalaciones: Un bloque contiene muchas instalaciones (1:N)",
                    
                    "[TABLA] instalaciones: Espacios físicos (aulas, oficinas, labs). Columnas: id_instalacion(PK), nombre, tipo_instalacion, piso, capacidad, id_bloque(FK), id_area(FK), id_estado(FK)",
                    "[RELACION] instalaciones → horario_instalacion: Una instalación puede tener múltiples horarios (1:N)",
                    "[RELACION] instalaciones → asignacion_instalaciones: Una instalación puede ser asignada a clases (1:N)",
                    
                    "[TABLA] areas_funcionales: Categorías de áreas (Administración, Académica, etc.). Columnas: id_area(PK), nombre_area, descripcion",
                    "[RELACION] areas_funcionales → instalaciones: Un área funcional agrupa muchas instalaciones (1:N)",
                    
                    "[TABLA] estado_instalacion: Estados disponibles para instalaciones (Disponible, Mantenimiento, etc.). Columnas: id_estado(PK), nombre_estado, descripcion",
                    
                    "[TABLA] horario_instalacion: Horarios de disponibilidad de instalaciones. Columnas: id_horario(PK), id_instalacion(FK), dia_semana, hora_apertura, hora_cierre",
                    
                    # MÓDULO 2: GESTIÓN ACADÉMICA
                    "[MODULO] GESTIÓN ACADÉMICA: Define personas, roles, materias y programas académicos",
                    
                    "[TABLA] personas: Registro de todos (docentes, estudiantes, admin). Columnas: id_persona(PK), nombre, documento(CONFIDENCIAL), correo, telefono",
                    "[RELACION] personas → persona_rol: Una persona puede tener múltiples roles (1:N a través de tabla puente)",
                    "[RELACION] personas → asignacion_instalaciones: Una persona (profesor) puede enseñar múltiples clases (1:N)",
                    
                    "[TABLA] roles: Define roles/cargos (Estudiante, Profesor, Administrador, etc.). Columnas: id_rol(PK), nombre_rol, descripcion",
                    
                    "[TABLA_PUENTE] persona_rol: Relaciona personas con roles (una persona puede tener múltiples roles). Columnas: id_persona(FK), id_rol(FK). PK=(id_persona, id_rol)",
                    
                    "[TABLA] materias: Define asignaturas de programas académicos. Columnas: id_materia(PK), nombre, creditos, descripcion",
                    "[RELACION] materias → programa_materia: Una materia puede pertenecer a múltiples programas (N:N)",
                    "[RELACION] materias → asignacion_instalaciones: Una materia se enseña en múltiples horarios/aulas (1:N)",
                    
                    "[TABLA] programas: Carreras universitarias (Ingeniería, Administración, etc.). Columnas: id_programa(PK), nombre, tipo_programa, duracion_semestres",
                    
                    "[TABLA_PUENTE] programa_materia: Relaciona programas con materias. Columnas: id_programa(FK), id_materia(FK). PK=(id_programa, id_materia)",
                    
                    # MÓDULO 3: OPERACIÓN (MOTOR CENTRAL)
                    "[MODULO] OPERACIÓN: Módulo central que conecta todo para gestionar horarios reales",
                    
                    "[TABLA_CRITICA] asignacion_instalaciones: MOTOR CENTRAL que conecta profesor + materia + aula + horario. Columnas: id_asignacion(PK), id_instalacion(FK), id_materia(FK), dia_semana, hora_inicio, hora_fin, id_persona(FK)",
                    "[IMPORTANCIA_ASIGNACION] Esta tabla es la respuesta a la mayoría de preguntas: ¿dónde está? ¿cuándo? ¿quién? ¿qué materia?",
                    
                    # MÓDULO 4: THANIA
                    "[MODULO] sistema: Base de conocimiento vectorizado",
                    "[TABLA] conocimiento: Base de conocimiento RAG. Columnas: id(PK), contenido(TEXT), embedding(VECTOR 384D)",
                ]

                # ========================================================================
                # 2. ESQUEMAS ESPECÍFICOS CON TIPOS DE DATOS
                # ========================================================================
                esquemas_tipos = [
                    "[ESQUEMA] campus: id_campus(INTEGER), nombre(VARCHAR), direccion(VARCHAR), descripcion(TEXT)",
                    "[ESQUEMA] bloques: id_bloque(INTEGER), nombre(VARCHAR), descripcion(TEXT), id_campus(FK→campus)",
                    "[ESQUEMA] instalaciones: id_instalacion(INTEGER), nombre(VARCHAR), tipo_instalacion(VARCHAR), piso(INTEGER), capacidad(INTEGER), id_bloque(FK→bloques), id_area(FK→areas), id_estado(FK→estado)",
                    "[ESQUEMA] areas_funcionales: id_area(INTEGER), nombre_area(VARCHAR), descripcion(TEXT)",
                    "[ESQUEMA] estado_instalacion: id_estado(INTEGER), nombre_estado(VARCHAR), descripcion(TEXT)",
                    "[ESQUEMA] horario_instalacion: id_horario(INTEGER), id_instalacion(FK→instalaciones), dia_semana(VARCHAR), hora_apertura(TIME), hora_cierre(TIME)",
                    "[ESQUEMA] personas: id_persona(INTEGER), nombre(VARCHAR), documento(VARCHAR,CONFIDENCIAL), correo(VARCHAR), telefono(VARCHAR)",
                    "[ESQUEMA] roles: id_rol(INTEGER), nombre_rol(VARCHAR), descripcion(TEXT)",
                    "[ESQUEMA] persona_rol: id_persona(FK→personas), id_rol(FK→roles) | PK=(id_persona, id_rol)",
                    "[ESQUEMA] materias: id_materia(INTEGER), nombre(VARCHAR), creditos(INTEGER), descripcion(TEXT)",
                    "[ESQUEMA] programas: id_programa(INTEGER), nombre(VARCHAR), tipo_programa(VARCHAR), duracion_semestres(INTEGER)",
                    "[ESQUEMA] programa_materia: id_programa(FK→programas), id_materia(FK→materias) | PK=(id_programa, id_materia)",
                    "[ESQUEMA] asignacion_instalaciones: id_asignacion(INTEGER), id_instalacion(FK→instalaciones), id_materia(FK→materias), dia_semana(VARCHAR), hora_inicio(TIME), hora_fin(TIME), id_persona(FK→personas)",
                    "[ESQUEMA] conocimiento: id(INTEGER), contenido(TEXT), embedding(VECTOR 384)",
                ]

                # ========================================================================
                # 3. FLUJOS DE DATOS Y PATRONES DE CONSULTA
                # ========================================================================
                flujos = [
                    "[FLUJO] Pregunta COMÚN 1: '¿Qué profesor enseña X materia?' → IR A: asignacion_instalaciones + personas + materias",
                    "[CONSULTA_PATRON] SELECT DISTINCT p.nombre FROM personas p JOIN asignacion_instalaciones Sistema ON p.id_persona=Sistema.id_persona JOIN materias m ON Sistema.id_materia=m.id_materia WHERE m.nombre LIKE '%X%'",
                    
                    "[FLUJO] Pregunta COMÚN 2: '¿Dónde está la clase de X?' → IR A: asignacion_instalaciones + instalaciones + materias + bloques",
                    "[CONSULTA_PATRON] SELECT DISTINCT i.nombre, b.nombre FROM instalaciones i JOIN bloques b ON i.id_bloque=b.id_bloque JOIN asignacion_instalaciones Sistema ON i.id_instalacion=Sistema.id_instalacion JOIN materias m ON Sistema.id_materia=m.id_materia WHERE m.nombre LIKE '%X%'",
                    
                    "[FLUJO] Pregunta COMÚN 3: '¿Qué clases hay el Y (día)?' → IR A: asignacion_instalaciones con dia_semana",
                    "[CONSULTA_PATRON] SELECT DISTINCT m.nombre, p.nombre, i.nombre, Sistema.hora_inicio, Sistema.hora_fin FROM materias m JOIN asignacion_instalaciones Sistema ON m.id_materia=Sistema.id_materia JOIN personas p ON Sistema.id_persona=p.id_persona JOIN instalaciones i ON Sistema.id_instalacion=i.id_instalacion WHERE LOWER(Sistema.dia_semana)=LOWER('Y')",
                    
                    "[FLUJO] Pregunta COMÚN 4: '¿Quién tiene rol Z?' → IR A: personas + persona_rol + roles",
                    "[CONSULTA_PATRON] SELECT p.nombre FROM personas p JOIN persona_rol pr ON p.id_persona=pr.id_persona JOIN roles r ON pr.id_rol=r.id_rol WHERE LOWER(r.nombre_rol) LIKE '%Z%'",
                    
                    "[FLUJO] Pregunta COMÚN 5: '¿Cuál es la capacidad total?' → IR A: instalaciones, SUM(capacidad)",
                    "[CONSULTA_PATRON] SELECT SUM(capacidad) AS capacidad_total FROM instalaciones",
                    
                    "[FLUJO] Pregunta COMÚN 6: '¿Cuántos campus?' → IR A: campus, COUNT(*)",
                    "[CONSULTA_PATRON] SELECT COUNT(DISTINCT id_campus) FROM campus",
                ]

                # ========================================================================
                # 4. REGLAS CRÍTICAS PARA LA THANIA
                # ========================================================================
                reglas_criticas = [
                    "[REGLA] TABLA CENTRAL: asignacion_instalaciones conecta TODO (profesor, materia, aula, horario). Esta tabla es la RESPUESTA a la mayoría de preguntas",
                    
                    "[REGLA] COLUMNAS IMPORTANTES A RECORDAR: personas.nombre, materias.nombre, instalaciones.nombre, roles.nombre_rol (NO 'roles.nombre')",
                    
                    "[REGLA] ALWAYS: Use 'dia_semana' column for day-of-week searches, with LOWER() for case-insensitive comparison",
                    "[REGLA] ALWAYS: Use 'hora_inicio' AND 'hora_fin' TOGETHER for time range queries - never use just one",
                    
                    "[REGLA] CRITICAL: roles.nombre_rol is the correct column name (NOT roles.nombre). Using roles.nombre will cause SQL error",
                    "[REGLA] CRITICAL: When joining personas_rol, always use: personas → persona_rol → roles chain",
                    
                    "[REGLA] MATERIAS: Use LIKE '%nombre%' for flexible searches. Include accents: Matemáticas, Física, Programación, etc.",
                    "[REGLA] PERSONAS: Use LIKE '%nombre%' for flexible searches. Join with asignacion_instalaciones to find professors",
                    
                    "[REGLA] CONFIDENTIAL: Never expose personas.documento without proper authorization",
                    "[REGLA] SECURITY: Only SELECT queries allowed. No INSERT/UPDATE/DELETE",
                    "[REGLA] SECURITY: Maximum 100 rows per query (enforce LIMIT 100)",
                    
                    "[REGLA] CAMPUS: CUL and CUC are two universities in one system, differentiated by id_campus",
                    "[REGLA] BLOQUES: Each campus can have multiple blocks (A, B, C, etc.). Each block belongs to ONE campus",
                    "[REGLA] INSTALACIONES: Can be aula, laboratorio, oficina administrativa, sala de conferencias, biblioteca, etc.",
                    
                    "[REGLA] FK_CHECK: Always verify foreign key relationships: bloques.id_campus→campus, instalaciones.id_bloque→bloques, instalaciones.id_area→areas, instalaciones.id_estado→estado",
                ]

                # ========================================================================
                # 5. EJEMPLOS ESPECÍFICOS CON DATOS REALES
                # ========================================================================
                ejemplos = [
                    "[EJEMPLO] 'Qué profesor enseña Matemáticas' → JOIN asignacion_instalaciones + personas + materias, FILTER materias.nombre LIKE '%Matemática%'",
                    "[EJEMPLO] 'Dónde está la clase de Programación' → asignacion_instalaciones → instalaciones, FILTER materias.nombre LIKE '%Programación%'",
                    "[EJEMPLO] 'Qué clases hay el lunes' → asignacion_instalaciones, FILTER LOWER(dia_semana)='lunes'",
                    "[EJEMPLO] 'Quién es administrador' → personas + persona_rol + roles, FILTER LOWER(roles.nombre_rol) LIKE '%administrador%'",
                    "[EJEMPLO] 'Cuántos campus' → SELECT COUNT(DISTINCT id_campus) FROM campus",
                    "[EJEMPLO] 'Capacidad total de la universidad' → SELECT SUM(capacidad) FROM instalaciones",
                ]

                # ========================================================================
                # 5. FLUJOS AVANZADOS CON RELACIONES ENCADENADAS
                # ========================================================================
                flujos_avanzados = [
                    "[FLUJO_AVANZADO] '¿Dónde dan clase?' → asignacion_instalaciones (id_instalacion) → instalaciones (id_bloque) → bloques (id_campus) → campus",
                    "[FLUJO_AVANZADO] '¿Quién da clase?' → asignacion_instalaciones (id_persona) → personas → persona_rol → roles",
                    "[FLUJO_AVANZADO] '¿Qué materia es?' → asignacion_instalaciones (id_materia) → materias → programa_materia → programas",
                    "[FLUJO_AVANZADO] '¿Quién es admin?' → personas → persona_rol (puente N:N) → roles (filtro nombre_rol LIKE 'administrador')",
                    "[FLUJO_AVANZADO] 'TODO sobre una clase' → asignacion_instalaciones activa 8 relaciones simultáneamente: profesor, materia, aula, campus, bloque, estado, área, horarios",
                    
                    "[CADENA_FK] bloques.id_campus → campus.id_campus | Cardinalidad: 1:N (un campus, muchos bloques)",
                    "[CADENA_FK] instalaciones.id_bloque → bloques.id_bloque | Cardinalidad: 1:N (un bloque, muchas instalaciones)",
                    "[CADENA_FK] instalaciones.id_area → areas_funcionales.id_area | Cardinalidad: 1:N (un área, muchas instalaciones)",
                    "[CADENA_FK] instalaciones.id_estado → estado_instalacion.id_estado | Cardinalidad: 1:N (un estado, muchas instalaciones)",
                    "[CADENA_FK] horario_instalacion.id_instalacion → instalaciones.id_instalacion | Cardinalidad: 1:N (una instalación, muchos horarios)",
                    "[CADENA_FK] persona_rol.id_persona → personas.id_persona AND persona_rol.id_rol → roles.id_rol | Cardinalidad: N:N (personas ↔ roles vía tabla puente)",
                    "[CADENA_FK] programa_materia.id_programa → programas.id_programa AND programa_materia.id_materia → materias.id_materia | Cardinalidad: N:N (programas ↔ materias vía tabla puente)",
                    "[CADENA_FK_CORE] asignacion_instalaciones (id_instalacion) → instalaciones | (id_materia) → materias | (id_persona) → personas | Cardinalidad: N:1 x3 (TABLA CENTRAL)",
                ]

                # ========================================================================
                # 5. RELACIONES ESPECÍFICAS CON EJEMPLOS DE DATOS REALES
                # ========================================================================
                relaciones_ejemplos = [
                    "[RELACION_EJEMPLO] Campus 'CUL' (id=1) tiene Bloque A (id=1) y Bloque B (id=2) → bloques.id_campus = 1",
                    "[RELACION_EJEMPLO] Bloque A contiene Aula 101 (id=1), Lab A (id=2), Oficina A (id=3) → instalaciones.id_bloque = 1",
                    "[RELACION_EJEMPLO] Aula 101 está en Área Académica (id=1) y Estado Disponible (id=1) → instalaciones (id=1) tiene id_area=1, id_estado=1",
                    "[RELACION_EJEMPLO] Aula 101 abre Lunes-Viernes 8:00-18:00 → horario_instalacion con id_instalacion=1",
                    "[RELACION_EJEMPLO] Ana Perez (id=1) tiene rol Profesor (id=1) y rol Coordinadora (id=2) → persona_rol con id_persona=1 e id_rol=1,2",
                    "[RELACION_EJEMPLO] Carlos Ruiz enseña Programación en Aula 102 Lunes 8:00-10:00 → asignacion_instalaciones (id_persona=2, id_materia=1, id_instalacion=2, dia_semana='Lunes', hora_inicio='08:00')",
                    "[RELACION_EJEMPLO] Programa Ingeniería tiene Materias: Cálculo (id=1), Física (id=2), Programación (id=3) → programa_materia con id_programa=1",
                    "[RELACION_EJEMPLO] Materias enseñadas el Lunes → filtra asignacion_instalaciones WHERE LOWER(dia_semana)='lunes' → obtiene id_materia → JOIN materias",
                ]

                # ========================================================================
                # 7. QUERIES DE EJEMPLO POR FLUJO
                # ========================================================================
                queries_flujo = [
                    "[QUERY_FLUJO_1] Dónde dan clase de Matemáticas: SELECT i.nombre, b.nombre, c.nombre FROM asignacion_instalaciones Sistema JOIN instalaciones i ON Sistema.id_instalacion=i.id_instalacion JOIN bloques b ON i.id_bloque=b.id_bloque JOIN campus c ON b.id_campus=c.id_campus WHERE Sistema.id_materia IN (SELECT id_materia FROM materias WHERE nombre LIKE '%Matemática%')",
                    
                    "[QUERY_FLUJO_2] Quién enseña Programación: SELECT DISTINCT p.nombre FROM personas p JOIN asignacion_instalaciones Sistema ON p.id_persona=Sistema.id_persona JOIN materias m ON Sistema.id_materia=m.id_materia WHERE m.nombre LIKE '%Programación%'",
                    
                    "[QUERY_FLUJO_3] Qué se enseña el Lunes: SELECT DISTINCT m.nombre, p.nombre, i.nombre, Sistema.hora_inicio, Sistema.hora_fin FROM asignacion_instalaciones Sistema JOIN materias m ON Sistema.id_materia=m.id_materia JOIN personas p ON Sistema.id_persona=p.id_persona JOIN instalaciones i ON Sistema.id_instalacion=i.id_instalacion WHERE LOWER(Sistema.dia_semana)='lunes'",
                    
                    "[QUERY_FLUJO_4] Quiénes son administradores: SELECT p.nombre FROM personas p JOIN persona_rol pr ON p.id_persona=pr.id_persona JOIN roles r ON pr.id_rol=r.id_rol WHERE LOWER(r.nombre_rol) LIKE '%administrador%'",
                    
                    "[QUERY_FLUJO_5] TODO sobre una clase (id_asignacion=5): SELECT p.nombre, m.nombre, i.nombre, b.nombre, Sistema.dia_semana, Sistema.hora_inicio, Sistema.hora_fin, e.nombre_estado, a.nombre_area FROM asignacion_instalaciones Sistema JOIN personas p ON Sistema.id_persona=p.id_persona JOIN materias m ON Sistema.id_materia=m.id_materia JOIN instalaciones i ON Sistema.id_instalacion=i.id_instalacion JOIN bloques b ON i.id_bloque=b.id_bloque JOIN estado_instalacion e ON i.id_estado=e.id_estado JOIN areas_funcionales a ON i.id_area=a.id_area WHERE Sistema.id_asignacion=5",
                    
                    "[QUERY_FLUJO_6] Disponibilidad de aulas para Programación: SELECT DISTINCT i.nombre, i.capacidad, b.nombre FROM instalaciones i JOIN bloques b ON i.id_bloque=b.id_bloque JOIN asignacion_instalaciones Sistema ON i.id_instalacion=Sistema.id_instalacion WHERE Sistema.id_materia IN (SELECT id_materia FROM materias WHERE nombre LIKE '%Programación%')",
                ]

                # ========================================================================
                # 8. COMBINACIÓN FINAL (ACTUALIZADA CON FLUJOS Y RELACIONES)
                # ========================================================================
                todos_contextos = (
                    modulos + esquemas_tipos + flujos + reglas_criticas + ejemplos +
                    flujos_avanzados + relaciones_ejemplos + queries_flujo
                )

                print(f"\n[*] Insertando {len(todos_contextos)} registros de contexto...")
                for i, texto in enumerate(todos_contextos, 1):
                    try:
                        embedding = modelo.encode(texto).tolist()
                        cursor.execute("""
                            INSERT INTO conocimiento (contenido, embedding)
                            VALUES (%s, %s::vector)
                        """, (texto, embedding))
                        if i % 10 == 0:
                            print(f"    [{i}/{len(todos_contextos)}] Insertados...")
                    except Exception as e:
                        print(f"    [ERROR] Registro {i}: {e}")

                conn.commit()
                
                print(f"\n✅ {len(todos_contextos)} registros de contexto insertados exitosamente")
                print(f"   - Módulos: {len(modulos)}")
                print(f"   - Esquemas con tipos: {len(esquemas_tipos)}")
                print(f"   - Flujos y patrones: {len(flujos)}")
                print(f"   - Reglas críticas: {len(reglas_criticas)}")
                print(f"   - Ejemplos: {len(ejemplos)}")
                print(f"   - Flujos avanzados con FK: {len(flujos_avanzados)}")
                print(f"   - Relaciones con ejemplos reales: {len(relaciones_ejemplos)}")
                print(f"   - Queries por flujo: {len(queries_flujo)}")
                print(f"\n[✓] Sistema RAG actualizado con DOCUMENTACIÓN EXHAUSTIVA del esquema")
                print(f"[✓] La THANIA ahora comprende completamente la estructura de la BD")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    print("=" * 80)
    print("POBLADOR EXHAUSTIVO DE CONOCIMIENTO - DOCUMENTACIÓN COMPLETA DEL ESQUEMA")
    print("=" * 80)
    print("[*] Poblando tabla conocimiento con información COMPLETA del esquema...")
    print()
    
    if poblar_conocimiento_exhaustivo():
        print("\n" + "=" * 80)
        print("✅ OK - La THANIA tiene acceso a documentación COMPLETA del esquema")
        print("=" * 80)
    else:
        print("\n❌ ERROR - No se pudo poblar conocimiento")
        sys.exit(1)
