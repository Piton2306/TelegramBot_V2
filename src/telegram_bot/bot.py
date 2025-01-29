import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from config import TELEGRAM_TOKEN
from src.database.db_manager import select_last_telegram
from src.logging_config import setup_logging

# Настройка логирования
logger = setup_logging(log_file='telegram.log', logger_name='telegram')

# Объект бота
bot = Bot(token=TELEGRAM_TOKEN)

# Диспетчер
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать! Используйте команды /usd, /eur и /rates для получения курсов валют.")
    logger.info("Отправлено приветственное сообщение")


@dp.message(Command("usd"))
async def cmd_usd(message: types.Message):
    price_old = select_last_telegram('Dollars')
    if price_old:
        await message.answer(f'Курс доллара:\n{price_old}')
        logger.info(f"Отправлен курс доллара:\n{price_old}")
    else:
        await message.answer("Информация о курсе доллара отсутствует.")
        logger.warning("Информация о курсе доллара отсутствует.")


@dp.message(Command("eur"))
async def cmd_eur(message: types.Message):
    price_old = select_last_telegram('Euros')
    if price_old:
        await message.answer(f'Курс евро:\n{price_old}')
        logger.info(f"Отправлен курс евро:\n{price_old}")
    else:
        await message.answer("Информация о курсе евро отсутствует.")
        logger.warning("Информация о курсе евро отсутствует.")


@dp.message(Command("rates"))
async def cmd_rates(message: types.Message):
    price_usd = select_last_telegram('Dollars')
    price_eur = select_last_telegram('Euros')
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
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
