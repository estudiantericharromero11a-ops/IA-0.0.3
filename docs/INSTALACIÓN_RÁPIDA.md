# 🚀 THANIA THANIA - GUÍA RÁPIDA DE INICIO (v0.0.3)

**Estado:** 🟢 LISTO PARA PRODUCCIÓN

---

## ⚡ 5 Pasos Rápidos

### 1️⃣ Instalar Dependencias (5 minutos)
```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Instalar todos los paquetes
pip install -r requirements.txt

# Verificar versiones
python scripts/verify_versions.py
```

**Versiones que DEBEN coincidir:**
- ✅ `torch==2.3.0` (CPU)
- ✅ `transformers==4.36.0` (CRÍTICO para sentence-transformers 3.0.1)
- ✅ `sentence_transformers==3.0.1`
- ✅ `psycopg>=3.1.0`

---

### 2️⃣ Configurar Base de Datos (10 minutos)

**A. Crear base de datos en PostgreSQL:**
```sql
CREATE DATABASE universidad OWNER postgres;
CREATE EXTENSION IF NOT EXISTS vector;
```

**B. Editar archivo `.env`:**
```bash
# Copiar template
cp .env.example .env

# Editar con tus credenciales:
DB_HOST=localhost
DB_NAME=universidad
DB_USER=postgres
DB_PASSWORD=tu_password
DB_PORT=5432
```

**C. Crear esquema automáticamente:**
```powershell
python scripts/setup_db.py
```

**D. Poblar con datos de ejemplo:**
```powershell
# Opción rápida (pequeño dataset):
python scripts/poblar_datos_ejemplo.py

# O datos completos:
python scripts/poblar_conocimiento_exhaustivo.py
```

---

### 3️⃣ Instalar y Ejecutar Ollama (3 minutos)

```powershell
# Descargar desde: https://ollama.Sistema

# En TERMINAL SEPARADA:
ollama serve

# En otra terminal:
ollama pull llama3

# Verificar:
ollama list
```

**Debe mostrar:** `llama3` en la lista

---

### 4️⃣ Verificar Instalación (2 minutos)

```powershell
# Verificar todo funciona
python scripts/install_thania.py
```

Debe mostrar:
```
✅ Python 3.12+
✅ .env encontrado
✅ torch==2.3.0
✅ transformers==4.36.0
✅ Conexión a PostgreSQL
✅ Ollama conectado
✅ Módulos THANIA cargados
```

---

### 5️⃣ Ejecutar THANIA THANIA (1 minuto)

```powershell
# Modo LOCAL (pruebas):
python app.py --local

# O directamente:
python app.py
```

Debe mostrar:
```
THANIA UNIVERSITARIA THANIA - MODO LOCAL INTERACTIVO

Tu pregunta: _
```

¡Haz una pregunta y la THANIA responderá! 🎉

---

## 📋 Checklist Rápido

- [ ] Python 3.12+
- [ ] requirements.txt instalado (`pip install -r requirements.txt`)
- [ ] Versiones OK (`python scripts/verify_versions.py`)
- [ ] PostgreSQL ejecutándose
- [ ] Base datos `universidad` creada
- [ ] `.env` configurado
- [ ] Esquema creado (`python scripts/setup_db.py`)
- [ ] Datos poblados (`python scripts/poblar_datos_ejemplo.py`)
- [ ] Ollama corriendo (`ollama serve` en otra terminal)
- [ ] App funciona (`python app.py`)

---

## 🐛 Problemas Comunes

| Problema | Solución |
|----------|----------|
| `No module named 'torch'` | `pip install -r requirements.txt` |
| `Could not import TrainerCallback` | `pip install transformers==4.36.0` |
| `Db connection refused` | Verificar PostgreSQL esté ejecutándose |
| `Ollama not available` | Ejecutar `ollama serve` en terminal separada |
| `Column duracion_semestre not exist` | Ya corregido en v0.0.3 ✅ |

---

## 📚 Documentación Completa

Ver **SETUP_COMPLETO.md** para detalles exhaustivos

---

## 🎯 Próximos Pasos

1. **Modo Telegram** → Editar `.env` con `TELEGRAM_TOKEN` y ejecutar `python app.py --telegram`
2. **Datos Personalizados** → Modificar `scripts/poblar_datos_ejemplo.py`
3. **Nuevos Modelos** → Cambiar `OLLAMA_MODEL` en `Sistema/config_ia.py`

---

**¡THANIA THANIA está listo!** 🚀
