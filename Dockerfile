FROM python:3.8-slim

# Встановлення git та curl
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Встановлення Railway CLI
RUN curl -sSL https://raw.githubusercontent.com/railwayapp/cli/master/install.sh | bash

# Копіювання requirements.txt та встановлення залежностей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Клонування репозиторію
RUN git clone https://github.com/Viktorbauhelfer/construction-bot.git /app

# Встановлення робочого каталогу
WORKDIR /app

# Копіювання всіх файлів до контейнера
COPY . /app

# Команда для запуску бота
CMD ["python", "bot.py"]
