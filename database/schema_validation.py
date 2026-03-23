import re
import logging

logger = logging.getLogger(__name__)

def validar_sql(sql):
    """
    Valida que el SQL sea seguro y válido.
    Incluye validaciones para Q10 (TIME fields) y Q14 (parámetros).
    """
    errores = []

    # Solo permitir SELECT
    if not sql.strip().upper().startswith('SELECT'):
        errores.append("Solo se permiten consultas SELECT")

    # No permitir operaciones peligrosas
    operaciones_prohibidas = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER']
    sql_upper = sql.upper()
    for op in operaciones_prohibidas:
        if op in sql_upper:
            errores.append(f"Operación no permitida: {op}")

    # Validar sintaxis básica
    sql_clean = re.sub(r'\s+', ' ', sql_upper.strip())
    if not re.search(r'SELECT.*FROM', sql_clean):
        errores.append("SQL debe contener SELECT ... FROM")

    # FIX Q14: Validar parámetros sin asignar
    errores_parametros = _validar_parametros_sql(sql)
    errores.extend(errores_parametros)

    # FIX Q10: Validar comparaciones TIME problemáticas
    errores_time = _validar_comparaciones_time_sql(sql)
    errores.extend(errores_time)

    return {
        "valido": len(errores) == 0,
        "errores": errores
    }


def _validar_parametros_sql(sql):
    """
    FIX Q14: Valida que no haya parámetros sin asignar en el SQL.
    """
    errores = []

    # 1. Detectar placeholders de interrogación (?)
    if '?' in sql:
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
    named_placeholders = re.findall(r'[@:]\w+', sql)
    if named_placeholders:
        errores.append(f"Contiene placeholders nombrados: {', '.join(named_placeholders)}")

    return errores


def _validar_comparaciones_time_sql(sql):
    """
    FIX Q10: Detecta comparaciones LIKE problemáticas en campos TIME.
    """
    errores = []

    # Buscar patrones LIKE en campos TIME que puedan causar problemas
    time_like_pattern = re.compile(
        r'(\w+\.hora_\w+|hora_\w+)\s+LIKE\s+[\'"]([^\'"]*)[\'"]',
        re.IGNORECASE
    )

    matches = time_like_pattern.findall(sql)
    if matches:
        campos_problematicos = [match[0] for match in matches]
        errores.append(f"LIKE en campos TIME detectado (usar comparación temporal): {', '.join(campos_problematicos)}")

    return errores