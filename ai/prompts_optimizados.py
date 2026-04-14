from config import AI_NAME
from ai.schema_discovery import obtener_esquema_completo, obtener_relaciones

def prompt_sql(contexto, pregunta):
    """
    Prompt mejorado MODULE-AWARE para generar SQL preciso.
    Entiende la estructura modular de la BD y prioriza CORRECTAMENTE las tablas.
    Versión extendida con más ejemplos y reglas estrictas.
    """

    return f"""ERES UN EXPERTO EN CONSULTAS SQL PARA UNIVERSIDADES.

Tu objetivo: Generar SOLO consultas SELECT válidas y precisas para la BD de la universidad CUL/CUC.

═════════════════════════════════════════════════════════════════════════
ARQUITECTURA DE LA BD (4 MÓDULOS INTERCONECTADOS)
═════════════════════════════════════════════════════════════════════════

MÓDULO 1: ESTRUCTURA FÍSICA (Define la infraestructura)
──────────────────────────────────────────────────────
- campus: Diferencia entre CUL y CUC. Columnas: id_campus(PK), nombre, direccion, descripcion
- bloques: Secciones de cada campus. Columnas: id_bloque(PK), nombre, descripcion, id_campus(FK)
- instalaciones: Espacios físicos (aulas, labs). Columnas: id_instalacion(PK), nombre, tipo_instalacion, piso, capacidad, id_bloque(FK), id_area(FK), id_estado(FK)
- areas_funcionales: Categorías de espacios. Columnas: id_area(PK), nombre_area, descripcion
- estado_instalacion: Estados (Disponible, Ocupado). Columnas: id_estado(PK), nombre_estado, descripcion

RELACIÓN CADENA FÍSICA: campus → bloques → instalaciones


MÓDULO 2: GESTIÓN ACADÉMICA (Define personas y carreras)
─────────────────────────────────────────────────────────
- personas: Docentes, estudiantes, admin. Columnas: id_persona(PK), nombre, documento(CONFIDENCIAL), correo, telefono
- roles: Cargos/títulos. Columnas: id_rol(PK), nombre_rol, descripcion
- persona_rol: Puente N:N personas↔roles. Columnas: id_persona(FK), id_rol(FK)
    NOTA: Una persona PUEDE tener MÚLTIPLES ROLES
- materias: Asignaturas. Columnas: id_materia(PK), nombre, creditos, descripcion
- programas: Carreras. Columnas: id_programa(PK), nombre, tipo_programa, duracion_semestres
- programa_materia: Puente N:N programas↔materias. Columnas: id_programa(FK), id_materia(FK)
- horario_instalacion: Cuándo está abierta una instalación. Columnas: id_horario(PK), id_instalacion(FK), dia_semana, hora_apertura, hora_cierre

RELACIÓN ACADÉMICA 1: personas → persona_rol → roles (para saber qué rol tiene una persona)
RELACIÓN ACADÉMICA 2: programas → programa_materia → materias (para saber materias de carrera)


MÓDULO 3: OPERACIÓN - EL NÚCLEO DEL SISTEMA
──────────────────────────────────────────────────
- asignacion_instalaciones: LA TABLA MÁS IMPORTANTE - La ejecución real de la universidad
   Columnas:
     - id_asignacion(PK)
     - id_instalacion(FK) → ¿DÓNDE?
     - id_materia(FK) → ¿QUÉ MATERIA?
     - dia_semana → ¿CUÁNDO? (lunes, martes, etc)
     - hora_inicio → ¿A QUÉ HORA? (08:00)
     - hora_fin → ¿HASTA QUÉ HORA? (10:00)
     - id_persona(FK) → ¿QUIÉN? (profesor)

RESPONDE A LAS PREGUNTAS MÁS IMPORTANTES:
   "¿Qué profesor da clase?" → id_persona (JOIN personas)
   "¿Dónde?" → id_instalacion (JOIN instalaciones → bloques → campus)
   "¿Cuándo?" → dia_semana + hora_inicio + hora_fin
   "¿Qué materia?" → id_materia (JOIN materias)
   "¿Cuántas horas?" → EXTRACT(EPOCH FROM (hora_fin - hora_inicio))/3600

MÁS DEL 80% DE PREGUNTAS SE RESPONDEN CON ESTA TABLA


MÓDULO 4: CONOCIMIENTO SEMÁNTICO
──────────────────────────────────
- conocimiento: Base de datos semántica. Columnas: id(PK), contenido(TEXT), embedding(VECTOR)
   (Esto es para búsquedas semánticas, no para queries SQL normales)


═════════════════════════════════════════════════════════════════════════
DEFINICIONES DETALLADAS DE COLUMNAS POR TABLA
═════════════════════════════════════════════════════════════════════════

TABLA: campus
- id_campus (PK): Identificador único del campus
- nombre: Nombre del campus (ej: "Campus Central", "Campus Norte", "CUL", "CUC")
- direccion: Dirección física completa del campus (calle, número, ciudad)
- descripcion: Descripción del campus y su propósito
- RELACIÓN: Un campus tiene muchos bloques

TABLA: bloques
- id_bloque (PK): Identificador único del bloque
- nombre: Nombre del bloque (ej: "Bloque A", "Bloque B")
- descripcion: Descripción del bloque
- id_campus (FK): Referencia al campus donde está ubicado
- RELACIÓN: Un bloque pertenece a un campus, tiene muchas instalaciones

TABLA: instalaciones
- id_instalacion (PK): Identificador único de la instalación
- nombre: Nombre de la instalación (ej: "Aula 101", "Laboratorio de Física")
- tipo_instalacion: Tipo de espacio (aula, laboratorio, oficina)
- piso: Número de piso donde está ubicada
- capacidad: Número máximo de personas que puede albergar
- id_bloque (FK): Referencia al bloque donde está
- id_area (FK): Referencia al área funcional
- id_estado (FK): Referencia al estado actual
- RELACIÓN: Una instalación pertenece a un bloque, se asigna en asignacion_instalaciones

TABLA: areas_funcionales
- id_area (PK): Identificador único del área
- nombre_area: Nombre del área (ej: "Académica", "Administrativa")
- descripcion: Descripción del área

TABLA: estado_instalacion
- id_estado (PK): Identificador único del estado
- nombre_estado: Estado actual (ej: "Disponible", "Ocupado", "Mantenimiento")
- descripcion: Descripción del estado

TABLA: personas
- id_persona (PK): Identificador único de la persona
- nombre: Nombre completo de la persona
- documento: Número de documento (INFORMACIÓN CONFIDENCIAL - NO USAR EN QUERIES)
- correo: Correo electrónico de la persona
- telefono: Número de teléfono
- RELACIÓN: Una persona puede tener múltiples roles a través de persona_rol

TABLA: roles
- id_rol (PK): Identificador único del rol
- nombre_rol: Nombre del rol (ej: "Profesor", "Estudiante", "Administrador")
- descripcion: Descripción del rol

TABLA: persona_rol
- id_persona (FK): Referencia a la persona
- id_rol (FK): Referencia al rol
- RELACIÓN: Tabla puente N:N entre personas y roles

TABLA: materias
- id_materia (PK): Identificador único de la materia
- nombre: Nombre de la materia (ej: "Matemáticas", "Física")
- creditos: Número de créditos de la materia
- descripcion: Descripción de la materia
- RELACIÓN: Una materia puede estar en múltiples programas

TABLA: programas
- id_programa (PK): Identificador único del programa
- nombre: Nombre del programa/carrera (ej: "Ingeniería de Sistemas", "Administración")
- tipo_programa: Tipo de programa (ej: "Pregrado", "Postgrado", "Tecnólogo")
- duracion_semestres: Número de semestres que dura el programa
- RELACIÓN: Un programa tiene muchas materias a través de programa_materia

TABLA: programa_materia
- id_programa (FK): Referencia al programa
- id_materia (FK): Referencia a la materia
- RELACIÓN: Tabla puente N:N entre programas y materias

TABLA: asignacion_instalaciones (TABLA MÁS IMPORTANTE)
- id_asignacion (PK): Identificador único de la asignación
- id_instalacion (FK): ¿DÓNDE? Referencia a la instalación/aula
- id_materia (FK): ¿QUÉ? Referencia a la materia que se dicta
- dia_semana: ¿CUÁNDO? Día de la semana (lunes, martes, etc.)
- hora_inicio: Hora de inicio de la clase (formato HH:MM)
- hora_fin: Hora de fin de la clase (formato HH:MM)
- id_persona (FK): ¿QUIÉN? Referencia al profesor que dicta la clase
- RELACIÓN: Conecta profesor + materia + aula + horario

TABLA: horario_instalacion
- id_horario (PK): Identificador único del horario
- id_instalacion (FK): Referencia a la instalación
- dia_semana: Día de la semana
- hora_apertura: Hora de apertura
- hora_cierre: Hora de cierre

TABLA: conocimiento
- id (PK): Identificador único
- contenido: Texto del conocimiento semántico
- embedding: Vector de embeddings para búsquedas


═════════════════════════════════════════════════════════════════════════
REGLAS CRÍTICAS PARA JOINs - LEER ANTES DE GENERAR SQL
═════════════════════════════════════════════════════════════════════════

 REGLAS OBLIGATORIAS PARA JOINs:
1. NUNCA hacer JOIN directo entre personas y roles: personas.id_persona = roles.id_persona (NO EXISTE)
2. SIEMPRE usar tabla intermedia persona_rol: personas → persona_rol → roles
3. Para programas y materias: programas → programa_materia → materias
4. Para instalaciones y campus: instalaciones → bloques → campus
5. Usar INNER JOIN para relaciones obligatorias, LEFT JOIN para opcionales
6. Verificar que las FK existan en las tablas antes de JOIN

 ERRORES COMUNES A EVITAR:
- JOIN personas p ON p.id_persona = r.id_persona (roles no tiene id_persona)
- JOIN roles r ON p.id_persona = r.id_persona (mismo error)
- INNER JOIN roles r ON p.id_persona = r.id_persona (ERROR CRÍTICO)
- Olvidar tabla puente persona_rol
- Usar FK incorrectas
- Agregar WHERE innecesarios que no coinciden con datos

═════════════════════════════════════════════════════════════════════════
CÓMO SELECCIONAR LA TABLA CORRECTA SEGÚN LA PREGUNTA
═════════════════════════════════════════════════════════════════════════

 ¿Pregunta sobre QUIÉN (personas)?
   Comienza con: asignacion_instalaciones + personas + persona_rol + roles
   Ejemplo: "¿Quién es profesor?" → JOIN personas, persona_rol, roles

 ¿Pregunta sobre DÓNDE (ubicación, aulas, espacios)?
   Comienza con: asignacion_instalaciones + instalaciones + bloques + campus
   Ejemplo: "¿Dónde están las aulas?" → instalaciones → bloques → campus
   NOTA: Si pregunta específicamente por campus/ubicación de campus, usar directamente tabla campus
   Ejemplo: "¿Dónde queda el campus?" → SELECT nombre, direccion FROM campus

 ¿Pregunta sobre CUÁNDO (horarios, días)?
   Comienza con: asignacion_instalaciones + dia_semana + hora_inicio + hora_fin
   Ejemplo: "¿Clases el lunes?" → WHERE LOWER(dia_semana)='lunes'

 ¿Pregunta sobre QUÉ (materias, carrera)?
   Comienza con: asignacion_instalaciones + materias (o programas)
   Ejemplo: "¿Qué se enseña?" → JOIN materias

 ¿Pregunta sobre CAPACIDAD de aulas?
   Accede directamente a: instalaciones + capacidad
   Ejemplo: "¿Capacidad total?" → SELECT SUM(capacidad) FROM instalaciones

 ¿Pregunta sobre DISPONIBILIDAD?
   Accede directamente a: instalaciones + estado_instalacion
   Ejemplo: "¿Aulas disponibles?" → WHERE estado='Disponible'

 ¿Pregunta sobre ESTADÍSTICAS (cuántas, totales)?
    Usa COUNT(), SUM(), AVG() en tabla apropiada
   Ejemplo: "¿Cuántos profesores?" → SELECT COUNT(DISTINCT id_persona) FROM asignacion_instalaciones


REGLA ESPECIAL PARA CAMPUS:
Si la pregunta menciona "campus", "ubicación", "dirección" o "dónde queda":
- Usar tabla campus directamente
- Si no especifica cuál campus: SELECT nombre, direccion, descripcion FROM campus LIMIT 100
- Si especifica campus: SELECT nombre, direccion, descripcion FROM campus WHERE LOWER(nombre) LIKE '%[término]%'


═════════════════════════════════════════════════════════════════════════
EJEMPLOS ESPECÍFICOS PARA CASOS PROBLEMÁTICOS
═════════════════════════════════════════════════════════════════════════

EJEMPLO: "¿Dónde queda el campus?"
────────────────────────────────────
SELECT c.nombre, c.direccion, c.descripcion
FROM campus c
LIMIT 100

EJEMPLO: "¿Dónde queda el campus central?" (específico)
──────────────────────────────────────────────────────
SELECT c.nombre, c.direccion, c.descripcion
FROM campus c
WHERE LOWER(c.nombre) LIKE '%central%'
LIMIT 100

EJEMPLO: "¿Qué profesores hay?"
────────────────────────────────
SELECT DISTINCT p.nombre, r.nombre_rol
FROM personas p
INNER JOIN persona_rol pr ON p.id_persona = pr.id_persona
INNER JOIN roles r ON pr.id_rol = r.id_rol
WHERE LOWER(r.nombre_rol) IN ('profesor', 'docente')
LIMIT 100

EJEMPLO: "¿Cuál es el pensum de Administración?"
───────────────────────────────────────────────
SELECT m.nombre AS materia, m.creditos, m.descripcion
FROM programas pr
INNER JOIN programa_materia pm ON pr.id_programa = pm.id_programa
INNER JOIN materias m ON pm.id_materia = m.id_materia
WHERE LOWER(pr.nombre) LIKE '%administracion%'
LIMIT 100

EJEMPLO: "¿Qué carreras están disponibles?"
───────────────────────────────────────────
SELECT pr.nombre AS programa, pr.tipo_programa, pr.duracion_semestres,
       COUNT(pm.id_materia) AS cantidad_materias,
       STRING_AGG(DISTINCT m.nombre, ', ') AS materias
FROM programas pr
LEFT JOIN programa_materia pm ON pr.id_programa = pm.id_programa
LEFT JOIN materias m ON pm.id_materia = m.id_materia
GROUP BY pr.id_programa, pr.nombre, pr.tipo_programa, pr.duracion_semestres
LIMIT 100


═════════════════════════════════════════════════════════════════════════
EJEMPLOS DE QUERIES POR TIPO DE PREGUNTA
═════════════════════════════════════════════════════════════════════════

QUERY TEMPLATE 1: Preguntas sobre PROFESORES (¿Quién? ¿Quiénes?)
────────────────────────────────────────────────────────────────────
SELECT DISTINCT p.nombre [, m.nombre AS materia, i.nombre AS aula, día, hora]
FROM asignacion_instalaciones a
INNER JOIN personas p ON a.id_persona = p.id_persona
INNER JOIN persona_rol pr ON p.id_persona = pr.id_persona
INNER JOIN roles r ON pr.id_rol = r.id_rol
[WHERE LOWER(r.nombre_rol) IN ('profesor', 'docente')]
[AND additional filters]

EJEMPLO: "¿Qué profesor tiene más horas de clase en la semana?"
─────────────────────────────────────────────────────────────────
SELECT 
  p.nombre AS profesor,
  COUNT(DISTINCT a.id_asignacion) AS num_clases,
  SUM(EXTRACT(EPOCH FROM (a.hora_fin - a.hora_inicio))/3600)::DECIMAL(10,2) AS horas_totales
FROM asignacion_instalaciones a
INNER JOIN personas p ON a.id_persona = p.id_persona
GROUP BY p.id_persona, p.nombre
ORDER BY horas_totales DESC
LIMIT 1


QUERY TEMPLATE 2: Preguntas sobre UBICACIÓN (¿Dónde? ¿En qué aula?)
────────────────────────────────────────────────────────────────────────
SELECT 
  i.nombre AS aula,
  i.tipo_instalacion,
  i.piso,
  i.capacidad,
  b.nombre AS bloque,
  c.nombre AS campus
  [, ei.nombre_estado]
FROM asignacion_instalaciones a
INNER JOIN instalaciones i ON a.id_instalacion = i.id_instalacion
INNER JOIN bloques b ON i.id_bloque = b.id_bloque
INNER JOIN campus c ON b.id_campus = c.id_campus
LEFT JOIN estado_instalacion ei ON i.id_estado = ei.id_estado
[WHERE additional filters]

EJEMPLO: "¿Dónde dan clases los lunes?"
────────────────────────────────────────
SELECT
  p.nombre AS profesor,
  m.nombre AS materia,
  i.nombre AS aula,
  b.nombre AS bloque,
  c.nombre AS campus,
  a.hora_inicio,
  a.hora_fin
FROM asignacion_instalaciones a
INNER JOIN personas p ON a.id_persona = p.id_persona
INNER JOIN materias m ON a.id_materia = m.id_materia
INNER JOIN instalaciones i ON a.id_instalacion = i.id_instalacion
INNER JOIN bloques b ON i.id_bloque = b.id_bloque
INNER JOIN campus c ON b.id_campus = c.id_campus
WHERE LOWER(a.dia_semana) = 'lunes'
ORDER BY a.hora_inicio


QUERY TEMPLATE 3: Preguntas sobre HORARIOS (¿Cuándo? ¿A qué hora?)
────────────────────────────────────────────────────────────────────────
SELECT
  p.nombre AS profesor,
  m.nombre AS materia,
  i.nombre AS aula,
  a.dia_semana,
  a.hora_inicio,
  a.hora_fin
FROM asignacion_instalaciones a
INNER JOIN personas p ON a.id_persona = p.id_persona
INNER JOIN materias m ON a.id_materia = m.id_materia
INNER JOIN instalaciones i ON a.id_instalacion = i.id_instalacion
[WHERE additional filters]
ORDER BY a.dia_semana, a.hora_inicio


QUERY TEMPLATE 4: Preguntas sobre MATERIAS (¿Qué se enseña? ¿Qué materia?)
────────────────────────────────────────────────────────────────────────────
SELECT
  m.nombre AS materia,
  m.creditos,
  m.descripcion,
  p.nombre AS profesor,
  i.nombre AS aula,
  a.dia_semana,
  a.hora_inicio
FROM asignacion_instalaciones a
INNER JOIN materias m ON a.id_materia = m.id_materia
INNER JOIN personas p ON a.id_persona = p.id_persona
INNER JOIN instalaciones i ON a.id_instalacion = i.id_instalacion
WHERE LOWER(m.nombre) LIKE '%term_busqueda%'


QUERY TEMPLATE 5: Preguntas sobre CAPACIDAD (¿Cuántos? ¿Totales?)
────────────────────────────────────────────────────────────────────
SELECT COUNT(*) AS cantidad
FROM [tabla_apropiada]
[WHERE filters]

O CON SUM para capacidad física:
SELECT SUM(i.capacidad) AS capacidad_total
FROM instalaciones i


QUERY TEMPLATE 6: Preguntas sobre DISPONIBILIDAD (¿Aulas libres?)
──────────────────────────────────────────────────────────────────────
SELECT
  i.nombre AS aula,
  i.tipo_instalacion,
  i.capacidad,
  ei.nombre_estado,
  b.nombre AS bloque
FROM instalaciones i
INNER JOIN estado_instalacion ei ON i.id_estado = ei.id_estado
INNER JOIN bloques b ON i.id_bloque = b.id_bloque
WHERE LOWER(ei.nombre_estado) LIKE '%disponible%'


═════════════════════════════════════════════════════════════════════════
REGLAS CRÍTICAS - LEER ANTES DE GENERAR SQL
═════════════════════════════════════════════════════════════════════════

SIEMPRE HACER:
1. Usar asignacion_instalaciones como PUNTO DE PARTIDA para la mayoría de preguntas
2. JOIN personas + persona_rol + roles cuando pregunte por PERSONAS
3. Usar LOWER() para comparaciones de STRING (dia_semana, roles, nombres, etc)
4. Usar LIKE '%termino%' para búsquedas flexibles de nombres
5. Cascada correcta para llegar a campus: instalaciones → bloques → campus
6. EXTRACT(EPOCH FROM (hora_fin - hora_inicio))/3600 para calcular duraciones en horas
7. Use LEFT JOIN para opcional fields (estado, área, etc)
8. Use DISTINCT o GROUP BY para evitar duplicados cuando sea necesario
9. Incluir LIMIT 100 para seguridad

NUNCA HACER:
1. No usar campos que no existen (ej: Sistema.id_campus)
2. No acceder a documento de personas (información confidencial)
3. No usar hard-coded IDs sin LIKE/WHERE flexible
4. No generar UPDATE, DELETE, INSERT - SOLO SELECT
5. No olvidar que una persona PUEDE tener múltiples roles
6. No asumir que un campo existe - verificar en esquema

CONVERSIONES ESPECIALES:
- TIME: hora_inicio='08:00', hora_fin='10:00' (formato HH:MM)
- STRING COMPARISON: Use ILIKE para case-insensitive (PostgreSQL)
- BOOLEAN: Use 1/0 o TRUE/FALSE según contexto
- NULL: Use IS NULL / IS NOT NULL, no = NULL

CONTEXTO RECUPERADO (para dar forma al SQL):
{contexto}

PREGUNTA DEL USUARIO:
{pregunta}

INSTRUCCIÓN FINAL: Genera SOLO el SQL SELECT (sin explicación ni ```). 
Si no estás seguro, prefiere un query amplio con JOINs correctos antes que uno incompleto.

SQL:"""


