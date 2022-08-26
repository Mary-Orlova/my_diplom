import requests
import logging
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from main import dp, bot
import datetime
from information_API.locations import make_locations_list, exact_location
from information_API.hotels import get_hotels
from check.checking import is_user_in_db, add_user, make_message, is_input_correct, get_parameters_information,\
    extract_search_parameters
from bot_redis import redis_db


# задаем уровень логов
logging.basicConfig(level=logging.INFO)

url = "https://hotels4.p.rapidapi.com/get-meta-data"
headers = {
    "X-RapidAPI-Key": "c708d9c8e5msh807481cebff88b9p1a6645jsnff323625d862",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers)


# Хэндлер на команду /hello-world
@dp.message_handler(commands=["hello-world"])
async def hello_world(message: types.Message):
    if not is_user_in_db(message):
        add_user(message)
    logging.info(f'Команда "/hello-world" была вызвана')
    await message.answer('Привет, это бот для поиска отелей!\nНапиши "/help" и познакомлю Вас с моими командами')


# Хэндлер на команду /help
@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    if not is_user_in_db(message):
        add_user(message)
    logging.info(f'Команда "/help" была вызвана')
    await message.answer(
        '\n/lowprice — вывод самых дешёвых отелей в городе'
        '\n/highprice — вывод самых дорогих отелей в городе'
        '\n/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра'
        '\n/history — вывод истории поиска отелей')


@dp.message_handler(commands=["lowprice"])
async def lowprice(message: types.Message):
    await message.answer('')
    if not is_user_in_db(message):
        add_user(message)
    chat_id = message.chat.id
    redis_db.hset(chat_id, 'state', 1)
    redis_db.hset(chat_id, 'order', 'PRICE')
    logging.info('Команда "/lowprice" была вызвана.')
    logging.info(redis_db.hget(chat_id, 'order'))
    state = redis_db.hget(chat_id, 'state')
    logging.info(f"Current state: {state}")
    await message.answer(chat_id)


@dp.message_handler(commands=["highprice"])
async def highprice(message: types.Message):
    await message.answer('')
    if not is_user_in_db(message):
        add_user(message)
    chat_id = message.chat.id
    redis_db.hset(chat_id, 'state', 1)
    redis_db.hset(chat_id, 'order', 'PRICE_HIGHEST_FIRST')
    logging.info('Команда "/highprice" была вызвана.')
    logging.info(redis_db.hget(chat_id, 'order'))
    state = redis_db.hget(chat_id, 'state')
    logging.info(f"Current state: {state}")
    await message.answer(chat_id)


@dp.message_handler(commands=["bestdeal"])
async def bestdeal(message: types.Message):
    await message.answer('')
    if not is_user_in_db(message):
        add_user(message)
    chat_id = message.chat.id
    redis_db.hset(chat_id, 'state', 1)
    redis_db.hset(chat_id, 'order', 'DISTANCE_FROM_LANDMARK')
    logging.info('Команда "/bestdeal" была вызвана.')
    logging.info(redis_db.hget(chat_id, 'order'))
    state = redis_db.hget(chat_id, 'state')
    logging.info(f"Current state: {state}")
    await message.answer(chat_id)


# # @dp.message_handler(commands=["history"])
# # async def history(message: types.Message):
# #     await message.answer('')
#
#
# @dp.message_handler(commands=['calendar'])
# def start(message: types.Message):
#     calendar, step = DetailedTelegramCalendar().build()
#     await message.answer(message.chat.id, f'Select {LSTEP[step]}', reply_markup=calendar)
#
#
# # @dp.callback_query_handler(func=DetailedTelegramCalendar.func())
# # def cal(message: types.Message):
# #     result, key, step = process(message.data)
# #     if not result and key:
# #         await message.answer(f'Select {LSTEP[step]}', message.chat.id, message.message_id, reply_markup=key)
# #     elif result:
# #         await message.answer(f'Вы выбрали {result}', message.chat.id, message.message_id)
#
#
# Хэндлер на сообщение приветствия
@dp.message_handler(content_types=['text'])
async def hello(message: types.Message):
    if message.text == 'Привет, Journey Hotels':
        await message.answer('Привет, это бот для поиска отелей!\nНапиши "/help" и познакомлю с моими командами')
    else:
        await message.answer('Привет, к сожалению, не понял запрос!\nНапиши "/help" и познакомлю с моими командами')

