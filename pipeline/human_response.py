import re
import logging
from datetime import datetime, time, date
from decimal import Decimal
from ai.llm import llamar_llm
from ai.prompts_optimizados import prompt_respuesta
from ai.config_ia import PALABRAS_CLAVE_IA, PALABRAS_EXACTAS_IA, RESPUESTA_PREGUNTAS_IA, MAX_TOKENS_RESPUESTA

logger = logging.getLogger(__name__)

def _serializar_valor(valor):
    """Convierte tipos de datos complejos a strings legibles."""
    if valor is None:
        return None
    elif isinstance(valor, time):
        # Convertir time(8, 0) -> "08:00"
        return valor.strftime("%H:%M") if hasattr(valor, 'strftime') else str(valor)
    elif isinstance(valor, (datetime, date)):
        # Convertir datetime/date a string ISO
        return valor.isoformat() if hasattr(valor, 'isoformat') else str(valor)
    elif isinstance(valor, Decimal):
        # Convertir Decimal a float
        return float(valor)
    elif isinstance(valor, bool):
        # Convertir bool a string legible
        return "Sí" if valor else "No"
    else:
        return valor

def _serializar_filas(filas, columnas):
    """
    CRÍTICO: Convierte sqlite3.Row objects a dicts ANTES de pasar a Ollama.
    Los Row objects crean problemas de representacion en strings.
    AHORA TAMBIÉN convierte tipos complejos (datetime.time, Decimal, etc) a strings.
    """
    if not filas or not columnas:
        logger.warning(f"_serializar_filas: filas vacias o sin columnas")
        return []
    
    filas_serializadas = []
    for fila in filas:
        if hasattr(fila, 'keys'):  # sqlite3.Row tiene .keys()
            try:
                fila_dict = {col: _serializar_valor(fila[col]) for col in columnas}
                filas_serializadas.append(fila_dict)
            except Exception as e:
                logger.error(f"Error serializando Row: {e}")
        elif isinstance(fila, (tuple, list)):
            try:
                fila_dict = {columnas[i]: _serializar_valor(fila[i]) for i in range(len(columnas))}
                filas_serializadas.append(fila_dict)
            except Exception as e:
                logger.error(f"Error serializando tupla: {e}")
        else:
            filas_serializadas.append({"valor": str(fila)})
    
    logger.info(f"[OK] Filas serializadas: {len(filas_serializadas)} registros convertidos")
    return filas_serializadas


def _formatear_fila_natural(fila, columnas):
    """Construye una frase natural a partir de una fila de datos."""
    datos = {col.lower(): fila.get(col) for col in columnas}

    profesor = datos.get('profesor') or datos.get('nombre')
    materia = datos.get('materia') or datos.get('nombre_materia')
    instalacion = datos.get('instalacion') or datos.get('aula') or datos.get('nombre_aula')
    tipo_instalacion = datos.get('tipo_instalacion') or datos.get('tipo')
    bloque = datos.get('bloque')
    campus = datos.get('campus')
    area = datos.get('nombre_area')
    estado = datos.get('nombre_estado') or datos.get('estado')
    dia = datos.get('dia_semana') or datos.get('dia')
    hora_inicio = datos.get('hora_inicio')
    hora_fin = datos.get('hora_fin')

    def fmt(valor):
        return str(valor) if valor is not None else None

    profesor = fmt(profesor)
    materia = fmt(materia)
    instalacion = fmt(instalacion)
    tipo_instalacion = fmt(tipo_instalacion)
    bloque = fmt(bloque)
    campus = fmt(campus)
    area = fmt(area)
    estado = fmt(estado)
    dia = fmt(dia)
    hora_inicio = fmt(hora_inicio)
    hora_fin = fmt(hora_fin)

    partes = []

    if profesor and materia:
        frase = f"{profesor} dicta {materia}"
        if instalacion:
            frase += f" en {instalacion}"
        if tipo_instalacion:
            frase += f" ({tipo_instalacion})"
        ubicacion = []
        if bloque:
            ubicacion.append(f"bloque {bloque}")
        if campus:
            ubicacion.append(f"campus {campus}")
        if ubicacion:
            frase += f", {' - '.join(ubicacion)}"
        if dia or hora_inicio or hora_fin:
            horario = []
            if dia:
                horario.append(f"los {dia}")
            if hora_inicio and hora_fin:
                horario.append(f"de {hora_inicio} a {hora_fin}")
            elif hora_inicio:
                horario.append(f"a partir de {hora_inicio}")
            elif hora_fin:
                horario.append(f"hasta {hora_fin}")
            frase += f", {' '.join(horario)}"
        if area:
            frase += f", área {area}"
        if estado:
            frase += f", estado {estado}"
        return frase

    if instalacion:
        frase = f"Instalación: {instalacion}"
        detalles = []
        if tipo_instalacion:
            detalles.append(tipo_instalacion)
        if bloque:
            detalles.append(f"bloque {bloque}")
        if campus:
            detalles.append(f"campus {campus}")
        if estado:
            detalles.append(f"estado {estado}")
        if detalles:
            frase += f" ({', '.join(detalles)})"
        return frase

    if materia:
        frase = f"Materia: {materia}"
        if profesor:
            frase += f", dictada por {profesor}"
        if dia or hora_inicio or hora_fin:
            horario = []
            if dia:
                horario.append(f"los {dia}")
            if hora_inicio and hora_fin:
                horario.append(f"de {hora_inicio} a {hora_fin}")
            if horario:
                frase += f", {' '.join(horario)}"
        return frase

    # Detectar campos numéricos típicos de estadísticas
    contador = None
    for key in ['cantidad', 'count', 'num_clases', 'horas_totales', 'total', 'valor']:
        if datos.get(key) is not None:
            contador = datos.get(key)
            break

    if contador is not None and len(columnas) == 1:
        return f"Valor: {contador}"

    if contador is not None:
        partes.append(f"Cantidad: {contador}")
    for col in columnas:
        if col.lower() in ['cantidad', 'count', 'num_clases', 'horas_totales', 'total', 'valor']:
            continue
        valor = fila.get(col)
        if valor not in (None, ''):
            partes.append(f"{col}: {valor}")
    if partes:
        return "; ".join(partes)

    # Fallback genérico legible
    partes = []
    for col in columnas:
        valor = fila.get(col)
        if valor is not None and valor != '':
            partes.append(f"{col}: {valor}")
    return "; ".join(partes) if partes else "Registro sin datos legibles"


