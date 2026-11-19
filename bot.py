
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🎁 NFT Offer Bot\n\n"
        "Команды:\n"
        "/buy — создать предложение\n"
        "/help — помощь"
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Как пользоваться ботом:\n"
        "1. Напиши /buy\n"
        "2. Укажи ссылку на подарок\n"
        "3. Выбери валюту\n"
        "4. Укажи сумму\n"
        "5. Укажи получателя подарка\n\n"
        "Пока бот находится в разработке."
    )


@dp.message(Command("buy"))
async def buy(message: Message):
    await message.answer(
        "Создание NFT-офера скоро будет доступно 🎁"
    )


async def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не установлен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
