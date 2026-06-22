# itsm.mos.ru_4me_parser_bot — Docker образ

FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создаём папку для БД и last_check
RUN mkdir -p db && chmod 777 db

# Не запускаем бот при сборке
CMD ["python", "main.py"]