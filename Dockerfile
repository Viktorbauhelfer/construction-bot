# Використовуємо базовий образ з Python
FROM python:3.8-slim

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Встановлення Railway CLI
RUN curl -sSL https://raw.githubusercontent.com/railwayapp/cli/master/install.sh | bash

# Додавання Railway CLI до PATH
ENV PATH="/root/.railway/bin:${PATH}"

# Клонування репозиторію
RUN git clone https://github.com/Viktorbauhelfer/construction-bot.git /app

# Встановлюємо робочу директорію
WORKDIR /app

# Встановлення залежностей
RUN pip install --no-cache-dir -r requirements.txt

# Виводимо інформацію про файли в директорії для налагодження
RUN ls -la

# Запуск бота
CMD ["python", "bot.py"]
