# THANIA - Sistema de Consultas Universitarias (v0.0.7)

## ¿Qué es THANIA?

THANIA es un sistema que permite consultar información sobre una universidad (datos sobre profesores, clases, horarios, instalaciones, etc.) mediante preguntas en lenguaje natural.

En lugar de escribir comandos complicados, puedes hacer preguntas naturales como:
- "¿Quiénes son los profesores de matemáticas?"
- "¿Dónde se dicta física?"
- "¿Cuál es el horario de la clase de programación?"

Y THANIA automáticamente:
1. Procesa tu pregunta
2. Busca la información en la base de datos
3. Te da una respuesta clara en español
 
### ¿Cómo funciona internamente?

THANIA integra tres tecnologías principales:

- **Búsqueda Semántica**: Un sistema que busca información relevante basada en significado.
- **Modelos de Lenguaje**: Usa procesamiento de lenguaje natural para entender preguntas.
- **PostgreSQL**: Base de datos que almacena toda la información de la universidad.

---

## Arquitectura y Funcionamiento del Sistema

### Visión General de la Arquitectura

THANIA es un sistema de procesamiento de lenguaje natural que convierte preguntas en español sobre información universitaria en consultas SQL precisas. El sistema está dividido en tres capas principales:

```
[Frontend/API] ←→ [Backend THANIA] ←→ [Base de Datos PostgreSQL]
      ↑                    ↑
   Usuario            Procesamiento IA
```

### Flujo de Funcionamiento Paso a Paso

#### 1. **Recepción de la Pregunta**
- El usuario envía una pregunta en lenguaje natural (ej: "¿Dónde está el aula 101?")
- El sistema puede recibir preguntas a través de:
  - **Interfaz de línea de comandos** (modo local)
  - **API REST** (para aplicaciones web)
  - **Bot de Telegram** (para mensajería)

#### 2. **Detección de Intención**
- **Módulo**: `ai/config_ia.py`
- El sistema identifica si es una pregunta sobre datos universitarios o sobre el propio sistema
- Palabras clave como "profesor", "aula", "horario" activan el procesamiento de consultas
- Preguntas como "qué eres" o "cómo funciona" generan respuestas directas

#### 3. **Búsqueda Semántica de Contexto**
- **Módulo**: `ai/retrieval.py`
- Se busca información relevante en la base de datos vectorial (`conocimiento`)
- Usa embeddings semánticos para encontrar tablas y relaciones relacionadas con la pregunta
- Recupera contexto de hasta 5 registros más relevantes

#### 4. **Generación de SQL**
- **Módulo**: `pipeline/generate_sql.py`
- Combina el contexto recuperado con la pregunta del usuario
- Envía prompt optimizado al modelo de lenguaje (Ollama + llama3)
- Aplica heurísticas para casos comunes (ej: listas de profesores)
- Genera consulta SQL SELECT válida y segura

#### 5. **Ejecución de Consulta**
- **Módulo**: `pipeline/execute_query.py`
- Ejecuta la consulta SQL en PostgreSQL con pgvector
- Valida que solo sean operaciones SELECT (seguridad)
- Maneja errores de sintaxis SQL
- Retorna resultados en formato estructurado

#### 6. **Generación de Respuesta Natural**
- **Módulo**: `pipeline/human_response.py`
- Convierte los datos SQL crudos en respuesta conversacional en español
- Aplica reglas de presentación inteligente:
  - 1 resultado: descripción completa
  - 2-5 resultados: lista enumerada
  - Más de 5: resumen con total
- Maneja tipos de datos complejos (fechas, horas, decimales)

#### 7. **Entrega de Respuesta**
- Respuesta se envía al canal correspondiente:
  - Terminal (modo local)
  - JSON API (para frontend)
  - Mensaje de Telegram

### Tecnologías y Componentes

#### **Backend - Python/FastAPI**
- **Framework**: FastAPI para API REST
- **ORM**: SQLAlchemy con async support
- **Base de datos**: PostgreSQL con extensión pgvector
- **IA**: Ollama + modelo llama3 local
- **Embeddings**: SentenceTransformers (384 dimensiones)

#### **Frontend - Integración**
- **API REST**: Endpoints en `/query` para consultas
- **WebSocket**: Para respuestas en tiempo real (opcional)
- **CORS**: Configurado para desarrollo local

