# RESUMEN: TEST DE PRECISION CON 10 PREGUNTAS COMPLEJAS

**Fecha**: 2026-03-23  
**Versión**: 0.0.3-TESTING  
**Estado**: Listo para ejecutar

---

## QUE SE HA PREPARADO

Se ha diseñado un **test completo de precisión** que valida si el sistema THANIA interpreta correctamente las relaciones entre todas las **14 tablas** de la base de datos universitaria.

### Archivos Creados

| Archivo | Proposito | Ubicacion |
|---------|-----------|-----------|
| `test_interactivo.py` | Script Python interactivo (recomendado) | `scripts/` |
| `test_precision_10_preguntas.py` | Script de test automatizado | `scripts/` |
| `TEST_PRECISION_10_PREGUNTAS.md` | Documentacion detallada de cada test | `docs/` |
| `GUIA_TEST_PRECISION.md` | Guia completa de ejecucion | `docs/` |
| `test_run.bat` | Script batch para Windows | raiz |

---

## LAS 10 PREGUNTAS COMPLEJAS

Cada pregunta valida un aspecto diferente de las relaciones entre tablas:

### 1️⃣ Tabla Puente
**Pregunta**: "¿Quiénes son los profesores?"  
**Valida**: FK + tabla puente (persona_rol)  
**Ruta BD**: personas ← persona_rol → roles  

### 2️⃣ ILIKE Automático
**Pregunta**: "¿Cuál es el correo de Juan Pérez?"  
**Valida**: Búsqueda parcial + campo específico  
**Esperado**: juan.perez@universidad.edu  

### 3️⃣ 4 JOINs Encadenados (CRÍTICO)
**Pregunta**: "¿En qué aulas se dictan clases los lunes?"  
**Valida**: asignacion→instalaciones→bloques→campus  
**Esperado**: Aula 101, Bloque B, Campus CUL  

### 4️⃣ Agregación
**Pregunta**: "¿Cuál es la capacidad total de las instalaciones?"  
**Valida**: SUM(capacidad)  
**Esperado**: 120 personas  

### 5️⃣ FK con 2 JOINs
**Pregunta**: "¿Dónde está el Laboratorio 201?"  
**Valida**: instalaciones→bloques→campus  
**Esperado**: Bloque C, Campus CUC, 25 personas  

### 6️⃣ FK Inversa
**Pregunta**: "¿Cuál es el horario de la Dra. María García?"  
**Valida**: personas←asignacion  
**Esperado**: Múltiples clases con días/horas  

### 7️⃣ FK Bidireccional
**Pregunta**: "¿Qué materias se dictan en el Aula 101?"  
**Valida**: aula←asignacion→materias  
**Esperado**: Matemáticas (Lunes) + Física (Martes)  

### 8️⃣ COUNT con Filtro
**Pregunta**: "¿Cuántas aulas hay en el Bloque B?"  
**Valida**: COUNT() + WHERE en FK  
**Esperado**: 2 aulas  

### 9️⃣ Búsqueda en Tabla Referenciada
**Pregunta**: "¿Quién dicta Programación?"  
**Valida**: materias←asignacion→personas  
**Esperado**: Dr. Juan Pérez  

### 🔟 FK con Filtro en Tabla Puente
**Pregunta**: "¿Qué profesor da clases el miércoles?"  
**Valida**: WHERE en asignacion + FK  
**Esperado**: Dr. Juan Pérez (Programación)  

---

## DATOS REALES EXTRAIDOS

Se han extraído datos reales de la BD que se usan en las preguntas:

```
Personas:
  - ID 1: Dr. Juan Pérez (juan.perez@universidad.edu) - Profesor
  - ID 2: Dra. María García (maria.garcia@universidad.edu) - Profesor
  - ID 3: Carlos López (carlos.lopez@universidad.edu) - Estudiante

Instalaciones:
  - Aula 101 (50p) - Bloque B - Campus CUL
  - Aula 102 (40p) - Bloque B - Campus CUL
  - Laboratorio 201 (25p) - Bloque C - Campus CUC
  - Oficina 301 (5p) - Bloque A - Campus CUL

Asignaciones:
  - Juan Pérez: Matemáticas (Lunes 08:00-10:00) en Aula 101
  - María García: Física (Martes 10:00-12:00) en Aula 101
  - Juan Pérez: Programación (Miércoles 14:00-16:00) en Aula 102
  - María García: Base de Datos (Jueves 08:00-11:00) en Laboratorio 201
```

---

## COMO EJECUTAR EL TEST

### Opción 1: Script Interactivo (RECOMENDADO)

```powershell
cd "C:\Users\Richar\Desktop\IA 0.0.3"
.\.venv\Scripts\python.exe .\scripts\test_interactivo.py
```

