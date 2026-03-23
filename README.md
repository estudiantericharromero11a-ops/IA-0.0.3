# THANIA IA - Sistema Universitario (v0.0.3)

## ¿Qué es THANIA?

THANIA es un **asistente inteligente** que responde preguntas sobre una universidad (datos sobre profesores, clases, horarios, instalaciones, etc.) **sin necesidad de escribir código ni queries SQL**.

En lugar de escribir comandos complicados, puedes hacer preguntas naturales como:
- "¿Quiénes son los profesores de matemáticas?"
- "¿Dónde se dicta física?"
- "¿Cuál es el horario de la clase de programación?"

Y **THANIA automáticamente**:
1. Entiende tu pregunta con IA
2. Busca la información en la base de datos
3. Te da una respuesta clara en español

### ¿Cómo funciona internamente?

THANIA usa tres tecnologías principales:

- **RAG (Retrieval-Augmented Generation)**: Un sistema que primero busca información relevante, luego genera respuestas precisas.
- **LLM (Modelo de Lenguaje)**: Usa Ollama + llama3 para entender preguntas de lenguaje natural.
- **PostgreSQL**: Base de datos que almacena toda la información de la universidad.

---

## Requisitos previos

### 1. Software que necesitas instalar

Antes de empezar, asegúrate de tener instalado:

