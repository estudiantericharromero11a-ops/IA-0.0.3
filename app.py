 #!/usr/bin/env python3
"""
Aplicación principal del sistema universitario THANIA.
Soporta dos modos:
  1. Modo LOCAL (interactivo): python app.py --local
  2. Modo TELEGRAM: python app.py --telegram (o solo python app.py)
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
        return "Soy el asistente del sistema THANIA. Estoy preparado para responder preguntas sobre profesores, clases, horarios, ubicaciones y más de tu universidad."
    elif any(p in pregunta_lower for p in ['sirves', 'proposito', 'funcion', 'haces', 'para qué']):
        return "Mi función es ayudarte a encontrar información académica de la universidad."
    elif any(p in pregunta_lower for p in ['hola', 'saludos', 'buenos']):
        return "¡Hola! Me alegra conocerte. Estoy listo para ayudarte con datos universitarios."
    else:
        return "Soy el asistente del sistema. Puedo ayudarte con información sobre programas, materias, profesores y horarios."

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
        """
    )
    
    parser.add_argument(
        '--telegram',
        action='store_true',
        help='Ejecutar en modo Telegram (default es local)'
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
        if args.telegram:
            # Modo Telegram (solo si se especifica)
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