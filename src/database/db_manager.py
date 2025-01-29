from datetime import datetime

import psycopg2
from psycopg2 import OperationalError

from config import DB_PARAMS
from src.logging_config import setup_logging

# Настройка логирования
logger = setup_logging(log_file='sql_postgress.log', logger_name='sql_postgress')

def create_connection():
    try:
        connection = psycopg2.connect(**DB_PARAMS)
        logger.info("Подключение к базе данных установлено")
        return connection
    except OperationalError as e:
        logger.error(f"Ошибка соединения с БД: {e}")
        raise

connection = create_connection()

def add_database():
    with connection.cursor() as cursor:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Dollars (
            id SERIAL PRIMARY KEY,
            Дата TEXT NOT NULL,
            Время TEXT NOT NULL,
            Цена_доллара FLOAT,
            Комментарий TEXT,
            Разница TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Euros (
            id SERIAL PRIMARY KEY,
            Дата TEXT NOT NULL,
            Время TEXT NOT NULL,
            Цена_евро FLOAT,
            Комментарий TEXT,
            Разница TEXT
        )
        ''')
        connection.commit()
        logger.info("Таблицы Dollars и Euros созданы или уже существуют")

def add_column(name_table, name_column, data_type):
    with connection.cursor() as cursor:
        cursor.execute(f'''
            ALTER TABLE {name_table}
            ADD {name_column} {data_type};
        ''')
        connection.commit()
        logger.info(f"Столбец {name_column} добавлен в таблицу {name_table}")

def insert_into_currency(table_name, price, difference):
    with connection.cursor() as cursor:
        date = datetime.now().date()
        time_now = datetime.now().time().strftime('%H:%M:%S')
        if table_name == 'Dollars':
            cursor.execute('''
                INSERT INTO Dollars (Дата, Время, Цена_доллара, Разница)
                VALUES (%s, %s, %s, %s);
            ''', (date, time_now, price, difference))
        elif table_name == 'Euros':
            cursor.execute('''
                INSERT INTO Euros (Дата, Время, Цена_евро, Разница)
                VALUES (%s, %s, %s, %s);
            ''', (date, time_now, price, difference))
        connection.commit()
        logger.info(
            f"Запись добавлена в таблицу {table_name}: Дата={date}, Время={time_now}, Цена={price}, Разница={difference}")

def select_last_telegram(table_name):
    with connection.cursor() as cursor:
        if table_name == 'Dollars':
            cursor.execute('''
                SELECT Дата, Время, Цена_доллара FROM Dollars
                ORDER BY id DESC LIMIT 1;
            ''')
        elif table_name == 'Euros':
            cursor.execute('''
                SELECT Дата, Время, Цена_евро FROM Euros
                ORDER BY id DESC LIMIT 1;
            ''')
        result = cursor.fetchone()
        if result:
            return f'💵 Курс: {result[2]}\n⏰ Время: {result[1]}\n📅 Дата: {result[0]}'
        else:
            logger.warning(f"Нет записей в таблице {table_name}")
            return None

def select_last_float(table_name):
    with connection.cursor() as cursor:
        if table_name == 'Dollars':
            cursor.execute('''
                SELECT Цена_доллара FROM Dollars
                ORDER BY id DESC LIMIT 1;
            ''')
        elif table_name == 'Euros':
            cursor.execute('''
                SELECT Цена_евро FROM Euros
                ORDER BY id DESC LIMIT 1;
            ''')
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            logger.warning(f"Нет записей в таблице {table_name}")
            return None
