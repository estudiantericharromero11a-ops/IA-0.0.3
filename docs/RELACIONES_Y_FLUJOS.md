# RELACIONES Y FLUJOS DE DATOS - Base de Datos THANIA

**Sistema**: THANIA v0.0.3 | **Estado**: 🟢 PRODUCCIÓN LISTA | **Validación**: 90%+ (9/10 en vivo) ⭐
**Reporte Detallado**: Ver [REPORTE_VALIDACION_VIVO.md](REPORTE_VALIDACION_VIVO.md)

## Análisis de Llaves Foráneas y Conectividad (8 Relaciones Críticas)

---

## 🔗 RELACIONES PRINCIPALES (8 RELACIONES CRÍTICAS)

### 🏗️ MÓDULO 1: ESTRUCTURA FÍSICA

#### **Relación 1: Campus → Bloques**
```
bloques.id_campus → campus.id_campus (N:1)
```
- **Significado**: Cada bloque pertenece a un campus
- **Cardinalidad**: Un campus ← muchos bloques
- **Ejemplo**: Campus "CUL" tiene Bloque A, Bloque B, Bloque C
- **SQL JOIN**: `bloques b JOIN campus c ON b.id_campus = c.id_campus`

#### **Relación 2: Bloques → Instalaciones**
```
instalaciones.id_bloque → bloques.id_bloque (N:1)
```
- **Significado**: Cada instalación está dentro de un bloque
- **Cardinalidad**: Un bloque ← muchas instalaciones
- **Ejemplo**: Bloque A contiene Aula 101, Aula 102, Lab A, Oficina A
- **SQL JOIN**: `instalaciones i JOIN bloques b ON i.id_bloque = b.id_bloque`

#### **Relación 3: Instalaciones → Áreas Funcionales**
```
instalaciones.id_area → areas_funcionales.id_area (N:1)
```
- **Significado**: Cada instalación tiene un área funcional
- **Cardinalidad**: Un área ← muchas instalaciones
- **Ejemplo**: Área "Académica" tiene múltiples aulas; Área "Administrativa" tiene oficinas
- **SQL JOIN**: `instalaciones i JOIN areas_funcionales a ON i.id_area = a.id_area`

#### **Relación 4: Instalaciones → Estados**
```
instalaciones.id_estado → estado_instalacion.id_estado (N:1)
```
- **Significado**: Cada instalación tiene un estado actual
- **Cardinalidad**: Un estado ← muchas instalaciones
- **Ejemplo**: Estado "Disponible", "Mantenimiento", "Clausurada"
- **SQL JOIN**: `instalaciones i JOIN estado_instalacion e ON i.id_estado = e.id_estado`

#### **Relación 5: Instalaciones → Horarios**
```
horario_instalacion.id_instalacion → instalaciones.id_instalacion (N:1)
```
- **Significado**: Cada instalación tiene horarios definidos
- **Cardinalidad**: Una instalación ← múltiples horarios
- **Ejemplo**: Aula 101 abre: Lunes-Viernes 8:00-18:00, Sábado 8:00-14:00
- **SQL JOIN**: `horario_instalacion h JOIN instalaciones i ON h.id_instalacion = i.id_instalacion`

---

### 🎓 MÓDULO 2: GESTIÓN ACADÉMICA

#### **Relación 6: Personas ↔ Roles (TABLA PUENTE)**
```
persona_rol.id_persona → personas.id_persona (N:1)
persona_rol.id_rol → roles.id_rol (N:1)
PK: (id_persona, id_rol)
```
- **Significado**: Una persona puede tener MÚLTIPLES roles
- **Cardinalidad**: Muchos a muchos (N:N)
- **Ejemplo**: 
  - Ana Perez: Profesor + Coordinadora
  - Carlos Ruiz: Profesor + Investigador
  - Maria Gomez: Estudiante + Monitor
- **SQL JOIN**: `personas p JOIN persona_rol pr ON p.id_persona = pr.id_persona JOIN roles r ON pr.id_rol = r.id_rol`

#### **Relación 7: Programas ↔ Materias (TABLA PUENTE)**
```
programa_materia.id_programa → programas.id_programa (N:1)
programa_materia.id_materia → materias.id_materia (N:1)
PK: (id_programa, id_materia)
```
- **Significado**: Un programa tiene MÚLTIPLES materias
- **Cardinalidad**: Muchos a muchos (N:N)
- **Ejemplo**:
  - Programa "Ingeniería" tiene: Cálculo I, Cálculo II, Física, Programación
  - Programa "Administración" tiene: Contabilidad, Finanzas, Administración
  - Una materia (Cálculo I) puede estar en múltiples programas
- **SQL JOIN**: `programas p JOIN programa_materia pm ON p.id_programa = pm.id_programa JOIN materias m ON pm.id_materia = m.id_materia`

---

