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


@dp.message(Command("usd"))
async def cmd_usd(message: types.Message):
    price_old = select_last_telegram('Dollars')
    await message.answer(f'{price_old}')
    logger.info(f"Отправлен курс доллара: {price_old}")


@dp.message(Command("eur"))
async def cmd_eur(message: types.Message):
    price_old = select_last_telegram('Euros')
    await message.answer(f'{price_old}')
    logger.info(f"Отправлен курс евро: {price_old}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
