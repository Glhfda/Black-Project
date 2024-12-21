# weather_bot/weather/api.py

import requests
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise ValueError("Не найден API_KEY в переменных окружения.")

logger = logging.getLogger(__name__)

def get_location_data(city_name, api_key=API_KEY):

    url = 'https://dataservice.accuweather.com/locations/v1/cities/search'
    params = {
        'apikey': api_key,
        'q': city_name,
        'language': 'ru-RU'
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and 'GeoPosition' in data[0]:
            location = data[0]
            location_key = location['Key']
            lat = location['GeoPosition']['Latitude']
            lon = location['GeoPosition']['Longitude']
            city = location['LocalizedName']
            logger.debug(f"Найдено местоположение: {city} (Key: {location_key})")
            return {'key': location_key, 'lat': lat, 'lon': lon, 'city': city}
        else:
            logger.warning(f"Город '{city_name}' не найден или нет координат.")
            return None
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP ошибка при получении данных о локации: {http_err}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении данных о локации: {e}")
        return None

def get_weather_forecast(location_key, days=1, api_key=API_KEY):

    try:
        if days == 1:
            # Получение текущей погоды
            url = f'https://dataservice.accuweather.com/currentconditions/v1/{location_key}'
            params = {
                'apikey': api_key,
                'details': 'true',
                'language': 'ru-RU'
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data:
                temperature = data[0]['Temperature']['Metric']['Value']
                wind_speed = data[0]['Wind']['Speed']['Metric']['Value']
                precip_prob = data[0].get('PrecipitationProbability', 0)
                weather_status = check_bad_weather(temperature, wind_speed, precip_prob)
                forecast = [{
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'min_temp': temperature,  # Для текущего дня мин и макс одинаковы
                    'max_temp': temperature,
                    'wind_speed': wind_speed,
                    'precip_prob': precip_prob,
                    'weather_text_day': weather_status,
                    'weather_text_night': weather_status
                }]
                logger.debug(f"Получен текущий прогноз для Key {location_key}: {forecast}")
                return forecast
        else:
            # Получение многодневного прогноза
            url = f'https://dataservice.accuweather.com/forecasts/v1/daily/{days}day/{location_key}'
            params = {
                'apikey': api_key,
                'metric': 'true',
                'language': 'ru-RU',
                'details': 'true'
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            forecasts = []
            for day in data.get('DailyForecasts', []):
                date_raw = day.get('Date', '')
                try:
                    date_obj = datetime.fromisoformat(date_raw.rstrip('Z'))
                    date_str = date_obj.strftime('%Y-%m-%d')
                except Exception:
                    date_str = date_raw
                min_temp = day['Temperature']['Minimum']['Value']
                max_temp = day['Temperature']['Maximum']['Value']
                wind_speed = day['Day']['Wind']['Speed']['Value']
                precip_prob = day['Day']['PrecipitationProbability']
                weather_text_day = day['Day']['IconPhrase']
                weather_text_night = day['Night']['IconPhrase']
                forecasts.append({
                    'date': date_str,
                    'min_temp': min_temp,
                    'max_temp': max_temp,
                    'wind_speed': wind_speed,
                    'precip_prob': precip_prob,
                    'weather_text_day': weather_text_day,
                    'weather_text_night': weather_text_night
                })
            logger.debug(f"Получен {days}-дневный прогноз для Key {location_key}: {forecasts}")
            return forecasts
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP ошибка при получении прогноза погоды: {http_err}")
        return []
    except Exception as e:
        logger.error(f"Ошибка при получении прогноза погоды: {e}")
        return []

def check_bad_weather(temperature, wind, precip_prob):

    try:
        if temperature > 35:
            if wind > 20:
                if precip_prob > 70:
                    return ('Очень жаркая погода с сильным ветром и высокой вероятностью осадков. '
                            'Избегайте длительного пребывания на улице.')
                else:
                    return ('Очень жаркая погода с сильным ветром. '
                            'Запаситесь водой и избегайте прямых солнечных лучей.')
            elif precip_prob > 70:
                return ('Очень жаркая погода с высокой вероятностью осадков. '
                        'Избегайте длительного пребывания на улице.')
            else:
                return ('Очень жаркая и сухая погода. '
                        'Пейте много воды и избегайте физической нагрузки в полдень.')
        elif temperature > 25:
            if wind > 20:
                if precip_prob > 70:
                    return ('Тёплая погода с сильным ветром и осадками. '
                            'Возьмите зонтик и ветровку.')
                else:
                    return ('Тёплая погода с сильным ветром. '
                            'Возьмите ветровку.')
            elif precip_prob > 70:
                return ('Тёплая погода с осадками. '
                        'Возьмите зонтик.')
            else:
                return ('Тёплая погода без сильного ветра и высокой вероятности осадков. '
                        'Подходит для прогулок.')
        elif temperature > 15:
            if wind > 20:
                if precip_prob > 70:
                    return ('Прохладно, ветрено и осадки. '
                            'Возьмите защиту от дождя.')
                else:
                    return ('Прохладно и ветрено. '
                            'Учтите ветер при планировании.')
            elif precip_prob > 70:
                return ('Прохладно и есть осадки. '
                        'Возьмите зонтик.')
            else:
                return ('Прохладная и спокойная погода. '
                        'Подходит для прогулок.')
        elif temperature > 0:
            if wind > 20:
                if precip_prob > 70:
                    return ('Холодно, ветрено и осадки. '
                            'Нужна тёплая одежда и зонтик.')
                else:
                    return ('Холодно и небольшой ветер. '
                            'Нужна тёплая одежда.')
            elif precip_prob > 70:
                return ('Холодно и осадки. '
                        'Тёплая одежда и зонтик обязательны.')
            else:
                return ('Холодно и сухо. '
                        'Нужна тёплая одежда.')
        else:
            if wind > 20:
                if precip_prob > 70:
                    return ('Морозно, сильный ветер и осадки. '
                            'Очень тёплая одежда необходима.')
                else:
                    return ('Морозно и ветрено. '
                            'Очень тёплая одежда необходима.')
            elif precip_prob > 70:
                return ('Морозно и осадки. '
                        'Тёплая одежда обязательна.')
            else:
                return ('Морозно и сухо. '
                        'Тёплая одежда обязательна.')
    except Exception as e:
        logger.error(f"Ошибка check_bad_weather: {e}")
        return "Не удалось оценить погодные условия."
