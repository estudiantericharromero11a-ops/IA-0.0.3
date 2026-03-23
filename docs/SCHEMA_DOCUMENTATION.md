# Documentación del Esquema de Base de Datos - THANIA

**Sistema**: THANIA v0.0.3 | **Estado**: 🟢 PRODUCCIÓN LISTA | **Validación**: 90%+ (9/10 en vivo) ⭐
**Schema**: 12 tablas + 8 relaciones | **Embeddings**: 102+ documentados
**Reporte de Precisión**: Ver [REPORTE_VALIDACION_VIVO.md](REPORTE_VALIDACION_VIVO.md)

## Sistema de Gestión Universitaria (CUL/CUC)

---

## MÓDULO 1: ESTRUCTURA FÍSICA

### Tabla: `campus`
**Propósito**: Diferencia las universidades (CUL y CUC son dos universidades en una misma).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_campus` | PK | Llave única e identificador de la universidad |
| `nombre` | VARCHAR | Nombre de la universidad (ej: CUL, CUC) |
| `direccion` | VARCHAR | Dirección física de la universidad |
| `descripcion` | TEXT | Descripción y definición de la universidad |

**Relaciones**:
- Un campus tiene muchos `bloques` (1:N)
- Un campus puede tener muchas `instalaciones` (1:N indirecta a través de bloques)

---

### Tabla: `bloques`
**Propósito**: Define los bloques/secciones dentro de cada universidad (Bloque A, Bloque B, etc.).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_bloque` | PK | Llave única del bloque |
| `nombre` | VARCHAR | Nombre del bloque (A, B, C, etc.) |
| `descripcion` | TEXT | Descripción del bloque |
| `id_campus` | FK → campus | Identifica a qué campus/universidad pertenece |

**Relaciones**:
- Un bloque pertenece a un campus (N:1)
- Un bloque contiene muchas instalaciones (1:N)

---

### Tabla: `instalaciones`
**Propósito**: Define espacios físicos (aulas, oficinas, laboratorios, salas de conferencias, etc.).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_instalacion` | PK | Llave única de la instalación |
| `nombre` | VARCHAR | Nombre de la instalación (Aula 101, Lab A, etc.) |
| `tipo_instalacion` | VARCHAR | Tipo (aula, administrativa, biblioteca, laboratorio, etc.) |
| `piso` | INT | Número de piso (1, 2, 3, -1 para sótano, etc.) |
| `capacidad` | INT | Cantidad de personas que puede ocupar |
| `id_bloque` | FK → bloques | Bloque a que pertenece |
| `id_area` | FK → areas_funcionales | Área funcional a que pertenece |
| `id_estado` | FK → estado_instalacion | Estado actual de la instalación |

**Relaciones**:
- Una instalación pertenece a un bloque (N:1)
- Una instalación pertenece a un área funcional (N:1)
- Una instalación tiene un estado (N:1)
- Una instalación puede tener múltiples horarios (1:N)
- Una instalación puede ser asignada a clases (1:N)

---

### Tabla: `areas_funcionales`
**Propósito**: Categoriza áreas dentro de la universidad (Administración, Académica, Servicios, etc.).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_area` | PK | Llave única del área |
| `nombre_area` | VARCHAR | Nombre del área funcional |
| `descripcion` | TEXT | Descripción del área |

---

### Tabla: `estado_instalacion`
**Propósito**: Define posibles estados de una instalación (Disponible, Mantenimiento, Clausurada, etc.).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_estado` | PK | Llave única del estado |
| `nombre_estado` | VARCHAR | Nombre del estado (Disponible, Mantenimiento, etc.) |
| `descripcion` | TEXT | Descripción del estado (ej: "Disponible = instalación libre para uso") |

---

### Tabla: `horario_instalacion`
**Propósito**: Define horarios de disponibilidad de cada instalación.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_horario` | PK | Llave única del horario |
| `id_instalacion` | FK → instalaciones | Instalación a la que pertenece el horario |
| `dia_semana` | VARCHAR | Día de la semana (Lunes, Martes, etc.) |
| `hora_apertura` | TIME | Hora de apertura (ej: 08:00) |
| `hora_cierre` | TIME | Hora de cierre (ej: 18:00) |

**Relaciones**:
- Un horario pertenece a una instalación (N:1)
- Una instalación puede tener múltiples horarios (1:N)

---

