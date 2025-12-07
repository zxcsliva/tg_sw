#!/usr/bin/env python3
"""
ТГ-бот для конфигуратора умного дома
Поддерживает запуск с polling (локально) и webhook (облако)
"""

import os
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
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


def run_bot():
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
    
    # Polling режим
    print("🤖 Бот запущен в режиме polling!")
    print("Нажмите Ctrl+C для остановки.")
    app.run_polling()


def main():
    """Запуск Flask и бота в отдельных потоках"""
    port = int(os.getenv('PORT', 8080))
    print(f"🚀 Запуск приложения на порту {port}")
    
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Запускаем бота в основном потоке
    run_bot()


if __name__ == '__main__':
    main()
