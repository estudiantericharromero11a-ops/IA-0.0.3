# TEST DE PRECISION: 10 PREGUNTAS COMPLEJAS CON RELACIONES ENTRE TABLAS

**Objetivo**: Validar que la IA interprete correctamente:
- Foreign Keys (FK) entre tablas
- Tablas puente (persona_rol, programa_materia)
- Múltiples JOINs
- Relaciones bidireccionales
- Precisión en respuestas

---

## DATOS REALES EN LA BD (Extraídos)

### Tablas Principales
- **CAMPUS**: ID 1 (CUL), ID 2 (CUC)
- **PERSONAS**: ID 1 (Dr. Juan Pérez - juan.perez@universidad.edu), ID 2 (Dra. María García), ID 3 (Carlos López)
- **ROLES**: ID 1 (Profesor), ID 2 (Estudiante), ID 3 (Administrativo)
- **MATERIAS**: ID 1 (Matemáticas-3 créditos), ID 2 (Física-4 créditos), ID 3 (Programación-3 créditos), ID 4 (Base de Datos-3 créditos)
- **INSTALACIONES**: ID 1 (Aula 101-50p), ID 2 (Aula 102-40p), ID 3 (Laboratorio 201-25p), ID 4 (Oficina 301-5p)
- **BLOQUES**: ID 1 (Bloque A-Campus 1), ID 2 (Bloque B-Campus 1), ID 3 (Bloque C-Campus 2)
- **ASIGNACION_INSTALACIONES**: 4 registros con profesores+materias+aulas+horarios

### Tabla Puente persona_rol
```
Persona ID 1 (Juan Pérez) -> Rol 1 (Profesor)
Persona ID 2 (María García) -> Rol 1 (Profesor)
Persona ID 3 (Carlos López) -> Rol 2 (Estudiante)
```

### Tabla Central asignacion_instalaciones
```
Prof: Juan Pérez | Materia: Matemáticas | Aula: 101 | Lunes 08:00-10:00
Prof: María García | Materia: Física | Aula: 101 | Martes 10:00-12:00
Prof: Juan Pérez | Materia: Programación | Aula: 102 | Miércoles 14:00-16:00
Prof: María García | Materia: Base de Datos | Laboratorio 201 | Jueves 08:00-11:00
```

---

## TEST #1: FK Simple - Tabla Puente
**Pregunta**: "¿Quiénes son los profesores?"
**Tipo**: Tabla puente persona_rol
**Tablas**: personas <- persona_rol -> roles
**Relación**: persona_rol.id_persona FK -> personas.id_persona
**SQL Esperado**: 
```sql
SELECT DISTINCT p.nombre 
FROM personas p 
LEFT JOIN persona_rol pr ON p.id_persona = pr.id_persona
LEFT JOIN roles r ON pr.id_rol = r.id_rol
WHERE LOWER(r.nombre_rol) = 'profesor'
```
**Respuesta Esperada**: "Los profesores son: Dr. Juan Pérez y Dra. María García"
**Validación**: ✓ Debe identificar tabla puente y relaciones FK

---

## TEST #2: Campo Específico con ILIKE
**Pregunta**: "¿Cuál es el correo de Juan Pérez?"
**Tipo**: Búsqueda por nombre parcial + campo específico
**Tablas**: personas
**Relación**: ILIKE en personas.nombre
**SQL Esperado**:
```sql
SELECT p.nombre, p.correo 
FROM personas p 
WHERE p.nombre ILIKE '%Juan%'
```
**Respuesta Esperada**: "Dr. Juan Pérez: juan.perez@universidad.edu"
**Validación**: ✓ Debe convertir = a ILIKE y incluir correo

---

