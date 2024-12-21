# weather_bot/weather/models.py

from dataclasses import dataclass
from typing import List

@dataclass
class DailyForecast:
    date: str
    min_temp: float
    max_temp: float
    wind_speed: float
    precip_prob: int
    weather_text_day: str
    weather_text_night: str

@dataclass
class LocationForecast:
    city: str
    forecast: List[DailyForecast]
    lat: float
    lon: float
