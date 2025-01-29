import os

# Database configuration
DB_PARAMS = {
    'dbname': 'postgres',
    'host': os.getenv('DB_HOST', 'host.docker.internal'),
    'port': '5432',
    'user': 'root',
    'password': '12345'
}

# Telegram bot token
TELEGRAM_TOKEN = "6594195662:AAF0Ssws8t0EzSvnjOpEHymHr4P0L6kgRr8"
