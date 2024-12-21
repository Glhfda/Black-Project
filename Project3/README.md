```markdown
# Telegram Weather Bot

![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Содержание

- [Описание](#описание)
- [Особенности](#особенности)
- [Требования](#требования)
- [Установка](#установка)
- [Настройка](#настройка)
- [Использование](#использование)
- [Структура Проекта](#структура-проекта)
- [Логирование](#логирование)
- [Вклад](#вклад)
- [Лицензия](#лицензия)

## Описание

**Telegram Weather Bot** — это бот для Telegram, который предоставляет прогнозы погоды по заданному маршруту. Пользователи могут:

- Получать текущую погоду и прогноз на несколько дней для начальной и конечной точек маршрута.
- Добавлять промежуточные остановки.
- Просматривать прогнозы на карте и графиках.

## Особенности

- **Интерактивный интерфейс:** Удобное взаимодействие через команды и кнопки.
- **Геолокация:** Возможность отправки геолокации для автоматического определения местоположения.
- **Многодневный прогноз:** Получение прогноза погоды на 1, 3 или 5 дней.
- **Графики:** Визуализация данных прогноза погоды с помощью графиков.
- **Маршрут на карте:** Генерация ссылок на Google Maps для просмотра маршрута.

## Требования

- Python 3.8 или выше
- Аккаунт Telegram
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))
- Аккаунт AccuWeather API и API Key

## Установка

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/ваш_репозиторий/telegram-weather-bot.git
   cd telegram-weather-bot
   ```

2. **Создайте и активируйте виртуальное окружение (рекомендуется):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Для Unix/Linux
   # или
   venv\Scripts\activate  # Для Windows
   ```

3. **Установите зависимости:**

   ```bash
   pip install -r requirements.txt
   ```

## Настройка

1. **Создайте файл `.env` в корне проекта и добавьте в него ваши ключи:**

   ```env
   TELEGRAM_TOKEN=ваш_телеграм_токен
   API_KEY=ваш_accuweather_api_key
   ```

   **Важно:** Убедитесь, что файл `.env` добавлен в `.gitignore`, чтобы избежать утечки ключей.

2. **Проверьте корректность `.gitignore`:**

   ```gitignore
   # .gitignore

   .env
   *.pyc
   __pycache__/
   charts/generated_charts/
   ```

## Использование

1. **Запустите бота:**

   ```bash
   python main.py
   ```

2. **В Telegram:**

   - Найдите вашего бота и отправьте команду `/start` для приветствия.
   - Используйте команду `/help` для получения списка доступных команд и инструкций.
   - Отправьте команду `/weather` и следуйте инструкциям:
     1. Введите начальную точку маршрута (например, "Москва" или отправьте геолокацию).
     2. Введите конечную точку маршрута или отправьте геолокацию.
     3. При необходимости добавьте промежуточные точки.
     4. Выберите количество дней для прогноза (1, 3 или 5).
   - Получите прогнозы погоды, графики и ссылку на карту маршрута.

## Структура Проекта

```
weather_bot/
├── bot/
│   ├── __init__.py
│   ├── commands.py
│   ├── handlers.py
│   ├── keyboards.py
│   └── utils.py
├── charts/
│   ├── __init__.py
│   └── chart_generator.py
├── weather/
│   ├── __init__.py
│   ├── api.py
│   └── models.py
├── main.py
├── .env
├── .gitignore
└── requirements.txt
```

- **bot/**: Содержит основные модули бота, включая команды, обработчики, клавиатуры и утилиты.
- **charts/**: Модули для генерации графиков прогнозов погоды.
- **weather/**: Модули для взаимодействия с AccuWeather API и обработки данных.
- **main.py**: Точка входа в приложение, инициализация бота и запуск поллинга.
- **.env**: Файл для хранения секретных ключей и токенов.
- **.gitignore**: Файл для исключения чувствительных данных и временных файлов из репозитория.
- **requirements.txt**: Список зависимостей проекта.

## Логирование

Бот использует модуль `logging` для записи логов. Логи включают информацию об отправленных сообщениях, ошибках API и других событиях.

- **Уровни логирования:**
  - `INFO`: Основные события, такие как отправка сообщений.
  - `WARNING`: Предупреждения, например, если город не найден.
  - `ERROR`: Ошибки, такие как проблемы с API запросами.

**Пример лога:**

```
2024-12-21 16:36:04,121 - root - ERROR - Ошибка при получении прогноза погоды: 401 Client Error: Unauthorized for url: https://dataservice.accuweather.com/forecasts/v1/daily/3day/294021?apikey=ВАШ_API_KEY&metric=true&language=ru-RU&details=true
```

## Вклад

Будем рады вашему участию! Пожалуйста, следуйте этим шагам для внесения изменений:

1. **Форкните репозиторий.**
2. **Создайте новую ветку для вашей функции:**

   ```bash
   git checkout -b feature/НазваниеФункции
   ```

3. **Внесите изменения и закоммитьте их:**

   ```bash
   git commit -m "Добавил новую функцию ..."
   ```