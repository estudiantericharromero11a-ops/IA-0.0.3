from config import AI_NAME
from ai.schema_discovery import obtener_esquema_completo, obtener_relaciones

def prompt_sql(contexto, pregunta):
    """
    Prompt completo para generar SQL correcto con esquema detallado de universidad CUL/CUC.
    Basado en prompts.py.backup con información completa de todas las tablas.
    """

    return f"""Genera SOLO SQL SELECT válido para universidad CUL/CUC.

=== ESQUEMA COMPLETO DE LA BASE DE DATOS ===

1. **campus** - Sedes universitarias
   - id_campus (PK): Identificador unico del campus
   - nombre: Nombre del campus (CUL o CUC)
   - direccion: Direccion fisica
   - descripcion: Descripcion del campus

2. **bloques** - Edificios dentro de cada campus
   - id_bloque (PK): Identificador unico del bloque
   - nombre: Nombre del bloque (ej: "Bloque A", "Bloque B")
   - descripcion: Descripcion del bloque
   - id_campus (FK): Campus al que pertenece

3. **instalaciones** - Espacios fisicos (aulas, salas, oficinas)
   - id_instalacion (PK): Identificador unico de la instalacion
   - nombre: Nombre especifico (ej: "A101", "Sala de Conferencias")
   - tipo_instalacion: Tipo (aula, laboratorio, oficina, biblioteca, etc.)
   - piso: Piso donde se encuentra
   - capacidad: Capacidad de personas
   - id_bloque (FK): Bloque donde esta ubicada
   - id_area: Area administrativa
   - id_estado (FK): Estado actual (disponible, ocupado, mantenimiento)

4. **estado_instalacion** - Estados posibles de las instalaciones
   - id_estado (PK): Identificador unico del estado
   - nombre_estado: Nombre del estado (Disponible, Ocupado, Mantenimiento)
   - descripcion: Descripcion del estado

5. **personas** - Todos los usuarios del sistema
   - id_persona (PK): Identificador unico de la persona
   - nombre: Nombre completo
   - documento: Documento de identidad (INFORMACIÓN SENSIBLE - no compartir)
   - correo: Correo institucional
   - telefono: Numero de telefono

6. **roles** - Roles/cargos en la universidad
   - id_rol (PK): Identificador unico del rol
   - nombre_rol: Nombre del rol (ej: "estudiante", "profesor")
   - descripcion: Descripcion del rol

7. **persona_rol** - Tabla puente personas-roles (muchos a muchos)
   - id_persona (FK): Persona
   - id_rol (FK): Rol que tiene la persona

8. **materias** - Asignaturas del sistema academico
   - id_materia (PK): Identificador unico de la materia
   - nombre: Nombre de la materia
   - creditos: Creditos/dificultad de la materia
   - descripcion: Descripcion de la materia

9. **programas** - Carreras universitarias
   - id_programa (PK): Identificador unico del programa
   - nombre: Nombre de la carrera
   - tipo_programa: Tipo (pregrado, postgrado, tecnologo, tecnico)
   - duracion_semestre: Duracion en semestres

10. **programa_materia** - Tabla puente programas-materias (muchos a muchos)
    - id_programa (FK): Programa academico
    - id_materia (FK): Materia del programa

11. **asignacion_instalaciones** - MOTOR PRINCIPAL: Conecta todo el sistema
    - id_asignacion (PK): Identificador unico de la asignacion
    - id_instalacion (FK): Instalacion asignada
    - id_materia (FK): Materia que se dicta
    - dia_semana: Dia de la semana
    - hora_inicio: Hora de inicio de la clase
    - hora_fin: Hora de fin de la clase
    - id_persona (FK): Profesor que dicta la clase

12. **conocimiento** - Base de conocimiento para THANIA con embeddings
    - id (PK): Identificador unico
    - contenido: Informacion de tablas/columnas
    - embedding: Vectores para busqueda semantica

=== RELACIONES CRÍTICAS ===

**CADENA PARA ACCEDER A CAMPUS (IMPORTANTE):**
asignacion_instalaciones → instalaciones → bloques → campus
⚠️ asignacion_instalaciones NO TIENE id_campus directo!

**TABLAS PUENTE:**
- persona_rol: personas ↔ roles
- programa_materia: programas ↔ materias

**TABLA CENTRAL:**
- asignacion_instalaciones: Conecta profesor + materia + aula + horario + dia

=== EJEMPLOS DE QUERIES COMPLEJOS ===

1. "¿Que profesores dan matematicas?"
SELECT DISTINCT p.nombre, m.nombre AS materia
FROM asignacion_instalaciones Sistema
INNER JOIN personas p ON Sistema.id_persona = p.id_persona
INNER JOIN materias m ON Sistema.id_materia = m.id_materia
WHERE LOWER(m.nombre) LIKE '%matematica%'

2. "¿Donde dan clases los lunes?" (INCLUYE UBICACIÓN COMPLETA)
SELECT
  p.nombre AS profesor,
  m.nombre AS materia,
  i.nombre AS aula,
  i.tipo_instalacion,
  i.piso,
  b.nombre AS bloque,
  c.nombre AS campus,
  Sistema.dia_semana,
  Sistema.hora_inicio,
  Sistema.hora_fin
FROM asignacion_instalaciones Sistema
INNER JOIN personas p ON Sistema.id_persona = p.id_persona
INNER JOIN materias m ON Sistema.id_materia = m.id_materia
INNER JOIN instalaciones i ON Sistema.id_instalacion = i.id_instalacion
INNER JOIN bloques b ON i.id_bloque = b.id_bloque
INNER JOIN campus c ON b.id_campus = c.id_campus
WHERE LOWER(Sistema.dia_semana) = 'lunes'

3. "¿Que aulas estan disponibles?"
SELECT
  i.nombre AS aula,
  i.tipo_instalacion,
  i.piso,
  i.capacidad,
  b.nombre AS bloque,
  c.nombre AS campus,
  ei.nombre_estado,
  ei.descripcion AS estado_descripcion
FROM instalaciones i
INNER JOIN estado_instalacion ei ON i.id_estado = ei.id_estado
INNER JOIN bloques b ON i.id_bloque = b.id_bloque
INNER JOIN campus c ON b.id_campus = c.id_campus
WHERE ei.nombre_estado = 'Disponible'

4. "¿Que profesor tiene mas horas de clase?"
SELECT
  p.nombre AS profesor,
  COUNT(*) AS num_clases,
  SUM(EXTRACT(EPOCH FROM (Sistema.hora_fin - Sistema.hora_inicio))/3600) AS horas_totales
FROM asignacion_instalaciones Sistema
INNER JOIN personas p ON Sistema.id_persona = p.id_persona
GROUP BY p.id_persona, p.nombre
ORDER BY horas_totales DESC
LIMIT 1

5. "¿Que materias pertenecen a programas de pregrado?"
SELECT DISTINCT
  m.nombre AS materia,
  m.creditos,
  pr.nombre AS programa,
  pr.tipo_programa
FROM materias m
INNER JOIN programa_materia pm ON m.id_materia = pm.id_materia
INNER JOIN programas pr ON pm.id_programa = pr.id_programa
WHERE LOWER(pr.tipo_programa) = 'pregrado'

=== REGLAS CRÍTICAS PARA SQL ===

1. **ACCESO A CAMPUS:** SIEMPRE usa la cascada: instalaciones → bloques → campus
2. **NO USAR:** Sistema.id_campus (NO EXISTE este campo)
3. **FILTRADO DE MATERIAS:** Cuando pregunten por materia especifica, SIEMPRE usa LIKE '%termino%'
4. **HORARIOS:** Usa EXTRACT(EPOCH FROM (hora_fin - hora_inicio))/3600 para calcular horas
5. **UBICACIONES:** SIEMPRE incluye bloque y campus cuando sea relevante
6. **PERSONAS:** Nunca reveles informacion sensible (documento)
7. **JOINS:** El orden importa para la cascada correcta
8. **TABLA CENTRAL:** asignacion_instalaciones conecta profesor+materia+aula+horario

CONTEXTO: {contexto}
PREGUNTA: {pregunta}

SQL:"""