### ⚙️ MÓDULO 3: OPERACIÓN (EL CORAZÓN)

#### **Relación 8: Asignación de Instalaciones (TABLA CENTRAL CRÍTICA)**
```
asignacion_instalaciones.id_instalacion → instalaciones.id_instalacion (N:1)
asignacion_instalaciones.id_materia → materias.id_materia (N:1)
asignacion_instalaciones.id_persona → personas.id_persona (N:1)
```
- **Significado**: CONECTA TODO - profesor + materia + aula + horario
- **Cardinalidad**: 
  - Un profesor (persona) → muchas clases
  - Una materia → muchas asignaciones (múltiples grupos, horarios)
  - Una instalación → muchas clases (diferentes materias, horarios)
- **Ejemplo**:
  - Carlos Ruiz enseña Programación → Aula 102 → Lunes 8:00-10:00
  - Carlos Ruiz enseña Programación → Aula 103 → Miércoles 10:00-12:00
  - Ana Perez enseña Matemáticas → Sala de conferencias → Lunes 8:00-10:00
- **SQL JOIN**: 
  ```sql
  asignacion_instalaciones Sistema
  JOIN personas p ON Sistema.id_persona = p.id_persona
  JOIN materias m ON Sistema.id_materia = m.id_materia
  JOIN instalaciones i ON Sistema.id_instalacion = i.id_instalacion
  ```

---

## 🧠 FLUJOS DE INFORMACIÓN

### 🎯 FLUJO 1: "¿Dónde dan clase?" (Ubicación)
```
asignacion_instalaciones
  ↓ (id_instalacion)
instalaciones
  ↓ (id_bloque)
bloques
  ↓ (id_campus)
campus
```

**Ejemplo real**:
- Pregunta: "¿Dónde está la clase de Matemáticas?"
- Flujo: Busca en asignacion_instalaciones → encuentra aula → va a instalaciones → ve bloque → va a bloques → descubre campus
- SQL:
```sql
SELECT c.nombre, b.nombre, i.nombre
FROM asignacion_instalaciones Sistema
JOIN instalaciones i ON Sistema.id_instalacion = i.id_instalacion
JOIN bloques b ON i.id_bloque = b.id_bloque
JOIN campus c ON b.id_campus = c.id_campus
WHERE Sistema.id_materia IN (SELECT id_materia FROM materias WHERE nombre LIKE '%Matemática%')
```

---

### 🎯 FLUJO 2: "¿Quién da la clase?" (Profesor)
```
asignacion_instalaciones
  ↓ (id_persona)
personas
  ↓ (puente)
persona_rol
  ↓ (id_rol)
roles
```

**Ejemplo real**:
- Pregunta: "¿Quién enseña Programación?"
- Flujo: Busca en asignacion_instalaciones → encuentra persona → verifica rol (es profesor)
- SQL:
```sql
SELECT p.nombre
FROM asignacion_instalaciones Sistema
JOIN personas p ON Sistema.id_persona = p.id_persona
JOIN materias m ON Sistema.id_materia = m.id_materia
WHERE m.nombre LIKE '%Programación%'
```

---

### 🎯 FLUJO 3: "¿Qué materia es?" (Contenido académico)
```
asignacion_instalaciones
  ↓ (id_materia)
materias
  ↓ (puente)
programa_materia
  ↓ (id_programa)
programas
```

**Ejemplo real**:
- Pregunta: "¿Qué materia se enseña el lunes en Aula 101?"
- Flujo: Busca en asignacion_instalaciones → encuentra materia → identifica programa
- SQL:
```sql
SELECT m.nombre, p.nombre AS programa
FROM asignacion_instalaciones Sistema
JOIN materias m ON Sistema.id_materia = m.id_materia
JOIN programa_materia pm ON m.id_materia = pm.id_materia
JOIN programas p ON pm.id_programa = p.id_programa
WHERE LOWER(Sistema.dia_semana) = 'lunes'
  AND Sistema.id_instalacion IN (SELECT id FROM instalaciones WHERE nombre LIKE '%Aula 101%')
```

---

### 🎯 FLUJO 4: "¿Quién tiene rol de administrador?" (Autorización)
```
personas
  ↓ (puente)
persona_rol
  ↓ (id_rol)
roles (filtro: nombre_rol LIKE '%Administrador%')
```

**Ejemplo real**:
- Pregunta: "¿Quiénes son administradores?"
- Flujo: Busca en persona_rol → filtra por rol = "Administrador" → obtiene personas
- SQL:
```sql
SELECT DISTINCT p.nombre
FROM personas p
JOIN persona_rol pr ON p.id_persona = pr.id_persona
JOIN roles r ON pr.id_rol = r.id_rol
WHERE LOWER(r.nombre_rol) LIKE '%administrador%'
```

---

## 📊 REPRESENTACIÓN VISUAL GLOBAL

