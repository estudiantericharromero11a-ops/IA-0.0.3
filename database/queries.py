import psycopg
from psycopg import sql
import logging
from config import DATABASE_URL

logger = logging.getLogger(__name__)

def get_connection():
    """Obtiene conexión a la base de datos PostgreSQL."""
    try:
        # psycopg3 usa la URL directamente
        conn = psycopg.connect(DATABASE_URL, row_factory=psycopg.rows.dict_row)
        return conn
    except Exception as e:
        logger.error(f"Error conectando a BD: {e}")
        raise

def ejecutar_query(sql_query):
    """
    Ejecuta una consulta SQL y retorna resultados.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query)
                if sql_query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    # cursor.description contiene objetos Column, extraer solo los nombres
                    columns = [desc.name for desc in cursor.description] if cursor.description else []
                    # En psycopg3, cursor con dict_row ya retorna dicts
                    return {
                        "columnas": columns,
                        "filas": results
                    }
                else:
                    conn.commit()
                    return {"mensaje": "Query ejecutada exitosamente"}
    except Exception as e:
        logger.error(f"Error ejecutando query: {e}")
        return {"error": str(e)}

def buscar_contexto_embeddings(embedding, top_k=5):
    """
    Busca contexto relevante usando embeddings con pgvector en la tabla conocimiento.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Buscar en tabla conocimiento con columna embedding vector(384)
                cursor.execute("""
                    SELECT contenido
                    FROM conocimiento
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (embedding, top_k))

                results = cursor.fetchall()
                contexto = "\n".join([row['contenido'] if isinstance(row, dict) else row[0] for row in results])
                return contexto
    except Exception as e:
        logger.error(f"Error buscando contexto: {e}")
        return ""