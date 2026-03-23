# QUICK START: EJECUTA EL TEST AHORA

## TL;DR - En 30 Segundos

```powershell
cd "C:\Users\Richar\Desktop\IA 0.0.3"
.\.venv\Scripts\python.exe .\scripts\test_interactivo.py
```

**Duración**: 5-10 minutos (30s por pregunta x 10)  
**Resultado final**: Tasa de éxito % que indica si sistema está listo  

---

## LOS 3 PASOS

### Paso 1: Abre PowerShell
```
Windows Key → Type "PowerShell" → Enter
```

### Paso 2: Navega al directorio
```powershell
cd "C:\Users\Richar\Desktop\IA 0.0.3"
```

### Paso 3: Ejecuta el test
```powershell
.\.venv\Scripts\python.exe .\scripts\test_interactivo.py
```

---

## QUE PASARÁ

```
===============================================================
TEST INTERACTIVO DE PRECISION: 10 PREGUNTAS COMPLEJAS
===============================================================

PREGUNTA #1
-----------
Pregunta: ¿Quiénes son los profesores?
Tipo: FK + Tabla Puente (persona_rol)

Presiona ENTER para ejecutar la pregunta...
```

Presionas ENTER → Ve SQL generado → Ve respuesta → Ve resultado → Repite para Q2-Q10

---

## CUANDO TERMINE

Verás algo como:

```
RESUMEN FINAL
=============

Resultados por pregunta:
  Q1: ¿Quiénes son los profesores? [APROBADA]
  Q2: ¿Cuál es el correo de Juan Pérez? [APROBADA]
  Q3: ¿En qué aulas se dictan clases los lunes? [APROBADA]
  ...

TASA DE EXITO: 90.0% (9/10 preguntas aprobadas)

CONCLUSION: Sistema LISTO PARA PRODUCCION
===========================================
```

---

## INTERPRETACIÓN RÁPIDA

| Resultado | Significado | Acción |
|-----------|-----------|--------|
| 🟢 90-100% | COMPLETAMENTE LISTO | ✓ Producción |
| 🟡 70-89% | FUNCIONAL | ~ Revisar fallos |
| 🔴 <70% | REVISAR | ✗ Ajustes necesarios |

---

## SI ALGO FALLA

**Error**: "ModuleNotFoundError"  
**Solución**: Asegúrate que estás en el directorio correcto

**Error**: "Timeout en Ollama"  
**Solución**: Ollama no está corriendo. Ejecuta:
```powershell
ollama run llama3
# En otra terminal
```

**Pregunta sin respuesta**  
**Solución**: Es normal para algunos JOINs complejos. Anota cuál falló.

---

## ARCHIVOS IMPORTANTES POR SI NECESITAS

| Archivo | Para qué |
|---------|----------|
| `TEST_RESUMEN.md` | Resumen completo de todo |
| `TEST_PRECISION_10_PREGUNTAS.md` | Detalles de cada test |
| `GUIA_TEST_PRECISION.md` | Guía completa + troubleshooting |
| `app.py` | Para probar manualmente |

---

## DESPUES DEL TEST

### Si Todas Pasan (90%+)
```
Sistema LISTO PARA PRODUCCION
✓ Sube cambios a GitHub
✓ Vers ión 0.0.3 confirmada
```

### Si Algunas Fallan (70-89%)
```
Revisar qué pregunta falló
→ Ver documentación en TEST_PRECISION_10_PREGUNTAS.md
→ Ajustar si necesario
→ Re-ejecutar
```

### Si Pocas Pasan (<70%)
```
Problema serio. Necesitas debuguear:
→ Revisar pipeline/generate_sql.py
→ Aumentar contexto en ai/retrieval.py
→ Revisar prompts en ai/prompts_optimizados.py
```

---

## NOTAS

✓ Se han mejorado respuestas para ser más humanas  
✓ Se truncan automáticamente a 900 caracteres  
✓ Se incluyen emails cuando pregunta sobre contacto  
✓ datetime.time ahora muestra "08:00" no "datetime.time(8, 0)"  

---

## COMANDO COMPLETO (Copiar-Pegar)

```powershell
cd "C:\Users\Richar\Desktop\IA 0.0.3"; .\.venv\Scripts\python.exe .\scripts\test_interactivo.py
```

---

**¡LISTO! Ejecuta y dame saber los resultados** 🚀
