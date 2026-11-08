# finalproject_Remizov_M26-555

# ValutaTrade Hub

Платформа для управления виртуальным портфелем фиатных и криптовалют.

Платформа позволяет регистрировать пользователей, просматривать портфель, покупать и продавать виртуальные валюты, получать актуальные курсы и обновлять локальный кэш через внешние API.

## Структура каталогов

```text
valutatrade_hub/
├── cli/
│   └── interface.py # Интерфейс командной строки
├── core/
│   ├── models.py # Модели пользователя, кошелька и портфеля валют
│   ├── currencies.py # Классы валют
│   ├── usecases.py # Бизнес-логика
│   ├── exceptions.py # Исключения 
│   └── utils.py # Вспомогательные функции
├── infra/
│   └── settings.py  # Настройки
├── parser_service/
│   ├── api_clients.py # API-клиенты
│   ├── config.py # Конфигурация парсера
│   ├── updater.py # основной модуль обновления курсов
│   └── storage.py # операции чтения/записи в JSON
├── logging_config.py # Настройка логирования
└── decorators.py # Декораторы

data/
├── users.json # Данные пользователей
├── portfolios.json # Портфели пользователей 
├── rates.json # локальный кэш
└── exchange_rates.json # хранилище парсера

config.json
pyproject.toml
README.md
```

## Установка

Требуется Python 3.12 и uv.

Клонируйте репозиторий и войдите в каталог проекта.

Установите зависимость:
uv sync

## Запуск

uv run python -m valutatrade_hub.cli.interface

После запуска откроется интерфейс командной строки (CLI) со списком команд.

## Команды CLI

### Регистрация

register --username testuser --password 1234

### Авторизация

login --username testuser --password 1234

### Просмотр портфеля

show-portfolio --base USD

Валютные кошельки, их балансы и общая стоимость портфеля отображаются в выбранной базовой валюте.

### Покупка валюты

buy --currency BTC --amount 0.01

Указывается код валюты и необходимое количество.

### Продажа валюты

sell --currency BTC --amount 0.005

Указывается код валюты и необходимое количество.

### Получение курса

get-rate --from BTC --to USD

### Просмотр сохранённых курсов

show-rates
show-rates --currency BTC
show-rates --top 2

Показывает курсы из локального кэша с возможностью фильтрации.

### Обновление курсов

update-rates

Запрос курсов у внешних API.

## Кэширование и TTL

Курсы хранятся в файле `data/rates.json`.

Для каждой валютной пары сохраняются курс, источник и время обновления (`updated_at`), а также фиксируется время последнего обновления (`last_refresh`).

Период актуальности курса определяется параметром `RATES_TTL_SECONDS` в `config.json`.

История полученных курсов хранится в `data/exchange_rates.json`.

## Parser Service

Parser Service получает курсы из двух внешних источников:

- CoinGecko — курсы криптовалют.
- ExchangeRate-API — курсы фиатных валют.

Настройки находятся в `valutatrade_hub/parser_service/config.py`.

Для ExchangeRate-API необходим API-ключ, который передаётся через переменную окружения `EXCHANGERATE_API_KEY`.

Пример настройки в Git Bash:

export EXCHANGERATE_API_KEY="YOUR_API_KEY"

## Демонстрация полного цикла, включая обработку ошибок
https://asciinema.org/a/7xWRllW6lZQCEcHU