- **Python 3.11+** (descarga desde https://www.python.org/)
  - En Windows, marca "Add Python to PATH" durante la instalación
  
- **PostgreSQL 13+** (descarga desde https://www.postgresql.org/)
  - Durante la instalación, recuerda tu contraseña de postgres
  
- **Git** (descarga desde https://git-scm.com/)
  - Para clonar el repositorio

- **Ollama** (descarga desde https://ollama.ai/)
  - Necesario para el modelo de IA llama3
  - Ejecuta en una terminal: `ollama serve`
  - Si no está el modelo: `ollama pull llama3`

- **pgvector** (operaciones de vectores en PostgreSQL)

### 2. Verifica que todo está instalado

Abre una terminal (PowerShell en Windows) y comprueba:

```bash
python --version          # Debe mostrar Python 3.11 o superior
psql --version           # Debe mostrar PostgreSQL 13 o superior
git --version            # Debe mostrar git version
```

Si alguno no funciona, revisa la instalación.

---

## Instalación paso a paso

### Paso 1: Descarga el código

Abre terminal y ejecuta:

```bash
git clone https://github.com/estudiantericharromero11a-ops/IA-0.0.3.git
cd "IA 0.0.3"
```

Esto descarga todo el código en tu computadora.

### Paso 2: Crea un ambiente virtual (virtualenv)

Un "ambiente virtual" es un espacio aislado donde instalaremos las librerías de Python sin afectar tu sistema.

```bash
python -m venv .venv
```

Luego **activa** el ambiente virtual:

**En Windows PowerShell:**
```bash
.venv\Scripts\Activate.ps1
```

**En Mac/Linux:**
```bash
source .venv/bin/activate
```

Verás que el prompt cambia a algo como `(.venv) PS C:\...>` (indica que el ambiente está activo).

### Paso 3: Instala las dependencias

```bash
pip install -r docs/requirements.txt
```

Esto descarga e instala todas las librerías necesarias (puede tomar 5-10 minutos).

### Paso 4: Configura la base de datos

Crea un archivo `.env` en la raíz del proyecto con la información de tu base de datos:

```
DATABASE_URL=postgresql://postgres:tu_contraseña@localhost:5432/thania_db
TELEGRAM_TOKEN=tu_token_telegram_aqui_opcional
```

Reemplaza `tu_contraseña` con tu contraseña de PostgreSQL.

### Paso 5: Inicializa la base de datos

```bash
python scripts/setup_db.py
```

Esto crea todas las tablas necesarias en PostgreSQL.

### Paso 6: Carga datos de ejemplo

```bash
python scripts/seed_data.py
```

Esto inserta datos básicos (campus, bloques, personas, etc.).

### Paso 7: Carga el contexto semántico (IA)

```bash
python scripts/poblar_conocimiento.py
```

Esto prepara el sistema de IA con información sobre la estructura de la base de datos.

### Paso 8: ¡Ejecuta la aplicación!

```bash
python app.py
```

Deberías ver algo como:

```
================================================================================
Sistema Universitario THANIA - MODO LOCAL INTERACTIVO
================================================================================

Tu pregunta: 
```

¡Ahora puedes hacer preguntas! Intenta:
```
Tu pregunta: ¿Quiénes son los profesores?
```

Presiona Enter y THANIA buscará la respuesta.

---

## Uso práctico

### Modo interactivo (por defecto)

```bash
python app.py
```

Aquí puedes hacer preguntas una por una. Escribe `salir` para terminar.

### Preguntas de ejemplo que funcionan

```
¿Cuál es la descripción de CUL?
¿Dónde están las aulas del bloque A?
¿Quiénes dictan programación?
¿Cuál es el horario de clase el lunes?
¿Qué materias tiene el programa de ingeniería?
```

### Modo una sola pregunta

```bash
python app.py "¿Quiénes son los profesores?"
```

### Modo Telegram (opcional)

Si configuraste un token de Telegram en `.env`:

```bash
python app.py --telegram
```

---

## Estructura del proyecto explicada

```
IA 0.0.3/
├── app.py                    # Punto de entrada - interfaz de usuario
├── config.py                 # Configuración principal
│
├── ai/                       # Módulo de Inteligencia Artificial
│   ├── retrieval.py         # Busca información (RAG)
│   ├── llm.py               # Comunicación con Ollama
│   ├── prompts_optimizados.py # Plantillas de preguntas al LLM
│   └── config_ia.py         # Palabras clave del sistema
│
├── pipeline/                 # Flujo de procesamiento
│   ├── generate_sql.py       # Genera SQL desde preguntas
│   ├── execute_query.py      # Ejecuta SQL en la DB
│   └── human_response.py     # Formatea respuestas en español
│
├── database/                 # Gestión de base de datos
│   ├── queries.py            # Conexión a PostgreSQL
│   └── schema_validation.py  # Valida que SQL sea seguro
│
├── scripts/                  # Scripts de utilidad
│   ├── setup_db.py          # Crea las tablas
│   ├── seed_data.py         # Inserta datos de ejemplo
│   ├── poblar_conocimiento.py # Prepara la IA
│   └── test_precision.py    # Prueba la precisión
│
└── docs/                     # Documentación
    └── requirements.txt      # Lista de librerías necesarias
```

### ¿Qué hace cada parte?

**ai/retrieval.py**
- Busca información relevante en la base de datos
- Usa embeddings (vectores) para entender el significado, no solo palabras exactas

**pipeline/generate_sql.py**
- Convierte tu pregunta en lenguaje natural a SQL
- Usa el modelo IA para generar queries que busquen exactamente lo que preguntaste

**pipeline/execute_query.py**
- Ejecuta la consulta SQL en PostgreSQL
- Valida que solo sean consultas seguras (solo SELECT, nunca elimina datos)

**pipeline/human_response.py**
- Toma los datos de la base de datos y genera una respuesta en español
- Asegura que la respuesta sea útil y no técnica

---

## Bases de datos: Las 14 tablas

THANIA organiza la información en 14 tablas:

### Tablas de Estructura Física
- **campus**: Las universidades (CUL, CUC)
- **bloques**: Edificios dentro de cada campus
- **instalaciones**: Aulas, oficinas, laboratorios
- **areas_funcionales**: Tipos de espacios (académico, administrativo)
- **estado_instalacion**: Si está disponible, ocupado, etc.
- **horario_instalacion**: Horarios en que se usan los espacios

### Tablas de Gestión Académica
- **personas**: Profesores, estudiantes, administrativos
- **roles**: Qué rol tiene cada persona
- **persona_rol**: Tabla que conecta personas con sus roles
- **materias**: Las asignaturas
- **programas**: Las carreras universitarias
- **programa_materia**: Tabla que conecta carreras con sus materias

### Tabla Central (el corazón del sistema)
- **asignacion_instalaciones**: Conecta: profesor + materia + aula + horario
  - Responde: ¿Quién enseña? ¿Qué? ¿Dónde? ¿Cuándo?

### Tabla de IA
- **conocimiento**: Almacena información para el sistema de IA con embeddings

---

## Solución de problemas (FAQ)

### "ModuleNotFoundError: No module named 'torch'"
**Problema:** Las librerías no se instalaron correctamente.
**Solución:**
```bash
pip install torch==2.3.0
pip install -r docs/requirements.txt
```

### "FATAL: Ident authentication failed for user 'postgres'"
**Problema:** La contraseña de PostgreSQL es incorrecta.
**Solución:** Revisa tu archivo `.env` y asegúrate de que `DATABASE_URL` tiene la contraseña correcta.

### "No se encontraron datos"
**Problema:** La base de datos está vacía.
**Solución:** Ejecuta los scripts de seed data:
```bash
python scripts/seed_data.py
python scripts/poblar_conocimiento.py
```

### La IA no entiende mis preguntas
**Problema:** El contexto de IA podría estar incompleto.
**Solución:** Recarga el contexto:
```bash
python scripts/poblar_conocimiento.py
```

---

## Próximos pasos

Una vez todo funcione:

1. **Prueba con más preguntas** para familiarizarte con qué puede hacer
2. **Agrega tus datos propios** editando `scripts/seed_data.py`
3. **Configura el bot Telegram** si lo necesitas
4. **Contáctame** si encuentras errores en https://github.com/estudiantericharromero11a-ops/IA-0.0.3/issues

---

## Versión
- **v0.0.3** - Versión estable y validada (~90% de precisión)

---

## Licencia
Este proyecto es de código abierto. úsalo libremente.


## Estructura del proyecto y utilidad de archivos

### app.py
- Interfaz local (terminal) y enrutamiento a pipeline.
- Procesa pregunta, genera SQL, ejecuta la consulta y formatea respuesta.

### pipeline/
- `generate_sql.py`: crea consultas SQL usando heurísticas + contexto RAG + LLM.
- `execute_query.py`: valida y ejecuta la consulta contra PostgreSQL.
- `human_response.py`: construye respuesta en lenguaje natural con datos obtenidos.

### ai/
- `retrieval.py`: recupera contexto semántico desde `conocimiento` usando embeddings y fallbacks directos.
- `llm.py`: wrapper de llamada al modelo Ollama (`llama3`).
- `prompts_optimizados.py`: prompts para SQL y respuesta (incluye esquema y reglas).
- `config_ia.py`: lista de palabras clave y configuraciones del sistema.

### database/
- `queries.py`: conexión a DB y ejecución de sentencias SQL en funciones reutilizables.
- `schema_validation.py`: validación de consultas para evitar operaciones peligrosas y asegurar solo SELECT.

### scripts/
- `setup_db.py`: crea schema y tablas en PostgreSQL.
- `create_schema.py`: script alternativo para esquema (SQL crudo).
- `seed_data.py`: inserta datos básicos de campus, bloques, personas, materias, roles, etc.
- `poblar_conocimiento.py`: pobla la tabla `conocimiento` con embeddings y descripciones de esquema.
- `poblar_conocimiento_exhaustivo.py`: versión ampliada del anterior con más contexto.
- `poblar_contexto_bd.py`: carga datos para el módulo de búsqueda contextual.
- `poblar_datos_ejemplo.py`: inserta datos de ejemplo de instalaciones y asignaciones.
- `test_precision.py`, `test_precision_simple.py`: scripts de prueba de precisión QA.
- `verify_versions.py`: valida versiones de dependencias.
- `install_thania.py`: instalación completa y chequeos de entorno.

### telegram_bot/
- `bot.py`: implementa bot Telegram que usa la misma pipeline.

---

## Guía de instalación completa
1. Clonar repo y entrar al directorio:
   - `git clone <repo_url>`
   - `cd "IA 0.0.3"`

2. Crear virtualenv e instalar dependencias:
   - `python -m venv .venv`
   - Windows PowerShell: `.venv\Scripts\Activate.ps1`
   - `pip install -r docs/requirements.txt`

3. Configurar variables de entorno en `.env` (por ejemplo `DATABASE_URL`).

4. Inicializar la base de datos:
   - `python scripts/setup_db.py`
   - `python scripts/seed_data.py`

5. Poblado de conocimiento semántico:
   - `python scripts/poblar_conocimiento.py`

6. Ejecutar app local:
   - `python app.py`

7. Opcional: ejecutar bot Telegram (necesita token en `.env`)
   - `python app.py --telegram`

---

## SQL del esquema de la base de datos
Archivo principal: `scripts/create_schema.sql` (generado por `setup_db.py`). Incluye:

- `campus` (id_campus, nombre, direccion, descripcion)
- `bloques` (id_bloque, nombre, descripcion, id_campus)
- `instalaciones` (id_instalacion, nombre, tipo_instalacion, piso, capacidad, id_bloque, id_area, id_estado)
- `areas_funcionales` (id_area, nombre_area, descripcion)
- `estado_instalacion` (id_estado, nombre_estado, descripcion)
- `horario_instalacion` (id_horario, id_instalacion, dia_semana, hora_apertura, hora_cierre)
- `personas` (id_persona, nombre, documento, correo, telefono)
- `roles` (id_rol, nombre_rol, descripcion)
- `persona_rol` (id_persona, id_rol)
- `materias` (id_materia, nombre, creditos, descripcion)
- `programas` (id_programa, nombre, tipo_programa, duracion_semestres)
- `programa_materia` (id_programa, id_materia)
- `asignacion_instalaciones` (id_asignacion, id_instalacion, id_materia, dia_semana, hora_inicio, hora_fin, id_persona)
- `conocimiento` (id, contenido, embedding vector)

### Ejemplo SQL (extracto):
```sql
-- This script was generated by the ERD tool in pgAdmin 4.
BEGIN;

CREATE TABLE IF NOT EXISTS public.areas_funcionales
(
    id_area serial NOT NULL,
    nombre_area character varying(100) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT areas_funcionales_pkey PRIMARY KEY (id_area)
);

CREATE TABLE IF NOT EXISTS public.asignacion_instalaciones
(
    id_asignacion serial NOT NULL,
    id_instalacion integer,
    id_materia integer,
    dia_semana character varying(20) COLLATE pg_catalog."default",
    hora_inicio time without time zone,
    hora_fin time without time zone,
    id_persona integer,
    CONSTRAINT asignacion_instalaciones_pkey PRIMARY KEY (id_asignacion)
);

CREATE TABLE IF NOT EXISTS public.bloques
(
    id_bloque serial NOT NULL,
    nombre character varying(50) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    id_campus integer,
    CONSTRAINT bloques_pkey PRIMARY KEY (id_bloque)
);

CREATE TABLE IF NOT EXISTS public.campus
(
    id_campus serial NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    direccion character varying(150) COLLATE pg_catalog."default",
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT campus_pkey PRIMARY KEY (id_campus)
);

CREATE TABLE IF NOT EXISTS public.conocimiento
(
    id serial NOT NULL,
    contenido text COLLATE pg_catalog."default",
    embedding vector(384),
    CONSTRAINT conocimiento_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.estado_instalacion
(
    id_estado serial NOT NULL,
    nombre_estado character varying(50) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT estado_instalacion_pkey PRIMARY KEY (id_estado)
);

CREATE TABLE IF NOT EXISTS public.horario_instalacion
(
    id_horario serial NOT NULL,
    id_instalacion integer,
    dia_semana character varying(20) COLLATE pg_catalog."default",
    hora_apertura time without time zone,
    hora_cierre time without time zone,
    CONSTRAINT horario_instalacion_pkey PRIMARY KEY (id_horario)
);

CREATE TABLE IF NOT EXISTS public.instalaciones
(
    id_instalacion serial NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    tipo_instalacion character varying(50) COLLATE pg_catalog."default",
    piso integer,
    capacidad integer,
    id_bloque integer,
    id_area integer,
    id_estado integer,
    CONSTRAINT instalaciones_pkey PRIMARY KEY (id_instalacion)
);

CREATE TABLE IF NOT EXISTS public.materias
(
    id_materia serial NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    creditos integer,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT materias_pkey PRIMARY KEY (id_materia)
);

CREATE TABLE IF NOT EXISTS public.persona_rol
(
    id_persona integer NOT NULL,
    id_rol integer NOT NULL,
    CONSTRAINT persona_rol_pkey PRIMARY KEY (id_persona, id_rol)
);

CREATE TABLE IF NOT EXISTS public.personas
(
    id_persona serial NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    documento character varying(20) COLLATE pg_catalog."default",
    correo character varying(100) COLLATE pg_catalog."default",
    telefono character varying(20) COLLATE pg_catalog."default",
    CONSTRAINT personas_pkey PRIMARY KEY (id_persona),
    CONSTRAINT personas_documento_key UNIQUE (documento)
);

CREATE TABLE IF NOT EXISTS public.programa_materia
(
    id_programa integer NOT NULL,
    id_materia integer NOT NULL,
    CONSTRAINT programa_materia_pkey PRIMARY KEY (id_programa, id_materia)
);

CREATE TABLE IF NOT EXISTS public.programas
(
    id_programa serial NOT NULL,
    nombre character varying(100) COLLATE pg_catalog."default" NOT NULL,
    tipo_programa character varying(50) COLLATE pg_catalog."default",
    duracion_semestres integer,
    CONSTRAINT programas_pkey PRIMARY KEY (id_programa)
);

CREATE TABLE IF NOT EXISTS public.roles
(
    id_rol serial NOT NULL,
    nombre_rol character varying(50) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    CONSTRAINT roles_pkey PRIMARY KEY (id_rol)
);

-- Foreign Keys

ALTER TABLE IF EXISTS public.asignacion_instalaciones
    ADD CONSTRAINT asignacion_instalaciones_id_instalacion_fkey FOREIGN KEY (id_instalacion)
    REFERENCES public.instalaciones (id_instalacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.asignacion_instalaciones
    ADD CONSTRAINT asignacion_instalaciones_id_materia_fkey FOREIGN KEY (id_materia)
    REFERENCES public.materias (id_materia) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.asignacion_instalaciones
    ADD CONSTRAINT fk_profesor FOREIGN KEY (id_persona)
    REFERENCES public.personas (id_persona) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.bloques
    ADD CONSTRAINT bloques_id_campus_fkey FOREIGN KEY (id_campus)
    REFERENCES public.campus (id_campus) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.horario_instalacion
    ADD CONSTRAINT horario_instalacion_id_instalacion_fkey FOREIGN KEY (id_instalacion)
    REFERENCES public.instalaciones (id_instalacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.instalaciones
    ADD CONSTRAINT instalaciones_id_area_fkey FOREIGN KEY (id_area)
    REFERENCES public.areas_funcionales (id_area) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.instalaciones
    ADD CONSTRAINT instalaciones_id_bloque_fkey FOREIGN KEY (id_bloque)
    REFERENCES public.bloques (id_bloque) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.instalaciones
    ADD CONSTRAINT instalaciones_id_estado_fkey FOREIGN KEY (id_estado)
    REFERENCES public.estado_instalacion (id_estado) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.persona_rol
    ADD CONSTRAINT persona_rol_id_persona_fkey FOREIGN KEY (id_persona)
    REFERENCES public.personas (id_persona) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.persona_rol
    ADD CONSTRAINT persona_rol_id_rol_fkey FOREIGN KEY (id_rol)
    REFERENCES public.roles (id_rol) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.programa_materia
    ADD CONSTRAINT programa_materia_id_materia_fkey FOREIGN KEY (id_materia)
    REFERENCES public.materias (id_materia) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.programa_materia
    ADD CONSTRAINT programa_materia_id_programa_fkey FOREIGN KEY (id_programa)
    REFERENCES public.programas (id_programa) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

END;
```

---

## Ajustes recientes en este repo
- Filtro robusto en `pipeline/generate_sql.py`: convierte comparaciones exactas `= 'CUL'` a `ILIKE '%CUL%'`
- Fallback mejorado para queries sin filas
- Validación de SQL para evitar `DROP|DELETE|UPDATE|INSERT` en ejecución

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
