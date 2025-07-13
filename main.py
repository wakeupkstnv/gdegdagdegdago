import asyncio
import logging
import os
from typing import Optional
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")
ADMIN_ID = int(os.getenv("ADMIN_ID", "your_admin_id_here"))
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", "8080"))

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Pydantic модели для API
class ComplaintRequest(BaseModel):
    complaint: str
    user_name: Optional[str] = "Неизвестный"
    email: Optional[str] = "Не указан"
    phone: Optional[str] = "Не указан"
    post_id: Optional[str] = "Не указан"

class FeedbackRequest(BaseModel):
    feedback: str
    user_name: Optional[str] = "Неизвестный"
    email: Optional[str] = "Не указан"
    phone: Optional[str] = "Не указан"


@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "Привет! Я бот для обработки жалоб.\n"
        "Отправь мне жалобу, и я перешлю её администратору."
    )


@dp.message(Command("status"))
async def cmd_status(message: Message):
    """Проверка статуса бота (только для админа)"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    
    me = await bot.get_me()
    await message.answer(
        f"Статус бота:\n"
        f"Бот: @{me.username}\n"
        f"Режим: Polling (без вебхуков)\n"
        f"Admin ID: {ADMIN_ID}\n"
        f"API сервер: http://localhost:{WEBAPP_PORT}"
    )


@dp.message()
async def handle_complaint(message: Message):
    """Обработчик жалоб от пользователей"""
    if message.from_user.id == ADMIN_ID:
        await message.answer("Иаиа, сгл")
        return
   
    await message.answer("Cет четам")



# Создаем FastAPI приложение с lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if not await init_bot():
        raise RuntimeError("Не удалось инициализировать бота")
    
    # Запускаем бота в фоновой задаче
    task = asyncio.create_task(dp.start_polling(bot, skip_updates=True))
    
    yield
    
    # Shutdown
    task.cancel()
    await bot.session.close()

app = FastAPI(
    title="TTA Bot API",
    description="API для отправки жалоб и отзывов через Telegram бота",
    version="1.0.0",
    lifespan=lifespan
)


# FastAPI эндпоинты
@app.post("/complaint")
async def create_complaint(complaint: ComplaintRequest):
    """Создать жалобу"""
    try:
        # Формируем сообщение для админа
        complaint_text = (
            f"📝 Новая жалоба через API:\n\n"
            f"👤 От: {complaint.user_name}\n"
            f"📧 Email: {complaint.email}\n"
            f"📱 Телефон: {complaint.phone}\n\n"
            f"💬 Жалоба:\n{complaint.complaint}\n"
            f"🔗 Пост: {complaint.post_id}\n"
        )
        
        await bot.send_message(ADMIN_ID, complaint_text)
        return {"status": "success", "message": "Жалоба отправлена администратору"}
        
    except Exception as e:
        logger.error(f"Ошибка при отправке жалобы: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при отправке жалобы")


@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {"status": "healthy", "service": "TTA Bot API"}


async def init_bot():
    """Инициализация бота"""
    logger.info("Инициализация бота...")
    
    # Проверяем токен
    try:
        me = await bot.get_me()
        logger.info(f"Бот запущен: @{me.username}")
    except Exception as e:
        logger.error(f"Ошибка получения информации о боте: {e}")
        return False
    
    # Удаляем webhook если был установлен
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook удален, используется polling")
    except Exception as e:
        logger.error(f"Ошибка удаления webhook: {e}")
    
    return True


def main():
    """Главная функция"""
    logger.info("Запуск TTA Bot API...")
    
    # Запускаем FastAPI сервер с uvicorn
    uvicorn.run(
        app,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()
