import asyncio
import os
import secrets
import string
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable must be set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def generate_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

@dp.message(Command("start"))
async def start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сгенерировать пароль", callback_data="generate")],
        [InlineKeyboardButton(text="Помощь", callback_data="help")]
    ])
    await message.reply("Привет! Я бот для генерации паролей. Выбери действие:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "generate")
async def generate_callback(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="8 символов", callback_data="length_8")],
        [InlineKeyboardButton(text="12 символов", callback_data="length_12")],
        [InlineKeyboardButton(text="16 символов", callback_data="length_16")],
        [InlineKeyboardButton(text="20 символов", callback_data="length_20")]
    ])
    await callback.message.edit_text("Выбери длину пароля:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("length_"))
async def length_callback(callback: CallbackQuery):
    length = int(callback.data.split("_")[1])
    password = generate_password(length)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Еще один пароль", callback_data=f"regenerate_length_{length}")]
    ])
    await callback.message.edit_text(f"Ваш пароль: `{password}`", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("regenerate_length_"))
async def regenerate_callback(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="8 символов", callback_data="length_8")],
        [InlineKeyboardButton(text="12 символов", callback_data="length_12")],
        [InlineKeyboardButton(text="16 символов", callback_data="length_16")],
        [InlineKeyboardButton(text="20 символов", callback_data="length_20")]
    ])
    await callback.message.edit_text("Выбери длину пароля:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "help")
async def help_callback(callback: CallbackQuery):
    text = "Я генерирую безопасные пароли.\n\nКоманды:\n/start - меню\n\nИли просто нажми 'Сгенерировать пароль'."
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back")
async def back_callback(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сгенерировать пароль", callback_data="generate")],
        [InlineKeyboardButton(text="Помощь", callback_data="help")]
    ])
    await callback.message.edit_text("Привет! Я бот для генерации паролей. Выбери действие:", reply_markup=keyboard)
    await callback.answer()

@dp.message(Command("password"))
async def password_command(message: Message):
    args = message.text.split()
    if len(args) > 1:
        try:
            length = int(args[1])
            if 4 <= length <= 50:
                password = generate_password(length)
                await message.reply(f"Пароль длиной {length}: `{password}`", parse_mode="Markdown")
            else:
                await message.reply("Длина должна быть от 4 до 50.")
        except ValueError:
            await message.reply("Укажи число для длины, например /password 16")
    else:
        password = generate_password()
        await message.reply(f"Пароль: `{password}`", parse_mode="Markdown")

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())