#### **Base de Datos - PostgreSQL**
- **14 tablas** organizadas en 5 módulos
- **pgvector**: Para búsquedas semánticas con embeddings
- **Índices**: Optimizados para consultas JOIN complejas
- **Constraints**: Foreign keys y validaciones de integridad

### Conexión Frontend-Backend

#### **API Endpoints Disponibles**
```
POST /query
- Body: {"query": "tu pregunta aquí"}
- Response: {"response": "respuesta", "sql": "consulta generada", "status": "success"}
```

#### **Ejemplo de Integración Web**
```javascript
// Frontend JavaScript
async function consultarTHANIA(pregunta) {
    const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: pregunta})
    });
    
    const data = await response.json();
    return data.response;
}
```

#### **Configuración de Producción**
- **Variables de entorno**: `.env` para credenciales
- **CORS**: Configurado para orígenes específicos
- **Rate limiting**: Recomendado para producción
- **Logging**: Configurado para monitoreo

### Seguridad y Limitaciones

#### **Medidas de Seguridad**
- **Solo SELECT**: No permite INSERT, UPDATE, DELETE
- **Validación SQL**: Regex para prevenir inyección
- **Timeouts**: Límite de tiempo en consultas IA y BD
- **Datos confidenciales**: Campos como `documento` no se muestran

#### **Limitaciones Actuales**
- **Idioma**: Solo procesa preguntas en español
- **Alcance**: Limitado a datos universitarios
- **Modelo local**: Requiere recursos de hardware
- **Sin autenticación**: No implementado control de usuarios

---

## Requisitos previos

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
  - Necesario para el modelo llama3
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

## Instalación Completa del Sistema

### Prerrequisitos del Sistema

**Hardware mínimo recomendado:**
- **RAM**: 8GB (16GB recomendado para mejor rendimiento)
- **Disco**: 10GB libres
- **CPU**: Procesador con AVX2 support (para aceleración de IA)

**Software requerido:**
- Python 3.11+ con pip
- PostgreSQL 13+ con pgvector
- Git
- Ollama (para modelo de IA local)

### Guía de Instalación Paso a Paso

#### Paso 1: Preparación del Entorno

**1.1 Instalar Python 3.11+**
```bash
# Verificar versión instalada
python --version

# Si no tienes Python, descarga desde:
# https://www.python.org/downloads/
# IMPORTANTE: Marca "Add Python to PATH" en Windows
```

**1.2 Instalar PostgreSQL**
```bash
# Descarga desde: https://www.postgresql.org/download/
# Durante instalación:
# - Recuerda la contraseña del usuario 'postgres'
# - Instala pgAdmin (herramienta gráfica opcional)
# - Puerto por defecto: 5432
```

**1.3 Instalar Ollama**
```bash
# Descarga desde: https://ollama.ai/download
# Después de instalar, ejecuta:
ollama serve

# En otra terminal, descarga el modelo:
ollama pull llama3
```

**1.4 Instalar pgvector en PostgreSQL**
```sql
-- Conecta a PostgreSQL como superusuario
-- Ejecuta este comando SQL:
CREATE EXTENSION IF NOT EXISTS vector;
```

#### Paso 2: Descarga y Configuración del Proyecto

**2.1 Clonar el repositorio**
```bash
git clone https://github.com/estudiantericharromero11a-ops/IA-0.0.3.git
cd "IA 0.0.3"
```

**2.2 Crear ambiente virtual**
```bash
# Crear ambiente virtual
python -m venv .venv

# Activar ambiente virtual
# Windows:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Verificar activación (deberías ver (.venv) en el prompt)
```

**2.3 Instalar dependencias**
```bash
# Instalar todas las librerías requeridas
pip install -r docs/requirements.txt

# Verificar instalación
python -c "import torch, transformers, sentence_transformers; print('Dependencias OK')"
```

#### Paso 3: Configuración de Base de Datos

**3.1 Crear archivo de configuración**
```bash
# Crear archivo .env en la raíz del proyecto
# Copia y pega este contenido, reemplaza con tus datos:

DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA_AQUI@localhost:5432/thania_db
TELEGRAM_TOKEN=tu_token_telegram_opcional

# Variables adicionales (opcionales)
OLLAMA_URL=http://localhost:11434
MODEL_NAME=llama3
OLLAMA_TIMEOUT=120
```

