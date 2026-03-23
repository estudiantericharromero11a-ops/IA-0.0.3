# GUIA DE TEST: VALIDACION DE PRECISION CON 10 PREGUNTAS COMPLEJAS

## INTRODUCCION

Se ha preparado un **test completo de precisión** para validar que el sistema THANIA entienda correctamente:

✓ Foreign Keys (FK) entre tablas  
✓ Tablas puente (persona_rol, programa_materia)  
✓ Múltiples JOINs encadenados  
✓ Relaciones bidireccionales  
✓ Búsquedas con ILIKE automático  
✓ Agregaciones (SUM, COUNT)  
✓ Truncamiento de respuestas (máximo 900 caracteres)  

---

## COMO EJECUTAR EL TEST

### OPCION 1: Interfaz Interactiva (RECOMENDADO)

```bash
cd "C:\Users\Richar\Desktop\IA 0.0.3"
.venv\Scripts\python.exe scripts/test_interactivo.py
```

**Ventajas:**
- Presionas ENTER para ver cada pregunta
- Ves SQL generado Y respuesta final
- Puedes revisar cada paso
- Tiempo estimado: 5-10 minutos (30s por pregunta x 10)

### OPCION 2: Via app.py (Modo Interactivo Normal)

```bash
cd "C:\Users\Richar\Desktop\IA 0.0.3"
.venv\Scripts\python.exe app.py
```

Luego copia-pega estas 10 preguntas una por una:

1. ¿Quiénes son los profesores?
2. ¿Cuál es el correo de Juan Pérez?
3. ¿En qué aulas se dictan clases los lunes?
4. ¿Cuál es la capacidad total de las instalaciones?
5. ¿Dónde está el Laboratorio 201?
6. ¿Cuál es el horario de la Dra. María García?
7. ¿Qué materias se dictan en el Aula 101?
8. ¿Cuántas aulas hay en el Bloque B?
9. ¿Quién dicta Programación?
10. ¿Qué profesor da clases el miércoles?

---

## QUE SE VALIDA EN CADA PREGUNTA

### Pregunta 1: FK + Tabla Puente
```
Pregunta: "¿Quiénes son los profesores?"
Validaciones:
  ✓ Detecta dos tablas: personas Y roles
  ✓ Usa tabla puente: persona_rol
  ✓ Resultado: Juan Pérez y María García
```

### Pregunta 2: ILIKE + Campo Específico
```
Pregunta: "¿Cuál es el correo de Juan Pérez?"
Validaciones:
  ✓ Convierte búsqueda exacta a ILIKE
  ✓ Incluye correo en SELECT
  ✓ Resultado: juan.perez@universidad.edu
```

### Pregunta 3: 4 JOINs Encadenados (CRÍTICO)
```
Pregunta: "¿En qué aulas se dictan clases los lunes?"
Camino: asignacion_instalaciones → instalaciones → bloques → campus
Validaciones:
  ✓ Encadena 4 JOINs sin errores
  ✓ Filtra correctamente por día
  ✓ Incluye ubicación completa (aula, bloque, campus)
```

### Pregunta 4: Agregación (SUM)
```
Pregunta: "¿Cuál es la capacidad total?"
Validaciones:
  ✓ Usa SUM(capacidad)
  ✓ Resultado: 120 personas (50+40+25+5)
```

### Pregunta 5: FK Ubicación Completa
```
Pregunta: "¿Dónde está el Laboratorio 201?"
Path: instalaciones → bloques → campus
Validaciones:
  ✓ 2 JOINs correctos
  ✓ Incluye: nombre, bloque, campus, capacidad
```

### Pregunta 6: FK Inversa
```
Pregunta: "¿Cuál es el horario de María García?"
Path: personas ← asignacion_instalaciones
Validaciones:
  ✓ Encuentra múltiples clases de una persona
  ✓ Incluye: materias, días, horarios
```

### Pregunta 7: FK Bidireccional
```
Pregunta: "¿Qué materias se dictan en el Aula 101?"
Path: aula ← asignacion → materias
Path: aula ← asignacion → profesores
Validaciones:
  ✓ Múltiples relaciones desde una tabla
```

### Pregunta 8: COUNT con Filtro
```
Pregunta: "¿Cuántas aulas hay en el Bloque B?"
Validaciones:
  ✓ COUNT() + filtro por bloque
  ✓ Resultado: 2 aulas
```

### Pregunta 9: Buscar en Tabla Referenciada
```
Pregunta: "¿Quién dicta Programación?"
Path: materias ← asignacion → personas
Validaciones:
  ✓ Búsqueda en tabla intermedia
  ✓ Resultado: Juan Pérez
```

### Pregunta 10: FK con Filtro
```
Pregunta: "¿Qué profesor da clases el miércoles?"
Validaciones:
  ✓ Filtro en tabla puente
  ✓ Resultado: Juan Pérez (Programación)
```

---

## CRITERIOS DE EXITO

| Test | Criterio | Si Falla = Problema |
|------|----------|---------------------|
| 1 | Detecta tabla puente | No entiende persona_rol |
| 2 | ILIKE automático | No convierte = a LIKE |
| 3 | 4 JOINs encadenados | No puede hacer JOINs profundos |
| 4 | Agregaciones | No interpreta SUM/COUNT |
| 5 | Ubicación completa | No sigue FKs de FOREIGN KEY |
| 6 | FK inversa | No encuentra relaciones "hacia atrás" |
| 7 | JOINs múltiples | No puede FROM -> JOIN -> JOIN |
| 8 | Filtros con COUNT | Filtros incorrectos |
| 9 | Búsqueda en tablas | No entiende referencias |
| 10 | Combine filtro + FK | Problemas con WHERE + JOIN |

