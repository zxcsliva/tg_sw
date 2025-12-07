"""
Flask приложение для Back4App
Альтернатива main.py для запуска через WSGI-сервер
"""

import os
import json
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import TELEGRAM_BOT_TOKEN
from database import init_db
from handlers import start, help_command, config_command, button_callback, status_command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Инициализация БД при старте
init_db()

# Инициализация приложения telegram.ext
tg_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Регистрация обработчиков
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("help", help_command))
tg_app.add_handler(CommandHandler("config", config_command))
tg_app.add_handler(CommandHandler("status", status_command))
tg_app.add_handler(CallbackQueryHandler(button_callback))


@app.route('/', methods=['GET'])
def index():
    """Проверка здоровья приложения"""
    return {
        'status': 'ok',
        'message': 'Smart Home Bot is running'
    }, 200


@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    """Webhook для получения обновлений от Telegram"""
    try:
        update = Update.de_json(request.get_json(force=True), tg_app.bot)
        
        # Обработка обновления
        tg_app.process_update(update)
        
        return 'ok', 200
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook: {e}")
        return 'error', 500


@app.route('/health', methods=['GET'])
def health():
    """Healthcheck для Back4App"""
    return {'status': 'healthy'}, 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