**3.2 Crear base de datos**
```bash
# Crear la base de datos (ejecutar como usuario postgres)
createdb thania_db

# O usando pgAdmin/SQL Shell:
# CREATE DATABASE thania_db;
```

**3.3 Inicializar esquema**
```bash
# Crear todas las tablas
python scripts/setup_db.py

# Verificar creación de tablas
psql -d thania_db -c "\dt"
```

#### Paso 4: Carga de Datos Iniciales

**4.1 Insertar datos de ejemplo**
```bash
# Cargar datos básicos de universidad
python scripts/seed_data.py

# Verificar datos insertados
psql -d thania_db -c "SELECT COUNT(*) FROM personas;"
```

**4.2 Preparar contexto semántico**
```bash
# Crear embeddings para búsqueda inteligente
python scripts/poblar_conocimiento.py

# Este proceso puede tomar varios minutos
# Crea representaciones vectoriales de la estructura BD
```

#### Paso 5: Verificación y Primer Test

**5.1 Verificar servicios**
```bash
# Verificar que Ollama esté corriendo
curl http://localhost:11434/api/tags

# Verificar conexión a base de datos
python -c "from database.queries import get_connection; conn = get_connection(); print('Conexión OK'); conn.close()"
```

**5.2 Ejecutar test de funcionamiento**
```bash
# Ejecutar tests de precisión
python scripts/test_precision_simple.py

# Deberías ver: "STATUS: 🟢 PRODUCCIÓN LISTA"
```

#### Paso 6: Puesta en Marcha

**6.1 Modo interactivo (recomendado para testing)**
```bash
python app.py
```

**6.2 Modo API REST (para integración web)**
```bash
python app.py --web --host 0.0.0.0 --port 8000
```

**6.3 Modo Telegram Bot**
```bash
# Requiere configurar TELEGRAM_TOKEN en .env
python app.py --telegram
```

### Verificación de Instalación Completa

Ejecuta estos comandos para verificar que todo funciona:

```bash
# 1. Verificar ambiente virtual
which python  # Debería apuntar a .venv/

# 2. Verificar dependencias
python -c "import fastapi, uvicorn, psycopg2, torch; print('OK')"

# 3. Verificar base de datos
psql -d thania_db -c "SELECT COUNT(*) FROM campus;"

# 4. Verificar Ollama
curl -s http://localhost:11434/api/tags | grep llama3

# 5. Test funcional
echo "¿Cuántos profesores hay?" | python app.py
```

### Solución de Problemas Comunes

#### "ModuleNotFoundError: No module named 'torch'"
```bash
pip install torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu
```

#### "FATAL: password authentication failed for user 'postgres'"
- Verifica la contraseña en `.env`
- Asegúrate de que PostgreSQL esté corriendo
- Prueba conectarte manualmente: `psql -U postgres -d thania_db`

#### "Connection refused" en Ollama
```bash
# Inicia Ollama
ollama serve

# En otra terminal
ollama pull llama3
```

#### "extension 'vector' does not exist"
```sql
-- Conecta como superusuario y ejecuta:
CREATE EXTENSION vector;
```

### Configuración para Desarrollo vs Producción

#### **Desarrollo Local**
- Host: `localhost`
- Puerto: `8000`
- CORS: Permitir `http://localhost:*`
- Logging: Nivel `DEBUG`

#### **Producción**
- Host: `0.0.0.0`
- Puerto: `80` o `443`
- CORS: Configurar dominios específicos
- Logging: Nivel `INFO` o `WARNING`
- HTTPS: Recomendado
- Rate limiting: Implementar
- Monitoring: Logs centralizados

### Integración con Frontend

#### **API Endpoints**
```
POST /query          # Consulta principal
GET  /health         # Estado del sistema
GET  /docs           # Documentación automática (Swagger)
```

#### **Ejemplo de integración React/Vue**
```javascript
const consultarTHANIA = async (pregunta) => {
    try {
        const response = await fetch('http://localhost:8000/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: pregunta })
        });
        
        const data = await response.json();
        return {
            respuesta: data.response,
            sql: data.sql,
            status: data.status
        };
    } catch (error) {
        console.error('Error consultando THANIA:', error);
        return { error: 'Error de conexión' };
    }
};
```

