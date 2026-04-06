import logging
import re
from sentence_transformers import SentenceTransformer
from database.queries import get_connection, ejecutar_query

logger = logging.getLogger(__name__)

# Cargar modelo UNA SOLA VEZ (al inicio del módulo)
try:
    _modelo = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("[OK] Modelo SentenceTransformer cargado correctamente")
except Exception as e:
    logger.warning(f"[WARN] No se pudo cargar modelo SentenceTransformer: {e}")
    _modelo = None


def _tokenizar_pregunta(pregunta):
    """Tokeniza la pregunta para buscar coincidencias exactas/contexto."""
    if not pregunta:
        return []
    # solo palabras de >2 caracteres
    tokens = [t for t in re.findall(r"\b\w{3,}\b", pregunta.lower())]
    return list(dict.fromkeys(tokens))  # conservar orden, evitar duplicados


def _obtener_contexto_tablas(pregunta):
    """Búsqueda directa en tablas clave a partir de términos detectados."""
    if not pregunta:
        return ""

    clue = pregunta.lower()
    resultados = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if any(k in clue for k in ['cul', 'cuc', 'campus']):
            cursor.execute("SELECT nombre, direccion, descripcion FROM campus WHERE nombre ILIKE %s LIMIT 5", ('%' + clue + '%',))
            rows = cursor.fetchall()
            for row in rows:
                resultados.append(f"Campus directo: nombre={row['nombre']}, direccion={row.get('direccion')}, descripcion={row.get('descripcion')}")

        if any(k in clue for k in ['profesor', 'docente', 'instructor', 'catedratico', 'catedrático']):
            cursor.execute(
                "SELECT p.nombre, r.nombre_rol FROM personas p "
                "JOIN persona_rol pr ON p.id_persona = pr.id_persona "
                "JOIN roles r ON pr.id_rol = r.id_rol "
                "WHERE LOWER(r.nombre_rol) IN ('profesor','docente','instructor','catedratico','catedrático') LIMIT 5"
            )
            rows = cursor.fetchall()
            for row in rows:
                resultados.append(f"Profesor directo: nombre={row['nombre']}, rol={row['nombre_rol']}")

        if any(k in clue for k in ['materia', 'asignatura', 'curso']):
            cursor.execute("SELECT nombre, descripcion FROM materias WHERE nombre ILIKE %s OR descripcion ILIKE %s LIMIT 5", ('%' + clue + '%', '%' + clue + '%'))
            rows = cursor.fetchall()
            for row in rows:
                resultados.append(f"Materia directa: nombre={row['nombre']}, descripcion={row.get('descripcion')}")

    except Exception as e:
        logger.warning(f"Error en _obtener_contexto_tablas: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

    return "\n".join(resultados)


def _obtener_contexto_anyword(pregunta):
    """Busca el término completo de la pregunta en todas las tablas principales (match LIKE)."""
    if not pregunta:
        return ""

    clue = pregunta.strip()
    if not clue:
        return ""

    resultados = []
    terms = [f"%{clue}%"]

    try:
        conn = get_connection()
        cursor = conn.cursor()

        table_queries = [
            ("campus", "SELECT nombre,direccion,descripcion FROM campus WHERE nombre ILIKE %s OR direccion ILIKE %s OR descripcion ILIKE %s LIMIT 5", (terms[0], terms[0], terms[0])),
            ("bloques", "SELECT nombre,descripcion,id_campus FROM bloques WHERE nombre ILIKE %s OR descripcion ILIKE %s LIMIT 5", (terms[0], terms[0])),
            ("instalaciones", "SELECT nombre,tipo_instalacion,piso,capacidad,id_bloque FROM instalaciones WHERE nombre ILIKE %s OR tipo_instalacion ILIKE %s LIMIT 5", (terms[0], terms[0])),
            ("personas", "SELECT nombre,correo,telefono FROM personas WHERE nombre ILIKE %s OR correo ILIKE %s LIMIT 5", (terms[0], terms[0])),
            ("materias", "SELECT nombre,creditos,descripcion FROM materias WHERE nombre ILIKE %s OR descripcion ILIKE %s LIMIT 5", (terms[0], terms[0])),
            ("programas", "SELECT nombre,tipo_programa,duracion_semestres FROM programas WHERE nombre ILIKE %s OR tipo_programa ILIKE %s LIMIT 5", (terms[0], terms[0])),
        ]

        for table_name, query, params in table_queries:
            try:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                for row in rows:
                    if isinstance(row, dict):
                        valores = ", ".join([f"{k}={row[k]}" for k in row if row[k] is not None])
                    else:
                        valores = ", ".join([str(x) for x in row if x is not None])
                    resultados.append(f"ANYWORD {table_name}: {valores}")
            except Exception as e:
                logger.warning(f"Error en ANYWORD {table_name}: {e}")

    except Exception as e:
        logger.warning(f"Error en _obtener_contexto_anyword: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

    if resultados:
        return "CONTEXTO BUSQUEDA ANYWORD (término completo):\n" + "\n".join(resultados)
    return ""


def _obtener_contexto_global(pregunta):
    """Busca el término en TODA la base de datos (full-table/full-column LIKE de todas las tablas principales)."""
    if not pregunta:
        return ""

    clue = pregunta.strip()
    if not clue:
        return ""

    resultados = []
    term = f"%{clue}%"

    try:
        conn = get_connection()
        cursor = conn.cursor()

        global_queries = [
            ("campus", "SELECT nombre,direccion,descripcion FROM campus WHERE nombre ILIKE %s OR direccion ILIKE %s OR descripcion ILIKE %s LIMIT 10", (term, term, term)),
            ("bloques", "SELECT nombre,descripcion,id_campus FROM bloques WHERE nombre ILIKE %s OR descripcion ILIKE %s LIMIT 10", (term, term)),
            ("instalaciones", "SELECT nombre,tipo_instalacion,piso,capacidad,id_bloque,id_area,id_estado FROM instalaciones WHERE nombre ILIKE %s OR tipo_instalacion ILIKE %s LIMIT 10", (term, term)),
            ("estado_instalacion", "SELECT nombre_estado,descripcion FROM estado_instalacion WHERE nombre_estado ILIKE %s OR descripcion ILIKE %s LIMIT 10", (term, term)),
            ("personas", "SELECT nombre,correo,telefono FROM personas WHERE nombre ILIKE %s OR correo ILIKE %s OR telefono ILIKE %s LIMIT 10", (term, term, term)),
            ("roles", "SELECT nombre_rol,descripcion FROM roles WHERE nombre_rol ILIKE %s OR descripcion ILIKE %s LIMIT 10", (term, term)),
            ("materias", "SELECT nombre,creditos,descripcion FROM materias WHERE nombre ILIKE %s OR descripcion ILIKE %s LIMIT 10", (term, term)),
            ("programas", "SELECT nombre,tipo_programa,duracion_semestres FROM programas WHERE nombre ILIKE %s OR tipo_programa ILIKE %s LIMIT 10", (term, term)),
            ("asignacion_instalaciones", "SELECT id_asignacion,id_instalacion,id_materia,dia_semana,hora_inicio,hora_fin,id_persona FROM asignacion_instalaciones WHERE dia_semana ILIKE %s OR CAST(id_instalacion AS TEXT) ILIKE %s OR CAST(id_materia AS TEXT) ILIKE %s OR CAST(id_persona AS TEXT) ILIKE %s LIMIT 10", (term, term, term, term)),
            ("conocimiento", "SELECT contenido FROM conocimiento WHERE contenido ILIKE %s LIMIT 10", (term,)),
        ]

        for table_name, query, params in global_queries:
            try:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                for row in rows:
                    if isinstance(row, dict):
                        values = ", ".join([f"{k}={row[k]}" for k in row if row[k] is not None])
                    else:
                        values = ", ".join([str(x) for x in row if x is not None])
                    resultados.append(f"GLOBAL {table_name}: {values}")
            except Exception as e:
                logger.warning(f"Error en GLOBAL {table_name}: {e}")

    except Exception as e:
        logger.warning(f"Error en _obtener_contexto_global: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

    if resultados:
        # Guardar extracto muy relevante en la tabla conocimiento, para enriquecer embeddings futuros
        try:
            _agregar_conocimiento_si_no_existe(f"GLOBAL: {clue}")
        except Exception:
            pass
        return "CONTEXTO GLOBAL DB (full-text):\n" + "\n".join(resultados)

    return ""


def _agregar_conocimiento_si_no_existe(contenido):
    """Inserta un contenido en la tabla conocimiento con embedding, si no existe ya."""
    if not contenido or not contenido.strip():
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM conocimiento WHERE contenido = %s LIMIT 1", (contenido,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return

        embedding_val = None
        if _modelo:
            try:
                emb = _modelo.encode(contenido)
                embedding_val = emb.tolist() if hasattr(emb, 'tolist') else list(emb)
            except Exception as e:
                logger.warning(f"No se pudo generar embedding para conocimiento: {e}")

        cursor.execute("INSERT INTO conocimiento (contenido, embedding) VALUES (%s, %s)", (contenido, embedding_val))
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("[OK] Se agregó contenido a conocimiento para futuros embeddings")
    except Exception as e:
        logger.warning(f"Error al insertar en conocimiento: {e}")


def _enriquecer_contexto_conocimiento(pregunta):
    """Complementa el contexto con búsquedas en la tabla conocimiento usando tokens clave."""
    if not pregunta:
        return ""

    tokens = _tokenizar_pregunta(pregunta)
    if not tokens:
        return ""

    filtros = " OR ".join(["contenido ILIKE %s" for _ in tokens])
    valores = [f"%{t}%" for t in tokens]
    q = f"SELECT contenido FROM conocimiento WHERE {filtros} LIMIT 5"

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(q, tuple(valores))
        rows = cursor.fetchall()
        if rows:
            contexto_rows = [row['contenido'] if isinstance(row, dict) else row[0] for row in rows]
            return "INFO DB encontrada: \n" + "\n".join(contexto_rows)
    except Exception as e:
        logger.warning(f"Error en _enriquecer_contexto_conocimiento: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

    return ""


def _obtener_contexto_fallback(pregunta):
    """
    Contexto fallback cuando los embeddings no están disponibles.
    Retorna información orientada por palabras clave en la pregunta.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Búsqueda simple por palabras clave en la tabla conocimiento
        cursor.execute("""
            SELECT contenido
            FROM conocimiento 
            WHERE contenido ILIKE %s
            LIMIT 5
        """, (f'%{pregunta}%',))

        registros = cursor.fetchall()
        if registros:
            contexto = "CONTEXTO RELEVANTE (Búsqueda por palabras clave):\n\n"
            for i, registro in enumerate(registros, 1):
                if isinstance(registro, dict):
                    contenido = registro.get('contenido', '')
                else:
                    contenido = registro[0] if registro else ''
                contexto += f"{i}. {contenido}\n\n"

            logger.info(f"[OK] Contexto fallback obtenido: {len(registros)} registros por palabras clave")
            # Enriquecer con búsqueda adicional por tokens
            enriquecido = _enriquecer_contexto_conocimiento(pregunta)
            if enriquecido:
                contexto += "\n" + enriquecido
            cursor.close()
            conn.close()
            return contexto

        logger.info("[WARN] No se encontro contexto en tabla conocimiento, usando contexto general")

        # Fallback final si no hay contexto en BD
        contexto = """CONTEXTO GENERAL DE LA BASE DE DATOS UNIVERSITARIA:

La base de datos contiene información sobre:
- Campus y Bloques: ubicaciones físicas de la universidad
- Instalaciones: aulas, laboratorios, auditorios (con capacidad y estado)
- Personas: profesores, estudiantes, administrativos
- Roles: asignaciones de funciones (profesor, estudiante, etc)
- Materias: asignaturas con créditos y descripción
- Programas: carreras académicas con duración
- Asignaciones: vincula profesores, materias, instalaciones y horarios

TABLAS PRINCIPALES:
- campus: sedes de la universidad
- bloques: edificios dentro de campus
- instalaciones: aulas, laboratorios, etc
- personas: datos de usuarios
- roles: funciones/cargos
- persona_rol: asignación de roles a personas
- materias: asignaturas
- programas: carreras
- programa_materia: relación carrera-materia
- asignacion_instalaciones: horarios y asignaciones de clases
- areas_funcionales: tipos de áreas (aula, laboratorio, etc)
- estado_instalacion: disponibilidad de espacios
- horario_instalacion: horarios de apertura/cierre
"""

        pregunta_lower = pregunta.lower()

        if any(palabra in pregunta_lower for palabra in ['profesor', 'docente', 'enseña', 'enseñan']):
            contexto += "\nRELEVANTE: Busca en personas JOIN persona_rol JOIN asignacion_instalaciones"

        if any(palabra in pregunta_lower for palabra in ['horario', 'hora', 'cuando', 'qué hora', 'que hora']):
            contexto += "\nRELEVANTE: Usa asignacion_instalaciones (dia_semana, hora_inicio, hora_fin)"

        if any(palabra in pregunta_lower for palabra in ['donde', 'dónde', 'ubicación', 'aula', 'sala', 'ubicacion']):
            contexto += "\nRELEVANTE: JOIN instalaciones > bloques > campus para ubicaciones"

        if any(palabra in pregunta_lower for palabra in ['materia', 'asignatura', 'curso', 'materias']):
            contexto += "\nRELEVANTE: Consulta tabla materias y programa_materia"

        if any(palabra in pregunta_lower for palabra in ['estudiante', 'alumno', 'estudiantes', 'alumnos']):
            contexto += "\nRELEVANTE: Busca roles como 'Estudiante' en persona_rol"

        logger.info("[WARN] Usando contexto fallback (sin BD)")

        # Enriquecer con búsqueda adicional por tokens
        enriquecido = _enriquecer_contexto_conocimiento(pregunta)
        if enriquecido:
            contexto += "\n\n" + enriquecido

        cursor.close()
        conn.close()
        return contexto

    except Exception as e:
        logger.error(f"Error en contexto fallback: {e}")
        return "Error al obtener contexto de la base de datos."


def obtener_contexto(pregunta, top_k=5):
    """
    Obtiene contexto relevante usando embeddings de la tabla conocimiento.
    Utiliza pgvector para búsqueda eficiente con embeddings reales de SentenceTransformer.
    """
    try:
        # 1) Búsqueda directa en tablas (campus/personas/materias), para evitar falta de contexto
        contexto_tablas = _obtener_contexto_tablas(pregunta)
        contexto_anyword = _obtener_contexto_anyword(pregunta)
        contexto_extra = ""
        if contexto_tablas:
            contexto_extra += contexto_tablas + "\n\n"
        if contexto_anyword:
            contexto_extra += contexto_anyword + "\n\n"

        conn = get_connection()
        cursor = conn.cursor()

        # Si SentenceTransformer está disponible, usarlo con pgvector
        if _modelo:
            try:
                embedding_pregunta = _modelo.encode(pregunta)
                embedding_lista = embedding_pregunta.tolist() if hasattr(embedding_pregunta, 'tolist') else list(embedding_pregunta)
                logger.debug(f"Embedding generado: {len(embedding_lista)} dimensiones")

                cursor.execute("""
                    SELECT contenido, embedding <=> %s::vector AS distancia
                    FROM conocimiento
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (embedding_lista, embedding_lista, top_k))

                registros = cursor.fetchall()
                if registros:
                    contexto_final = "CONTEXTO RELEVANTE DE LA BASE DE DATOS (Búsqueda semántica):\n\n"
                    for i, registro in enumerate(registros, 1):
                        contenido = registro.get('contenido') if isinstance(registro, dict) else registro[0]
                        contexto_final += f"{i}. {contenido}\n"

                    if contexto_extra:
                        contexto_final = contexto_extra + contexto_final

                    # Enriquecer con contenido de conocimientos por tokens (para robustez)
                    contexto_enriquecido = _enriquecer_contexto_conocimiento(pregunta)
                    if contexto_enriquecido:
                        contexto_final += "\n" + contexto_enriquecido

                    cursor.close()
                    conn.close()
                    logger.info(f"[OK] Contexto obtenido con pgvector: {len(registros)} registros relevantes")
                    return contexto_final

                logger.warning("No hay registros en tabla conocimiento con pgvector")

            except Exception as e:
                logger.error(f"Error usando pgvector: {type(e).__name__}: {str(e)}. Usando fallback...")
                try:
                    cursor.close()
                    conn.close()
                except:
                    pass

        # Fallback de búsqueda directa por texto en conocimiento
        if contexto_extra:
            # aun si no hay resultados pgvector, mantenemos contexto_tablas previo
            contexto_extra += "\n"

        contexto_fallback = _obtener_contexto_fallback(pregunta)
        if contexto_fallback:
            return contexto_extra + contexto_fallback

        contexto_global = _obtener_contexto_global(pregunta)
        if contexto_global:
            return contexto_extra + contexto_global

        return contexto_extra or ""

    except Exception as e:
        logger.error(f"Error obteniendo contexto: {e}")
        return _obtener_contexto_fallback(pregunta)


def _obtener_contexto_fallback(pregunta):
    """
    Contexto fallback cuando los embeddings no están disponibles.
    Retorna información orientada por palabras clave en la pregunta.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Búsqueda simple por palabras clave en la tabla conocimiento
        cursor.execute("""
            SELECT contenido
            FROM conocimiento 
            WHERE contenido ILIKE %s
            LIMIT 5
        """, (f'%{pregunta}%',))
        
        registros = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if registros:
            contexto = "CONTEXTO RELEVANTE (Búsqueda por palabras clave):\n\n"
            for i, registro in enumerate(registros, 1):
                # Manejar tanto diccionarios como tuplas
                if isinstance(registro, dict):
                    contenido = registro.get('contenido', '')
                else:
                    contenido = registro[0] if registro else ''
                contexto += f"{i}. {contenido}\n\n"
            logger.info(f"[OK] Contexto fallback obtenido: {len(registros)} registros por palabras clave")
            return contexto
        
        logger.info("[WARN] No se encontro contexto en tabla conocimiento, usando contexto general")
        
        # Fallback final si no hay contexto en BD
        contexto = """CONTEXTO GENERAL DE LA BASE DE DATOS UNIVERSITARIA:

La base de datos contiene información sobre:
- Campus y Bloques: ubicaciones físicas de la universidad
- Instalaciones: aulas, laboratorios, auditorios (con capacidad y estado)
- Personas: profesores, estudiantes, administrativos
- Roles: asignaciones de funciones (profesor, estudiante, etc)
- Materias: asignaturas con créditos y descripción
- Programas: carreras académicas con duración
- Asignaciones: vincula profesores, materias, instalaciones y horarios

TABLAS PRINCIPALES:
- campus: sedes de la universidad
- bloques: edificios dentro de campus
- instalaciones: aulas, laboratorios, etc
- personas: datos de usuarios
- roles: funciones/cargos
- persona_rol: asignación de roles a personas
- materias: asignaturas
- programas: carreras
- programa_materia: relación carrera-materia
- asignacion_instalaciones: horarios y asignaciones de clases
- areas_funcionales: tipos de áreas (aula, laboratorio, etc)
- estado_instalacion: disponibilidad de espacios
- horario_instalacion: horarios de apertura/cierre
"""
        
        # Mejoras según la pregunta
        pregunta_lower = pregunta.lower()
        
        if any(palabra in pregunta_lower for palabra in ['profesor', 'docente', 'enseña', 'enseñan']):
            contexto += "\nRELEVANTE: Busca en personas JOIN persona_rol JOIN asignacion_instalaciones"
        
        if any(palabra in pregunta_lower for palabra in ['horario', 'hora', 'cuando', 'qué hora', 'que hora']):
            contexto += "\nRELEVANTE: Usa asignacion_instalaciones (dia_semana, hora_inicio, hora_fin)"
        
        if any(palabra in pregunta_lower for palabra in ['donde', 'dónde', 'ubicación', 'aula', 'sala', 'ubicacion']):
            contexto += "\nRELEVANTE: JOIN instalaciones > bloques > campus para ubicaciones"
        
        if any(palabra in pregunta_lower for palabra in ['materia', 'asignatura', 'curso', 'materias']):
            contexto += "\nRELEVANTE: Consulta tabla materias y programa_materia"
        
        if any(palabra in pregunta_lower for palabra in ['estudiante', 'alumno', 'estudiantes', 'alumnos']):
            contexto += "\nRELEVANTE: Busca roles como 'Estudiante' en persona_rol"
        
        logger.info("[WARN] Usando contexto fallback (sin BD)")
        return contexto
        
    except Exception as e:
        logger.error(f"Error en contexto fallback: {e}")
        return "Error al obtener contexto de la base de datos."