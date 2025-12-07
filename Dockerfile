# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения
COPY . .

# Создаем директорию для БД (если используем SQLite)
RUN mkdir -p /app/data

# Устанавливаем переменные окружения по умолчанию
ENV BOT_MODE=polling
ENV PYTHONUNBUFFERED=1

# Команда для запуска приложения
CMD ["python", "main.py"]