```
┌─────────────┐
│   CAMPUS    │ ← Universidades (CUL, CUC)
└──────┬──────┘
       │ 1:N (id_campus)
       ↓
┌─────────────┐
│   BLOQUES   │ ← Secciones (A, B, C)
└──────┬──────┘
       │ 1:N (id_bloque)
       ↓
┌──────────────────┐
│ INSTALACIONES ◄─┼─ ÁREAS FUNCIONALES (Academic, Admin, etc.)
└──┬──────┬────────┘
   │      │ 1:N (id_estado)
   │      ↓
   │   ESTADO_INSTALACION
   │
   │ 1:N (id_instalacion)
   ↓
┌────────────────────────────────────┐
│ ASIGNACION_INSTALACIONES (⭐CORE)  │ ← Conecta TODO
└─┬──────────────┬──────────────┬────┘
  │              │              │
  │ 1:N          │ 1:N          │ 1:N
  ↓              ↓              ↓
PERSONAS    MATERIAS        INSTALACIONES
  │              │               │
  ├─ ROLES       ├─ PROGRAMAS    └─ BLOQUES
  │   (puente)   │  (puente)        (circular)
  │              │
PERSONA_ROL   PROGRAMA_MATERIA

┌──────────────┐
│ CONOCIMIENTO │ ← THANIA (conecta lógicamente con todas)
└──────────────┘
```

---

## 💥 CASOS DE USO CON CADENAS DE RELACIONES

### Caso 1: "Quiero saber TODO sobre una clase específica"
**Tabla inicial**: `asignacion_instalaciones` (id_asignacion = 5)

**Relaciones que activan**:
1. Relación 8a (id_persona) → PERSONAS → Relación 6 → ROLES
2. Relación 8b (id_materia) → MATERIAS → Relación 7 → PROGRAMAS
3. Relación 8c (id_instalacion) → Relación 2 → BLOQUES → Relación 1 → CAMPUS
4. Relación 3 (id_area) → AREAS_FUNCIONALES
5. Relación 4 (id_estado) → ESTADO_INSTALACION
6. Relación 5 (horario) → HORARIO_INSTALACION

**Resultado**: Sé EXACTAMENTE dónde, cuándo, quién, qué, con qué capacidad.

---

### Caso 2: "Mostrar disponibilidad de aulas para una materia"
**Tabla inicial**: `materias` (buscando "Programación")

**Relaciones que activan**:
1. Relación 8b ← ASIGNACION_INSTALACIONES
2. Relación 8c → INSTALACIONES → Relación 2 → BLOQUES
3. Relación 3 → AREAS_FUNCIONALES
4. Relación 4 → ESTADO_INSTALACION

**Resultado**: Todas las aulas donde se enseña Programación, dónde están, qué capacidad tienen, estado actual.

---

## 🧩 PUNTOS CLAVE PARA IMPLEMENTACIÓN

### Para la THANIA (Ollama + Retrieval):

1. **Entrada de pregunta** → busca conocimiento vectorizado
2. **Contexto recuperado** → contiene relaciones, flujos, ejemplos
3. **Generación de SQL** → usa relaciones explícitas en JOINs
4. **Validación** → confirma que respeta cardinalidad (1:N, N:N, etc.)

### Relaciones que la THANIA DEBE SABER:

| Relación | Tipo | Tabla Fuente | Tab Destino | SQL |
|----------|------|-------------|------------|-----|
| 1 | N:1 | bloques | campus | `bloques.id_campus = campus.id_campus` |
| 2 | N:1 | instalaciones | bloques | `instalaciones.id_bloque = bloques.id_bloque` |
| 3 | N:1 | instalaciones | areas | `instalaciones.id_area = areas.id_area` |
| 4 | N:1 | instalaciones | estado | `instalaciones.id_estado = estado.id_estado` |
| 5 | N:1 | horario | instalaciones | `horario.id_instalacion = instalaciones.id_instalacion` |
| 6 | N:N | personas ↔ roles | persona_rol | `persona_rol.id_persona = personas.id_persona AND persona_rol.id_rol = roles.id_rol` |
| 7 | N:N | programas ↔ materias | programa_materia | `programa_materia.id_programa = programas.id_programa AND programa_materia.id_materia = materias.id_materia` |
| 8★ | N:1 x3 | asignacion | personas, materias, instalaciones | `Sistema.id_persona = p.id_persona AND Sistema.id_materia = m.id_materia AND Sistema.id_instalacion = i.id_instalacion` |

---

## 🔥 LA FRASE GANADORA

> "Las llaves foráneas permiten integrar la estructura física con la gestión académica, y la tabla de asignaciones actúa como núcleo operacional, permitiendo responder preguntas complejas mediante la relación entre entidades. El flujo deel información fluye desde campus → bloques → instalaciones ← asignaciones ← personas/materias, formando una red de consultas interconectadas."

---
