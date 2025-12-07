#!/usr/bin/env python3
"""
ТГ-бот для конфигуратора умного дома
Поддерживает запуск с polling (локально) и webhook (облако)
"""

import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import TELEGRAM_BOT_TOKEN
from database import init_db
from handlers import start, help_command, config_command, button_callback, status_command


def main():
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
    
    # Определяем режим запуска (polling или webhook)
    mode = os.getenv('BOT_MODE', 'polling')
    
    if mode == 'webhook':
        # Webhook режим для облака (Back4App)
        webhook_url = os.getenv('WEBHOOK_URL')
        port = int(os.getenv('PORT', 8443))
        
        print(f"🤖 Бот запущен в режиме webhook!")
        print(f"📍 URL: {webhook_url}")
        print(f"🔌 Порт: {port}")
        
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TELEGRAM_BOT_TOKEN,
            webhook_url=f"{webhook_url}/{TELEGRAM_BOT_TOKEN}"
        )
    else:
        # Polling режим для локальной разработки
        print("🤖 Бот запущен в режиме polling!")
        print("Нажмите Ctrl+C для остановки.")
        app.run_polling()


if __name__ == '__main__':
    main()
