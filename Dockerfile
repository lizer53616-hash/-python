FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов
COPY requirements.txt .
COPY src/ ./src/
COPY data/ ./data/
COPY main.py .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Запуск приложения
CMD ["python", "main.py"]