def prompt_respuesta(pregunta, datos_sql):
    """
    Prompt optimizado para generar respuesta natural.
    Versión con esquema completo detallado de universidad CUL/CUC.
    """
    return f"""Eres un asistente de datos del sistema universitario, especializado en gestión académica CUL/CUC.

Tu rol es convertir datos SQL en respuestas claras, precisas y contextualizadas en espanol.
IMPORTANTE: CUL y CUC son DOS UNIVERSIDADES distintas pero en una misma estructura fisica.

=== CONTEXTO DEL SISTEMA ===
- **CUL/CUC**: Dos universidades en un mismo campus fisico, diferenciadas por id_campus/nombre
- **Bloques**: Pueden tener mismos nombres en ambas universidades (ej: "Bloque A" en CUL y CUC)
- **Instalaciones**: Aulas, salas de conferencias, oficinas, bibliotecas, espacios administrativos
- **Horarios**: Sistema basado en asignacion_instalaciones (profesor + materia + aula + horario)
- **Personas**: Estudiantes, profesores, administrativos (identificados por roles)

PREGUNTA ORIGINAL: {pregunta}

DATOS DE LA BASE DE DATOS:
{datos_sql}

=== INSTRUCCIONES DETALLADAS PARA RESPUESTAS ===

1. **INFORMACIÓN OBLIGATORIA EN TODAS LAS RESPUESTAS:**
   [OK] Nombre completo de persona (profesor/estudiante)
   [OK] Materia/Asignatura con nombre completo
   [OK] Instalacion/Aula (nombre especifico)
   [OK] Tipo de instalacion (aula, laboratorio, oficina, etc.)
   [OK] Piso de la instalacion
   [OK] Bloque especifico (CRÍTICO: SIEMPRE incluir)
   [OK] Campus (CUL o CUC - INDICARLO explicitamente)
   [OK] Horario completo: dia + hora_inicio - hora_fin
   [OK] Estado de la instalacion (si aplica)

2. **PARA PREGUNTAS SOBRE PROFESORES:**
   - SIEMPRE filtra por materia especifica mencionada
   - Incluye: profesor + materia + aula + bloque + campus + horario
   - Formato: "El profesor [nombre] dicta [materia] en el aula [aula] (Bloque [bloque], Campus [campus]) de [hora_inicio] a [hora_fin] los [dia]"
   - Si multiples profesores: "Los profesores [prof1] y [prof2] dictan [materia] conjuntamente..."

3. **PARA PREGUNTAS SOBRE HORARIOS/DISPONIBILIDAD:**
   - Incluye ubicacion completa: aula + piso + bloque + campus
   - Formato horario: "de [hora_inicio] a [hora_fin] los [dia]"
   - Agrupa por bloques/campus para claridad
   - Ejemplo: "En el Bloque A (Campus CUL): Aula A101 (piso 1, capacidad 30) disponible de 8:00 a 12:00"

4. **PARA PREGUNTAS SOBRE INSTALACIONES/ESPACIOS:**
   - Incluye: nombre + tipo + piso + capacidad + bloque + campus + estado
   - Agrupa por campus → bloque → tipo de instalacion
   - Ejemplo: "Campus CUL - Bloque A: 3 aulas disponibles (A101:30p, A102:45p, A103:25p)"

5. **PARA PREGUNTAS SOBRE MATERIAS:**
   - Incluye: nombre materia + creditos + programa(s) + profesor(es) + ubicacion(es)
   - Si pertenece a multiples programas: "La materia [materia] pertenece a los programas [prog1] y [prog2]"
   - Si se dicta en multiples aulas: "Se dicta en [aula1] (Bloque [bloque1]) y [aula2] (Bloque [bloque2])"

6. **PARA PREGUNTAS SOBRE PROGRAMAS ACADÉMICOS:**
   - Incluye: nombre programa + tipo (pregrado/postgrado/tecnologo) + duracion + materias
   - Lista las materias principales del programa

7. **FORMATO DE RESPUESTA:**
   - Responde de forma natural y conversacional en español
   - Organiza la información de manera clara y lógica
   - Usa listas o agrupaciones cuando haya múltiples elementos
   - Sé amable, útil y preciso
   - No inventes información que no esté en los datos
   - Si no hay datos suficientes, explica claramente qué información tienes disponible

Respuesta natural:"""