## TEST #3: Múltiples JOINs (4 Tablas)
**Pregunta**: "¿En qué aulas se dictan clases los lunes?"
**Tipo**: Multiples JOINs con filtro
**Tablas**: asignacion_instalaciones -> personas, materias, instalaciones -> bloques -> campus
**Relaciones**: 
- asignacion.id_instalacion FK -> instalaciones.id_instalacion
- instalaciones.id_bloque FK -> bloques.id_bloque
- bloques.id_campus FK -> campus.id_campus
**SQL Esperado**:
```sql
SELECT p.nombre, m.nombre, i.nombre, b.nombre, c.nombre, a.hora_inicio, a.hora_fin
FROM asignacion_instalaciones a
JOIN personas p ON a.id_persona = p.id_persona
JOIN materias m ON a.id_materia = m.id_materia
JOIN instalaciones i ON a.id_instalacion = i.id_instalacion
JOIN bloques b ON i.id_bloque = b.id_bloque
JOIN campus c ON b.id_campus = c.id_campus
WHERE LOWER(a.dia_semana) = 'lunes'
```
**Respuesta Esperada**: "Juan Pérez dicta Matemáticas en Aula 101 (Bloque B, Campus CUL) de 8:00 a 10:00"
**Validación**: ✓ Debe encadenar 4 JOINs correctamente

---

## TEST #4: Agregación (SUM)
**Pregunta**: "¿Cuál es la capacidad total de las instalaciones?"
**Tipo**: Agregación con SUM
**Tablas**: instalaciones
**Relación**: Ninguna (solo cálculo)
**SQL Esperado**:
```sql
SELECT SUM(capacidad) AS capacidad_total FROM instalaciones
```
**Respuesta Esperada**: "La capacidad total es de 120 personas (50+40+25+5)"
**Validación**: ✓ Debe usar SUM correctamente

---

## TEST #5: FK con 2 JOINs + Ubicación Completa
**Pregunta**: "¿Dónde está el Laboratorio 201 y cuál es su capacidad?"
**Tipo**: FK con ubicación completa
**Tablas**: instalaciones -> bloques -> campus
**Relaciones**:
- instalaciones.id_bloque FK -> bloques.id_bloque
- bloques.id_campus FK -> campus.id_campus
**SQL Esperado**:
```sql
SELECT i.nombre, i.capacidad, b.nombre, c.nombre
FROM instalaciones i
JOIN bloques b ON i.id_bloque = b.id_bloque
JOIN campus c ON b.id_campus = c.id_campus
WHERE i.nombre ILIKE '%Laboratorio 201%'
```
**Respuesta Esperada**: "El Laboratorio 201 está en el Bloque C (Campus CUC) con capacidad para 25 personas"
**Validación**: ✓ Debe incluir ubicación completa

---

## TEST #6: FK Inversa - Persona a Asignación
**Pregunta**: "¿Cuál es el horario de la Dra. María García?"
**Tipo**: FK inversa (persona -> asignacion)
**Tablas**: personas, asignacion_instalaciones
**Relaciones**: personas.id_persona <- asignacion_instalaciones.id_persona FK
**SQL Esperado**:
```sql
SELECT p.nombre, m.nombre, a.dia_semana, a.hora_inicio, a.hora_fin
FROM personas p
JOIN asignacion_instalaciones a ON p.id_persona = a.id_persona
JOIN materias m ON a.id_materia = m.id_materia
WHERE p.nombre ILIKE '%María García%'
```
**Respuesta Esperada**: "La Dra. María García dicta Física los martes de 10:00 a 12:00 y Base de Datos los jueves de 8:00 a 11:00"
**Validación**: ✓ Debe encontrar múltiples clases de una persona

---

## TEST #7: FK Bidireccional
**Pregunta**: "¿Qué materias se dictan en el Aula 101?"
**Tipo**: FK bidireccional (instalacion <- asignacion -> materia)
**Tablas**: instalaciones, asignacion_instalaciones, materias
**Relaciones**:
- asignacion.id_instalacion FK -> instalaciones.id_instalacion
- asignacion.id_materia FK -> materias.id_materia
**SQL Esperado**:
```sql
SELECT DISTINCT m.nombre, p.nombre, a.dia_semana
FROM asignacion_instalaciones a
JOIN instalaciones i ON a.id_instalacion = i.id_instalacion
JOIN materias m ON a.id_materia = m.id_materia
JOIN personas p ON a.id_persona = p.id_persona
WHERE i.nombre ILIKE '%Aula 101%'
```
**Respuesta Esperada**: "En el Aula 101 se dictan: Matemáticas (lunes, Prof. Juan Pérez) y Física (martes, Prof. María García)"
**Validación**: ✓ Debe mostrar múltiples relaciones desde la aula

---

