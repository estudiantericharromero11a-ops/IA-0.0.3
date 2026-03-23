# REFERENCIA RÁPIDA - ARQUITECTURA DE BASE DE DATOS THANIA

**Sistema**: THANIA v0.0.3 | **Estado**: 🟢 PRODUCCIÓN LISTA | **Validación**: 90%+ (9/10 en vivo) ⭐
**Versiones**: torch==2.3.0 | transformers==4.36.0 | sentence-transformers==3.0.1
**Reporte**: Ver [REPORTE_VALIDACION_VIVO.md](REPORTE_VALIDACION_VIVO.md) para detalles completos

## Guía de Relaciones, Flujos y Queries (Validado)

---

## 📋 TABLA DE RELACIONES (RESUMEN EJECUTIVO)

| # | Tipo | Desde | Hacia | Cardinalidad | Ejemplo |
|----|------|-------|-------|--------------|---------|
| 1 | FK:N:1 | `bloques.id_campus` | `campus.id_campus` | 1:N | Bloque A ← Campus CUL |
| 2 | FK:N:1 | `instalaciones.id_bloque` | `bloques.id_bloque` | 1:N | Aula 101 ← Bloque A |
| 3 | FK:N:1 | `instalaciones.id_area` | `areas_funcionales.id_area` | 1:N | Aula ← Área Académica |
| 4 | FK:N:1 | `instalaciones.id_estado` | `estado_instalacion.id_estado` | 1:N | Aula ← Estado: Disponible |
| 5 | FK:N:1 | `horario_instalacion.id_instalacion` | `instalaciones.id_instalacion` | 1:N | Horario ← Aula |
| 6 | **PUENTE** | `persona_rol` | `personas` ↔ `roles` | **N:N** | Ana Perez ← Profesor, Coordinadora |
| 7 | **PUENTE** | `programa_materia` | `programas` ↔ `materias` | **N:N** | Ingeniería ← Cálculo, Física, Prog |
| 8⭐ | FK:N:1x3 | `asignacion_instalaciones` | `personas`, `materias`, `instalaciones` | N:1 | **MOTOR CENTRAL** |

---

## 🔄 FLUJOS PRINCIPALES (MAPA MENTAL)

### Flujo 1: Estructura Física
```
campus ← bloques ← instalaciones ← {areas_funcionales, estado_instalacion, horario_instalacion}
```

### Flujo 2: Académico
```
personas ← persona_rol ← roles
materias ← programa_materia ← programas
```

### Flujo 3: Operación (CORE)
```
asignacion_instalaciones ← [personas, materias, instalaciones]
                         ↓
                   Conecta TODOS los flujos
```

---

## 🎯 QUERIES RÁPIDAS (COPIAR Y PEGAR)

### Query 1: ¿Qué profesor enseña X?
```sql
SELECT DISTINCT p.nombre
FROM personas p
JOIN asignacion_instalaciones Sistema ON p.id_persona = Sistema.id_persona
JOIN materias m ON Sistema.id_materia = m.id_materia
WHERE m.nombre LIKE '%X%'
```

### Query 2: ¿Dónde está la clase de X?
```sql
SELECT i.nombre, b.nombre, c.nombre, Sistema.hora_inicio, Sistema.hora_fin
FROM asignacion_instalaciones Sistema
JOIN instalaciones i ON Sistema.id_instalacion = i.id_instalacion
JOIN bloques b ON i.id_bloque = b.id_bloque
JOIN campus c ON b.id_campus = c.id_campus
WHERE Sistema.id_materia IN (SELECT id_materia FROM materias WHERE nombre LIKE '%X%')
```

### Query 3: ¿Qué clases hay el día Y?
```sql
SELECT DISTINCT m.nombre, p.nombre, i.nombre, Sistema.hora_inicio, Sistema.hora_fin
FROM asignacion_instalaciones Sistema
JOIN materias m ON Sistema.id_materia = m.id_materia
JOIN personas p ON Sistema.id_persona = p.id_persona
JOIN instalaciones i ON Sistema.id_instalacion = i.id_instalacion
WHERE LOWER(Sistema.dia_semana) = 'Y'
```

