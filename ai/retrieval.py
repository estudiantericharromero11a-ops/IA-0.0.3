import logging
from sentence_transformers import SentenceTransformer
from database.queries import get_connection

logger = logging.getLogger(__name__)

# Cargar modelo UNA SOLA VEZ (al inicio del módulo)
try:
    _modelo = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("[OK] Modelo SentenceTransformer cargado correctamente")
except Exception as e:
    logger.warning(f"[WARN] No se pudo cargar modelo SentenceTransformer: {e}")
    _modelo = None


def obtener_contexto(pregunta, top_k=5):
    """
    Obtiene contexto relevante usando embeddings de la tabla conocimiento.
    Utiliza pgvector para búsqueda eficiente con embeddings reales de SentenceTransformer.
    
    Args:
        pregunta (str): Pregunta del usuario
        top_k (int): Número de resultados a retornar
    
    Returns:
        str: Contexto formateado con los registros relevantes
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Si SentenceTransformer está disponible, usarlo con pgvector
        if _modelo:
            try:
                # Generar embedding de la pregunta con el MISMO modelo que en poblado_conocimiento.py
                embedding_pregunta = _modelo.encode(pregunta)
                # Convertir numpy array a lista para que psycopg pueda adaptarlo
                embedding_lista = embedding_pregunta.tolist() if hasattr(embedding_pregunta, 'tolist') else list(embedding_pregunta)
                logger.debug(f"Embedding generado: {len(embedding_lista)} dimensiones")
                
                # Usar pgvector para búsqueda eficiente en PostgreSQL
                # El operador <=> calcula la distancia coseno
                # psycopg necesita el vector como lista para adaptarlo correctamente
                cursor.execute("""
                    SELECT contenido, embedding <=> %s::vector AS distancia
                    FROM conocimiento
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (embedding_lista, embedding_lista, top_k))
                
                registros = cursor.fetchall()
                
                if not registros:
                    logger.warning("No hay registros en tabla conocimiento con pgvector")
                    return _obtener_contexto_fallback(pregunta)
                
                # Construir contexto con pgvector
                contexto_final = "CONTEXTO RELEVANTE DE LA BASE DE DATOS (Búsqueda semántica):\n\n"
                for i, registro in enumerate(registros, 1):
                    # psycopg3 con dict_row retorna diccionarios, no tuplas
                    contenido = registro.get('contenido') if isinstance(registro, dict) else registro[0]
                    distancia = registro.get('distancia') if isinstance(registro, dict) else registro[1]
                    if distancia is not None:
                        similaridad = 1 - distancia  # Convertir distancia a similaridad
                    contexto_final += f"{i}. {contenido}\n"
                
                logger.info(f"[OK] Contexto obtenido con pgvector: {len(registros)} registros relevantes")
                cursor.close()
                conn.close()
                return contexto_final
                
            except Exception as e:
                logger.error(f"Error usando pgvector: {type(e).__name__}: {str(e)}. Usando fallback...")
                try:
                    cursor.close()
                    conn.close()
                except:
                    pass
        
        # Fallback: búsqueda por palabras clave (simple, sin embeddings)
        try:
            cursor.close()
            conn.close()
        except:
            pass
        return _obtener_contexto_fallback(pregunta)
        
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