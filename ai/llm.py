import requests
import logging
import time
from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

def llamar_llm(prompt, temperature=0.1, max_tokens=300, intentos=3, timeout=None):
    """
    Llama a Ollama con el modelo llama3 y parámetros optimizados para velocidad.
    Incluye retry logic con exponential backoff.
    
    Args:
        prompt (str): Prompt para el modelo
        temperature (float): Temperatura (0 = determinístico, 1 = creativo)
        max_tokens (int): Máximo número de tokens a generar (reducido para velocidad)
        intentos (int): Número de reintentos en caso de error
        timeout (int): Timeout en segundos para la llamada
    
    Returns:
        str: Respuesta del modelo o mensaje de error
    """
    if timeout is None:
        timeout = OLLAMA_TIMEOUT

    for intento in range(intentos):
        try:
            url = f"{OLLAMA_HOST}/api/generate"
            data = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }

            logger.info(f"Llamando a Ollama {OLLAMA_MODEL} (intento {intento+1}/{intentos}, timeout={timeout}s)")
            response = requests.post(url, json=data, timeout=timeout)

            if response.status_code == 200:
                result = response.json()
                respuesta = result.get('response', '').strip()
                logger.info(f"[OK] Ollama respondio correctamente en intento {intento+1}")
                return respuesta
            else:
                error_msg = f"Error {response.status_code}"
                logger.warning(f"Ollama: {error_msg} (intento {intento+1}/{intentos})")
                
                if intento < intentos - 1:
                    espera = 2 ** intento  # Exponential backoff: 1s, 2s, 4s
                    logger.info(f"Esperando {espera}s antes de reintentar...")
                    time.sleep(espera)
                else:
                    return f"Error: Ollama no respondió después de {intentos} intentos"

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout en Ollama (>{timeout}s) en intento {intento+1}/{intentos}")
            if intento < intentos - 1:
                espera = 2 ** intento
                time.sleep(espera)
            else:
                return f"Error: Timeout en Ollama (>{timeout}s) después de reintentos"
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"Error de conexión con Ollama en intento {intento+1}/{intentos}")
            if intento < intentos - 1:
                espera = 2 ** intento
                time.sleep(espera)
            else:
                return "Error: No se pudo conectar con Ollama después de reintentos"
                
        except Exception as e:
            logger.error(f"Error inesperado llamando a Ollama: {str(e)}")
            if intento < intentos - 1:
                espera = 2 ** intento
                time.sleep(espera)
            else:
                return f"Error: {str(e)}"

    return "Error: No se pudo conectar con Ollama"