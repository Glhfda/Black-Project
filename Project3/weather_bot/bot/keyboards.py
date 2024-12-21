# weather_bot/bot/keyboards.py

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def days_keyboard():

    keyboard = [
        [InlineKeyboardButton("1 день", callback_data='1')],
        [InlineKeyboardButton("3 дня", callback_data='3')],
        [InlineKeyboardButton("5 дней", callback_data='5')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def confirmation_keyboard():

    keyboard = [
        [InlineKeyboardButton("Да", callback_data='yes')],
        [InlineKeyboardButton("Нет", callback_data='no')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def location_keyboard():

    keyboard = [
        [KeyboardButton("📍 Отправить геолокацию", request_location=True)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
