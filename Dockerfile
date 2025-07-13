# Используем официальный Python образ
FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml ./

# Извлекаем зависимости из pyproject.toml и устанавливаем через pip
RUN pip install \
    aiogram \
    fastapi \
    uvicorn \
    python-dotenv \
    pydantic \
    httpx \
    requests

# Копируем исходный код
COPY main.py .

# Создаем пользователя для запуска приложения (безопасность)
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Открываем порт
EXPOSE 8080

# Команда для запуска приложения
CMD ["python", "main.py"] 