#### **WebSocket (para respuestas en tiempo real)**
```javascript
// Conexión WebSocket opcional
const ws = new WebSocket('ws://localhost:8000/ws');

// Escuchar respuestas
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Respuesta THANIA:', data.response);
};
```

### Monitoreo y Mantenimiento

#### **Comandos útiles para mantenimiento**
```bash
# Ver logs de la aplicación
tail -f app.log

# Verificar uso de disco de la BD
psql -d thania_db -c "SELECT pg_size_pretty(pg_database_size('thania_db'));"

# Backup de la base de datos
pg_dump thania_db > backup_$(date +%Y%m%d).sql

# Recargar contexto semántico
python scripts/poblar_conocimiento.py
```

#### **Métricas de rendimiento**
- **Tiempo de respuesta**: < 30 segundos por consulta
- **Precisión**: > 90% en tests de validación
- **Uptime**: Servicio disponible 24/7
- **Uso de memoria**: < 4GB en operación normal

---

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

### Modo Web API (para integración con frontend)

```bash
python app.py --web
```

Esto inicia un servidor FastAPI en `http://localhost:8000` con endpoints REST:

- `GET /` - Estado del servidor
- `POST /query` - Enviar pregunta (JSON: `{"query": "tu pregunta"}`)

**Ejemplo de uso con curl:**
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "¿Quiénes son los profesores?"}'
```

**Respuesta:**
```json
{
  "response": "Los profesores registrados son: Juan Pérez (Matemáticas), María García (Física)...",
  "sql": "SELECT * FROM personas WHERE rol = 'profesor'",
  "status": "success"
}
```

---

## Estructura del proyecto explicada

```
IA 0.0.3/
├── app.py                    # Punto de entrada - interfaz de usuario
├── config.py                 # Configuración principal
│
├── ai/                       # Módulo de Procesamiento de Lenguaje
│   ├── retrieval.py         # Busca información relevante
│   ├── llm.py               # Comunicación con modelos de lenguaje
│   ├── prompts_optimizados.py # Plantillas de procesamiento
│   └── config_ia.py         # Configuración del sistema
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
- Usa vectores para entender el significado, no solo palabras exactas

**pipeline/generate_sql.py**
- Convierte tu pregunta en lenguaje natural a SQL
- Usa procesamiento de lenguaje para generar queries que busquen exactamente lo que preguntaste

**pipeline/execute_query.py**
- Ejecuta la consulta SQL en PostgreSQL
- Valida que solo sean consultas seguras (solo SELECT, nunca elimina datos)

**pipeline/human_response.py**
- Toma los datos de la base de datos y genera una respuesta en español
- Asegura que la respuesta sea clara y legible

---

## Bases de datos: Las 14 tablas del sistema

THANIA organiza la información en **14 tablas** interconectadas que representan la estructura completa de una universidad:

### Módulo 1: Estructura Física (Infraestructura de la universidad)

#### campus
- **Propósito**: Información de las sedes universitarias (CUL, CUC, etc.)
- **Campos principales**: id_campus, nombre, dirección, descripción
- **Relaciones**: Un campus tiene muchos bloques

#### bloques 
- **Propósito**: Edificios o secciones dentro de cada campus
- **Campos principales**: id_bloque, nombre, descripción, id_campus (FK)
- **Relaciones**: Pertenece a un campus, contiene muchas instalaciones

#### instalaciones
- **Propósito**: Espacios físicos individuales (aulas, laboratorios, oficinas)
- **Campos principales**: id_instalacion, nombre, tipo_instalacion, piso, capacidad, id_bloque (FK), id_area (FK), id_estado (FK)
- **Relaciones**: Pertenece a un bloque, tiene área funcional y estado

#### areas_funcionales
- **Propósito**: Categorización de los espacios (académico, administrativo, investigación)
- **Campos principales**: id_area, nombre_area, descripción
- **Relaciones**: Clasifica las instalaciones

#### estado_instalacion
- **Propósito**: Estados de disponibilidad de los espacios
- **Campos principales**: id_estado, nombre_estado, descripción
- **Ejemplos**: Disponible, Ocupado, En mantenimiento

#### horario_instalacion
- **Propósito**: Horarios de apertura/cierre de las instalaciones
- **Campos principales**: id_horario, id_instalacion (FK), dia_semana, hora_apertura, hora_cierre
- **Relaciones**: Define cuándo está disponible cada instalación

