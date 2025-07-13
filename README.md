# TTA Bot - Telegram Bot для жалоб

Бот для приема жалоб через Telegram и FastAPI с автоматической пересылкой администратору.

## Возможности

- Прием жалоб через Telegram (polling)
- Прием жалоб через FastAPI REST API
- Прием отзывов через FastAPI REST API
- Автоматическая пересылка администратору
- Команды для администрирования
- Автоматическая документация API (Swagger UI)

## Установка

1. Установите зависимости:

```bash
uv sync
```

2. Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

3. Заполните конфигурацию в `.env`:
   - `BOT_TOKEN` - получите от @BotFather
   - `ADMIN_ID` - ваш ID (получите через @userinfobot)
   - `PORT` - порт для API сервера (по умолчанию 8080)

## Запуск

```bash
uv run python main.py
```

После запуска:

- API будет доступен на `http://localhost:8080`
- Swagger UI документация: `http://localhost:8080/docs`
- ReDoc документация: `http://localhost:8080/redoc`

## FastAPI REST API для внешних жалоб и отзывов

### Жалобы

Отправьте POST запрос на `/complaint` с JSON:

```json
{
  "complaint": "Текст жалобы",
  "user_name": "Имя пользователя",
  "email": "user@example.com",
  "phone": "+7123456789"
}
```

### Отзывы

Отправьте POST запрос на `/feedback` с JSON:

```json
{
  "feedback": "Текст отзыва",
  "user_name": "Имя пользователя",
  "email": "user@example.com",
  "phone": "+7123456789"
}
```

## Команды бота

- `/start` - Приветствие
- `/status` - Статус бота (только для админа)
- Любое другое сообщение - жалоба

## Деплой

Для деплоя на сервер убедитесь, что:

1. Порт `PORT` открыт для API запросов
2. Бот имеет доступ к интернету для polling

Пример запуска в продакшене:

```bash
# Через systemd или supervisor
uv run python main.py

# Или через Docker
docker build -t tta-bot .
docker run -p 8080:8080 --env-file .env tta-bot
```
