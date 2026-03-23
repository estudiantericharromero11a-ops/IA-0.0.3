# Configuración de la aplicación
import os
from dotenv import load_dotenv

load_dotenv()

# Token del bot de Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Nombre del sistema
AI_NAME = "THANIA Universitaria"

# Configuración de Ollama
OLLAMA_MODEL = os.getenv('MODEL_NAME', 'llama3')
OLLAMA_HOST = os.getenv('OLLAMA_URL', 'http://localhost:11434').replace('/api/generate', '')
OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', '120'))

# Configuración de base de datos
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"