### Módulo 2: Gestión de Personas (Usuarios del sistema)

#### personas
- **Propósito**: Todos los individuos en la universidad (profesores, estudiantes, administrativos)
- **Campos principales**: id_persona, nombre, documento, correo, telefono
- **Nota**: El documento es información confidencial, no se muestra en respuestas

#### roles
- **Propósito**: Tipos de roles o cargos (profesor, estudiante, administrador, etc.)
- **Campos principales**: id_rol, nombre_rol, descripción
- **Ejemplos**: profesor, docente, estudiante, administrador

#### persona_rol
- **Propósito**: Tabla puente que conecta personas con sus roles (N:N)
- **Campos principales**: id_persona (FK), id_rol (FK)
- **Nota**: Una persona puede tener múltiples roles

### Módulo 3: Gestión Académica (Carreras y asignaturas)

#### programas
- **Propósito**: Carreras universitarias o programas académicos
- **Campos principales**: id_programa, nombre, tipo_programa, duracion_semestres
- **Ejemplos**: Ingeniería de Sistemas, Medicina, Derecho

#### materias
- **Propósito**: Asignaturas o cursos individuales
- **Campos principales**: id_materia, nombre, creditos, descripción
- **Ejemplos**: Matemáticas I, Física General, Programación

#### programa_materia
- **Propósito**: Tabla puente que conecta programas con sus materias (N:N)
- **Campos principales**: id_programa (FK), id_materia (FK)
- **Relaciones**: Define qué materias pertenecen a cada programa

### Módulo 4: Núcleo Operativo (El corazón del sistema)

#### asignacion_instalaciones
- **Propósito**: **TABLA MÁS IMPORTANTE** - Conecta todas las entidades para representar clases reales
- **Campos principales**: 
  - id_asignacion, id_instalacion (FK), id_materia (FK), id_persona (FK)
  - dia_semana, hora_inicio, hora_fin
- **Responde las preguntas clave**:
  - ¿Quién enseña? (id_persona → personas)
  - ¿Qué se enseña? (id_materia → materias) 
  - ¿Dónde? (id_instalacion → instalaciones → bloques → campus)
  - ¿Cuándo? (dia_semana, hora_inicio, hora_fin)

### Módulo 5: Conocimiento Semántico (Búsqueda inteligente)

#### conocimiento
- **Propósito**: Base de datos vectorial para búsquedas semánticas
- **Campos principales**: id, contenido (texto), embedding (vector de 384 dimensiones)
- **Tecnología**: Usa pgvector para similitud coseno
- **Función**: Permite búsquedas por significado, no solo palabras exactas

### Relaciones Clave del Sistema

```
campus → bloques → instalaciones ← asignacion_instalaciones → personas
    ↓         ↓             ↓                    ↓
  programas → programa_materia → materias     persona_rol → roles
                                      ↓             ↓
                                    areas_funcionales ← estado_instalacion
```

### Estadísticas del Sistema
- **Total de tablas**: 14
- **Relaciones FK**: 15+ foreign keys
- **Tablas puente**: 3 (persona_rol, programa_materia, asignacion_instalaciones)
- **Soporte vectorial**: pgvector para embeddings de 384 dimensiones

---

## Cambios Recientes (v0.0.7)

### Mejoras en Respuestas
- **Temperatura optimizada**: De 0.5 → 0.3 para respuestas más precisas
- **Tokens ajustados**: Máximo 1200 tokens para respuestas más concisas
- **Reglas para listas simples**: Preguntas como "solo los nombres" generan respuestas directas
- **Detección mejorada**: Palabras clave adicionales para preguntas sobre el sistema

### Documentación Actualizada
- **Esquema de BD completo**: Detalle de las 14 tablas con campos y relaciones
- **Módulos organizados**: Estructura clara por funcionalidad (Física, Personas, Académica, Operativo, Semántico)
- **Relaciones visuales**: Diagramas ASCII de las conexiones entre tablas
- **Estadísticas del sistema**: Métricas sobre la arquitectura de datos

### Precisión Mejorada
- **Test de validación**: 100% de precisión en 15 preguntas de prueba
- **Heurísticas inteligentes**: Respuestas directas para consultas comunes
- **Detección de sistema**: Preguntas sobre THANIA responden automáticamente

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

### El sistema no procesa correctamente mis preguntas
**Problema:** El contexto podría estar incompleto.
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

