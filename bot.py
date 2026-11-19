import os
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class OfferForm(StatesGroup):
    gift_link = State()
    recipient = State()
    currency = State()
    price = State()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🎁 NFT Offer Bot\n\n"
        "/buy — создать предложение\n"
        "/cancel — отменить\n"
        "/help — помощь"
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Создание предложения:\n"
        "1. /buy\n"
        "2. Ссылка на подарок\n"
        "3. Telegram ID получателя\n"
        "4. Валюта\n"
        "5. Цена\n"
        "6. Предпросмотр"
    )


@dp.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Создание предложения отменено.")


@dp.message(Command("buy"))
async def buy(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(OfferForm.gift_link)
    await message.answer("Пришли ссылку на Telegram-подарок:")


@dp.message(OfferForm.gift_link)
async def get_gift(message: Message, state: FSMContext):
    link = (message.text or "").strip()

    if not link.startswith("https://t.me/"):
        await message.answer(
            "Нужна ссылка Telegram, начинающаяся с https://t.me/"
        )
        return

    await state.update_data(gift_link=link)
    await state.set_state(OfferForm.recipient)

    await message.answer(
        "Теперь введи Telegram ID получателя подарка "
        "(только цифры)."
    )


@dp.message(OfferForm.recipient)
async def get_recipient(message: Message, state: FSMContext):
    recipient = (message.text or "").strip()

    if not recipient.isdigit():
        await message.answer("ID должен состоять только из цифр. Попробуй ещё.")
        return

    await state.update_data(recipient=recipient)
    await state.set_state(OfferForm.currency)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="TON", callback_data="cur:TON"),
                InlineKeyboardButton(text="₽ RUB", callback_data="cur:RUB"),
                InlineKeyboardButton(text="⭐ Stars", callback_data="cur:STARS"),
            ]
        ]
    )

    await message.answer("Выбери валюту предложения:", reply_markup=keyboard)


@dp.callback_query(F.data.startswith("cur:"))
async def get_currency(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.split(":")[1]
    await state.update_data(currency=currency)
    await state.set_state(OfferForm.price)

    await callback.answer()
    await callback.message.answer(
        f"Введи сумму предложения в {currency} (числом):"
    )


@dp.message(OfferForm.price)
async def get_price(message: Message, state: FSMContext):
    raw = (message.text or "").strip().replace(",", ".")

    try:
        price = float(raw)
        if not (0 < price <= 1_000_000_000):
            raise ValueError
    except ValueError:
        await message.answer("Введи корректную сумму больше 0.")
        return

    data = await state.get_data()
    currency = data["currency"]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить (демо)",
                    callback_data="demo_accept"
                ),
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="demo_decline"
                ),
            ]
        ]
    )

    await message.answer(
        "🎁 ПРЕДПРОСМОТР ОФЕРА\n\n"
        f"Подарок: {data['gift_link']}\n"
        f"Получатель ID: {data['recipient']}\n"
        f"Цена: {price:g} {currency}\n\n"
        "Это демонстрационный офер. Оплата и передача подарка не выполняются.",
        reply_markup=keyboard
    )

    await state.clear()


@dp.callback_query(F.data.startswith("demo_"))
async def demo_buttons(callback: CallbackQuery):
    if callback.data == "demo_accept":
        await callback.answer("Демо: принято")
        await callback.message.answer(
            "Демонстрация: офер отмечен как принятый. "
            "Никакая сделка не совершена."
        )
    else:
        await callback.answer("Демо: отменено")
        await callback.message.answer("Демонстрационный офер отменён.")

    await callback.message.edit_reply_markup(reply_markup=None)


async def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не установлен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
