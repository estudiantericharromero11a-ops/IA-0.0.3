# THANIA IA - Sistema Universitario (v0.0.3)

## Descripción
THANIA es un asistente de datos que convierte preguntas en lenguaje natural en SQL seguro (solo SELECT), busca en PostgreSQL y devuelve respuestas en español.

Usa RAG (Retrieval-Augmented Generation) con:
- embeddings (`sentence-transformers` + `pgvector`)
- modelo LLM local (`ollama llama3`)
- esquema universitario CUL/CUC

---

## Características principales
- Motor interactivo local (`app.py`)
- Bot Telegram opcional (`telegram_bot/bot.py`)
- Generación SQL controlada (`pipeline/generate_sql.py`)
- Ejecución con validación de esquema (`pipeline/execute_query.py`)
- Ensamblado de respuesta con datos reales (`pipeline/human_response.py`)
- Contexto semántico desde `conocimiento` (pgvector)
- Fallback por keywords + reglas heurísticas
- Seguridad: únicamente SELECT, control de placeholders y operaciones peligrosas

---

## Requisitos
- Python 3.11+
- PostgreSQL
- Virtualenv
- Dependencias en `docs/requirements.txt` (o `pip install -r docs/requirements.txt`)

Dependencias clave:
- torch==2.3.0
- transformers==4.36.0
- sentence-transformers==3.0.1
- psycopg[binary,pool]>=3.1.0
- pgvector>=0.2.0
- ollama==0.1.7

---

## Instalación rápida
1. Clonar repositorio:
   - `git clone <repo_url>`
   - `cd "IA 0.0.3"`

2. Crear y activar virtualenv (Windows):
   - `python -m venv .venv`
   - `.venv\Scripts\Activate.ps1`

3. Instalar dependencias:
   - `pip install -r docs/requirements.txt`

4. Inicializar DB:
   - `python scripts/setup_db.py`
   - `python scripts/seed_data.py`

5. Iniciar aplicación:
   - `python app.py` (modo local interactivo)
   - `python app.py --telegram` (modo bot Telegram)

---

## Uso
- Ejecuta: `python app.py`
- Preguntas tipo:
  - `¿Quiénes son los profesores?`
  - `¿Cuál es el horario de las clases?`
  - `¿Dónde está CUL?`
  - `¿Cuál es la descripción de la CUL corporación universitaria?`

---

## Estructura del proyecto
- `app.py` — entrada CLI/interactiva
- `pipeline/` — lógica de generación, ejecución, y respuesta
  - `generate_sql.py`
  - `execute_query.py`
  - `human_response.py`
- `ai/` — retrieval + LLM + prompts
  - `retrieval.py`, `llm.py`, `prompts_optimizados.py`, `config_ia.py`
- `database/` — conexión y validación de SQL
  - `queries.py`, `schema_validation.py`
- `scripts/` — setup, seed y pruebas
- `telegram_bot/` — bot Telegram

---

## Ajustes recientes en este repo
- Filtro robusto en `pipeline/generate_sql.py`: convierte comparaciones exactas `= 'CUL'` a `ILIKE '%CUL%'`
- Fallback mejorado para queries sin filas
- Validación de SQL para evitar `DROP|DELETE|UPDATE|INSERT` en ejecución

---

## Cómo contribuir
1. `git checkout -b feat/mi-cambio`
2. Cambiar código / tests
3. Probar localmente
4. `git add .` / `git commit`
5. `git push` / PR

Ideas de mejoras:
- caching de contexto en `ai/retrieval.py`
- paginación de resultados
- validación semántica de SQL más fuerte
- pruebas unitarias adicionales para `pipeline/` y `database/`

---

## Notas
- Versión validada: 0.0.3 con ~90% de acierto
- Pensado para consultas SQL de solo lectura en un entorno académico
- En producción, recomendamos controles extra de autenticación, autorización y escalado
