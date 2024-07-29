FROM python:3.8-slim

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Встановлення Railway CLI
RUN curl -sSL https://raw.githubusercontent.com/railwayapp/cli/master/install.sh | bash

# Клонування репозиторію
RUN git clone https://github.com/Viktorbauhelfer/construction-bot.git /app

# Встановлення робочої директорії
WORKDIR /app

# Встановлення Python-залежностей
RUN pip install --no-cache-dir -r requirements.txt

# Виконання перевірки файлів
RUN ls -la

# Запуск бота
CMD ["python", "bot.py"]