def _generar_respuesta_datos(columnas, filas):
    """Genera una respuesta natural y legible directamente desde los datos."""
    if not columnas or not filas:
        return "No encontré datos para esa consulta."

    total = len(filas)
    if total == 1:
        return f"Encontré 1 registro. {_formatear_fila_natural(filas[0], columnas)}"

    if total <= 5:
        lineas = [f"Encontré {total} resultados:"]
        for idx, fila in enumerate(filas, 1):
            lineas.append(f"{idx}. {_formatear_fila_natural(fila, columnas)}")
        return "\n".join(lineas)

    # Más de 5 resultados: resumir y mostrar los primeros 5
    lineas = [f"Encontré {total} resultados. Aquí están los primeros 5:"]
    for idx, fila in enumerate(filas[:5], 1):
        lineas.append(f"{idx}. {_formatear_fila_natural(fila, columnas)}")
    lineas.append(f"... y {total - 5} resultados más.")
    return "\n".join(lineas)


def _truncar_respuesta_si_es_necesario(respuesta, max_caracteres=5000):
    """
    Valida respuestas con límite flexible para permitir respuestas naturales.
    
    Args:
        respuesta: Texto de la respuesta
        max_caracteres: Máximo de caracteres permitidos (default: 5000 para respuestas completas)
    
    Returns:
        Respuesta original (sin truncar) a menos que sea excesivamente larga
    """
    if not respuesta or len(respuesta) <= max_caracteres:
        return respuesta
    
    # Solo truncar si es EXTREMADAMENTE larga (ej: errores de iteración infinita)
    logger.warning(f"Respuesta extremadamente larga ({len(respuesta)} caracteres). Truncando a {max_caracteres}...")
    
    # Truncar sin cortar en medio de una palabra
    truncado = respuesta[:max_caracteres]
    
    # Encontrar el último espacio para no cortar palabras
    ultimo_espacio = truncado.rfind(' ')
    if ultimo_espacio > max_caracteres * 0.8:  # Si está lo suficientemente cerca
        truncado = respuesta[:ultimo_espacio]
    
    # Agregar indicador de truncamiento
    truncado = truncado.rstrip('.,;:') + "..."
    
    logger.info(f"Respuesta truncada a {len(truncado)} caracteres")
    return truncado


