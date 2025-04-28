from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton

MAIN_MENU_KB = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🔥Новый Сеанс")],
    [KeyboardButton(text="🔱 Новая Cупер-Cессия")],
    [KeyboardButton(text="🟩 Gologin Apikey")],
    [KeyboardButton(text="☎ Helper-Sms Apikey")],
    [KeyboardButton(text="🔐 Изменить Прокси")],
], resize_keyboard=True)

APPROVE_KB = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="✅Начать сеанс"),
        KeyboardButton(text="⛔️Отмена")
    ]
], resize_keyboard=True)
