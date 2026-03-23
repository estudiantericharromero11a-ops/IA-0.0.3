# 🚀 THANIA THANIA - Setup Completo (v0.0.3)

## 📋 Tabla de Contenidos
1. [Requisitos Previos](#requisitos-previos)
2. [Instalación de Dependencias](#instalación-de-dependencias)
3. [Configuración de Base de Datos](#configuración-de-base-de-datos)
4. [Configuración de la THANIA](#configuración-de-la-THANIA)
5. [Prueba de Funcionamiento](#prueba-de-funcionamiento)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Requisitos Previos

### Software Requerido
```
✅ Python 3.12.10 o superior
✅ PostgreSQL 12+ (local o remoto)
✅ Ollama (para generación de SQL/respuestas)
✅ Git (opcional, para clonar)
```

### Servicios Necesarios
1. **PostgreSQL** - Base de datos (puerto 5432 por defecto)
2. **Ollama** - Servidor de LLM (puerto 11434 por defecto)

---

## 📦 Instalación de Dependencias

### Paso 1: Crear Virtual Environment
```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Paso 2: Instalar Requirements
```powershell
# Instalar todas las dependencias (versiones validadas)
pip install -r requirements.txt

# Verificar las versiones clave
pip show torch transformers sentence-transformers psycopg
```

**Versiones Validadas (NO MODIFICAR):**
- `torch==2.3.0` - PyTorch CPU
- `transformers==4.36.0` - Compatible con sentence-transformers 3.0.1
- `sentence-transformers==3.0.1` - Embeddings semánticos
- `psycopg==3.1.0+` - Driver PostgreSQL

### Paso 3: Verificar Instalación
```powershell
python -c "import torch; import transformers; import psycopg; print('✅ Todas las dependencias OK')"
```

---

## 🗄️ Configuración de Base de Datos

### Paso 1: Crear Base de Datos PostgreSQL
```sql
-- En psql o DBeaver
CREATE DATABASE universidad OWNER postgres;
CREATE EXTENSION IF NOT EXISTS vector;
```

### Paso 2: Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# IMPORTANTE: Cambiar estos valores:
DB_HOST=localhost          # IP de PostgreSQL
DB_NAME=universidad        # Nombre de la BD
DB_USER=postgres           # Usuario
DB_PASSWORD=tu_password    # Contraseña
DB_PORT=5432              # Puerto
```

### Paso 3: Crear Esquema de Base de Datos
```powershell
# Ejecutar setup
python scripts/setup_db.py

# Resultado esperado:
# ✅ Esquema de base de datos creado exitosamente
# ✅ Base de datos configurada. Ahora ejecuta:
#    python scripts/poblar_conocimiento.py
```

### Paso 4: Poblar Base de Datos con Datos
```powershell
# Opción A: Datos de ejemplo (recomendado para pruebas)
python scripts/poblar_datos_ejemplo.py

# Opción B: Datos universitarios completos
python scripts/poblar_conocimiento_exhaustivo.py

# Resultado: "✅ Base de datos poblada exitosamente"
```

### Paso 5: Verificar Base de Datos
```sql
-- En psql, ejecutar:
\c universidad
SELECT COUNT(*) FROM programas;       -- Debe devolver carreras
SELECT COUNT(*) FROM materias;        -- Debe devolver materias
SELECT COUNT(*) FROM personas;        -- Debe devolver personas
SELECT COUNT(*) FROM asignacion_instalaciones;  -- Debe devolver asignaciones
```

---

## 🤖 Configuración de la THANIA

### Paso 1: Instalar Ollama
```bash
# Descargar desde: https://ollama.Sistema

# Verificar instalación:
ollama --version

# Descargar modelo llama3 (recomendado):
ollama pull llama3

# Verificar disponibilidad:
ollama list
```

### Paso 2: Iniciar Ollama
```powershell
# En terminal separada:
ollama serve

# Resultado:
# Listening on 127.0.0.1:11434
```

### Paso 3: Verificar Conexión con THANIA
```powershell
python -c "
import requests
try:
    resp = requests.get('http://localhost:11434/api/tags')
    print('✅ Ollama conectado')
    print('Modelos disponibles:', resp.json())
except:
    print('❌ Ollama no disponible. Ejecuta: ollama serve')
"
```

---

## 🧪 Prueba de Funcionamiento

### Test 1: Verificar Base de Datos
```powershell
python -c "
from database.queries import get_connection
try:
    conn = get_connection()
    print('✅ Base de datos conectada')
    conn.close()
except Exception as e:
    print(f'❌ Error BD: {e}')
"
```

### Test 2: Verificar Sistema Modules
```powershell
python -c "
from Sistema.retrieval import obtener_contexto
from pipeline.generate_sql import generar_sql
from pipeline.execute_query import ejecutar_sql
print('✅ Módulos THANIA cargados correctamente')
"
```

### Test 3: Ejecutar Modo LOCAL
```powershell
# Iniciar aplicación en modo interactivo
python app.py --local

# O simplemente:
python app.py

# Esperar a que aparezca:
# THANIA UNIVERSITARIA THANIA - MODO LOCAL INTERACTIVO

# Escribe una pregunta, ej:
# Tu pregunta: ¿cuántas carreras tiene la universidad?
```

### Test 4: Bot de Telegram (Opcional)
```powershell
# Configurar TELEGRAM_TOKEN en .env primero

# Ejecutar bot:
python app.py --telegram

# Resultado: Bot escuchando en Telegram
```

---

## 📊 Estructura Esperada de Base de Datos

```
UNIVERSIDAD (BD)
├── MÓDULO 1: ESTRUCTURA FÍSICA
│   ├── campus (4 sedes)
│   ├── bloques (8 edificios)
│   ├── instalaciones (20+ espacios)
│   ├── areas_funcionales (5 áreas)
│   └── estado_instalacion (3 estados)
│
├── MÓDULO 2: GESTIÓN ACADÉMICA
│   ├── personas (50+ profesores + estudiantes)
│   ├── roles (5+ tipos de roles)
│   ├── programas (2+ carreras)
│   └── materias (10+ asignaturas)
│
└── MÓDULO 3: OPERACIÓN
    └── asignacion_instalaciones (100+ asignaciones)
        └── Conecta: Profesor + Materia + Lugar + Tiempo
```

---

## ✅ Checklist de Verificación Final

- [ ] Python 3.12+ instalado
- [ ] Virtual environment activado
- [ ] requirements.txt instalado (pip show torch → 2.3.0)
- [ ] PostgreSQL ejecutándose
- [ ] Base de datos 'universidad' creada
- [ ] Esquema creado (setup_db.py ejecutado)
- [ ] Datos poblados (5000+ registros)
- [ ] .env configurado correctamente
- [ ] Ollama ejecutándose (ollama serve)
- [ ] Test 1: Base de datos ✅
- [ ] Test 2: Módulos THANIA ✅
- [ ] Test 3: App local funciona ✅

---

## 🐛 Troubleshooting

### Error: "No module named 'torch'"
```powershell
# Solución:
pip uninstall -y torch torchvision torchaudio
pip install torch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0 --index-url https://download.pytorch.org/whl/cpu
```

### Error: "Could not import module 'TrainerCallback'"
```powershell
# Solución: transformers incompatible
pip uninstall -y transformers
pip install transformers==4.36.0
```

### Error: "no existe la columna pr.duracion_semestre"
```powershell
# Solución: Ya está corregido en v0.0.3
# Si persiste, ejecutar setup nuevamente:
python scripts/setup_db.py
```

### Error: "Ollama not available"
```powershell
# Asegúrate de ejecutar en terminal separada:
ollama serve

# Verificar puerto 11434:
netstat -an | findstr "11434"
```

### Error: "Database connection refused"
```powershell
# Verificar PostgreSQL:
# Windows: Services → PostgreSQL debe estar corriendo
# Linux: sudo systemctl status postgresql
# O iniciar en terminal: postgres
```

### Advertencias en startup (SO WARNINGS)
```
UserWarning: torch.utils._pytree._register_pytree_node is deprecated
FutureWarning: resume_download is deprecated
```
✅ **ES NORMAL** - Ya están silenciadas en app.py (v0.0.3)

---

## 📞 Soporte

Si encuentras problemas:

1. **Verifica el .env** - Todos los valores requeridos
2. **Revisa logs** - Ver `app.log`
3. **Confirma versiones** - `pip show [package]`
4. **Reinicia servicios** - Ollama y PostgreSQL

---

## 🎉 ¡Instalación Completa!

Una vez completados todos los pasos:

```powershell
# Arrancar sistema completo
python app.py --local

# O para Bot de Telegram:
python app.py --telegram
```

**THANIA THANIA está listo para responder preguntas universitarias** ✅