## TEST #8: COUNT con Filtro
**Pregunta**: "¿Cuántas aulas hay en el Bloque B?"
**Tipo**: COUNT con filtro en FK
**Tablas**: bloques, instalaciones
**Relaciones**: instalaciones.id_bloque FK -> bloques.id_bloque
**SQL Esperado**:
```sql
SELECT COUNT(*) AS cantidad
FROM instalaciones i
JOIN bloques b ON i.id_bloque = b.id_bloque
WHERE b.nombre ILIKE '%Bloque B%'
```
**Respuesta Esperada**: "Hay 2 aulas en el Bloque B (Aula 101 y Aula 102)"
**Validación**: ✓ Debe contar correctamente

---

## TEST #9: Buscar por Nombre en Tabla Referenciada
**Pregunta**: "¿Quién dicta Programación y en qué horario?"
**Tipo**: Búsqueda por nombre en tabla referenciada
**Tablas**: materias, asignacion_instalaciones, personas
**Relaciones**:
- asignacion.id_materia FK -> materias.id_materia
- asignacion.id_persona FK -> personas.id_persona
**SQL Esperado**:
```sql
SELECT p.nombre, m.nombre, a.dia_semana, a.hora_inicio, a.hora_fin
FROM asignacion_instalaciones a
JOIN personas p ON a.id_persona = p.id_persona
JOIN materias m ON a.id_materia = m.id_materia
WHERE m.nombre ILIKE '%Programación%'
```
**Respuesta Esperada**: "Dr. Juan Pérez dicta Programación los miércoles de 14:00 a 16:00"
**Validación**: ✓ Debe buscar en tabla puente correctamente

---

## TEST #10: FK con Filtro en Tabla Puente
**Pregunta**: "¿Qué profesor da clases el miércoles?"
**Tipo**: FK con filtro en tabla puente (asignacion_instalaciones)
**Tablas**: asignacion_instalaciones, personas
**Relaciones**: asignacion.id_persona FK -> personas.id_persona
**SQL Esperado**:
```sql
SELECT DISTINCT p.nombre, m.nombre, a.dia_semana
FROM asignacion_instalaciones a
JOIN personas p ON a.id_persona = p.id_persona
JOIN materias m ON a.id_materia = m.id_materia
WHERE LOWER(a.dia_semana) = 'miércoles'
```
**Respuesta Esperada**: "El Dr. Juan Pérez da clases el miércoles (Programación de 14:00 a 16:00)"
**Validación**: ✓ Debe filtrar correctamente por día

---

## CRITERIOS DE VALIDACION

| Criterio | Detalle |
|----------|---------|
| **Precisión SQL** | SQL generado es válido y accede a tablas correctas |
| **FK Correctas** | Relaciones entre tablas resueltas (usuario <- tabla_puente -> rol) |
| **JOINs Múltiples** | Puede encadenar 3+ JOINs sin errores |
| **ILIKE** | Convierte búsquedas exactas a ILIKE automáticamente |
| **Longitud Respuesta** | Máximo 900 caracteres (truncamiento automático) |
| **Coherencia Datos** | Respuesta contiene datos reales de la BD |
| **Formato** | Respuesta Natural en español, no SQL |
| **Tasa de Éxito** | Mínimo 7/10 preguntas correctas (70%) |

---

## EJECUCION ESPERADA

```
Pregunta #1 (Tabla Puente): SQL generado + ejecutado + respuesta natural
Pregunta #2 (ILIKE): SQL con conversión automática
Pregunta #3 (4 JOINs): Encadena correctamente instalaciones->bloques->campus
...
Pregunta #10 (FK Filtro): Identifica tabla puente y aplica filter

RESULTADO: X/10 preguntas correctas
```

---

## NOTAS IMPORTANTES

1. **Tablas Puente son Críticas**: persona_rol y programa_materia requieren JOINs especiales
2. **ILIKE Automático**: El sistema debe convertir = a ILIKE automáticamente
3. **FK Inversas**: Algunos datos fluyen "hacia atrás" (persona <= asignacion)
4. **Truncamiento**: Respuestas >900 caracteres se cortan automáticamente
5. **Relaciones Complejas**: Test #3 requiere 4 JOINs encadenados (CRÍTICO)

---

## EVALUACION FINAL ESPERADA

- **90-100%**: Sistema LISTO PARA PRODUCCION
- **70-89%**: Sistema FUNCIONAL (revisar fallos)
- **<70%**: Sistema REQUIERE AJUSTES (especialmente en JOINs)
