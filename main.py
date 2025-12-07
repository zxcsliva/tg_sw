#!/usr/bin/env python3
"""
ТГ-бот для конфигуратора умного дома
Поддерживает запуск с polling (локально) и webhook (облако)
"""

import os
import sys
import asyncio
import threading
from flask import Flask
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import TELEGRAM_BOT_TOKEN
from database import init_db
from handlers import start, help_command, config_command, button_callback, status_command

# Flask приложение для health check
flask_app = Flask(__name__)


@flask_app.route('/health', methods=['GET'])
def health():
    """Health check endpoint для Back4App"""
    return {'status': 'healthy'}, 200


@flask_app.route('/', methods=['GET'])
def index():
    """Главная страница"""
    return {'message': 'Smart Home Bot is running'}, 200


def run_flask():
    """Запуск Flask в отдельном потоке"""
    port = int(os.getenv('PORT', 8080))
    print(f"🌐 Flask запущен на http://0.0.0.0:{port}")
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)


async def run_bot():
    """Запуск бота"""
    # Инициализация БД
    init_db()
    
    # Создание приложения
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрация обработчиков команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("config", config_command))
    app.add_handler(CommandHandler("status", status_command))
    
    # Регистрация обработчика callback'ов
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 Бот запущен в режиме polling!")
    
    # Polling режим
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=[])
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("Остановка бота...")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


def main():
    """Запуск Flask и бота"""
    port = int(os.getenv('PORT', 8080))
    print(f"🚀 Запуск приложения на порту {port}")
    
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Даем Flask время на запуск
    import time
    time.sleep(1)
    
    # Запускаем бота в основном потоке
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n✋ Приложение остановлено")
        sys.exit(0)


if __name__ == '__main__':
    main()
