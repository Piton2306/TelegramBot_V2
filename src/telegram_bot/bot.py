import asyncio
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession  # Чистая сессия aiogram
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
import aiohttp

# Настройка логирования
from src.logging_config import setup_logging
logger = setup_logging(log_file='telegram.log', logger_name='telegram')

from config import TELEGRAM_TOKEN
from src.database.db_manager import select_last_telegram

# Диспетчер и бот на глобальном уровне
dp = Dispatcher()
bot: Bot = None


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать! Используйте команды /usd, /eur и /rates для получения курсов валют.")
    logger.info("Отправлено приветственное сообщение")


@dp.message(Command("usd"))
async def cmd_usd(message: types.Message):
    loop = asyncio.get_running_loop()
    # run_in_executor гарантирует чтение свежих данных из БД при каждом запросе
    price_old = await loop.run_in_executor(None, select_last_telegram, 'Dollars')
    
    if price_old:
        await message.answer(f'Курс доллара:\n{price_old}')
        logger.info(f"Отправлен курс доллара:\n{price_old}")
    else:
        await message.answer("Информация о курсе доллара отсутствует.")
        logger.warning("Информация о курсе доллара отсутствует.")


@dp.message(Command("eur"))
async def cmd_eur(message: types.Message):
    loop = asyncio.get_running_loop()
    price_old = await loop.run_in_executor(None, select_last_telegram, 'Euros')
    
    if price_old:
        await message.answer(f'Курс евро:\n{price_old}')
        logger.info(f"Отправлен курс евро:\n{price_old}")
    else:
        await message.answer("Информация о курсе евро отсутствует.")
        logger.warning("Информация о курсе евро отсутствует.")


@dp.message(Command("rates"))
async def cmd_rates(message: types.Message):
    loop = asyncio.get_running_loop()
    price_usd = await loop.run_in_executor(None, select_last_telegram, 'Dollars')
    price_eur = await loop.run_in_executor(None, select_last_telegram, 'Euros')
    
    if price_usd and price_eur:
        await message.answer(f'Курс доллара:\n{price_usd}\n\nКурс евро:\n{price_eur}')
        logger.info(f"Отправлены курсы доллара и евро:\n{price_usd}\n{price_eur}")
    elif price_usd:
        await message.answer(f'Курс доллара:\n{price_usd}\n\nИнформация о курсе евро отсутствует.')
        logger.info(f"Отправлен курс доллара:\n{price_usd}")
        logger.warning("Информация о курсе евро отсутствует.")
    elif price_eur:
        await message.answer(f'Информация о курсе доллара отсутствует.\n\nКурс евро:\n{price_eur}')
        logger.info(f"Отправлен курс евро:\n{price_eur}")
        logger.warning("Информация о курсе доллара отсутствует.")
    else:
        await message.answer("Информация о курсах доллара и евро отсутствует.")
        logger.warning("Информация о курсах доллара и евро отсутствует.")


async def main():
    global bot
    
    # Создаем стандартную асинхронную сессию aiogram
    session = AiohttpSession()
    
    # Передаем прокси напрямую в метод создания сессии aiogram.
    # Так как мы используем встроенный в aiohttp прокси-метод, нам больше не нужны 
    # сторонние библиотеки вроде aiohttp-socks, вызывавшие TypeError!
    session.proxy = "http://192.168.1.110:10808" 
    
    # Инициализируем бота с изолированным прокси
    bot = Bot(
        token=TELEGRAM_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    logger.info("Проверяем подключение к Telegram API...")
    try:
        me = await bot.get_me()
        logger.info(f"Успешное подключение! Бот @{me.username} готов к работе.")
    except Exception as e:
        logger.error(f"🛑 Ошибка подключения к Telegram: {e}")
        sys.exit(1)
        
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
