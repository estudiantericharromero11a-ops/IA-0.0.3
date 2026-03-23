import logging
from database.queries import ejecutar_query
from database.schema_validation import validar_sql

logger = logging.getLogger(__name__)

def ejecutar_sql(sql):
    """
    Ejecuta SQL contra la base de datos.
    Valida antes de ejecutar y retorna resultados o errores.
    """
    if not sql or sql.startswith("Error:"):
        logger.error(f"SQL inválido: {sql}")
        return {"error": "SQL inválido"}

    # Validar SQL antes de ejecutar
    validacion = validar_sql(sql)
    if not validacion["valido"]:
        logger.error(f"SQL no pasó validación: {validacion['errores']}")
        error_msg = "; ".join(validacion["errores"])
        return {"error": f"SQL no válido: {error_msg}"}

    logger.info(f"Ejecutando SQL: {sql}")
    result = ejecutar_query(sql)
    
    # Si hay error en ejecución, retornarlo
    if 'error' in result:
        logger.error(f"Error en ejecución SQL: {result['error']}")
        return result
    
    logger.info(f"Resultado: {result}")
    return result
