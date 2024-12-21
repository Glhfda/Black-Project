# weather_bot/charts/chart_generator.py

import plotly.graph_objs as go
import os
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

async def generate_weather_chart(city, forecast):

    try:
        dates = [day['date'] for day in forecast]
        min_temps = [day['min_temp'] for day in forecast]
        max_temps = [day['max_temp'] for day in forecast]
        wind_speeds = [day['wind_speed'] for day in forecast]

        fig = go.Figure()

        # Добавление графиков температур на левую ось Y
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=min_temps,
                mode='lines+markers',
                name='Мин. Температура',
                line=dict(color='blue'),
                yaxis='y1'
            )
        )
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=max_temps,
                mode='lines+markers',
                name='Макс. Температура',
                line=dict(color='red'),
                yaxis='y1'
            )
        )

        # Добавление графика скорости ветра на правую ось Y
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=wind_speeds,
                mode='lines+markers',
                name='Скорость ветра',
                line=dict(color='green'),
                yaxis='y2'
            )
        )

        # Настройка макета графика с двумя осями Y
        fig.update_layout(
            title=f'Прогноз погоды для {city}',
            xaxis_title='Дата',
            yaxis=dict(
                title='Температура (°C)',
                titlefont=dict(color='blue'),
                tickfont=dict(color='blue')
            ),
            yaxis2=dict(
                title='Скорость ветра (км/ч)',
                titlefont=dict(color='green'),
                tickfont=dict(color='green'),
                overlaying='y',
                side='right'
            ),
            legend=dict(x=0.01, y=0.99, bordercolor="Black", borderwidth=1),
            template='plotly_white'
        )

        # Создание директории для сохранения графиков, если она не существует
        os.makedirs('charts/generated_charts', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        safe_city = re.sub(r'\s+', '_', city)
        chart_path = f'charts/generated_charts/{safe_city}_{timestamp}.png'
        fig.write_image(chart_path)
        logger.debug(f"График сохранён по пути: {chart_path}")
        return chart_path
    except Exception as e:
        logger.error(f"Ошибка при генерации графика: {e}")
        return None