**Ventajas:**
- Ves cada paso de ejecución
- Presionas ENTER para continuar
- 5-10 minutos total
- Ideal para revisar SQL generado

### Opción 2: App Normal

```powershell
cd "C:\Users\Richar\Desktop\IA 0.0.3"
.\.venv\Scripts\python.exe .\app.py
```

Luego copia-pega las 10 preguntas manualmente.

### Opción 3: Archivo Batch

```cmd
C:\Users\Richar\Desktop\IA 0.0.3\test_run.bat
```

---

## CRITERIOS DE EVALUACION

### Por Pregunta
- ✓ SQL generado correctamente
- ✓ Identifica tablas corrientes
- ✓ Respuesta coherente
- ✓ Longitud ≤ 900 caracteres
- ✓ Sin errores de FK

### Overall
| Tasa | Evaluación | Acción |
|------|-----------|--------|
| 90-100% | LISTO PRODUCCION | Commit. Versión final |
| 70-89% | FUNCIONAL | Revisar fallos. Ajustes menores |
| <70% | REQUIERE AJUSTES | Debuguear JOINs/FK |

---

## QUE VALIDA CADA PREGUNTA

```
Q1: persona_rol (tabla puente) - Si falla: no entiende uniones N:N
Q2: ILIKE conversion - Si falla: búsquedas no toleran variaciones
Q3: JOINs profundos - Si falla: no puede encadenar 4+ tablas
Q4: Agregaciones - Si falla: no interpreta SUM/COUNT
Q5: FK inversas - Si falla: no sigue relaciones "hacia atrás"
Q6: Multiple results - Si falla: trunca cuando hay múltiples
Q7: Multiple JOINs - Si falla: no puede partir desde aula
Q8: COUNT + WHERE - Si falla: filtros incorrectos en COUNT
Q9: Referenciadas - Si falla: no busca en tablas intermedias
Q10: Complex WHERE - Si falla: problemas combinando filtros + FK
```

---

## CAMBIOS RECIENTES (Sesion Actual)

Se ha mejorado el sistema antes del test:

### 1. Serialización de datetime.time
**Archivo**: `pipeline/human_response.py`
- Ahora convierte `datetime.time(8, 0)` → `"08:00"`
- También convierte Decimal, bool, etc
- Las respuestas se ven legibles

### 2. Inclusión de correo en respuestas
**Archivo**: `pipeline/generate_sql.py`
- Detecta palabras clave: "correo", "email", "contacto"
- Agrega automáticamente campos `p.correo, p.telefono` al SELECT
- Pregunta #2 funcionará correctamente

### 3. Respuestas más humanas + Límite de caracteres
**Archivo**: `ai/prompts_optimizados.py` + `pipeline/human_response.py`
- Nuevo prompt con instrucciones de tono amigable
- Máximo 900 caracteres por respuesta (truncamiento automático)
- Função `_truncar_respuesta_si_es_necesario()`
- Respuestas fallback mejoradas

---

## PROXIMOS PASOS

### Inmediato
1. Ejecutar `test_interactivo.py`
2. Tomar nota de qué preguntas fallan
3. Si todas pasan: mover a producción

### Si Algunas Fallan
1. Revisar SQL generado vs esperado
2. Revisar logs de Ollama
3. Ajustar prompts en `ai/prompts_optimizados.py`
4. Re-ejecutar

### Si Muchas Fallan
1. Verificar que PostgreSQL está corriendo
2. Verificar que Ollama llama3 está disponible
3. Revisar `pipeline/generate_sql.py` heurísticas
4. Aumentar contexto en `ai/retrieval.py`

---

## DOCUMENTACION DE REFERENCIA

| Documento | Contenido |
|-----------|-----------|
| `TEST_PRECISION_10_PREGUNTAS.md` | Cada test + SQL esperado + soluciones |
| `GUIA_TEST_PRECISION.md` | Como ejecutar + criterios + troubleshooting |
| `README.md` | Información general del sistema |
| `ESTADO_DEL_SISTEMA.md` | Status de v0.0.3 |

---

## NOTA IMPORTANTE

**Este test valida si el sistema entiende relaciones complejas de BD**, no solo queries simples.

Si el 90%+ de preguntas pasan, significa que:
- ✓ FK están correctamente mapeadas
- ✓ Tablas puente se interpretan
- ✓ JOINs múltiples funcionan
- ✓ Búsquedas ILIKE automáticas
- ✓ Respuestas humanizadas y concisas

[LISTO PARA PRODUCCION]

---

**Creado**: 2026-03-23 10:46 UTC  
**Por**: GitHub Copilot (Claude Haiku)  
**Para**: Validación de Precisión THANIA v0.0.3  

```
Ejecuta el test: .\.venv\Scripts\python.exe .\scripts\test_interactivo.py
```
