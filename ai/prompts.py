from config import AI_NAME
from ai.schema_discovery import obtener_esquema_completo, obtener_relaciones

def prompt_sql(contexto, pregunta):
    """
    Prompt optimizado para generar SQL usando Ollama llama3.
    Version con esquema completo detallado de universidad CUL/CUC.
    """

    return f"""Eres experto SQL PostgreSQL para universidad CUL/CUC (dos universidades en una misma estructura).

=== ESQUEMA COMPLETO DE LA BASE DE DATOS ===

1. **campus** - Universidades del sistema CUL/CUC
   - id_campus (PK): Identificador unico de la universidad
   - nombre: Nombre de la universidad (CUL o CUC)
   - direccion: Direccion fisica de la universidad
   - descripcion: Descripcion detallada de la universidad

2. **bloques** - Secciones/edificios dentro de cada universidad
   - id_bloque (PK): Identificador unico del bloque
   - nombre: Nombre del bloque (ej: "Bloque A", "Bloque B")
   - descripcion: Descripcion del bloque
   - id_campus (FK): Universidad a la que pertenece el bloque

3. **instalaciones** - Espacios fisicos/instalaciones
   - id_instalacion (PK): Identificador unico de la instalacion
   - nombre: Nombre de la instalacion (salas, aulas, oficinas, etc.)
   - tipo_instalacion: Tipo (administrativa, aula, biblioteca, etc.)
   - piso: Numero de piso (-1 para sotanos)
   - capacidad: Capacidad en personas
   - id_bloque (FK): Bloque al que pertenece
   - id_area (FK): Área funcional
   - id_estado (FK): Estado actual de la instalacion

4. **estado_instalacion** - Estados de funcionamiento de instalaciones
   - id_estado (PK): Identificador unico del estado
   - nombre_estado: Nombre del estado (ej: "Disponible", "Ocupado")
   - descripcion: Descripcion del estado

5. **horario_instalacion** - Horarios de uso de instalaciones
   - id_horario (PK): Identificador unico del horario
   - id_instalacion (FK): Instalacion a la que aplica el horario
   - dia_semana: Dia de la semana
   - hora_apertura: Hora de inicio de uso
   - hora_cierre: Hora de fin de uso

6. **personas** - Todas las personas registradas en el sistema
   - id_persona (PK): Identificador unico de la persona
   - nombre: Nombre completo
   - documento: Documento de identidad (INFORMACIÓN SENSIBLE - no compartir)
   - correo: Correo institucional
   - telefono: Numero de telefono

7. **roles** - Roles/cargos en la universidad
   - id_rol (PK): Identificador unico del rol
   - nombre_rol: Nombre del rol (ej: "estudiante", "profesor")
   - descripcion: Descripcion del rol

8. **persona_rol** - Tabla puente personas-roles (muchos a muchos)
   - id_persona (FK): Persona
   - id_rol (FK): Rol que tiene la persona

9. **materias** - Asignaturas del sistema academico
   - id_materia (PK): Identificador unico de la materia
   - nombre: Nombre de la materia
   - creditos: Creditos/dificultad de la materia
   - descripcion: Descripcion de la materia

10. **programas** - Carreras universitarias
    - id_programa (PK): Identificador unico del programa
    - nombre: Nombre de la carrera
    - tipo_programa: Tipo (pregrado, postgrado, tecnologo, tecnico)
    - duracion_semestre: Duracion en semestres

11. **programa_materia** - Tabla puente programas-materias (muchos a muchos)
    - id_programa (FK): Programa academico
    - id_materia (FK): Materia del programa

12. **asignacion_instalaciones** - MOTOR PRINCIPAL: Conecta todo el sistema
    - id_asignacion (PK): Identificador unico de la asignacion
    - id_instalacion (FK): Instalacion asignada
    - id_materia (FK): Materia que se dicta
    - dia_semana: Dia de la semana
    - hora_inicio: Hora de inicio de la clase
    - hora_fin: Hora de fin de la clase
    - id_persona (FK): Profesor que dicta la clase

13. **conocimiento** - Base de conocimiento para THANIA con embeddings
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

1. "?Que profesores dan matematicas?"
SELECT DISTINCT p.nombre, m.nombre AS materia
FROM asignacion_instalaciones Sistema
INNER JOIN personas p ON Sistema.id_persona = p.id_persona
INNER JOIN materias m ON Sistema.id_materia = m.id_materia
WHERE LOWER(m.nombre) LIKE '%matematica%'

2. "?Donde dan clases los lunes?" (INCLUYE UBICACIÓN COMPLETA)
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

3. "?Que aulas estan disponibles?"
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

4. "?Que profesor tiene mas horas de clase?"
SELECT
  p.nombre AS profesor,
  COUNT(*) AS num_clases,
  SUM(EXTRACT(EPOCH FROM (Sistema.hora_fin - Sistema.hora_inicio))/3600) AS horas_totales
FROM asignacion_instalaciones Sistema
INNER JOIN personas p ON Sistema.id_persona = p.id_persona
GROUP BY p.id_persona, p.nombre
ORDER BY horas_totales DESC
LIMIT 1

5. "?Que materias pertenecen a programas de pregrado?"
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
    Prompt optimizado para generar respuesta natural usando Ollama llama3.
    Version con esquema completo detallado de universidad CUL/CUC.
    """
    return f"""Eres {AI_NAME}, asistente THANIA especializado en gestion academica universitaria CUL/CUC.

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
   - Ejemplo: "El programa [nombre] (tipo: pregrado, duracion: 10 semestres) incluye materias como [materia1], [materia2]..."

7. **MANEJO DE INFORMACIÓN SENSIBLE:**
   - NUNCA incluyas documento/cedula de identidad
   - Correo institucional: incluir solo si es necesario para identificacion
   - Telefono: incluir solo si es especificamente solicitado
   - Nombre completo: siempre incluir

8. **ESTRUCTURA DE RESPUESTA:**
   - **Linea inicial**: Resumen directo de la respuesta
   - **Detalles**: Lista con vinetas (•) organizada por campus/bloque
   - **Agrupacion**: Campus → Bloque → Espacio/Horario
   - **Claridad**: Se conciso pero informativo

9. **MANEJO DE DATOS FALTANTES:**
   - NO uses "[no especificado]" - indica que falta
   - Ejemplo CORRECTO: "La informacion del campus no esta disponible en los datos actuales"
   - Ofrece alternativas: "Para mas detalles, consulta el horario academico"

10. **DIFERENCIACIÓN CUL/CUC:**
    - SIEMPRE especifica a cual universidad pertenece la informacion
    - Los bloques pueden tener mismos nombres: "Bloque A (Campus CUL)" vs "Bloque A (Campus CUC)"
    - Si hay informacion de ambas universidades, separalas claramente

=== EJEMPLOS DE RESPUESTAS ===

**Pregunta: "?Que profesores dan matematicas?"**
"El profesor Carlos Ruiz dicta Matematicas en el aula A101 (Bloque A, Campus CUL) de 8:00 a 10:00 los lunes y miercoles."

**Pregunta: "?Donde dan clases los lunes?"**
"En el Campus CUL, Bloque A:
• Carlos Ruiz dicta Matematicas en aula A101 (piso 1) de 8:00 a 10:00
• Ana Perez dicta Fisica en aula A102 (piso 1) de 10:00 a 12:00

En el Campus CUC, Bloque B:
• Maria Gomez dicta Programacion en aula B201 (piso 2) de 14:00 a 16:00"

**Pregunta: "?Que aulas estan disponibles?"**
"En el Campus CUL hay 3 aulas disponibles:
Bloque A: Aula A101 (tipo: aula, piso 1, capacidad 30), Aula A102 (tipo: laboratorio, piso 1, capacidad 25)
Bloque B: Aula B201 (tipo: aula, piso 2, capacidad 40)"

Respuesta:"""

def prompt_sql_rapido():
    """Prompt SQL reducido para velocidad"""
    return """Genera SQL PostgreSQL conciso para universidad CUL/CUC.

Tablas: campus(id_campus,nombre), bloques(id_bloque,id_campus,nombre),
instalaciones(id_instalacion,id_bloque,capacidad,nombre),
asignacion_instalaciones(id_persona,id_materia,id_instalacion,dia_semana,hora_inicio,hora_fin),
personas(id_persona,nombre), materias(id_materia,nombre), roles(id_rol,nombre_rol),
persona_rol(id_persona,id_rol)

Reglas: INNER JOIN para relaciones, EXTRACT(EPOCH FROM (hora_fin-hora_inicio))/3600 para horas,
GROUP BY con agregaciones, ORDER BY para rankings.

SQL:"""

def prompt_respuesta_rapido():
    """Prompt respuesta reducido"""
    return """Responde en español natural sobre universidad CUL/CUC.

DATOS:
{datos}

INSTRUCCIONES:
- Responde claro y conciso
- Incluye números específicos
- Estructura información lógicamente
- Si no hay datos, di que no se encontraron

RESPUESTA:"""
