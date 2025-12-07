# ТГ-бот для конфигуратора умного дома 🏠

Телеграм-бот для управления и конфигурации умной домой. Поддерживает запуск локально и в облаке (Back4App).

## 📋 Функционал

- ✅ Добавление комнат и устройств
- ✅ Просмотр статуса всех устройств
- ✅ Управление конфигурацией
- ✅ Поддержка 4 типов устройств (Свет, Климат, Безопасность, Развлечение)
- ✅ Сохранение конфигурации в БД
- ✅ Поддержка Polling (локально) и Webhook (облако)

## 🚀 Локальный запуск (Polling)

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` и добавьте ваш Telegram Bot Token:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
BOT_MODE=polling
DATABASE_URL=sqlite:///smart_home.db
```

### 3. Запуск бота

```bash
python main.py
```

## ☁️ Хостинг на Back4App (Webhook)

### 1. Создание приложения на Back4App

1. Зарегистрируйтесь на [back4app.com](https://www.back4app.com)
2. Создайте новое приложение (Python)
3. Скопируйте URL вашего приложения (например: `https://your-app-name.back4app.io`)

### 2. Подготовка к деплою

```bash
# Инициализируем git репозиторий (если еще не инициализирован)
git init

# Добавляем remote для Back4App
git remote add back4app https://git.back4app.com/your-username/your-app-name.git
```

### 3. Установка переменных окружения на Back4App

В Dashboard Back4App перейдите в Settings → Environment Variables и установите:

```
TELEGRAM_BOT_TOKEN=your_bot_token
BOT_MODE=webhook
WEBHOOK_URL=https://your-app-name.back4app.io
PORT=8080
DATABASE_URL=sqlite:///smart_home.db
```

Или используйте PostgreSQL (рекомендуется):
```
DATABASE_URL=postgresql://user:password@back4app-postgres/smart_home
```

### 4. Деплой на Back4App

```bash
# Добавляем файлы
git add .
git commit -m "Deploy bot to Back4App"

# Пушим на Back4App
git push back4app main
```

### 5. Регистрация Webhook в Telegram

После успешного деплоя выполните этот запрос один раз (замените значения):

```bash
curl -X POST https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-app-name.back4app.io/<YOUR_BOT_TOKEN>"}'
```

Или используйте Python:

```python
import requests

token = "YOUR_BOT_TOKEN"
webhook_url = "https://your-app-name.back4app.io/YOUR_BOT_TOKEN"

response = requests.post(
    f"https://api.telegram.org/bot{token}/setWebhook",
    json={"url": webhook_url}
)
print(response.json())
```

### 6. Проверка статуса Webhook

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

## 📱 Использование

### Команды:

- `/start` - Главное меню
- `/config` - Начать настройку устройств
- `/status` - Показать статус всех устройств
- `/help` - Справка

### Поддерживаемые устройства:

**🔦 Свет:**
- Потолочный светильник
- Настольная лампа
- Настенный светильник

**❄️ Климат:**
- Кондиционер
- Обогреватель
- Увлажнитель

**📹 Безопасность:**
- Камера
- Датчик движения
- Дверной замок

**🎬 Развлечение:**
- Телевизор
- Музыкальная система
- Проектор

## 📁 Структура проекта

```
BOT/
├── main.py              # Точка входа
├── config.py            # Конфигурация
├── database.py          # Модели БД и инициализация
├── handlers.py          # Обработчики команд и callback'ов
├── requirements.txt     # Зависимости
├── .env.example         # Пример переменных окружения
└── README.md            # Документация
```

## 🔧 Возможные улучшения

- [ ] Интеграция с API умного дома
- [ ] Расширенное управление состоянием устройств
- [ ] Уведомления о статусе устройств
- [ ] Планирование включения/выключения устройств
- [ ] Поддержка сценариев автоматизации
- [ ] История изменений конфигурации
- [ ] Мультиязычная поддержка

## 📝 Лицензия

MIT License

## 👨‍💻 Разработка

Для разработки требуется Python 3.8+

```bash
# Установка зависимостей для разработки
pip install -r requirements.txt

# Запуск в режиме разработки
python main.py
```