#
# def get_locations(msg: types.Message) -> None:
#     """
#     Получает имя локации и ищет локации с похожим названием и отправляет результат
#     msg: сообщение
#     """
#     if not is_input_correct(msg):
#         bot.send_message(msg.chat.id, make_message(msg, 'mistake_'))
#     else:
#         wait_msg = bot.send_message(msg.chat.id, ('wait', msg))
#         locations = make_locations_list(msg)
#         bot.delete_message(msg.chat.id, wait_msg.id)
#         if not locations or len(locations) < 1:
#             bot.send_message(msg.chat.id, str(msg.text) + ('locations_not_found', msg))
#         elif locations.get('bad_request'):
#             bot.send_message(msg.chat.id, ('bad_request', msg))
#         else:
#             menu = InlineKeyboardMarkup()
#             for loc_name, loc_id in locations.items():
#                 menu.add(InlineKeyboardButton(
#                     text=loc_name,
#                     callback_data='code' + loc_id)
#                 )
#             menu.add(InlineKeyboardButton(text=('cancel', msg), callback_data='cancel'))
#             bot.send_message(msg.chat.id, ('loc_choose', msg), reply_markup=menu)
#
#
# @dp.callback_query_handler(func=lambda call: True)
# def keyboard_handler(call: types.CallbackQuery) -> None:
#     """
#     Вызов клавиатуры handlers
#     call: CallbackQuery
#     """
#     logging.info(f'Function {keyboard_handler.__name__} called with argument: {call}')
#     chat_id = call.message.chat.id
#     bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id)
#
#     if call.data.startswith('code'):
#         if redis_db.hget(chat_id, 'state') != '1':
#             bot.send_message(call.message.chat.id, ('enter_command', call.message))
#             redis_db.hset(chat_id, 'state', 0)
#         else:
#             loc_name = exact_location(call.message.json, call.data)
#             redis_db.hset(chat_id, mapping={"destination_id": call.data[4:], "destination_name": loc_name})
#             logging.info(f"{loc_name} selected")
#             bot.send_message(
#                 chat_id,
#                 f"{('loc_selected', call.message)}: {loc_name}",
#             )
#             if redis_db.hget(chat_id, 'order') == 'DISTANCE_FROM_LANDMARK':
#                 redis_db.hincrby(chat_id, 'state', 1)
#             else:
#                 redis_db.hincrby(chat_id, 'state', 3)
#             bot.send_message(chat_id, make_message(call.message, 'question_'))
#
#     elif call.data.startswith('loc'):
#         redis_db.hset(chat_id, mapping={"locale": call.data[4:]})
#         bot.send_message(chat_id, call.message)
#
#
# async def get_search_parameters(msg: types.Message) -> None:
#     """
#     Исправление параметров поиска
#     msg: сообщение
#     """
#     logging.info(f'Функция {get_search_parameters.__name__} была вызвана с параметрами: {msg}')
#     chat_id = msg.chat.id
#     state = redis_db.hget(chat_id, 'state')
#     if not is_input_correct(msg):
#         bot.send_message(chat_id, make_message(msg, 'error_'))
#     else:
#         redis_db.hincrby(msg.chat.id, 'state', 1)
#         if state == '2':
#             min_price, max_price = sorted(msg.text.strip().split(), key=int)
#             redis_db.hset(chat_id, [state + 'min'], min_price)
#             logging.info(f"{[state + 'min']} set to {min_price}")
#             redis_db.hset(chat_id,[state + 'max'], max_price)
#             logging.info(f"{[state + 'max']} set to {max_price}")
#             await bot.send_message(chat_id, make_message(msg, 'ask_'))
#         elif state == '4':
#             redis_db.hset(chat_id, [state], msg.text.strip())
#             logging.info(f"{[state]} установлено {msg.text.strip()}")
#             redis_db.hset(chat_id, 'state', 0)
#             hotels_list(msg)
#         else:
#             redis_db.hset(chat_id, [state], msg.text.strip())
#             logging.info(f"{[state]} установлено {msg.text.strip()}")
#             await bot.send_message(chat_id, make_message(msg, 'ask_'))
#
#
# def hotels_list(msg: types.Message) -> None:
#     """
#     Отображение результатов по отелям
#     msg: сообщение
#     """
#     chat_id = msg.chat.id
#     wait_msg = bot.send_message(chat_id, ('wait', msg))
#     params = extract_search_parameters(msg)
#     hotels = get_hotels(msg, params)
#     logging.info(f'Function {get_hotels.__name__} returned: {hotels}')
#     bot.delete_message(chat_id, wait_msg.id)
#     if not hotels or len(hotels) < 1:
#         bot.send_message(chat_id, ('hotels_not_found', msg))
#     elif 'bad_request' in hotels:
#         bot.send_message(chat_id, ('bad_request', msg))
#     else:
#         quantity = len(hotels)
#         bot.send_message(chat_id, get_parameters_information(msg))
#         bot.send_message(chat_id, f"{('hotels_found', msg)}: {quantity}")
#         for hotel in hotels:
#             bot.send_message(chat_id, hotel)
#
#
# @dp.message_handler(content_types=['text'])
# def get_text_messages(message: types.Message) -> None:
#     """
#     Хэндлер текстового сообщения
#     message: сообщение
#     """
#     if not is_user_in_db(message):
#         add_user(message)
#     state = redis_db.hget(message.chat.id, 'state')
#     if state == '1':
#         get_locations(message)
#     elif state in ['2', '3', '4']:
#         get_search_parameters(message)
#     else:
#         await message.answer(message.chat.id, ('К сожалению, команда не ясна', message))
