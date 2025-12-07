from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import ROOMS, DEVICES, CALLBACK_ROOM, CALLBACK_DEVICE, CALLBACK_CONTROL, CALLBACK_STATUS, CALLBACK_DELETE
from database import get_session, SmartHomeConfig, UserSettings


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    session = get_session()
    
    # Проверяем есть ли пользователь в БД
    user_settings = session.query(UserSettings).filter_by(user_id=user_id).first()
    if not user_settings:
        user_settings = UserSettings(user_id=user_id, username=username)
        session.add(user_settings)
        session.commit()
    
    session.close()
    
    welcome_text = f"""
👋 Добро пожаловать в конфигуратор умного дома, {username}!

Я помогу вам настроить и управлять вашей умной домой.

Доступные команды:
/start - Главное меню
/config - Настроить устройства
/status - Статус всех устройств
/help - Справка
    """
    
    keyboard = [
        [InlineKeyboardButton("⚙️ Настроить устройства", callback_data="config")],
        [InlineKeyboardButton("📊 Статус устройств", callback_data="status")],
        [InlineKeyboardButton("❌ Удалить конфигурацию", callback_data="clear_config")],
        [InlineKeyboardButton("ℹ️ Справка", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = """
🏠 *Конфигуратор умного дома*

*Основной функционал:*
• Добавление комнат и устройств
• Управление состоянием устройств
• Просмотр конфигурации
• Удаление устройств

*Поддерживаемые типы устройств:*

🔦 *Свет:* Потолочный светильник, Настольная лампа, Настенный светильник
❄️ *Климат:* Кондиционер, Обогреватель, Увлажнитель
📹 *Безопасность:* Камера, Датчик движения, Дверной замок
🎬 *Развлечение:* Телевизор, Музыкальная система, Проектор

*Команды:*
/start - Главное меню
/config - Начать настройку
/status - Показать статус
/help - Эта справка
    """
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def config_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начало конфигурации - выбор комнаты"""
    keyboard = []
    for room in ROOMS:
        keyboard.append([InlineKeyboardButton(room, callback_data=f"{CALLBACK_ROOM}{room}")])
    
    keyboard.append([InlineKeyboardButton("➕ Добавить новую комнату", callback_data="add_room")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🏠 Выберите комнату для добавления устройства:",
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатия на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    session = get_session()
    
    # Выбор комнаты
    if query.data.startswith(CALLBACK_ROOM):
        room = query.data.replace(CALLBACK_ROOM, "")
        context.user_data['selected_room'] = room
        
        keyboard = []
        for device_type, devices in DEVICES.items():
            keyboard.append([InlineKeyboardButton(f"🔹 {device_type}", callback_data=f"{CALLBACK_DEVICE}{device_type}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"🏠 Комната: {room}\n\nВыберите тип устройства:",
            reply_markup=reply_markup
        )
    
    # Выбор типа устройства
    elif query.data.startswith(CALLBACK_DEVICE):
        device_type = query.data.replace(CALLBACK_DEVICE, "")
        context.user_data['selected_device_type'] = device_type
        
        devices = DEVICES.get(device_type, [])
        keyboard = []
        for device in devices:
            callback = f"{CALLBACK_CONTROL}{device_type}|{device}"
            keyboard.append([InlineKeyboardButton(device, callback_data=callback)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"🔹 Тип: {device_type}\n\nВыберите устройство:",
            reply_markup=reply_markup
        )
    
    # Выбор конкретного устройства и сохранение
    elif query.data.startswith(CALLBACK_CONTROL):
        data = query.data.replace(CALLBACK_CONTROL, "").split("|")
        device_type = data[0]
        device_name = data[1]
        room = context.user_data.get('selected_room')
        
        # Сохраняем в БД
        config = SmartHomeConfig(
            user_id=user_id,
            room=room,
            device_type=device_type,
            device_name=device_name
        )
        session.add(config)
        session.commit()
        
        await query.edit_message_text(
            f"✅ Устройство добавлено!\n\n"
            f"Комната: {room}\n"
            f"Тип: {device_type}\n"
            f"Устройство: {device_name}"
        )
    
    # Статус всех устройств
    elif query.data == CALLBACK_STATUS:
        configs = session.query(SmartHomeConfig).filter_by(user_id=user_id).all()
        
        if not configs:
            await query.edit_message_text("📊 Нет настроенных устройств")
        else:
            status_text = "📊 *Статус устройств:*\n\n"
            for config in configs:
                status = "✅ Включено" if config.is_active else "❌ Выключено"
                status_text += f"🏠 {config.room}\n"
                status_text += f"  {config.device_type}: {config.device_name}\n"
                status_text += f"  {status}\n\n"
            
            keyboard = [
                [InlineKeyboardButton("🔄 Обновить", callback_data=CALLBACK_STATUS)],
                [InlineKeyboardButton("👈 Назад", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(status_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    # Главное меню
    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("⚙️ Настроить устройства", callback_data="config")],
            [InlineKeyboardButton("📊 Статус устройств", callback_data=CALLBACK_STATUS)],
            [InlineKeyboardButton("❌ Удалить конфигурацию", callback_data="clear_config")],
            [InlineKeyboardButton("ℹ️ Справка", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🏠 Главное меню:", reply_markup=reply_markup)
    
    # Справка
    elif query.data == "help":
        help_text = """
🏠 *Конфигуратор умного дома*

*Основной функционал:*
• Добавление комнат и устройств
• Управление состоянием устройств
• Просмотр конфигурации
• Удаление устройств

*Поддерживаемые типы устройств:*
🔦 *Свет:* Потолочный светильник, Настольная лампа, Настенный светильник
❄️ *Климат:* Кондиционер, Обогреватель, Увлажнитель
📹 *Безопасность:* Камера, Датчик движения, Дверной замок
🎬 *Развлечение:* Телевизор, Музыкальная система, Проектор
        """
        keyboard = [[InlineKeyboardButton("👈 Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    # Очистка конфигурации
    elif query.data == "clear_config":
        session.query(SmartHomeConfig).filter_by(user_id=user_id).delete()
        session.commit()
        
        keyboard = [[InlineKeyboardButton("👈 Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("✅ Конфигурация очищена!", reply_markup=reply_markup)
    
    # Выбор комнаты для просмотра конфигурации
    elif query.data == "config":
        keyboard = []
        for room in ROOMS:
            keyboard.append([InlineKeyboardButton(room, callback_data=f"{CALLBACK_ROOM}{room}")])
        
        keyboard.append([InlineKeyboardButton("👈 Назад", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🏠 Выберите комнату:", reply_markup=reply_markup)
    
    session.close()


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /status"""
    user_id = update.effective_user.id
    session = get_session()
    
    configs = session.query(SmartHomeConfig).filter_by(user_id=user_id).all()
    
    if not configs:
        await update.message.reply_text("📊 Нет настроенных устройств")
    else:
        status_text = "📊 *Статус устройств:*\n\n"
        for config in configs:
            status = "✅ Включено" if config.is_active else "❌ Выключено"
            status_text += f"🏠 {config.room}\n"
            status_text += f"  {config.device_type}: {config.device_name}\n"
            status_text += f"  {status}\n\n"
        
        await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)
    
    session.close()