## MÓDULO 2: GESTIÓN ACADÉMICA

### Tabla: `personas`
**Propósito**: Registro de todas las personas en la universidad (docentes, estudiantes, administrativos, etc.).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_persona` | PK | Llave única de la persona |
| `nombre` | VARCHAR | Nombre completo de la persona |
| `documento` | VARCHAR | Documento de identidad (ÚNICO, confidencial) |
| `correo` | VARCHAR | Correo institucional de la persona |
| `telefono` | VARCHAR | Teléfono de la persona |

**Relaciones**:
- Una persona puede tener múltiples roles (1:N a través de persona_rol)
- Una persona puede asignar clases (1:N a través de asignacion_instalaciones)

**Confidencialidad**: El documento no debe darse a todo el mundo (requiere permisos).

---

### Tabla: `roles`
**Propósito**: Define los roles/cargos que puede tener una persona (Estudiante, Profesor, Admin, etc.).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_rol` | PK | Llave única del rol |
| `nombre_rol` | VARCHAR | Nombre del rol (Estudiante, Profesor, Administrador, etc.) |
| `descripcion` | TEXT | Descripción o definición del rol |

---

### Tabla: `persona_rol`
**Propósito**: Tabla puente que relaciona personas con roles (una persona puede tener múltiples roles).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_persona` | FK → personas | Identifica la persona |
| `id_rol` | FK → roles | Identifica el rol |

**PK**: (`id_persona`, `id_rol`)

**Nota**: Una persona puede ser Profesor Y Coordinador simultáneamente.

---

### Tabla: `materias`
**Propósito**: Define las materias/asignaturas de los programas académicos.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_materia` | PK | Llave única de la materia |
| `nombre` | VARCHAR | Nombre de la materia (Matemáticas, Física, etc.) |
| `creditos` | INT | Créditos/dificultad de la materia |
| `descripcion` | TEXT | Descripción o definición de la materia |

**Relaciones**:
- Una materia puede pertenecer a múltiples programas (N:N a través de programa_materia)
- Una materia puede ser asignada en múltiples horarios (1:N a través de asignacion_instalaciones)

---

### Tabla: `programas`
**Propósito**: Define las carreras universitarias (Ingeniería, Administración, etc.).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_programa` | PK | Llave única de la carrera |
| `nombre` | VARCHAR | Nombre del programa/carrera |
| `tipo_programa` | VARCHAR | Tipo (Pregrado, Postgrado, Técnico, etc.) |
| `duracion_semestres` | INT | Duración en semestres |

**Relaciones**:
- Un programa contiene múltiples materias (1:N a través de programa_materia)

---

### Tabla: `programa_materia`
**Propósito**: Tabla puente que relaciona programas con materias (un programa tiene muchas materias).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_programa` | FK → programas | Identifica el programa |
| `id_materia` | FK → materias | Identifica la materia |

**PK**: (`id_programa`, `id_materia`)

---

## MÓDULO 3: OPERACIÓN (MOTOR PRINCIPAL)

