import re
import logging
from ai.retrieval import obtener_contexto
from ai.llm import llamar_llm
from ai.prompts_optimizados import prompt_sql
from ai.config_ia import PALABRAS_CLAVE_IA, PALABRAS_EXACTAS_IA
from database.queries import get_connection, ejecutar_query


def _obtener_contexto_exacto(pregunta):
    """Chequeo de coincidencia directa en tablas (campus/personas/materias)."""
    if not pregunta:
        return ""

    tokens = [t for t in re.findall(r"\b\w{3,}\b", pregunta.lower())]
    if not tokens:
        return ""

    contexto_list = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        for token in tokens[:6]:
            # Campus
            like_token = f"%{token}%"
            cursor.execute(
                "SELECT nombre, direccion, descripcion FROM campus WHERE nombre ILIKE %s OR descripcion ILIKE %s LIMIT 1",
                (like_token, like_token)
            )
            campus_row = cursor.fetchone()
            if campus_row:
                contexto_list.append(f"Campus encontrado: {campus_row['nombre']} - {campus_row.get('direccion')} - {campus_row.get('descripcion')}")

            # Materia
            cursor.execute(
                "SELECT nombre, descripcion FROM materias WHERE nombre ILIKE %s OR descripcion ILIKE %s LIMIT 1",
                (like_token, like_token)
            )
            materia_row = cursor.fetchone()
            if materia_row:
                contexto_list.append(f"Materia encontrada: {materia_row['nombre']} - {materia_row.get('descripcion')}")

            # Profesor
            cursor.execute(
                "SELECT p.nombre, r.nombre_rol FROM personas p "
                "JOIN persona_rol pr ON p.id_persona = pr.id_persona "
                "JOIN roles r ON pr.id_rol = r.id_rol "
                "WHERE p.nombre ILIKE %s AND LOWER(r.nombre_rol) IN ('profesor','docente','instructor','catedratico','catedrático') LIMIT 1",
                (like_token,)
            )
            profesor_row = cursor.fetchone()
            if profesor_row:
                contexto_list.append(f"Profesor encontrado: {profesor_row['nombre']} (rol: {profesor_row['nombre_rol']})")

            if len(contexto_list) >= 3:
                break

    except Exception as e:
        logger.warning(f"Error en _obtener_contexto_exacto: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

    return "\n".join(contexto_list)


def _extraer_sql_posible(text):
    """Extrae la primera query SELECT válida de un texto libre (respuesta LLM)."""
    if not text:
        return None

    # Si ya empieza con SELECT, usarlo directamente
    if re.match(r"^\s*SELECT\s", text, re.IGNORECASE):
        return text.strip()

    # Buscar la primera query SELECT ... (hasta ';' o final) si hace match
    match = re.search(r"(SELECT\s+.*?)(?:;|$)", text, re.IGNORECASE | re.DOTALL)
    if match:
        candidate = match.group(1).strip()
        if re.match(r"^SELECT\s", candidate, re.IGNORECASE):
            return candidate
    return None


def _es_sql_valida(sql):
    return bool(re.match(r"^\s*SELECT\s+", sql, re.IGNORECASE))


def _convertir_comparacion_nombre_a_ilike(sql):
    """Convierte comparaciones exactas de campos *.nombre a comparaciones ILIKE con comodines.

    Mejora la robustez de consultas generadas por el LLM cuando se usan nombres parciales o alias.
    Ejemplo: "c.nombre = 'CUL'" -> "c.nombre ILIKE '%CUL%'".
    """
    import re

    def reemplazo(match):
        campo = match.group(1)
        valor = match.group(2).strip()

        # Mantener si ya hay comodines o valor vacío
        if not valor or '%' in valor:
            return match.group(0)

        return f"{campo} ILIKE '%{valor}%'"

    # Columnas comunes que contienen nombres descriptivos en la base de datos
    pattern = re.compile(
        r"\b((?:c|b|i|p|m|pr|r)\.nombre)\s*=\s*['\"]([^'\"]+)['\"]",
        re.IGNORECASE
    )

    sql_nuevo = pattern.sub(reemplazo, sql)
    if sql != sql_nuevo:
        logging.getLogger(__name__).info(f"Ajuste de comparación exacta a ILIKE: '{sql}' -> '{sql_nuevo}'")
    return sql_nuevo

logger = logging.getLogger(__name__)


def _heuristica_sql_simple(pregunta):
    """Reglas de opción rápida para queries comunes y combinadas."""
    pregunta_lower = pregunta.lower()

    tiene_profesor = any(k in pregunta_lower for k in [
        'profesor', 'docente', 'instructor', 'catedrático', 'catedratico'
    ])
    tiene_capacidad_total = any(k in pregunta_lower for k in [
        'capacidad total', 'capacidad de la universidad', 'capacidad general', 'capacidad', 'espacio'
    ])
    tiene_materia = any(k in pregunta_lower for k in [
        'materia', 'asignatura', 'curso', 'clase', 'matematicas', 'matematica', 'fisica', 'quimica', 'biologia', 'historia', 'literatura'
    ])
    tiene_programa = any(k in pregunta_lower for k in [
        'programa', 'carrera', 'ingenieria', 'medicina', 'derecho', 'pregrado', 'postgrado', 'tecnologo', 'tecnico'
    ])
    tiene_horario = any(k in pregunta_lower for k in [
        'lunes', 'martes', 'miércoles', 'miercoles', 'jueves', 'viernes', 'sabado', 'sábado', 'domingo',
        'horario', 'dia', 'día', 'clases', 'semana'
    ])
    tiene_correo = any(k in pregunta_lower for k in [
        'correo', 'email', 'contacto', 'telefono', 'teléfono', 'dato de contacto', 'datos de contacto'
    ])
    tiene_aula = any(k in pregunta_lower for k in ['aula', 'laboratorio', 'oficina'])
    tiene_ubicacion = any(k in pregunta_lower for k in ['dónde', 'donde', 'Ubicación'.lower(), 'ubicación', 'ubicacion', 'piso', 'campus'])
    
    # ⭐ NUEVA DETECCIÓN: Preguntas sobre "MÁS" (estadísticas con agregación)
    tiene_mas = any(k in pregunta_lower for k in ['mas', 'más', 'mayor', 'máximo', 'máxima', 'maximo', 'maxima', 'cuantos'])
    tiene_horas = any(k in pregunta_lower for k in ['horas', 'hora', 'tiempo', 'duración', 'duracion'])

    # ⭐ CASO NUEVO: "Profesor con más horas de clase"
    if tiene_profesor and tiene_horas and tiene_mas:
        return (
            "SELECT "
            "p.nombre AS profesor, "
            "COUNT(DISTINCT a.id_asignacion) AS num_clases, "
            "SUM(EXTRACT(EPOCH FROM (a.hora_fin - a.hora_inicio))/3600)::DECIMAL AS horas_totales "
            "FROM asignacion_instalaciones a "
            "INNER JOIN personas p ON a.id_persona = p.id_persona "
            "GROUP BY p.id_persona, p.nombre "
            "ORDER BY horas_totales DESC "
            "LIMIT 1"
        )

    # NUEVA HEURÍSTICA: Listar solo nombres de profesores
    if ('nombres' in pregunta_lower and 'solo' in pregunta_lower) or (tiene_profesor and ('nombres' in pregunta_lower or 'lista' in pregunta_lower or 'quienes' in pregunta_lower)):
        return (
            "SELECT DISTINCT p.nombre "
            "FROM personas p "
            "INNER JOIN persona_rol pr ON p.id_persona = pr.id_persona "
            "INNER JOIN roles r ON pr.id_rol = r.id_rol "
            "WHERE LOWER(r.nombre_rol) IN ('profesor', 'docente', 'instructor', 'catedratico', 'catedrático') "
            "LIMIT 100"
        )

    if tiene_aula and (tiene_ubicacion or tiene_capacidad_total or 'capacidad' in pregunta_lower):
        # Extraer número o identificador de aula/laboratorio/oficina si existe
        match = re.search(r"(aula|laboratorio|oficina)\s*([0-9]+)", pregunta_lower)
        filtro_instalacion = ""
        if match:
            tipo = match.group(1)
            numero = match.group(2)
            filtro_instalacion = f"i.nombre ILIKE '%{tipo.capitalize()} {numero}%'"
        elif 'aula' in pregunta_lower:
            filtro_instalacion = "i.nombre ILIKE '%aula%'"
        elif 'laboratorio' in pregunta_lower:
            filtro_instalacion = "i.nombre ILIKE '%laboratorio%'"
        elif 'oficina' in pregunta_lower:
            filtro_instalacion = "i.nombre ILIKE '%oficina%'"

        if filtro_instalacion:
            return (
                "SELECT i.nombre, i.piso, i.capacidad, i.tipo_instalacion, b.nombre AS bloque, c.nombre AS campus, "
                "af.nombre_area, ei.nombre_estado "
                "FROM instalaciones i "
                "LEFT JOIN bloques b ON i.id_bloque = b.id_bloque "
                "LEFT JOIN campus c ON b.id_campus = c.id_campus "
                "LEFT JOIN areas_funcionales af ON i.id_area = af.id_area "
                "LEFT JOIN estado_instalacion ei ON i.id_estado = ei.id_estado "
                f"WHERE {filtro_instalacion} LIMIT 100"
            )

    # Consulta detallada multi-tabla para respuestas ricas de módulos
    if tiene_profesor and tiene_materia:
        # Extraer nombres específicos de profesor y materia si están mencionados
        nombre_profesor = None
        nombre_materia = None
        
        # Buscar patrón "profesor [Nombre]" o "[Nombre] profesor"
        match_prof = re.search(r'profesor\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', pregunta, re.IGNORECASE)
        if match_prof:
            nombre_profesor = match_prof.group(1).strip()
        
        # Buscar materia específica mencionada
        for materia_comun in ['matemáticas', 'matematicas', 'física', 'fisica', 'química', 'quimica', 'biología', 'biologia', 'historia', 'literatura', 'programación', 'programacion']:
            if materia_comun in pregunta_lower:
                nombre_materia = materia_comun
                break
        
        # Construir filtros
        filtros = []
        if nombre_profesor:
            filtros.append(f"p.nombre ILIKE '%{nombre_profesor}%'")
        if nombre_materia:
            filtros.append(f"m.nombre ILIKE '%{nombre_materia}%'")
        
        filtro_where = " AND ".join(filtros) if filtros else ""
        if filtro_where:
            filtro_where = f"WHERE {filtro_where}"
        
        return (
            "SELECT "
            "p.nombre AS profesor, m.nombre AS materia, i.nombre AS instalacion, i.tipo_instalacion, i.capacidad, "
            "b.nombre AS bloque, c.nombre AS campus, af.nombre_area, ei.nombre_estado, "
            "a.dia_semana, a.hora_inicio, a.hora_fin "
            "FROM asignacion_instalaciones a "
            "LEFT JOIN personas p ON a.id_persona = p.id_persona "
            "LEFT JOIN materias m ON a.id_materia = m.id_materia "
            "LEFT JOIN instalaciones i ON a.id_instalacion = i.id_instalacion "
            "LEFT JOIN bloques b ON i.id_bloque = b.id_bloque "
            "LEFT JOIN campus c ON b.id_campus = c.id_campus "
            "LEFT JOIN areas_funcionales af ON i.id_area = af.id_area "
            "LEFT JOIN estado_instalacion ei ON i.id_estado = ei.id_estado "
            f"{filtro_where} LIMIT 100"
        )

    if 'asignacion_instalaciones' in pregunta_lower or tiene_horario:
        return (
            "SELECT "
            "p.nombre AS profesor, m.nombre AS materia, i.nombre AS instalacion, i.tipo_instalacion, i.capacidad, "
            "b.nombre AS bloque, c.nombre AS campus, af.nombre_area, ei.nombre_estado, "
            "a.dia_semana, a.hora_inicio, a.hora_fin "
            "FROM asignacion_instalaciones a "
            "LEFT JOIN personas p ON a.id_persona = p.id_persona "
            "LEFT JOIN materias m ON a.id_materia = m.id_materia "
            "LEFT JOIN instalaciones i ON a.id_instalacion = i.id_instalacion "
            "LEFT JOIN bloques b ON i.id_bloque = b.id_bloque "
            "LEFT JOIN campus c ON b.id_campus = c.id_campus "
            "LEFT JOIN areas_funcionales af ON i.id_area = af.id_area "
            "LEFT JOIN estado_instalacion ei ON i.id_estado = ei.id_estado "
            "LIMIT 100"
        )

    # FIX Q14: Materias en programa + profesor que las dicta
    if tiene_programa:
        return (
            "SELECT "
            "pr.nombre AS programa, pr.tipo_programa, pr.duracion_semestres AS duracion_semestres, "
            "COUNT(pm.id_materia) AS cantidad_materias, "
            "STRING_AGG(DISTINCT m.nombre, ', ') AS materias "
            "FROM programas pr "
            "LEFT JOIN programa_materia pm ON pr.id_programa = pm.id_programa "
            "LEFT JOIN materias m ON pm.id_materia = m.id_materia "
            "GROUP BY pr.id_programa, pr.nombre, pr.tipo_programa, pr.duracion_semestres "
            "LIMIT 100"
        )

    if tiene_profesor and tiene_capacidad_total:
        return (
            "SELECT "
            "(SELECT STRING_AGG(DISTINCT p.nombre, ', ') "
            "FROM personas p "
            "INNER JOIN persona_rol pr ON p.id_persona = pr.id_persona "
            "INNER JOIN roles r ON pr.id_rol = r.id_rol "
            "WHERE LOWER(r.nombre_rol) IN ('profesor', 'docente', 'instructor', 'catedratico', 'catedrático')) AS profesores, "
            "(SELECT SUM(capacidad) FROM instalaciones) AS capacidad_total"
        )

    if tiene_profesor and tiene_horario:
        # Pregunta de horario o día de clases de profesor
        dia_clave = None
        for dia in ['lunes', 'martes', 'miércoles', 'miercoles', 'jueves', 'viernes', 'sabado', 'sábado', 'domingo']:
            if dia in pregunta_lower:
                dia_clave = dia
                break

        filtro_dia = f"AND LOWER(a.dia_semana) ILIKE LOWER('{dia_clave}')" if dia_clave else ""
        
        # Si pregunta por correo, incluirlo
        campo_contacto = ", p.correo, p.telefono" if tiene_correo else ""
        
        return (
            f"SELECT DISTINCT p.nombre{campo_contacto}, m.nombre AS materia, i.nombre AS instalacion, "
            "a.dia_semana, a.hora_inicio, a.hora_fin, b.nombre AS bloque, c.nombre AS campus "
            "FROM personas p "
            "INNER JOIN asignacion_instalaciones a ON p.id_persona = a.id_persona "
            "INNER JOIN persona_rol pr ON p.id_persona = pr.id_persona "
            "INNER JOIN roles r ON pr.id_rol = r.id_rol "
            "LEFT JOIN materias m ON a.id_materia = m.id_materia "
            "LEFT JOIN instalaciones i ON a.id_instalacion = i.id_instalacion "
            "LEFT JOIN bloques b ON i.id_bloque = b.id_bloque "
            "LEFT JOIN campus c ON b.id_campus = c.id_campus "
            "WHERE LOWER(r.nombre_rol) IN ('profesor', 'docente', 'instructor', 'catedratico', 'catedrático') "
            f"{filtro_dia} LIMIT 100"
        )

    if tiene_capacidad_total:
        return "SELECT SUM(capacidad) AS capacidad_total FROM instalaciones"

    if tiene_profesor:
        # Si pregunta por correo/email, incluir esos campos
        if tiene_correo:
            return (
                "SELECT DISTINCT p.nombre, p.correo, p.telefono "
                "FROM personas p "
                "INNER JOIN persona_rol pr ON p.id_persona = pr.id_persona "
                "INNER JOIN roles r ON pr.id_rol = r.id_rol "
                "WHERE LOWER(r.nombre_rol) IN ('profesor', 'docente', 'instructor', 'catedratico', 'catedrático') "
                "LIMIT 100"
            )
        else:
            return (
                "SELECT DISTINCT p.nombre "
                "FROM personas p "
                "INNER JOIN persona_rol pr ON p.id_persona = pr.id_persona "
                "INNER JOIN roles r ON pr.id_rol = r.id_rol "
                "WHERE LOWER(r.nombre_rol) IN ('profesor', 'docente', 'instructor', 'catedratico', 'catedrático') "
                "LIMIT 100"
            )

    # Preguntas genéricas sobre correo/contacto sin rol específico
    if tiene_correo:
        return (
            "SELECT DISTINCT p.nombre, p.correo, p.telefono "
            "FROM personas p "
            "LIMIT 100"
        )

    return None


def generar_sql(pregunta):
    """
    Genera SQL a partir de una pregunta en lenguaje natural.
    - Detecta preguntas sobre el sistema (no genera SQL)
    - Valida complejidad de SQL
    - Si es demasiado compleja, reintenta con prompt simplificado
    """
    logger.info(f"Generando SQL para pregunta: {pregunta}")
    
    # Verificar si es pregunta acerca del asistente del sistema
    pregunta_lower = pregunta.lower()
    
    # Cambiar detección a frases completas primero
    if any(phrase in pregunta_lower for phrase in PALABRAS_CLAVE_IA):
        logger.info(f"Pregunta sobre el sistema detectada (frase exacta): {pregunta}")
        return None  # No generar SQL para preguntas sobre el sistema
    
    # Buscar palabras exactas (no como substring)
    for palabra in PALABRAS_EXACTAS_IA:
        if re.search(rf'\b{palabra}\b', pregunta_lower):
            logger.info(f"Pregunta sobre THANIA detectada (palabra exacta: {palabra}): {pregunta}")
            return None

    # Reglas heurísticas para casos comunes sin pasar por LLM
    sql_heuristica = _heuristica_sql_simple(pregunta)
    prompt = None
    if sql_heuristica:
        logger.info(f"SQL heurística aplicado: {sql_heuristica}")
        sql = sql_heuristica
    else:
        # Capa de "exact-match context" antes de generar SQL
        contexto_exacto = _obtener_contexto_exacto(pregunta)

        # Obtener contexto de embeddings y tablas (RAG)
        contexto = obtener_contexto(pregunta)
        if contexto_exacto:
            contexto = f"{contexto_exacto}\n\n{contexto}" if contexto else contexto_exacto

        # Crear prompt para Ollama
        prompt = prompt_sql(contexto, pregunta)

        # Llamar Ollama para generar SQL
        sql = llamar_llm(prompt).strip()

        # Si Ollama devuelve un mensaje de error, aplicar fallback inmediato
        if sql.lower().startswith("error:"):
            logger.warning(f"Ollama retornó error en texto: {sql}")
            fallback_sql = _heuristica_sql_simple(pregunta)
            if fallback_sql:
                logger.info(f"SQL fallback heurístico aplicado: {fallback_sql}")
                sql = fallback_sql
            else:
                if 'capacidad' in pregunta.lower() or 'espacio' in pregunta.lower():
                    sql = "SELECT SUM(capacidad) AS capacidad_total FROM instalaciones"
                    logger.info("SQL fallback genérico: capacidad total")
                else:
                    sql = "SELECT DISTINCT p.nombre FROM personas p LIMIT 20"
                    logger.info("SQL fallback genérico: lista de personas")

    # Validar respuesta de Ollama
    if sql.strip().lower().startswith("error:"):
        # En caso extremo, aplicar fallback de seguridad no interrompible
        logger.error(f"SQL aún contiene error tras los intentos: {sql}. Aplicando fallback seguro.")
        sql = "SELECT DISTINCT p.nombre FROM personas p LIMIT 20"
        logger.info("SQL fallback seguro aplicado: lista de personas")
    
    # Limpiar SQL envuelto en backticks markdown (```sql ... ```)
    sql = _limpiar_markdown_sql(sql)

    # Si la respuesta LLM es texto y contiene un SELECT dentro, extraerlo
    extraido = _extraer_sql_posible(sql)
    if extraido:
        sql = extraido

    # Ajustar comparaciones exactas de nombre a consultas más tolerantes
    sql = _convertir_comparacion_nombre_a_ilike(sql)

    if not _es_sql_valida(sql):
        # Intentar heurístico adicional antes de fallar
        logger.warning(f"SQL no válida tras limpieza: {sql[:80]}...")
        sql_heuristica2 = _heuristica_sql_simple(pregunta)
        if sql_heuristica2:
            logger.info(f"SQL heurística alterna aplicada: {sql_heuristica2}")
            sql = sql_heuristica2
        else:
            raise Exception(f"No se pudo generar SQL válido: {sql[:120]}")

    # FIX Q10 y Q14: corregir comparaciones TIME y validar parámetros
    sql = _corregir_comparaciones_time(sql)
    try:
        _validar_no_parametros(sql)
    except Exception as e:
        logger.warning(f"[WARNING] Validación de parámetros falló: {e}. Intentando fallback heurístico.")
        # Si la heurística ya existe y es distinta, usarla; sino usar fallback seguro
        heuristica = _heuristica_sql_simple(pregunta)
        if heuristica and heuristica != sql:
            logger.info(f"Aplicando fallback heurístico SQL: {heuristica}")
            sql = heuristica
        else:
            sql = "SELECT DISTINCT p.nombre, p.correo, p.telefono FROM personas p LIMIT 100"
            logger.info("Aplicando fallback genérico SQL de contacto")
        _validar_no_parametros(sql)

    # Forzar comparación de roles case-insensitive
    # Convertir r.nombre_rol a LOWER(r.nombre_rol) para evitar problemas mayúsculas/minúsculas
    sql = re.sub(r"(?<!LOWER\()\br\.nombre_rol\b(?!\))", "LOWER(r.nombre_rol)", sql, flags=re.IGNORECASE)
    sql = re.sub(r"(?<!LOWER\()\broles\.nombre_rol\b(?!\))", "LOWER(roles.nombre_rol)", sql, flags=re.IGNORECASE)

    # Si se compara con literal, normalizar el literal a minusculas tambien
    sql = re.sub(
        r"LOWER\((?P<alias>r|roles)\.nombre_rol\)\s*=\s*'([^']*)'",
        lambda m: f"LOWER({m.group('alias')}.nombre_rol) = '{m.group(2).lower()}'",
        sql,
        flags=re.IGNORECASE,
    )

    # Validación básica: solo SELECT, no operaciones peligrosas
    if not re.match(r"^\s*SELECT\s+", sql, re.IGNORECASE):
        logger.error(f"SQL no válido (no es SELECT): {sql}")
        raise Exception(f"SQL generado no es SELECT: {sql[:100]}")
    
    if re.search(r"\b(DROP|DELETE|UPDATE|INSERT)\b", sql, re.IGNORECASE):
        logger.error(f"SQL contiene operación peligrosa: {sql}")
        raise Exception(f"SQL contiene operación no permitida: {sql[:100]}")
    
    # Validar complejidad SQL - si es demasiado compleja, puede ser incorrecta
    problema_complejidad = _validar_complejidad_sql(sql)
    if problema_complejidad:
        logger.warning(f"SQL demasiado compleja: {problema_complejidad}. Reintentando con prompt simplificado...")
        if prompt:
            # Reintentrar con un prompt que fuerce simpleza
            prompt_forzar_simple = prompt + "\n\n[IMPORTANTE: La respuesta anterior era demasiado complicada. Genera una query MÁS SIMPLE.]"
            try:
                sql = llamar_llm(prompt_forzar_simple).strip()
                sql = _limpiar_markdown_sql(sql)
                logger.info(f"SQL reintentado (simplificado): {sql[:80]}...")
            except Exception as e:
                logger.warning(f"Ollama falló en reintento de complejidad: {e}. Manteniendo SQL actual.")
        else:
            logger.warning("No existe prompt para reintentar con LLM; se mantiene SQL heurístico.")

    
    # ✅ FIX #6: Agregar LIMIT automático si no existe
    from ai.config_ia import MAX_FILAS_RESULTADO
    
    # Limpiar punto y coma si existe
    sql = sql.rstrip(';').strip()

    # ✅ Corregir mapeos comunes de columna de roles
    if re.search(r"\bFROM\s+roles\s+r\b", sql, re.IGNORECASE) and re.search(r"\br\.nombre\b", sql, re.IGNORECASE):
        logger.warning("Ajustando columa de roles: 'r.nombre' -> 'r.nombre_rol'")
        sql = re.sub(r"\br\.nombre\b", "r.nombre_rol", sql, flags=re.IGNORECASE)

    if 'LIMIT' not in sql.upper():
        sql = f"{sql} LIMIT {MAX_FILAS_RESULTADO}"
        logger.info(f"LIMIT automático agregado: {MAX_FILAS_RESULTADO}")
    
    logger.info(f"SQL generado correctamente: {sql[:80]}...")
    return sql


def _validar_complejidad_sql(sql):
    """
    Detecta SQL innecesariamente compleja que probablemente sea incorrecta.
    Retorna descripción del problema o None si está bien.
    """
    sql_upper = sql.upper()
    
    # Contar JOINs
    join_count = len(re.findall(r'\bJOIN\b', sql_upper))
    if join_count > 4:
        return f"{join_count} JOINs (probablemente innecesario)"
    
    # Detectar self-joins complicados (a, a2, a3...)
    alias_pattern = re.findall(r'\ba\d+\b', sql_upper)
    if len(alias_pattern) > 2:
        return f"Self-join complejo detectado: {', '.join(set(alias_pattern))}"
    
    # Detectar self-join simple (a ... a2)
    if re.search(r'FROM\s+\w+\s+a\s+(.*?)JOIN\s+\w+\s+a2', sql_upper):
        # Es un self-join - podría estar mal
        return "Self-join detectado (posiblemente incorrecto)"
    
    # Contar condiciones en WHERE (si hay más de 5, probablemente sea complejo)
    where_match = re.search(r'WHERE\s+(.*?)(?:ORDER BY|;|$)', sql_upper)
    if where_match:
        where_clause = where_match.group(1)
        and_count = len(re.findall(r'\bAND\b', where_clause))
        or_count = len(re.findall(r'\bOR\b', where_clause))
        if and_count + or_count > 8:
            return f"WHERE muy complejo: {and_count} AND, {or_count} OR"
    
    # Si llegó aquí, SQL es aceptable
    return None





def _corregir_comparaciones_time(sql):
    """
    FIX Q10: Corrige comparaciones LIKE en campos TIME que causan error en PostgreSQL.
    Convierte LIKE en campos TIME a comparaciones apropiadas (>=, <=, BETWEEN).
    """
    import re

    # Patrón para detectar LIKE en campos TIME
    # Busca patrones como: hora_inicio LIKE '%08%', Sistema.hora_inicio LIKE '08%'
    time_like_pattern = re.compile(
        r'(\w+\.hora_\w+|hora_\w+)\s+LIKE\s+[\'"]([^\'"]*)[\'"]',
        re.IGNORECASE
    )

    def reemplazar_time_like(match):
        campo = match.group(1)
        patron = match.group(2)

        # Limpiar el patrón (quitar % si existen)
        patron_limpio = patron.strip('%')

        try:
            # Intentar parsear como hora (HH:MM o HH:MM:SS)
            if ':' in patron_limpio:
                # Es un patrón de hora completo
                partes = patron_limpio.split(':')
                if len(partes) >= 2:
                    hora = int(partes[0])
                    minuto = int(partes[1])

                    # Si el patrón original tenía %, hacer comparación de rango
                    if patron.startswith('%') and patron.endswith('%'):
                        # Contiene la hora (cualquier hora que contenga estos dígitos)
                        return f"EXTRACT(HOUR FROM {campo}) = {hora} AND EXTRACT(MINUTE FROM {campo}) = {minuto}"
                    elif patron.startswith('%'):
                        # Termina con esta hora
                        return f"{campo}::time <= '{hora:02d}:{minuto:02d}'::time"
                    elif patron.endswith('%'):
                        # Empieza con esta hora
                        return f"{campo}::time >= '{hora:02d}:{minuto:02d}'::time"
                    else:
                        # Exact match
                        return f"{campo}::time = '{hora:02d}:{minuto:02d}'::time"
            else:
                # Es solo hora (número)
                hora = int(patron_limpio)
                if patron.startswith('%') and patron.endswith('%'):
                    return f"EXTRACT(HOUR FROM {campo}) = {hora}"
                elif patron.startswith('%'):
                    return f"EXTRACT(HOUR FROM {campo}) <= {hora}"
                elif patron.endswith('%'):
                    return f"EXTRACT(HOUR FROM {campo}) >= {hora}"
                else:
                    return f"EXTRACT(HOUR FROM {campo}) = {hora}"

        except (ValueError, IndexError):
            # Si no se puede parsear, mantener como está pero loggear
            logger.warning(f"No se pudo parsear patrón TIME: {patron} en campo {campo}")
            return match.group(0)

    # Aplicar correcciones
    sql_corregido = time_like_pattern.sub(reemplazar_time_like, sql)

    if sql != sql_corregido:
        logger.info(f"SQL TIME corregido: '{sql}' → '{sql_corregido}'")

    return sql_corregido


def _validar_no_parametros(sql):
    """
    FIX Q14: Valida que no haya parámetros sin asignar en el SQL.
    Detecta placeholders como ?, <nombre>, [valor], etc.
    """
    import re

    errores = []

    # 1. Detectar placeholders de interrogación (?)
    if '?' in sql:
        # Verificar si es un placeholder real (no parte de operadores como >=, <=, !=)
        # Contar ? que no están en contextos de operadores
        placeholders = re.findall(r'(?<![\>\<\!\=])\?(?![\>\<\!\=])', sql)
        if placeholders:
            errores.append(f"Contiene {len(placeholders)} placeholder(s) '?' sin valor")

    # 2. Detectar placeholders con <> (ej: <id_persona>, <nombre>)
    angle_brackets = re.findall(r'<\w+>', sql)
    if angle_brackets:
        errores.append(f"Contiene placeholders <>: {', '.join(angle_brackets)}")

    # 3. Detectar placeholders con [] (ej: [valor], [id])
    square_brackets = re.findall(r'\[\w+\]', sql)
    if square_brackets:
        errores.append(f"Contiene placeholders []: {', '.join(square_brackets)}")

    # 4. Detectar variables SQL sin asignar (ej: $1, $2)
    dollar_vars = re.findall(r'\$\d+', sql)
    if dollar_vars:
        errores.append(f"Contiene variables SQL sin asignar: {', '.join(dollar_vars)}")

    # 5. Detectar placeholders nombrados (ej: :nombre, @variable)
    # PERO: excluir PostgreSQL casts (::tipo) - no es un parámetro con negative lookbehind
    named_placeholders = re.findall(r'(?<!:)[:@]\w+', sql)
    if named_placeholders:
        errores.append(f"Contiene placeholders nombrados: {', '.join(named_placeholders)}")

    # 6. Detectar funciones sin parámetros completos
    # Ej: EXTRACT(HOUR FROM sin cerrar, DATE_PART( sin completar
    incomplete_functions = re.findall(r'\b(EXTRACT|DATE_PART|TO_CHAR|CAST)\s*\([^)]*$', sql, re.IGNORECASE)
    if incomplete_functions:
        errores.append(f"Contiene funciones incompletas: {', '.join(incomplete_functions)}")

    if errores:
        mensaje_error = "SQL contiene parámetros sin asignar: " + "; ".join(errores)
        logger.error(mensaje_error)
        logger.error(f"SQL problemático: {sql}")
        raise Exception(mensaje_error)


def _limpiar_markdown_sql(sql):
    """Extrae SQL puro de markdown con backticks (```sql ... ```)"""
    # Buscar patrón: ```sql\n...SQL...\n```
    match = re.search(r"```(?:sql)?\s*\n(.*?)\n```", sql, re.DOTALL)
    if match:
        sql = match.group(1).strip()
        logger.debug(f"SQL extraído de markdown: {sql[:100]}")
    else:
        # Buscar solo backticks sin sql
        match = re.search(r"`([^`]*)`", sql)
        if match:
            sql = match.group(1).strip()
            logger.debug(f"SQL extraído de backticks simples: {sql[:100]}")

    return sql
    """Extrae SQL puro de markdown con backticks (```sql ... ```)"""
    # Buscar patrón: ```sql\n...SQL...\n```
    match = re.search(r"```(?:sql)?\s*\n(.*?)\n```", sql, re.DOTALL)
    if match:
        sql = match.group(1).strip()
        logger.debug(f"SQL extraído de markdown: {sql[:100]}")
    else:
        # Si no hay backticks, usar el SQL tal cual
        sql = sql.strip()
    
    return sql