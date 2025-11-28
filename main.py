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

def generate_password(length=12, char_type='letters_digits'):
    if char_type == 'letters':
        chars = string.ascii_letters
    elif char_type == 'letters_digits':
        chars = string.ascii_letters + string.digits
    elif char_type == 'all':
        chars = string.ascii_letters + string.digits + string.punctuation
    else:
        chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def check_strength(password):
    score = 0
    if len(password) >= 8: score += 1
    if len(password) >= 12: score += 1
    if any(c.islower() for c in password): score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in string.punctuation for c in password): score += 1
    if score <= 3: return "Слабый"
    elif score <= 5: return "Средний"
    else: return "Сильный"

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
        [InlineKeyboardButton(text="Только буквы", callback_data="type_letters")],
        [InlineKeyboardButton(text="Буквы + цифры", callback_data="type_letters_digits")],
        [InlineKeyboardButton(text="Буквы + цифры + символы", callback_data="type_all")]
    ])
    await callback.message.edit_text("Выбери тип символов:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("type_"))
async def type_callback(callback: CallbackQuery):
    char_type = callback.data.split("_")[1]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="8 символов", callback_data=f"length_8_type_{char_type}")],
        [InlineKeyboardButton(text="12 символов", callback_data=f"length_12_type_{char_type}")],
        [InlineKeyboardButton(text="16 символов", callback_data=f"length_16_type_{char_type}")],
        [InlineKeyboardButton(text="20 символов", callback_data=f"length_20_type_{char_type}")]
    ])
    await callback.message.edit_text("Выбери длину пароля:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("length_") and "type_" in c.data)
async def length_callback(callback: CallbackQuery):
    parts = callback.data.split("_")
    length = int(parts[1])
    char_type = parts[3]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 пароль", callback_data=f"count_1_length_{length}_type_{char_type}")],
        [InlineKeyboardButton(text="3 пароля", callback_data=f"count_3_length_{length}_type_{char_type}")],
        [InlineKeyboardButton(text="5 паролей", callback_data=f"count_5_length_{length}_type_{char_type}")]
    ])
    await callback.message.edit_text("Выбери количество паролей:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("count_"))
async def count_callback(callback: CallbackQuery):
    parts = callback.data.split("_")
    count = int(parts[1])
    length = int(parts[3])
    char_type = parts[5]
    passwords = [generate_password(length, char_type) for _ in range(count)]
    text = ""
    for i, pwd in enumerate(passwords, 1):
        strength = check_strength(pwd)
        text += f"{i}. `{pwd}` - {strength}\n"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Еще раз", callback_data="regenerate")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "regenerate")
async def regenerate_callback(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Только буквы", callback_data="type_letters")],
        [InlineKeyboardButton(text="Буквы + цифры", callback_data="type_letters_digits")],
        [InlineKeyboardButton(text="Буквы + цифры + символы", callback_data="type_all")]
    ])
    await callback.message.edit_text("Выбери тип символов:", reply_markup=keyboard)
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