### Query 4: ¿Quién tiene rol Z?
```sql
SELECT p.nombre
FROM personas p
JOIN persona_rol pr ON p.id_persona = pr.id_persona
JOIN roles r ON pr.id_rol = r.id_rol
WHERE LOWER(r.nombre_rol) LIKE '%Z%'
```

### Query 5: TODO sobre una asignación
```sql
SELECT 
  p.nombre AS profesor,
  m.nombre AS materia,
  i.nombre AS aula,
  b.nombre AS bloque,
  c.nombre AS campus,
  e.nombre_estado AS estado,
  a.nombre_area AS area,
  Sistema.dia_semana,
  Sistema.hora_inicio,
  Sistema.hora_fin,
  i.capacidad
FROM asignacion_instalaciones Sistema
JOIN personas p ON Sistema.id_persona = p.id_persona
JOIN materias m ON Sistema.id_materia = m.id_materia
JOIN instalaciones i ON Sistema.id_instalacion = i.id_instalacion
JOIN bloques b ON i.id_bloque = b.id_bloque
JOIN campus c ON b.id_campus = c.id_campus
JOIN estado_instalacion e ON i.id_estado = e.id_estado
JOIN areas_funcionales a ON i.id_area = a.id_area
WHERE Sistema.id_asignacion = ?
```

---

## ⚠️ REGLAS CRÍTICAS DE ORO

1. **`asignacion_instalaciones` es EL CORAZÓN**: Si necesitas responder sobre clases, horarios, ubicaciones, profesores, materias → SIEMPRE pasa por esta tabla.

2. **Los nombres de columna son críticos**:
   - ✅ `roles.nombre_rol` (correcto)
   - ❌ `roles.nombre` (ERROR: no existe)
   - ✅ `personas.nombre`
   - ✅ `materias.nombre`
   - ✅ `instalaciones.nombre`

3. **Para búsquedas case-insensitive**:
   - Usa `LOWER()` o `UPPER()` en comparaciones
   - Ej: `LOWER(Sistema.dia_semana) = 'lunes'`
   - Ej: `LOWER(r.nombre_rol) LIKE '%profesor%'`

4. **Acentos en materias**: Las búsquedas deben incluir acentos
   - ✅ `WHERE m.nombre LIKE '%Matemáticas%'` (con acento)
   - ❌ `WHERE m.nombre LIKE '%Matematicas%'` (sin acento)

5. **Tabla puente vs FK normal**:
   - `persona_rol` y `programa_materia` son tablas puente (N:N)
   - Siempre necesitas 2 JOINs: persona_rol para llegar a ambas

6. **Horarios**:
   - Usa SIEMPRE `hora_inicio` Y `hora_fin` juntos
   - Nunca uses solo uno

7. **Seguridad**:
   - ❌ NO exponer `personas.documento` (CONFIDENCIAL)
   - ✅ Solo SELECT, nunca INSERT/UPDATE/DELETE
   - ✅ Enforcer LIMIT 100 en todas las queries

---

## 🧩 PATRONES COMUNES

### Patrón: Filtro por profesor
```sql
WHERE p.id_persona IN (SELECT id_persona FROM personas WHERE nombre LIKE '%Nombre%')
```

### Patrón: Filtro por día + hora
```sql
WHERE LOWER(Sistema.dia_semana) = 'lunes'
  AND Sistema.hora_inicio >= '08:00' 
  AND Sistema.hora_fin <= '18:00'
```

### Patrón: Agregación por capacidad
```sql
SELECT SUM(i.capacidad) FROM instalaciones i
```

### Patrón: Contar programas de una materia
```sql
SELECT COUNT(DISTINCT pm.id_programa)
FROM programa_materia pm
WHERE pm.id_materia = ?
```

---

