FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование .env (для конфигурации)
COPY .env .

# Копирование кода приложения
COPY . .

# Создание пустого .env для SlowAPI (чтобы не искал файл)
RUN touch /.env && chmod 644 /.env
ENV ENV_FILE=/.env

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