### Tabla: `asignacion_instalaciones` ⭐ CRÍTICA
**Propósito**: **MOTOR CENTRAL** de la base de datos. Conecta TODO: profesor + materia + aula + horario.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_asignacion` | PK | Llave única de la asignación |
| `id_instalacion` | FK → instalaciones | ¿Dónde se da la clase? |
| `id_materia` | FK → materias | ¿Qué materia se enseña? |
| `dia_semana` | VARCHAR | ¿Qué día? (Lunes, Martes, etc.) |
| `hora_inicio` | TIME | ¿A qué hora comienza? |
| `hora_fin` | TIME | ¿A qué hora termina? |
| `id_persona` | FK → personas | ¿Quién enseña? (profesor) |

**Relaciones**:
- Una asignación pertenece a una instalación (N:1)
- Una asignación pertenece a una materia (N:1)
- Una asignación es impartida por una persona/profesor (N:1)

**IMPORTANCIA**: 
- Para saber "qué clases hay el lunes": filtra por `dia_semana='Lunes'`
- Para saber "en dónde está la clase de Matemáticas": JOIN con materias y filtra por `nombre LIKE '%Matemática%'`
- Para saber "a qué hora comienza": usa `hora_inicio`
- Para saber "quién enseña": JOIN con personas
- Esta tabla es la respuesta a **la mayoría de las preguntas de consultas**

---

## MÓDULO 4: CONOCIMIENTO (THANIA)

### Tabla: `conocimiento`
**Propósito**: Base de conocimiento para el sistema RAG. Contiene contexto vectorizado para búsquedas semánticas.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | PK | Llave única |
| `contenido` | TEXT | Texto de contexto (esquema, relaciones, flujo, ejemplos) |
| `embedding` | VECTOR(384) | Vector de embeddings (SentenceTransformer all-MiniLM-L6-v2) |

---

## FLUJO DE DATOS PARA RESPONDER PREGUNTAS

### Patrón 1: "¿Qué profesor enseña X materia?"
```sql
SELECT DISTINCT p.nombre
FROM personas p
JOIN asignacion_instalaciones Sistema ON p.id_persona = Sistema.id_persona
JOIN materias m ON Sistema.id_materia = m.id_materia
WHERE m.nombre LIKE '%X%'
```

### Patrón 2: "¿Dónde está la clase de X?"
```sql
SELECT DISTINCT i.nombre, b.nombre
FROM instalaciones i
JOIN bloques b ON i.id_bloque = b.id_bloque
JOIN asignacion_instalaciones Sistema ON i.id_instalacion = Sistema.id_instalacion
JOIN materias m ON Sistema.id_materia = m.id_materia
WHERE m.nombre LIKE '%X%'
```

### Patrón 3: "¿Qué clases hay el Y?"
```sql
SELECT DISTINCT m.nombre, p.nombre, i.nombre, Sistema.hora_inicio, Sistema.hora_fin
FROM materias m
JOIN asignacion_instalaciones Sistema ON m.id_materia = Sistema.id_materia
JOIN personas p ON Sistema.id_persona = p.id_persona
JOIN instalaciones i ON Sistema.id_instalacion = i.id_instalacion
WHERE LOWER(Sistema.dia_semana) = LOWER('Y')
```

### Patrón 4: "¿Quién tiene rol de Z?"
```sql
SELECT p.nombre
FROM personas p
JOIN persona_rol pr ON p.id_persona = pr.id_persona
JOIN roles r ON pr.id_rol = r.id_rol
WHERE LOWER(r.nombre_rol) LIKE '%Z%'
```

### Patrón 5: "¿Cuál es la capacidad total de instalaciones?"
```sql
SELECT SUM(capacidad) AS capacidad_total
FROM instalaciones
```

---

## PUNTOS CLAVE PARA LA THANIA

1. **`asignacion_instalaciones` es el corazón**: Si genera esta tabla, puede responder casi cualquier pregunta sobre horarios, ubicaciones, materias y profesores.

2. **Campos importantes**:
   - `personas.nombre`: Nombres de profesores/estudiantes (usar LIKE '%nombre%' para búsquedas)
   - `materias.nombre`: Nombres de materias (usar LIKE '%nombre%' para búsquedas, incluir acentos)
   - `instalaciones.nombre`: Nombres de aulas/espacios
   - `roles.nombre_rol`: Tipos de roles (NO `r.nombre`, usar siempre `r.nombre_rol`)
   - `dia_semana`: Usar LOWER() para comparaciones case-insensitive
   - `hora_inicio`/`hora_fin`: Siempre juntas para horarios completos

3. **Relaciones FK→tabla**:
   - `bloques.id_campus` → `campus`
   - `instalaciones.id_bloque` → `bloques`
   - `instalaciones.id_area` → `areas_funcionales`
   - `instalaciones.id_estado` → `estado_instalacion`
   - `horario_instalacion.id_instalacion` → `instalaciones`
   - `asignacion_instalaciones.id_instalacion → instalaciones`
   - `asignacion_instalaciones.id_materia` → `materias`
   - `asignacion_instalaciones.id_persona` → `personas`
   - `persona_rol.id_persona` → `personas`
   - `persona_rol.id_rol` → `roles`
   - `programa_materia.id_programa` → `programas`
   - `programa_materia.id_materia` → `materias`

4. **Tablas puentes** (N:N):
   - `persona_rol`: Personas ↔ Roles
   - `programa_materia`: Programas ↔ Materias

5. **NO inventar información**: Los datos están EN LA BD, solo consultar con JOINs correctos.

6. **LÍMITES** (seguridad):
   - No acceder a `personas.documento` sin autorización
   - Máximo 100 filas por query (LIMIT 100)
   - Solo SELECT, NO INSERT/UPDATE/DELETE

---
