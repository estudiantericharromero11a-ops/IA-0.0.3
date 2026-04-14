 #!/usr/bin/env python3
"""
Aplicación principal del sistema universitario THANIA.
Soporta tres modos:
  1. Modo LOCAL (interactivo): python app.py --local
  2. Modo TELEGRAM: python app.py --telegram (o solo python app.py)
  3. Modo WEB API: python app.py --web
"""

import logging
import sys
import argparse
import os
import warnings

# Silenciar advertencias de deprecation
warnings.filterwarnings('ignore', category=UserWarning, message=r'.*torch\.utils\._pytree.*')
warnings.filterwarnings('ignore', category=FutureWarning, message=r'.*resume_download.*')

from pipeline.generate_sql import generar_sql
from pipeline.execute_query import ejecutar_sql
from pipeline.human_response import generar_respuesta
from telegram_bot.bot import run_bot

# Web API imports (solo si se necesita)
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# MODO LOCAL - VERSIÓN INTERACTIVA
# ============================================================================

def procesar_pregunta_local(pregunta):
    """Procesa una pregunta en modo local."""
    print("\n" + "="*80)
    print(f"PREGUNTA: {pregunta}")
    print("="*80)
    
    try:
        # Paso 1: Generar SQL
        print("\n[1/3] Generando SQL con embeddings semánticos...")
        sql = generar_sql(pregunta)
        
        if not sql or sql is None:
            # Es pregunta de describir el asistente del sistema
            print("Pregunta sobre el sistema detectada - usando respuesta directa\n")
            respuesta = _respuesta_pregunta_sistema(pregunta)
            print(f"RESPUESTA:\n{respuesta}\n")
            return True
        
        print(f"SQL:\n{sql}\n")
        
        # Paso 2: Ejecutar SQL
        print("[2/3] Ejecutando query en PostgreSQL...")
        resultado = ejecutar_sql(sql)
        
        if 'error' in resultado:
            print(f"ERROR en query: {resultado['error']}\n")
            return False
        
        filas = resultado.get('filas', [])
        columnas = resultado.get('columnas', [])
        
        print(f"Resultados: {len(filas)} fila(s)")
        if filas:
            for i, fila in enumerate(filas[:3], 1):
                print(f"  {i}. {fila}")
            if len(filas) > 3:
                print(f"  ... y {len(filas)-3} más")
        
        # Paso 3: Generar respuesta
        print("\n[3/3] Generando respuesta con Ollama (puede tomar 10-30 seg)...\n")
        respuesta = generar_respuesta(pregunta, resultado)
        
        print("="*80)
        print("RESPUESTA FINAL:")
        print("="*80)
        print(f"\n{respuesta}\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"ERROR: {e}\n")
        return False

def _respuesta_pregunta_sistema(pregunta):
    """Responde preguntas generales del sistema."""
    pregunta_lower = pregunta.lower()
    
    if any(p in pregunta_lower for p in ['nombre', 'llamas', 'eres', 'quien eres']):
        return "Soy la asistente del sistema THANIA. THANIA significa: Tecnología Híbrida De Análisis Y Navegación De Información Automática. Fui creada por Richar Andres Romero Pinto. Puedes ver mi código en: https://github.com/estudiantericharromero11a-ops. Estoy preparada para responder preguntas sobre profesores, clases, horarios, ubicaciones y más de tu universidad."
    elif any(p in pregunta_lower for p in ['sirves', 'proposito', 'funcion', 'haces', 'para qué']):
        return "Mi función es ayudarte a encontrar información académica de la universidad."
    elif any(p in pregunta_lower for p in ['hola', 'saludos', 'buenos']):
        return "¡Hola! Me alegra conocerte. Estoy preparada para ayudarte con datos universitarios."
    else:
        return "Soy la asistente del sistema. Puedo ayudarte con información sobre programas, materias, profesores y horarios."

def modo_local():
    """Interfaz interactiva en modo local."""
    print("\n" + "="*80)
    print("Sistema Universitario THANIA - MODO LOCAL INTERACTIVO")
    print("="*80)
    print("\nEste es el modo local. Escribe 'salir' para terminar.")
    print("Ejemplos de preguntas:")
    print("  - ¿Quiénes son los profesores?")
    print("  - ¿Cuál es el horario de las clases?")
    print("  - ¿En dónde están las aulas?")
    print("  - ¿Cuál es tu nombre?")
    print()
    
    while True:
        try:
            pregunta = input("Tu pregunta: ").strip()
            
            if not pregunta:
                print("Por favor ingresa una pregunta.\n")
                continue
            
            if pregunta.lower() in ['salir', 'exit', 'quit']:
                print("\nGracias por usar THANIA. Adios!\n")
                break
            
            procesar_pregunta_local(pregunta)
            
        except KeyboardInterrupt:
            print("\n\nAplicación detenida. Adios!\n")
            break
        except Exception as e:
            logger.error(f"Error en modo local: {e}")
            print(f"Error: {e}\n")

# ============================================================================
# MODO WEB API - SERVIDOR FASTAPI
# ============================================================================

class QueryRequest(BaseModel):
    query: str

def procesar_pregunta_api(pregunta: str) -> dict:
    """Procesa una pregunta para la API web."""
    try:
        # Paso 1: Generar SQL
        sql = generar_sql(pregunta)
        
        if not sql or sql is None:
            # Es pregunta de describir el asistente del sistema
            respuesta = _respuesta_pregunta_sistema(pregunta)
            return {"response": respuesta, "sql": None, "status": "success"}
        
        # Paso 2: Ejecutar SQL
        resultado = ejecutar_sql(sql)
        
        if 'error' in resultado:
            return {"response": f"Error en la consulta: {resultado['error']}", "sql": sql, "status": "error"}
        
        # Paso 3: Generar respuesta
        respuesta = generar_respuesta(pregunta, resultado)
        
        return {"response": respuesta, "sql": sql, "status": "success"}
        
    except Exception as e:
        logger.error(f"Error en API: {e}")
        return {"response": f"Error interno: {str(e)}", "sql": None, "status": "error"}

def crear_app_fastapi():
    """Crea la aplicación FastAPI."""
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI no está instalado. Instala con: pip install fastapi uvicorn")
    
    app = FastAPI(title="THANIA IA API", description="API para el asistente inteligente universitario", version="0.1.0")
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Permitir todas las origines (para desarrollo)
        allow_credentials=True,
        allow_methods=["*"],  # Permitir todos los métodos
        allow_headers=["*"],  # Permitir todos los headers
    )
    
    @app.get("/")
    def root():
        return {"message": "THANIA IA API v0.1.0", "status": "running"}
    
    @app.post("/query")
    def query_endpoint(request: QueryRequest):
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        result = procesar_pregunta_api(request.query)
        return result
    
    return app

