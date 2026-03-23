"""
Configuración centralizada para el sistema THANIA.
Evita duplicación de palabras clave y constantes.
"""

# ============================================================================
# PALABRAS CLAVE - Detección de preguntas sobre la THANIA
# ============================================================================

# Frases completas que definitivamente son sobre la THANIA
PALABRAS_CLAVE_IA = [
    'como te llamas', 'tu nombre', 'eres', 'quien eres', 'que eres',
    'para que sirves', 'para qué sirves', 'sirves', 'funcion', 'función',
    'proposito', 'propósito', 'que haces', 'presenta', 'presentate',
    'quien soy', 'hola', 'saludos', 'cual es tu nombre', 'cuál es tu nombre',
    'cual es tu proposito', 'cuál es tu propósito', 'bienvenida', 'hola thania',
    'greetings', 'introducete', 'introducción'
]

# Palabras exactas (word boundaries) que indican preguntas sobre THANIA
PALABRAS_EXACTAS_IA = ['thania', 'THANIA']

# ============================================================================
# INFORMACIÓN DE LA THANIA
# ============================================================================

IA_NOMBRE = "THANIA"
IA_DESCRIPCION = """Soy el asistente de datos del sistema universitario THANIA.

Puedo ayudarte con:
- Información sobre profesores y docentes
- Horarios de clases y disponibilidad
- Ubicación de aulas y espacios
- Materias y programas académicos
- Datos de estudiantes y administrativos
- Consultas sobre la universidad en general

Este sistema busca información en la base de datos de tu universidad y te proporciona respuestas contextualizadas."""

# Respuesta para preguntas sobre THANIA
RESPUESTA_PREGUNTAS_IA = """Soy el asistente del sistema universitario THANIA.

Funciono como un módulo de consulta de datos que:
1. Entiende tus preguntas en lenguaje natural
2. Busca contexto relevante en la base de datos
3. Genera consultas SQL optimizadas
4. Retorna respuestas claras y útiles

¿En qué puedo ayudarte?
- Información de profesores
- Horarios y ubicaciones
- Materias y programas
- Datos académicos en general"""

# ============================================================================
# LÍMITES DE SEGURIDAD
# ============================================================================

MAX_FILAS_RESULTADO = 100  # No devolver más de 100 filas por query
TIMEOUT_OLLAMA = 120  # 2 minutos para respuesta de Ollama
TIMEOUT_BD = 30  # 30 segundos máximo para ejecución SQL
REINTENTOS_OLLAMA = 3  # Número de reintentos si falla Ollama

# ============================================================================
# PARÁMETROS DE MODELOS
# ============================================================================

# Parámetros para generación de SQL (determinístico)
TEMPERATURA_SQL = 0.1  # Muy bajo = determinístico, menos creativo
MAX_TOKENS_SQL = 500  # Máximo tokens para generar SQL

# Parámetros para generación de respuestas (más conversacional)
TEMPERATURA_RESPUESTA = 0.5  # Medio = balance entre determinístico y creativo
MAX_TOKENS_RESPUESTA = 200  # Límite para respuestas

# Modelo de embeddings para RAG
MODELO_EMBEDDINGS = 'all-MiniLM-L6-v2'  # 384 dimensiones, ligero pero efectivo
DIMENSION_EMBEDDINGS = 384

# ============================================================================
# CONFIGURACIÓN DE PGVECTOR
# ============================================================================

TOP_K_SIMILITUD = 5  # Número de contextos a recuperar del RAG
METRICA_DISTANCIA = '<=>  '  # pgvector: <=> es la métrica coseno

# ============================================================================
# LOGS Y DEBUGGING
# ============================================================================

DEBUG_MODE = False  # Cambiar a True para logs más verbosos
LOG_NIVEL = 'INFO'  # Nivel de logging (DEBUG, INFO, WARNING, ERROR)

# ============================================================================
# VALIDACIÓN DE QUERIES
# ============================================================================

# Operaciones prohibidas en SQL (seguridad)
OPERACIONES_PROHIBIDAS = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']

# Máximo de JOINs permitidos en una query
MAX_JOINS = 4

# ============================================================================
# PROMPTS PREDEFINIDOS
# ============================================================================

PROMPT_INSTRUCCIONES_SQL = """Eres un experto en SQL para una base de datos universitaria PostgreSQL.
Genera SOLO una consulta SELECT simple y eficiente.
NO uses subqueries, UNION, CTEs ni self-joins complejos.
Usa LOWER() para comparaciones case-insensitive.
Usa LIKE '%term%' para búsquedas parciales."""

PROMPT_INSTRUCCIONES_RESPUESTA = """Eres un asistente del sistema universitario.
Convierte los datos de la BD en una respuesta natural, conversacional y útil.
Sé amable y profesional.
No inventes información que no esté en los datos."""

# ============================================================================
# PALABRAS CLAVE PARA CONTEXTO
# ============================================================================

# Palabras que indican búsqueda de profesores
PALABRAS_PROFESOR = ['profesor', 'docente', 'enseña', 'enseñan', 'instructor', 'catedrático']

# Palabras que indican búsqueda de horarios
PALABRAS_HORARIO = ['horario', 'hora', 'cuando', 'qué hora', 'que hora', 'disponibilidad', 'time']

# Palabras que indican búsqueda de ubicación
PALABRAS_UBICACION = ['donde', 'dónde', 'ubicación', 'aula', 'sala', 'ubicacion', 'localización', 'local']

# Palabras que indican búsqueda de materias
PALABRAS_MATERIA = ['materia', 'asignatura', 'curso', 'materias', 'asignaturas', 'cursos', 'subject']

# Palabras que indican búsqueda de estudiantes
PALABRAS_ESTUDIANTE = ['estudiante', 'alumno', 'estudiantes', 'alumnos', 'student']

# ============================================================================
# STATUS DE DEPLOYMENT
# ============================================================================

APP_NOMBRE = "THANIA THANIA"
APP_VERSION = "0.0.2"
APP_DESCRIPCION = "Sistema THANIA RAG para consultas universitarias"
AUTOR = "Equipo de Desarrollo"
FECHA_DEPLOY = "2026-03-21"
