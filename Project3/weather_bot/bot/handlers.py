# weather_bot/bot/handlers.py

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, ReplyKeyboardRemove
from Project3.weather_bot.weather.api import get_location_data, get_weather_forecast
from Project3.weather_bot.bot.keyboards import days_keyboard, confirmation_keyboard, location_keyboard
from Project3.weather_bot.charts.chart_generator import generate_weather_chart
from Project3.weather_bot.bot.utils import escape_markdown_v2, generate_route_map_link
import logging
import os
from aiogram.dispatcher import Dispatcher
import requests

logger = logging.getLogger(__name__)


class WeatherForm(StatesGroup):
    start = State()  # Ввод начальной точки
    end = State()    # Ввод конечной точки
    stops = State()  # Ввод промежуточных точек
    confirm_add_more_stops = State()  # Подтверждение добавления дополнительных точек
    days = State()   # Выбор количества дней

async def weather_start(message: types.Message):

    await WeatherForm.start.set()
    prompt_message = "Введите начальную точку маршрута (например, Москва):"
    escaped_message = escape_markdown_v2(prompt_message)
    logger.info(f"Отправляем сообщение /weather пользователю {message.from_user.id}")
    await message.reply(
        escaped_message,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=location_keyboard()
    )

async def weather_start_location(message: types.Message, state: FSMContext):

    if message.location:
        # Если пользователь отправил геолокацию
        latitude = message.location.latitude
        longitude = message.location.longitude
        location = get_location_from_coords(latitude, longitude)
        if location:
            await state.update_data(start=location['city'], start_coords=(latitude, longitude))
            await WeatherForm.end.set()
            reply_text = f"Начальная точка установлена: {escape_markdown_v2(location['city'])}\nВведите конечную точку маршрута:"
            escaped_reply_text = escape_markdown_v2(reply_text)
            logger.info(f"Начальная точка установлена: {location['city']} для пользователя {message.from_user.id}")
            await message.reply(
                escaped_reply_text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=location_keyboard()
            )
        else:
            error_message = "Не удалось определить местоположение. Пожалуйста, введите название города:"
            escaped_error = escape_markdown_v2(error_message)
            logger.warning(f"Не удалось определить начальную точку по геолокации для пользователя {message.from_user.id}")
            await message.reply(
                escaped_error,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            await WeatherForm.start.set()
    else:
        city = message.text.strip()
        loc_data = get_location_data(city)
        if loc_data:
            await state.update_data(start=loc_data['city'], start_coords=(loc_data['lat'], loc_data['lon']))
            await WeatherForm.end.set()
            reply_text = f"Начальная точка установлена: {escape_markdown_v2(loc_data['city'])}\nВведите конечную точку маршрута:"
            escaped_reply_text = escape_markdown_v2(reply_text)
            logger.info(f"Начальная точка установлена: {loc_data['city']} для пользователя {message.from_user.id}")
            await message.reply(
                escaped_reply_text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=location_keyboard()
            )
        else:
            error_message = "Не удалось найти город. Пожалуйста, попробуйте снова:"
            escaped_error = escape_markdown_v2(error_message)
            logger.warning(f"Не удалось найти город '{city}' для пользователя {message.from_user.id}")
            await message.reply(
                escaped_error,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            await WeatherForm.start.set()

async def weather_end_location(message: types.Message, state: FSMContext):

    if message.location:
        # Если пользователь отправил геолокацию
        latitude = message.location.latitude
        longitude = message.location.longitude
        location = get_location_from_coords(latitude, longitude)
        if location:
            await state.update_data(end=location['city'], end_coords=(latitude, longitude))
            await WeatherForm.confirm_add_more_stops.set()
            reply_text = (
                f"Конечная точка установлена: {escape_markdown_v2(location['city'])}\n"
                f"Хотите добавить промежуточные точки?"
            )
            escaped_reply_text = escape_markdown_v2(reply_text)
            logger.info(f"Конечная точка установлена: {location['city']} для пользователя {message.from_user.id}")
            await message.reply(
                escaped_reply_text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=confirmation_keyboard()
            )
        else:
            error_message = "Не удалось определить местоположение. Пожалуйста, введите название города:"
            escaped_error = escape_markdown_v2(error_message)
            logger.warning(f"Не удалось определить конечную точку по геолокации для пользователя {message.from_user.id}")
            await message.reply(
                escaped_error,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            await WeatherForm.end.set()
    else:
        city = message.text.strip()
        loc_data = get_location_data(city)
        if loc_data:
            await state.update_data(end=loc_data['city'], end_coords=(loc_data['lat'], loc_data['lon']))
            await WeatherForm.confirm_add_more_stops.set()
            reply_text = (
                f"Конечная точка установлена: {escape_markdown_v2(loc_data['city'])}\n"
                f"Хотите добавить промежуточные точки?"
            )
            escaped_reply_text = escape_markdown_v2(reply_text)
            logger.info(f"Конечная точка установлена: {loc_data['city']} для пользователя {message.from_user.id}")
            await message.reply(
                escaped_reply_text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=confirmation_keyboard()
            )
        else:
            error_message = "Не удалось найти город. Пожалуйста, попробуйте снова:"
            escaped_error = escape_markdown_v2(error_message)
            logger.warning(f"Не удалось найти город '{city}' для пользователя {message.from_user.id}")
            await message.reply(
                escaped_error,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            await WeatherForm.end.set()

async def weather_confirm_add_more_stops(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработка ответа на добавление промежуточных точек.
    Объединённый обработчик для всех подтверждений добавления промежуточных точек.
    """
    data = callback_query.data
    user_id = callback_query.from_user.id
    if data == 'yes':
        # Остаёмся в состоянии 'stops' для ввода промежуточных точек
        reply_text = "Введите промежуточные точки через запятую (например, Тула, Орёл):"
        escaped_reply_text = escape_markdown_v2(reply_text)
        logger.info(f"Пользователь {user_id} выбрал добавить промежуточные точки.")
        await callback_query.message.reply(
            escaped_reply_text,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=location_keyboard()
        )
        await WeatherForm.stops.set()
    elif data == 'no':
        # Переходим к выбору дней
        await WeatherForm.next()
        reply_text = "Промежуточные точки не добавлены.\nВыберите количество дней для прогноза:"
        escaped_reply_text = escape_markdown_v2(reply_text)
        logger.info(f"Пользователь {user_id} отказался от добавления промежуточных точек.")
        await callback_query.message.reply(
            escaped_reply_text,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=days_keyboard()
        )
    else:
        logger.warning(f"Получены неожиданные данные callback_query: {data} от пользователя {user_id}")
    await callback_query.answer()

async def weather_add_stops(message: types.Message, state: FSMContext):

    stops_text = message.text.strip()
    stops = [s.strip() for s in stops_text.split(',') if s.strip()]
    validated_stops = []
    for city in stops:
        loc_data = get_location_data(city)
        if loc_data:
            validated_stops.append(loc_data['city'])
        else:
            error_message = f"Не удалось найти город: {escape_markdown_v2(city)}. Пожалуйста, попробуйте снова:"
            escaped_error = escape_markdown_v2(error_message)
            logger.warning(f"Не удалось найти город '{city}' при добавлении промежуточных точек для пользователя {message.from_user.id}")
            await message.reply(
                escaped_error,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return WeatherForm.stops  # Остаёмся в состоянии 'stops'

    # Сохраняем промежуточные точки
    user_data = await state.get_data()
    existing_stops = user_data.get('stops', [])
    existing_stops.extend(validated_stops)
    await state.update_data(stops=existing_stops)
    logger.info(f"Пользователь {message.from_user.id} добавил промежуточные точки: {validated_stops}")

    # Спрашиваем, хочет ли пользователь добавить ещё промежуточные точки
    keyboard = confirmation_keyboard()  # Используем клавиатуру подтверждения
    reply_text = "Промежуточные точки добавлены. Хотите добавить ещё?"
    escaped_reply_text = escape_markdown_v2(reply_text)
    await message.reply(
        escaped_reply_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=keyboard
    )
    await WeatherForm.confirm_add_more_stops.set()  # Переходим в подтверждение добавления ещё

async def weather_days_selection(callback_query: types.CallbackQuery, state: FSMContext):

    days = int(callback_query.data)
    await state.update_data(days=days)
    prompt_message = f"Получаю прогноз погоды на {days} день(дней)..."
    escaped_prompt = escape_markdown_v2(prompt_message)
    user_id = callback_query.from_user.id
    logger.info(f"Пользователь {user_id} выбрал {days} день(дней) для прогноза.")
    await callback_query.message.answer(
        escaped_prompt,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    user_data = await state.get_data()
    start_city = user_data['start']
    end_city = user_data['end']
    stops = user_data.get('stops', [])
    days = user_data['days']

    route_points = [start_city] + stops + [end_city]
    logger.debug(f"Маршрут пользователя {user_id}: {route_points}")

    forecasts = []
    for city in route_points:
        loc_data = get_location_data(city)
        if not loc_data:
            error_message = f"Не удалось найти город: {escape_markdown_v2(city)}. Попробуйте снова."
            escaped_error = escape_markdown_v2(error_message)
            logger.error(f"Не удалось найти город '{city}' для пользователя {user_id}")
            await callback_query.message.answer(
                escaped_error,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            await state.finish()
            return
        forecast = get_weather_forecast(loc_data['key'], days)
        forecasts.append({
            'city': city,
            'forecast': forecast,
            'lat': loc_data['lat'],
            'lon': loc_data['lon']
        })

    # Генерация графиков
    chart_paths = []
    for point in forecasts:
        chart_path = await generate_weather_chart(point['city'], point['forecast'])
        if chart_path:
            chart_paths.append(chart_path)
        else:
            logger.warning(f"Не удалось сгенерировать график для города {point['city']}")

    # Генерация ссылки на карту маршрута
    map_link = generate_route_map_link(forecasts)
    logger.debug(f"Сгенерирована ссылка на карту маршрута: {map_link}")

    # Отправка прогнозов и графиков
    for idx, point in enumerate(forecasts):
        message_text = f"*{escape_markdown_v2(point['city'])}*\n"
        if point['forecast']:
            for day in point['forecast']:
                date = escape_markdown_v2(day['date'])
                weather_text_day = escape_markdown_v2(day['weather_text_day'])
                weather_text_night = escape_markdown_v2(day['weather_text_night'])
                message_text += (
                    f"📅 *Дата:* {date}\n"
                    f"🌡️ *Мин. Температура:* {day['min_temp']}°C\n"
                    f"🌡️ *Макс. Температура:* {day['max_temp']}°C\n"
                    f"💨 *Скорость ветра:* {day['wind_speed']} км/ч\n"
                    f"🌧️ *Вероятность осадков:* {day['precip_prob']}%\n"
                    f"☀️ *Днём:* {weather_text_day}\n"
                    f"🌙 *Ночью:* {weather_text_night}\n\n"
                )
        else:
            message_text += "❌ Нет данных для прогноза.\n\n"

        escaped_message_text = escape_markdown_v2(message_text)
        if idx < len(chart_paths):
            try:
                with open(chart_paths[idx], 'rb') as chart:
                    logger.info(f"Отправляем фото: {chart_paths[idx]} пользователю {user_id}")
                    await callback_query.bot.send_photo(
                        chat_id=user_id,
                        photo=chart,
                        caption=escaped_message_text,
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
            except Exception as e:
                logger.error(f"Ошибка при отправке фото: {e}")
                await callback_query.message.answer(
                    escaped_message_text,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
        else:
            logger.info(f"Отправляем текстовое сообщение пользователю {user_id}")
            await callback_query.message.answer(
                escaped_message_text,
                parse_mode=ParseMode.MARKDOWN_V2
            )

    # Отправка ссылки на карту маршрута
    if map_link:
        # Экранируем только текст ссылки, не URL
        escaped_link_text = escape_markdown_v2("Открыть карту")
        # Не экранируем URL
        route_map_message = f"🗺️ *Маршрут на карте:* [{escaped_link_text}]({map_link})"
        logger.info(f"Отправляем ссылку на карту маршрута пользователю {user_id}")
        await callback_query.message.answer(
            route_map_message,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=False
        )

    # Отправка всех графиков
    for chart_path in chart_paths:
        try:
            with open(chart_path, 'rb') as chart:
                chart_caption = escape_markdown_v2("📊 График прогноза погоды")
                logger.info(f"Отправляем фото: {chart_path} пользователю {user_id}")
                await callback_query.bot.send_photo(
                    chat_id=user_id,
                    photo=chart,
                    caption=chart_caption,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
        except Exception as e:
            logger.error(f"Ошибка при отправке фото: {e}")

    final_message = "✅ Прогноз погоды получен."
    escaped_final_message = escape_markdown_v2(final_message)
    logger.info(f"Отправляем финальное сообщение пользователю {user_id}")
    await callback_query.message.answer(
        escaped_final_message,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await state.finish()

async def weather_cancel(message: types.Message, state: FSMContext):

    canceled_message = "Отменено."
    escaped_canceled_message = escape_markdown_v2(canceled_message)
    logger.info(f"Пользователь {message.from_user.id} отменил процесс.")
    await message.reply(
        escaped_canceled_message,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=ReplyKeyboardRemove()
    )
    await state.finish()

def get_location_from_coords(lat, lon):

    logger = logging.getLogger(__name__)
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'language': 'ru'
        }
        headers = {
            'User-Agent': 'WeatherBot/1.0'
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            city = address.get('city') or address.get('town') or address.get('village')
            if city:
                logger.debug(f"Обратное геокодирование: найдена город {city} по координатам ({lat}, {lon})")
                return {'city': city, 'lat': lat, 'lon': lon}
        logger.warning(f"Не удалось выполнить обратное геокодирование для координат ({lat}, {lon})")
        return None
    except Exception as e:
        logger.error(f"Ошибка при обратном геокодировании: {e}")
        return None

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(weather_start, commands="weather", state="*")
    dp.register_message_handler(weather_start_location, state=WeatherForm.start, content_types=types.ContentTypes.TEXT | types.ContentTypes.LOCATION)
    dp.register_message_handler(weather_end_location, state=WeatherForm.end, content_types=types.ContentTypes.TEXT | types.ContentTypes.LOCATION)
    dp.register_callback_query_handler(weather_confirm_add_more_stops, state=WeatherForm.confirm_add_more_stops, text=['yes', 'no'])
    dp.register_message_handler(weather_add_stops, state=WeatherForm.stops, content_types=types.ContentTypes.TEXT | types.ContentTypes.LOCATION)
    dp.register_callback_query_handler(weather_days_selection, state=WeatherForm.days, text=['1', '3', '5'])
    dp.register_message_handler(weather_cancel, commands="cancel", state="*")
