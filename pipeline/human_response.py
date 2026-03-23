import re
import logging
from ai.llm import llamar_llm
from ai.prompts_optimizados import prompt_respuesta
from ai.config_ia import PALABRAS_CLAVE_IA, PALABRAS_EXACTAS_IA, RESPUESTA_PREGUNTAS_IA

logger = logging.getLogger(__name__)

def _serializar_filas(filas, columnas):
    """
    CRÍTICO: Convierte sqlite3.Row objects a dicts ANTES de pasar a Ollama.
    Los Row objects crean problemas de representacion en strings.
    """
    if not filas or not columnas:
        logger.warning(f"_serializar_filas: filas vacias o sin columnas")
        return []
    
    filas_serializadas = []
    for fila in filas:
        if hasattr(fila, 'keys'):  # sqlite3.Row tiene .keys()
            try:
                fila_dict = {col: fila[col] for col in columnas}
                filas_serializadas.append(fila_dict)
            except Exception as e:
                logger.error(f"Error serializando Row: {e}")
        elif isinstance(fila, (tuple, list)):
            try:
                fila_dict = {columnas[i]: fila[i] for i in range(len(columnas))}
                filas_serializadas.append(fila_dict)
            except Exception as e:
                logger.error(f"Error serializando tupla: {e}")
        else:
            filas_serializadas.append({"valor": str(fila)})
    
    logger.info(f"[OK] Filas serializadas: {len(filas_serializadas)} registros convertidos")
    return filas_serializadas


def _generar_respuesta_datos(columnas, filas):
    """Genera respuesta determinista a partir de los datos de la BD (sin inventos)."""
    if not columnas or not filas:
        return "No se encontraron datos concretos para esa consulta."

    # Nombres de columnas ordenados
    lineas = [f"He encontrado {len(filas)} registro(s) en la base de datos:"]
    for idx, fila in enumerate(filas, 1):
        partes = [f"{col}: {fila.get(col, '')}" for col in columnas]
        lineas.append(f"{idx}. {', '.join(partes)}")

    lineas.append("\nNota: informacion estricta de la base de datos. No se han agregado detalles no presentes.")
    return "\n".join(lineas)


def generar_respuesta(pregunta, resultado, timeout=60):
    """
    Genera una respuesta natural en lenguaje humano usando Ollama.
    CRÍTICO: Serializa filas ANTES de pasar a Ollama.
    
    Args:
        pregunta: La pregunta del usuario
        resultado: Resultado de la BD con columnas y filas
        timeout: Timeout en segundos para Ollama (default 120s)
    """
    from config import AI_NAME
    
    logger.info(f"Generando respuesta para pregunta: {pregunta}")
    
    # Verificar si es pregunta sobre la THANIA (usando config centralizada)
    pregunta_lower = pregunta.lower()
    
    # Cambiar deteccion a frases completas primero
    if any(phrase in pregunta_lower for phrase in PALABRAS_CLAVE_IA):
        logger.info(f"Pregunta sobre THANIA detectada")
        return RESPUESTA_PREGUNTAS_IA
    
    # Buscar palabras exactas (no como substring)
    for palabra in PALABRAS_EXACTAS_IA:
        if re.search(rf'\b{palabra}\b', pregunta_lower):
            logger.info(f"Palabra exacta '{palabra}' detectada")
            return RESPUESTA_PREGUNTAS_IA
    
    # PASO CRÍTICO 1: Validar que hay datos
    if isinstance(resultado, dict) and 'filas' in resultado and 'error' not in resultado:
        columnas = resultado.get('columnas', [])
        filas = resultado.get('filas', [])

        logger.info(f"[PASO 1] Datos recibidos: {len(filas)} filas, columnas={columnas}")

        if filas:
            filas_serializadas = _serializar_filas(filas, columnas)
            if filas_serializadas:
                logger.info(f"[PASO 2] [OK] Datos serializados correctamente")
                
                # PASO 3: Generar respuesta natural con Ollama usando los datos
                logger.info(f"[PASO 3] Generando respuesta natural con Ollama (timeout={timeout}s)...")
                datos_texto = f"Datos de la BD: {filas_serializadas}"
                prompt = prompt_respuesta(pregunta, datos_texto)
                response = llamar_llm(prompt, timeout=timeout)
                
                if response and not response.startswith("Error:") and len(response.strip()) >= 5:
                    logger.info(f"[PASO 4] [OK] Respuesta natural generada con Ollama")
                    return response.strip()
                else:
                    logger.warning(f"[PASO 3] Ollama fallo: {response}. Usando respuesta directa...")
                    # FALLBACK: Respuesta directa si Ollama falla
                    return _generar_respuesta_datos(columnas, filas_serializadas)
            else:
                logger.warning("[PASO 2] Las filas no pudieron serializarse correctamente")
                datos_texto = "Error al procesar los datos de la base de datos."
        else:
            logger.warning("[PASO 2] No hay filas para serializar")
            datos_texto = "No se encontraron registros en la base de datos."
    else:
        # Si no hay datos validos o hay error
        datos_texto = str(resultado)

    # Generar respuesta con Ollama
    logger.info(f"[PASO 3] Generando respuesta con Ollama (timeout={timeout}s)...")
    prompt = prompt_respuesta(pregunta, datos_texto)
    response = llamar_llm(prompt, timeout=timeout)

    if response.startswith("Error:") or not response or len(response.strip()) < 5:
        logger.error(f"Ollama no genero respuesta valida: {response}")
        logger.info(f"[FALLBACK] Ollama fallo. Devolviendo datos directos de la BD...")
        
        # FALLBACK: Devolver datos legibles de la BD si Ollama falla
        if isinstance(resultado, dict) and 'filas' in resultado:
            columnas = resultado.get('columnas', [])
            filas = resultado.get('filas', [])
            if columnas and filas:
                return _generar_respuesta_datos(columnas, filas)
        
        return "Lo siento, tuve un problema generando la respuesta. Por favor, intenta reformular tu pregunta."

    logger.info(f"[PASO 4] [OK] Respuesta generada correctamente con Ollama")
    return response.strip()