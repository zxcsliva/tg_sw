import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///smart_home.db')

# Константы для конфигурации умного дома
ROOMS = ['Спальня', 'Гостиная', 'Кухня', 'Ванная', 'Прихожая']
DEVICES = {
    'Свет': ['Потолочный светильник', 'Настольная лампа', 'Настенный светильник'],
    'Климат': ['Кондиционер', 'Обогреватель', 'Увлажнитель'],
    'Безопасность': ['Камера', 'Датчик движения', 'Дверной замок'],
    'Развлечение': ['Телевизор', 'Музыкальная система', 'Проектор']
}

# Коды для callback'ов
CALLBACK_ROOM = 'room_'
CALLBACK_DEVICE = 'device_'
CALLBACK_CONTROL = 'control_'
CALLBACK_STATUS = 'status_'
CALLBACK_DELETE = 'delete_'
