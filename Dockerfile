# Використовуємо базовий образ з Python
FROM python:3.8-slim

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Клонування репозиторію
RUN git clone https://github.com/Viktorbauhelfer/construction-bot.git /app

# Встановлюємо робочу директорію
WORKDIR /app

# Встановлення залежностей
RUN pip install --no-cache-dir -r requirements.txt

# Запуск бота
CMD ["python", "bot.py"]
