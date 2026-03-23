import logging
import asyncio
import time
import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import Conflict, NetworkError, TelegramError
from pipeline.generate_sql import generar_sql
from pipeline.execute_query import ejecutar_sql
from pipeline.human_response import generar_respuesta
from config import TELEGRAM_TOKEN

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start"""
    await update.message.reply_text(
        "¡Hola! Soy tu THANIA universitaria THANIA.\n\n"
        "Pregúntame sobre:\n"
        "- Profesores y docentes\n"
        "- Aulas y ubicaciones\n"
        "- Horarios de clases\n"
        "- Materias y programas\n"
        "- Estudiantes y roles\n\n"
        "¿Qué deseas saber?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de usuarios"""
    try:
        pregunta = update.message.text
        logger.info(f"Mensaje recibido: {pregunta}")
        
        # Enviar indicador de escritura
        await update.message.chat.send_action("typing")
        
        # Generar SQL
        sql = generar_sql(pregunta)
        if sql is None or "Error" in str(sql):
            respuesta = sql if sql else "No entiendo tu pregunta"
        else:
            # Ejecutar SQL
            resultado = ejecutar_sql(sql)
            
            # Generar respuesta
            if resultado and (resultado.get('filas') or resultado.get('error')):
                respuesta = generar_respuesta(pregunta, resultado)
            else:
                respuesta = "No se encontraron resultados en la base de datos."
        
        await update.message.reply_text(respuesta)
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        try:
            await update.message.reply_text(
                "Disculpa, ocurrió un error procesando tu pregunta. Intenta de nuevo."
            )
        except Exception as send_error:
            logger.error(f"Error enviando mensaje de error: {send_error}")

async def cleanup_and_start_polling(application):
    """
    Limpia webhooks y prepara el bot para polling.
    Esto es CRÍTICO para evitar el error 409 Conflict.
    """
    try:
        # Paso 1: Eliminar webhook si existe
        logger.info("Eliminando webhook anterior (si existe)...")
        await application.bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook eliminado correctamente")
        
        # Paso 2: Pequeña pausa para asegurar que Telegram procesó la solicitud
        await asyncio.sleep(1)
        
        # Paso 3: Iniciar polling
        logger.info("Iniciando polling...")
        await application.start()
        logger.info("Bot iniciado. Escuchando mensajes...")
        
        # Paso 4: Mantenerse activo
        await application.updater.start_polling(
            allowed_updates=["message"],
            drop_pending_updates=True
        )
        
    except TelegramError as e:
        logger.error(f"Error de Telegram: {e}")
        raise
    except Exception as e:
        logger.error(f"Error preparando polling: {e}")
        raise

def run_bot():
    """
    Inicia el bot de forma limpia y robusta.
    Maneja errores de Telegram de forma inteligente.
    """
    logger.info("Iniciando bot de Telegram THANIA...")
    
    max_reintentos = 3
    reintento = 0
    
    while reintento < max_reintentos:
        try:
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            
            # Agregar handlers
            application.add_handler(CommandHandler("start", start))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            
            # Ejecutar con polling limpio
            logger.info(f"Intento {reintento + 1}/{max_reintentos}")
            application.run_polling(
                allowed_updates=["message"],
                drop_pending_updates=True
            )
            
            # Si llegamos aquí, el polling se ejecutó sin problemas
            break
            
        except Conflict as e:
            reintento += 1
            logger.error(f"[INTENTO {reintento}] Conflicto 409: {e}")
            logger.error("Otra instancia del bot está usando este token")
            
            if reintento < max_reintentos:
                espera = 10 + (reintento * 5)  # 15, 20, 25 segundos
                logger.info(f"Esperando {espera} segundos antes de reintentar...")
                time.sleep(espera)
            else:
                logger.error("Máximo de reintentos alcanzado. Abortando.")
                raise
                
        except NetworkError as e:
            reintento += 1
            logger.error(f"[INTENTO {reintento}] Error de red: {e}")
            
            if reintento < max_reintentos:
                logger.info("Reintentando en 5 segundos...")
                time.sleep(5)
            else:
                logger.error("Máximo de reintentos de red alcanzado.")
                raise
                
        except KeyboardInterrupt:
            logger.info("Bot detenido por el usuario (Ctrl+C)")
            break
            
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            raise
    
    # Limpiar variable de entorno
    if os.environ.get("THANIA_BOT_RUNNING"):
        del os.environ["THANIA_BOT_RUNNING"]
    
    logger.info("Bot finalizado")

if __name__ == "__main__":
    run_bot()