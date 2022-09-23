from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


b1 = KeyboardButton('Да')
b2 = KeyboardButton('Нет')

yes_no = ReplyKeyboardMarkup()
yes_no.add(b1).add(b2)