## 📊 VISTA GLOBAL

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA GLOBAL THANIA                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MÓDULO FÍSICO                    MÓDULO ACADÉMICO             │
│  ═════════════                    ════════════════             │
│  campus                           personas                     │
│    ↓                                ↓                          │
│  bloques                          persona_rol (puente)        │
│    ↓                                ↓                          │
│  instalaciones ← areas              roles                      │
│    ↓              ← estado                                     │
│  horario                          materias                     │
│                                      ↓                         │
│                                   programa_materia (puente)    │
│                                      ↓                         │
│                                   programas                    │
│                                                                 │
│                    MÓDULO OPERACIÓN (⭐ CORE)                  │
│                    ════════════════════════════════            │
│                                                                 │
│            ╔════════════════════════════════════╗              │
│            ║   asignacion_instalaciones         ║              │
│            ║   (profesor + materia + aula)      ║              │
│            ╚════════════════════════════════════╝              │
│                   ↙          ↓           ↖                    │
│              personas   materias    instalaciones             │
│                                                                 │
│                  MÓDULO THANIA (VECTORIZADO - 102 registros)     │
│                  ════════════════════════════════════         │
│                                                                 │
│              conocimiento (RAG + pgvector)                     │
│              ← enlazado lógicamente a TODOS      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📖 DOCUMENTACIÓN RELACIONADA

- **[SCHEMA_DOCUMENTATION.md](SCHEMA_DOCUMENTATION.md)** - Documentación completa de cada tabla (4 módulos, 18 tablas)
- **[RELACIONES_Y_FLUJOS.md](RELACIONES_Y_FLUJOS.md)** - Flujos detallados con FK chains, ejemplos, y queries por caso

---

## 🚀 CÓMO USAR ESTA REFERENCIA

1. **Pregunta recibida** → verifica en "QUERIES RÁPIDAS"
2. **No encontrada** → busca en "FLUJOS PRINCIPALES"
3. **Dudas sobre columnas** → revisa "REGLAS CRÍTICAS"
4. **Patrón SQL personalizado** → consulta "PATRONES COMUNES"
5. **Explicación profunda** → ve a "RELACIONES_Y_FLUJOS.md"

---

## 📊 ESTADO ACTUAL - BASE DE CONOCIMIENTOS

✅ **102 Registros vectorizados en tabla `conocimiento`**
- 28 módulos y tablas
- 14 esquemas con tipos de datos
- 12 flujos y patrones básicos
- 15 reglas críticas
- 6 ejemplos reales
- **13 flujos avanzados con FK chains** ← NUEVO
- **8 relaciones con ejemplos reales** ← NUEVO
- **6 queries por flujo** ← NUEVO

**Última actualización**: 2026-03-22  
**Relaciones documentadas**: 8 (3 N:1, 2 N:N, 1 puente, 1 puente, 1 CORE)

---

## 🔥 LA FRASE GANADORA

> "Las llaves foráneas permiten integrar la estructura física con la gestión académica, y la tabla de asignaciones actúa como núcleo operacional, permitiendo responder preguntas complejas mediante la relación entre entidades. El flujo de información fluye desde campus → bloques → instalaciones ← asignaciones ← personas/materias, formando una red de consultas interconectadas."

   python -c "
   from sentence_transformers import SentenceTransformer
   modelo = SentenceTransformer('all-MiniLM-L6-v2')
   emb = modelo.encode('test')
   print(f'Embedding generado: {len(emb)} dimensiones')
   "
   ```

---

## 📞 CONTACTOS/REFERENCIAS

- **Ollama Docs:** https://ollama.Sistema
- **SentenceTransformers:** https://www.sbert.net/
- **PostgreSQL pgvector:** https://github.com/pgvector/pgvector
- **Telegram Bot API:** https://python-telegram-bot.readthedocs.io/

---

## ✅ VERIFICACIÓN POST-DEPLOY

Ejecutar este checklist después de los fixes:

```bash
# 1. Tests unitarios pasan
python -m pytest -v

# 2. Embeddings funcionan
python scripts/poblar_conocimiento.py

# 3. BD tiene datos
python -c "from database.queries import get_connection; conn = get_connection(); print('DB OK')"

# 4. Ollama responde
curl http://localhost:11434/api/tags

# 5. App local funciona
python app.py --local
# Escribir: "¿Quiénes son los profesores?"
# Esperar respuesta coherente

# 6. Bot Telegram responde
python app.py --telegram
# Enviar mensaje en Telegram
```

---

**Última actualización:** 21/03/2026
**Estado del proyecto:** Funcional pero con bugs críticos de embeddings