def _find_available_port(host: str, port: int, max_attempts: int = 20) -> int:
    """Busca un puerto disponible comenzando desde el puerto solicitado."""
    import socket

    for candidate in range(port, port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, candidate))
                return candidate
            except OSError:
                continue

    raise OSError(f"No se encontró un puerto disponible entre {port} y {port + max_attempts - 1}")


def modo_web(host: str = "0.0.0.0", port: int = 8000):
    """Ejecuta el servidor web API."""
    if not FASTAPI_AVAILABLE:
        print("ERROR: FastAPI no está disponible. Instala con: pip install fastapi uvicorn")
        return
    
    app = crear_app_fastapi()
    
    try:
        port = _find_available_port(host, port)
    except OSError as e:
        print(f"ERROR: {e}")
        return
    
    print("\n" + "="*80)
    print("Sistema Universitario THANIA - MODO WEB API")
    print("="*80)
    print(f"Servidor iniciando en http://{host}:{port}")
    print("Endpoints disponibles:")
    print(f"  GET  http://{host}:{port}/        - Estado del servidor")
    print(f"  POST http://{host}:{port}/query   - Enviar pregunta (JSON: {{'query': 'tu pregunta'}})")
    print("\nPresiona Ctrl+C para detener el servidor.")
    print("="*80)
    
    try:
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        print("\n\nServidor detenido. Adios!\n")

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal de la aplicación."""
    parser = argparse.ArgumentParser(
        description="Sistema Universitario THANIA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python app.py                    # Modo local interactivo (por defecto)
  python app.py "¿Pregunta?"       # Una sola pregunta en modo local
  python app.py --local            # Modo local interactivo (explícito)
  python app.py --telegram         # Modo Telegram
  python app.py --web              # Modo Web API (FastAPI)
        """
    )
    
    parser.add_argument(
        '--telegram',
        action='store_true',
        help='Ejecutar en modo Telegram'
    )
    parser.add_argument(
        '--web',
        action='store_true',
        help='Ejecutar servidor web API (FastAPI)'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host para el servidor web (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Puerto para el servidor web (default: 8000)'
    )
    parser.add_argument(
        'pregunta',
        nargs='?',
        help='(Modo local) Una pregunta para procesar'
    )
    
    args = parser.parse_args()
    
    logger.info("Iniciando sistema universitario THANIA...")
    logger.info("Usando modelo Ollama: llama3")
    
    try:
        if args.web:
            # Modo Web API
            logger.info(f"Modo web API - host={args.host}, port={args.port}")
            modo_web(host=args.host, port=args.port)
        elif args.telegram:
            # Modo Telegram
            logger.info("Modo Telegram - iniciando bot")
            run_bot()
        else:
            # Modo LOCAL (por defecto)
            if args.pregunta:
                # Pregunta única
                logger.info(f"Modo local - pregunta única")
                procesar_pregunta_local(args.pregunta)
            else:
                # Interactivo
                logger.info("Modo local - interfaz interactiva")
                modo_local()
    
    except KeyboardInterrupt:
        logger.info("Aplicación detenida por el usuario")
    except Exception as e:
        logger.error(f"Error fatal en la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()