---

## RESULTADOS ESPERADOS

Datos en Base de Datos:
```
Personas: Dr. Juan Pérez, Dra. María García, Carlos López
Profesores (persona_rol): Juan Pérez, María García
Asignaciones (4 total):
  - Juan Pérez: Matemáticas (Lunes 8-10), Programación (Miércoles 14-16)
  - María García: Física (Martes 10-12), Base de Datos (Jueves 8-11)
```

---

## EJECUCION PASO A PASO

Cuando ejecutes `test_interactivo.py`, verás:

```
================================================================================
TEST INTERACTIVO DE PRECISION: 10 PREGUNTAS COMPLEJAS
================================================================================

PREGUNTA #1
-----------
Pregunta: ¿Quiénes son los profesores?
Tipo: FK + Tabla Puente (persona_rol)

Presiona ENTER para ejecutar la pregunta...

[1/3] Generando SQL...
  SQL: SELECT DISTINCT p.nombre FROM personas p ...
[2/3] Ejecutando query...
  Resultados: 2 filas
[3/3] Generando respuesta (timeout: 30s)...

RESPUESTA:
  Los profesores que enseñan en este sistema son...
  Longitud: 87 caracteres (max 900)

EVALUACION: APROBADA

Presiona ENTER para continuar...
```

---

## INTERPRETACION DE RESULTADOS

### Tasa de Éxito ≥ 90% (Preguntas 9/10 o 10/10)
✓ **Sistema LISTO PARA PRODUCCION**
- Entiende relaciones complejas
- Maneja FK correctamente
- SQL generation es preciso

### Tasa de Éxito 70-89% (Preguntas 7-8/10)
~ **Sistema FUNCIONAL**
- Revisar preguntas fallidas
- Probablemente JOINs complejos o FK inversas
- Ajustes menores necesarios

### Tasa de Éxito < 70% (Preguntas < 7/10)
✗ **Sistema REQUIERE AJUSTES**
- Problemas en tabla puente O JOINs múltiples
- Revisar pipeline/generate_sql.py
- Revisar ai/retrieval.py para contexto

---

## SOLUCIONES SI ALGUNA PREGUNTA FALLA

### Si Pregunta 1 o 7 Falla (Tablas Puente)
Problema: No entiende persona_rol o programa_materia
Solución: Revisar `_heuristica_sql_simple()` en `pipeline/generate_sql.py`
Agregar lógica específica para tablas puente

### Si Pregunta 3 o 10 Falla (JOINs Múltiples)
Problema: No encadena JOINs correctamente
Solución: Revisar validación de complejidad SQL
Reducir límite de JOINs en `_validar_complejidad_sql()`

### Si Pregunta 6 Falla (FK Inversa)
Problema: No sigue relaciones "person ID ← tabla_intermedia"
Solución: El LLM requiere mejor contexto en prompt
Ver `ai/prompts_optimizados.py` sección ejemplos

### Si Pregunta 2 Falla (ILIKE)
Problema: No convierte = a LIKE automáticamente
Solución: `_convertir_comparacion_nombre_a_ilike()` en `generate_sql.py`
Está implementado, pero verificar regex

---

## DOCUMENTACION ASOCIADA

Archivo completo con escenarios: `docs/TEST_PRECISION_10_PREGUNTAS.md`

Este archivo contiene:
- Datos reales extraídos de la BD
- SQL esperado para cada pregunta
- Respuestas esperadas
- Criterios de validación detallados

---

## PROXIMOS PASOS TRAS VALIDACION

### Si Todas Pasan (90%+)
1. Commit a GitHub con comentario: "TEST: 10/10 preguntas complejas APROBADAS"
2. Marcar como v0.0.3-TEST-APPROVED en README
3. Considerar producción o carga de más datos

### Si Algunas Fallan (70-89%)
1. Revisar logs de Ollama en `generar_respuesta()`
2. Revisar SQL generado comparado con esperado
3. Ajustar prompts en `ai/prompts_optimizados.py`
4. Re-ejecutar test

### Si Muchas Fallan (<70%)
1. Revisar `pipeline/generate_sql.py` heurísticas
2. Verificar que Ollama está respondiendo
3. Aumentar contexto en `ai/retrieval.py`
4. Validar conocimiento en tabla `conocimiento`

---

## TIEMPO ESTIMADO

- **Ejecución interactiva**: 5-10 minutos (30s por pregunta)
- **Revisión de resultados**: 2-5 minutos
- **Ajustes si necesarios**: 15-30 minutos

---

## CONTACTO / SOPORTE

Si alguna pregunta no funciona:
1. Verificar que app.py está corriendo sin errores
2. Revisar logs de PostgreSQL
3. Verificar que Ollama está activo (`ollama run llama3`)
4. Revisar memoria de sesión en `TEST_PRECISION_10_PREGUNTAS.md`

---

**Versión**: 0.0.3-TESTING  
**Última actualización**: 2026-03-23  
**Estado**: Listo para ejecutar
