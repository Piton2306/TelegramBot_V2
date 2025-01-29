import os
import time
from datetime import datetime

import requests

from src.database.db_manager import add_database, insert_into_currency, select_last_float
from src.logging_config import setup_logging

# Настройка логирования
logger = setup_logging(log_file='parsing_rub_dollar.log', logger_name='parsing_rub_dollar')

# Константы
FILE_PATH_DOLLAR = 'file/dollar_exchange_rate.txt'
FILE_PATH_EURO = 'file/euro_exchange_rate.txt'

if not os.path.exists('file'):
    os.makedirs('file')


def save_file(file_path, text="Пример текста"):
    date = datetime.now().date()
    time_now = datetime.now().time().strftime('%H:%M:%S')
    with open(file_path, 'a+') as file:
        file.write(f'{date} {time_now} - {text} RUB\n')


def get_currency_rate_from_api(currency):
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    rate = data['Valute'][currency]['Value']
    return round(rate, 2)


def process_currency(currency, file_path, table_name):
    old_price = select_last_float(table_name)
    if old_price is None:
        logger.warning(f"Нет записей в таблице {table_name}. Используется начальное значение 0.")
        old_price = 0

    new_price = get_currency_rate_from_api(currency)
    logger.info(f"Последний курс {currency}: {old_price}")
    logger.info(f"Текущий курс {currency}: {new_price}")

    if old_price < new_price:
        save_file(file_path, str(new_price))
        insert_into_currency(table_name, new_price, difference="↑")
        logger.info(f"Цена {currency} выросла: {new_price} на {round(new_price - old_price, 2)}")
    elif old_price > new_price:
        save_file(file_path, str(new_price))
        insert_into_currency(table_name, new_price, difference="↓")
        logger.info(f"Цена {currency} упала: {new_price} на {round(old_price - new_price, 2)}")
    else:
        logger.info(f"Цена {currency} не изменилась: {new_price}")


def main():
    add_database()
    logger.info("Начало цикла парсинга курсов валют")
    while True:
        try:
            process_currency('USD', FILE_PATH_DOLLAR, 'Dollars')
            process_currency('EUR', FILE_PATH_EURO, 'Euros')
        except Exception as e:
            logger.error(f"Ошибка: {e}")
        time.sleep(60)


if __name__ == "__main__":
    main()
