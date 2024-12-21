from aiogram import types
from aiogram.dispatcher import Dispatcher
from Project3.weather_bot.bot.utils import escape_markdown_v2
import logging

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message):

    welcome_message = (
        "👋 Привет! Я бот для проверки погоды по маршруту.\n\n"
        "Вот что я могу:\n"
        "• Получить прогноз погоды для начальной и конечной точки маршрута.\n"
        "• Добавить промежуточные остановки.\n"
        "• Предоставить прогноз на выбранный период.\n"
        "• Отобразить прогнозы на карте и графиках.\n\n"
        "Используй /help, чтобы узнать больше о доступных командах."
    )
    escaped_message = escape_markdown_v2(welcome_message)
    logger.info(f"Отправляем сообщение /start пользователю {message.from_user.id}")
    await message.reply(
        escaped_message,
        parse_mode="MarkdownV2"
    )

async def cmd_help(message: types.Message):

    help_message = (
        "ℹ️ *Список доступных команд:*\n\n"
        "/start - Приветствие и описание возможностей бота\n"
        "/help - Список доступных команд и инструкция по использованию\n"
        "/weather - Запрос прогноза погоды по маршруту\n\n"
        "*Использование команды /weather:*\n"
        "1. Введи начальную точку маршрута.\n"
        "2. Введи конечную точку маршрута.\n"
        "3. Выбери количество дней для прогноза.\n"
        "4. При необходимости, добавь промежуточные точки.\n\n"
        "Также ты можешь отправить свою геолокацию для удобства."
    )
    escaped_message = escape_markdown_v2(help_message)
    logger.info(f"Отправляем сообщение /help пользователю {message.from_user.id}")
    await message.reply(
        escaped_message,
        parse_mode="MarkdownV2"
    )

def register_commands(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start")
    dp.register_message_handler(cmd_help, commands="help")