---

---

## C�mo contribuir
1. git checkout -b feat/mi-cambio
2. Cambiar c�digo / tests
3. Probar localmente
4. git add . / git commit
5. git push / PR

Ideas de mejoras:
- caching de contexto en i/retrieval.py
- paginaci�n de resultados
- validaci�n sem�ntica de SQL m�s fuerte
- pruebas unitarias adicionales para pipeline/ y database/

---

## Uso práctico

### Ejemplos de consultas que funcionan

#### Consultas básicas sobre infraestructura
```
¿Dónde está el campus CUL?
¿Cuántos bloques tiene el campus principal?
¿Cuáles son las aulas del bloque A?
¿Qué capacidad tiene el auditorio principal?
```

#### Consultas sobre personas y roles
```
¿Quiénes son los profesores?
¿Cuántos estudiantes hay matriculados?
¿Cuál es el correo del profesor Juan Pérez?
¿Quién dicta la materia de matemáticas?
```

#### Consultas académicas
```
¿Qué materias tiene la carrera de ingeniería?
¿Cuántos créditos vale programación?
¿Cuál es la duración de la carrera de medicina?
¿En qué programas se dicta física?
```

#### Consultas de horarios y asignaciones
```
¿Dónde es la clase de matemáticas el lunes?
¿Quién enseña programación los martes?
¿Cuál es el horario de clases del profesor García?
¿En qué aula es la clase de química?
```

#### Consultas complejas (JOINs)
```
¿Cuántos profesores hay por campus?
¿Cuáles son las materias más demandadas?
¿Dónde están ubicadas las clases de ingeniería?
¿Quiénes son los profesores con más horas de clase?
```

### Modos de uso

#### 1. Modo interactivo (terminal)
```bash
python app.py
```
- Ideal para testing y familiarización
- Respuestas detalladas con SQL generado
- Historial de conversación

#### 2. Modo pregunta única
```bash
python app.py "¿Cuántos profesores hay?"
```
- Para integración con scripts
- Salida formateada para procesamiento

#### 3. Modo API REST
```bash
python app.py --web --host 0.0.0.0 --port 8000
```
- Para integración web frontend
- Endpoints RESTful
- Documentación automática en `/docs`

#### 4. Modo Telegram Bot
```bash
python app.py --telegram
```
- Requiere TOKEN_TELEGRAM en .env
- Interfaz conversacional natural

### Integración con sistemas externos

#### API REST básica
```javascript
// Frontend JavaScript
async function consultarTHANIA(pregunta) {
    const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: pregunta })
    });
    
    const data = await response.json();
    return {
        respuesta: data.response,
        sql: data.sql,
        tiempo: data.execution_time
    };
}
```

#### Python script
```python
import requests

def preguntar_thania(pregunta):
    url = "http://localhost:8000/query"
    payload = {"query": pregunta}
    response = requests.post(url, json=payload)
    return response.json()

# Ejemplo
resultado = preguntar_thania("¿Dónde está el campus CUL?")
print(resultado['response'])
```

### Casos de uso recomendados

#### ✅ Bueno para:
- Consultas informativas sobre universidad
- Búsqueda de horarios y ubicaciones
- Información académica y administrativa
- Integración con sistemas de gestión universitaria
- Chatbots institucionales

#### ⚠️ Limitaciones conocidas:
- Solo consultas de lectura (SELECT)
- No maneja actualizaciones de datos
- Requiere contexto universitario específico
- Dependiente de calidad de datos en BD

### Troubleshooting común

#### "No se encontraron resultados"
- Verificar que los datos estén cargados: `python scripts/seed_data.py`
- Revisar contexto semántico: `python scripts/poblar_conocimiento.py`

#### "Error de conexión a base de datos"
- Verificar PostgreSQL esté corriendo
- Revisar DATABASE_URL en .env
- Probar conexión manual: `psql -d thania_db`

#### "Ollama no responde"
- Verificar servicio: `ollama serve`
- Confirmar modelo: `ollama pull llama3`
- Revisar puerto 11434 esté disponible

---

---

## Notas
- Versi�n validada: 0.0.7 con 100% de acierto
- Pensado para consultas SQL de solo lectura en un entorno acad�mico
- En producci�n, recomendamos controles extra de autenticaci�n, autorizaci�n y escalado
