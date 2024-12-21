# main.py

import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

from Project3.weather_bot.bot.commands import register_commands
from Project3.weather_bot.bot.handlers import register_handlers

# Загрузка переменных окружения из .env файла
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_KEY = os.getenv('API_KEY')

if not API_TOKEN:
    raise ValueError("Не найден TELEGRAM_TOKEN в переменных окружения.")

if not API_KEY:
    raise ValueError("Не найден API_KEY в переменных окружения.")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Измените на DEBUG для более подробного логирования
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.MARKDOWN_V2)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Регистрация команд и обработчиков
register_commands(dp)
register_handlers(dp)

if __name__ == '__main__':
    logger.info("Бот запускается...")
    executor.start_polling(dp, skip_updates=True)