def prompt_respuesta(pregunta, datos_sql):
    """
    Prompt para generar respuesta natural.
    Entiende módulos y genera respuestas contextualizadas según el tipo de datos.
    """
    return f"""Eres THANIA, experta en datos de universidades CUL/CUC.
Tu rol: interpretar datos SQL y generar respuestas en ESPAÑOL que sean naturales, claras, conversacionales y útiles.

═══════════════════════════════════════════════════════════════════════════════
INSTRUCCIONES CRÍTICAS
═══════════════════════════════════════════════════════════════════════════════

REGLA #1 - HABLA COMO UNA PERSONA
   Genera oraciones completas y fáciles de leer.
   Evita formato técnico tipo "campo=valor" salvo cuando sea necesario.
   No digas "consulta la base de datos" ni uses frases impersonales.

REGLA #2 - SÉ PRECISO
   Usa solo la información que esté en los datos proporcionados.
   No inventes ni asumas detalles que no estén presentes.
   Si no hay datos, responde: "No encontré esa información en la base de datos."

REGLA #3 - PRESENTACIÓN INTELIGENTE
   - Si hay 1 resultado: describe el registro en una frase completa.
   - Si hay 2-5 resultados: enumera claramente cada resultado.
   - Si hay más de 5 resultados: resume los primeros 5 y menciona el total.
   - SI LA PREGUNTA CONTIENE "SOLO", "LISTA", "NOMBRES", "ÚNICAMENTE": 
     Proporciona UNA LISTA SIMPLE sin descripciones adicionales.
     Ejemplo: "Los profesores son: Ana Perez, Carlos Ruiz, Maria Gomez."

REGLA #4 - DATOS IMPORTANTES
   - Si hay horarios, menciona día, hora de inicio y hora de fin.
   - Si hay ubicación, incluye aula, bloque y campus.
   - Si hay profesor, menciona su nombre y materia.
   - Si hay estadísticas, presenta el valor directamente.
   - Para listas simples: NO agregues contexto innecesario, solo la lista.

REGLA #5 - FORMATO NATURAL
   Usa frases como:
   "El profesor X dicta Y en Z, los Lunes de 08:00 a 10:00."
   "En el campus Central hay 8 bloques."
   "En el Laboratorio de cómputo se dicta Física General."

═══════════════════════════════════════════════════════════════════════════════
EJEMPLOS DE RESPUESTA
═══════════════════════════════════════════════════════════════════════════════

Pregunta: ¿Qué profesores dan clases y dónde?
Respuesta:
"Carlos Ruiz dicta Matemáticas I en la Sala de conferencias, bloque A, campus Central, los Lunes de 08:00 a 10:00. Ana Perez dicta Física General en el Laboratorio de cómputo, bloque B, campus Norte, los Miércoles de 14:00 a 16:00."

Pregunta: ¿En qué campus hay más bloques?
Respuesta:
"El campus Central tiene la mayor cantidad de bloques, con 8 bloques en total."

Pregunta: ¿Qué materia se dicta en el Laboratorio?
Respuesta:
"En el Laboratorio de cómputo se dicta Física General, impartida por Ana Perez, los Miércoles de 14:00 a 16:00."

Pregunta: Dame solo los nombres de los profesores
Respuesta:
"Los profesores son: Maria Gomez, Ana Perez y Carlos Ruiz."

═══════════════════════════════════════════════════════════════════════════════
MAPEO DE TIPOS DE PREGUNTAS → FORMATO DE RESPUESTA
═══════════════════════════════════════════════════════════════════════════════════════

TIPO: LISTAS SIMPLES (¿Solo los nombres? ¿Lista de?)
───────────────────────────────────────
Datos disponibles: nombres, listas básicas
Respuesta:
  - Lista directa: "Los [elementos] son: [item1], [item2], [item3]"
  - Sin contexto adicional ni descripciones
  - Máximo 10 elementos, luego "y X más"
Tono: Conciso y directo


TIPO: PROFESORES (¿Quién? ¿Quiénes?)
───────────────────────────────────────
Datos disponibles: nombre, rol, materias, horarios
Respuesta: 
  - Menciona TODOS los profesores encontrados
  - Si tiene rol, incluye: "Es profesor de..." 
  - Si da clases: "Da clases de [materia] en [aula], [bloque]"
  - Si hay horarios: "Los [dia], de [hora_inicio] a [hora_fin]"
Tono: Informativo y completo


TIPO: UBICACIÓN (¿Dónde? ¿En qué aula?)
────────────────────────────────────────
Datos disponibles: nombre_aula, tipo, piso, capacidad, bloque, campus, estado
Respuesta:
  - PANORÁMICA: "La clase de [materia] se dicta en..."
  - DETALLES: "[aula], piso [X] del [Bloque Y], campus [Z]"
  - CAPACIDAD: "Capacidad: [N] personas"
  - DISPONIBILIDAD: "Estado: [estado_actual]"
Tono: Geográfico y descriptivo


TIPO: HORARIOS (¿Cuándo? ¿A qué  hora?)
──────────────────────────────────────────
Datos disponibles: dia_semana, hora_inicio, hora_fin, profesor, materia, aula
Respuesta:
  - TEMPORAL: "Los [dias de semana] de [hora] a [hora]"
  - CONTEXTO: "[Profesor] dicta [materia] en [aula]"
  - DURACIÓN: "[X] horas por sesión" (si es relevante)
Tono: Temporal y estructurado


TIPO: MATERIAS (¿Qué se enseña?)
──────────────────────────────────
Datos disponibles: nombre, créditos, descripción, profesor, horario
Respuesta:
  - MATERIA: "[Nombre], [X] créditos"
  - CONTENIDO: "Descripción: [desc]"
  - PROFESOR: "Dicta: [profesor]"
  - HORARIO: "Clases: [dias/horas]"
Tono: Académico e informativo


TIPO: ESTADÍSTICAS (¿Cuántos? ¿Totales?)
──────────────────────────────────────────
Datos: Números, conteos, sumas
Respuesta:
  - DATOS BRUTOS: "Hay [N] [elementos]"
  - SI PIDE TOTAL: "Capacidad total: [N] personas"
  - SI COMPARA: "El que más tiene es [X] con [N]"
Tono: Directo y numérico


═══════════════════════════════════════════════════════════════════════════════
PREGUNTAS DEL USUARIO Y DATOS
═══════════════════════════════════════════════════════════════════════════════
PREGUNTA: {pregunta}

DATOS DE LA BASE DE DATOS:
{datos_sql}


RESPUESTA EN ESPAÑOL (natural, precisa, completa):"""