def generar_respuesta(pregunta, resultado, timeout=None):
    """
    Genera una respuesta natural en lenguaje humano usando Ollama.
    CRÍTICO: Serializa filas ANTES de pasar a Ollama.
    
    Args:
        pregunta: La pregunta del usuario
        resultado: Resultado de la BD con columnas y filas
        timeout: Timeout en segundos para Ollama (default from config)
    """
    from config import AI_NAME, OLLAMA_TIMEOUT
    if timeout is None:
        timeout = OLLAMA_TIMEOUT
    
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
                
                # PASO 3: Generar respuesta natural con Ollama usando los datos COMPLETOS
                logger.info(f"[PASO 3] Generando respuesta natural con Ollama (timeout={timeout}s)...")
                # CRÍTICO: Pasar TODOS los datos para contexto completo
                num_filas = len(filas_serializadas)
                datos_texto = f"Total de registros encontrados: {num_filas}\n\nDatos detallados:\n"
                
                # Mostrar TODOS los datos de forma clara
                for idx, fila in enumerate(filas_serializadas, 1):
                    datos_texto += f"\nRegistro {idx}: "
                    pares = [f"{k}='{v}'" for k, v in fila.items()]
                    datos_texto += " | ".join(pares)
                
                prompt = prompt_respuesta(pregunta, datos_texto)
                response = llamar_llm(prompt, max_tokens=MAX_TOKENS_RESPUESTA, timeout=timeout)
                
                if response and not response.startswith("Error:") and len(response.strip()) >= 10:
                    # Validar que la respuesta incluye datos relevantes del resultado para evitar respuestas genéricas.
                    respuesta_lower = response.lower()
                    
                    # VALIDACIÓN MÁS ESTRICTA: Buscar valores específicos de los datos
                    datos_relevantes = []
                    for fila in filas_serializadas:
                        for v in fila.values():
                            if v is not None and str(v).strip():
                                valor_str = str(v).strip()
                                # Priorizar valores específicos: nombres de personas, aulas, bloques, campus
                                if (len(valor_str) > 3 and 
                                    not valor_str.isdigit() and  # Evitar IDs numéricos solos
                                    not valor_str.lower() in ['cul', 'cuc', 'sí', 'no', 'true', 'false'] and  # Evitar valores genéricos
                                    not any(char.isdigit() for char in valor_str) or 'aula' in valor_str.lower() or 'bloque' in valor_str.lower()):  # Permitir aulas con números
                                    datos_relevantes.append(valor_str.lower())
                    
                    # Verificar que incluye al menos 2 valores específicos diferentes O un nombre completo
                    include_specific_data = False
                    valores_encontrados = []
                    
                    for item in datos_relevantes:
                        if item in respuesta_lower:
                            valores_encontrados.append(item)
                            if len(valores_encontrados) >= 2:
                                include_specific_data = True
                                break
                    
                    # Verificación adicional: si es una pregunta sobre persona específica, debe incluir el nombre
                    pregunta_lower = pregunta.lower()
                    if ('profesor' in pregunta_lower or 'quién' in pregunta_lower or 'quien' in pregunta_lower) and 'nombre' in columnas:
                        nombres_en_datos = [str(fila.get('nombre', '')).lower() for fila in filas_serializadas if fila.get('nombre')]
                        nombre_incluido = any(nombre in respuesta_lower for nombre in nombres_en_datos if len(nombre) > 3)
                        if nombre_incluido:
                            include_specific_data = True
                    
                    # Detectar respuestas genéricas comunes que deben ser rechazadas
                    respuestas_genericas = [
                        "no tengo información",
                        "no encontré datos", 
                        "no hay información",
                        "no puedo ayudarte",
                        "no está disponible",
                        "consulta la base de datos",
                        "revisa el sistema",
                        "contacta con administración",
                        "no se encuentra",
                        "sin resultados"
                    ]
                    
                    es_respuesta_generica = any(generica in respuesta_lower for generica in respuestas_genericas)
                    
                    if include_specific_data and not es_respuesta_generica:
                        logger.info(f"[PASO 4] [OK] Respuesta natural generada con Ollama")
                        return _truncar_respuesta_si_es_necesario(response.strip())
                    else:
                        logger.warning("[PASO 4] Respuesta de Ollama no incluye datos específicos. Usando fallback directo...")
                        return _truncar_respuesta_si_es_necesario(_generar_respuesta_datos(columnas, filas_serializadas))
                else:
                    logger.warning(f"[PASO 3] Ollama fallo: {response}. Usando respuesta directa...")
                    # FALLBACK: Respuesta directa si Ollama falla
                    return _truncar_respuesta_si_es_necesario(_generar_respuesta_datos(columnas, filas_serializadas))
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
    response = llamar_llm(prompt, max_tokens=MAX_TOKENS_RESPUESTA, timeout=timeout)

    if response.startswith("Error:") or not response or len(response.strip()) < 5:
        logger.error(f"Ollama no genero respuesta valida: {response}")
        logger.info(f"[FALLBACK] Ollama fallo. Devolviendo datos directos de la BD...")
        
        # FALLBACK: Devolver datos legibles de la BD si Ollama falla
        if isinstance(resultado, dict) and 'filas' in resultado:
            columnas = resultado.get('columnas', [])
            filas = resultado.get('filas', [])
            if columnas and filas:
                return _truncar_respuesta_si_es_necesario(_generar_respuesta_datos(columnas, filas))
        
        return "Lo siento, tuve un problema generando la respuesta. Por favor, intenta reformular tu pregunta."

    logger.info(f"[PASO 4] [OK] Respuesta generada correctamente con Ollama")
    return _truncar_respuesta_si_es_necesario(response.strip())