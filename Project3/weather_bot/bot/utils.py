# weather_bot/bot/utils.py

import re
import html
import logging

logger = logging.getLogger(__name__)


def escape_markdown_v2(text: str) -> str:

    escape_chars = r"_*[]()~`>#+-=|{}.!\\"
    try:
        return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)
    except Exception as e:
        logger.error(f"Ошибка при экранировании MarkdownV2: {e}")
        return text


def escape_html(text: str) -> str:

    try:
        return html.escape(text)
    except Exception as e:
        logger.error(f"Ошибка при экранировании HTML: {e}")
        return text


def generate_route_map_link(route_points):

    try:
        base_url = "https://www.google.com/maps/dir/"
        coordinates = []
        for point in route_points:
            lat = point.get('lat')
            lon = point.get('lon')
            if lat is not None and lon is not None:
                coordinates.append(f"{lat},{lon}")
            else:
                logger.warning(f"Точка маршрута пропущена из-за отсутствия координат: {point}")
        if coordinates:
            route_str = "/".join(coordinates)
            map_link = f"{base_url}{route_str}/"
            logger.debug(f"Сгенерирована ссылка на маршрут: {map_link}")
            return map_link
        else:
            logger.warning("Не удалось сгенерировать ссылку на маршрут: отсутствуют координаты.")
            return None
    except Exception as e:
        logger.error(f"Ошибка при генерации ссылки на карту: {e}")
        return None
