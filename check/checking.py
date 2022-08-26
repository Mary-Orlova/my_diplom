import re
from aiogram import types
import logging
from bot_redis import redis_db
from datetime import datetime

# задаем уровень логов
logging.basicConfig(level=logging.INFO)


def is_input_correct(msg: types.Message) -> bool:
    """
    Проверка корректного вода параметра данных по поиску
    Возвращает True если корректны данные, введенные пользователем
    """
    state = redis_db.hget(msg.chat.id, 'state')
    msg = msg.text.strip()
    if state == '4' and ' ' not in msg and msg.isdigit() and 0 < int(msg) <= 20:
        return True
    elif state == '3' and ' ' not in msg and msg.replace('.', '').isdigit():
        return True
    elif state == '2' and msg.replace(' ', '').isdigit() and len(msg.split()) == 2:
        return True
    elif state == '1' and msg.replace(' ', '').replace('-', '').isalpha():
        return True


def get_parameters_information(msg: types.Message) -> str:
    """ Формирует сообщение о текущих параметрах поиска """
    logging.info(f'Функция {get_parameters_information.__name__} была вызвана с параметрами: {msg}')
    parameters = redis_db.hgetall(msg.chat.id)
    sort_order = parameters['order']
    city = parameters['destination_name']
    currency = parameters['currency']
    message = (
        f"<b>{('Параметры: ', msg)}</b>\n"
        f"{('Город: ', msg)}: {city}\n"
    )
    if sort_order == "DISTANCE_FROM_LANDMARK":
        price_min = parameters['min_price']
        price_max = parameters['max_price']
        distance = parameters['distance']
        message += f"{('price', msg)}: {price_min} - {price_max} \n" \
                   f"{('max_distance', msg)}: {distance} {('dis_unit', msg)}"
    logging.info(f'Search parameters: {message}')
    return message


def make_message(msg: types.Message, prefix: str) -> str:
    """ Формирует и возвращает сообщение об недопустимом вводе информации или вопросе """
    state = redis_db.hget(msg.chat.id)
    message = (prefix, msg)
    if state == '2':
        message += f" ({redis_db.hget(msg.chat.id)})"
    return message


def hotel_price(hotel: dict) -> int:
    """ Возвращает стоимость отеля """
    price = 0
    try:
        if hotel.get('ratePlan').get('price'):
            price = hotel.get('ratePlan').get('price')
        else:
            price = hotel.get('ratePlan').get('price')
            price = int(re.sub(r'[^0-9]', '', price))
    except Exception as exception:
        logging.warning(f'Возникла ошибка при обработке запроса получения цены отеля {exception}')
    return price


def hotel_address(hotel: dict, msg: types.Message) -> str:
    """ Возвращает адресс отеля """
    message = ('Информация об адрессе отеля отсутствует', msg)
    if hotel.get('address'):
        message = hotel.get('address').get('streetAddress', message)
    return message


def hotel_rating(rating: float, msg: types.Message) -> str:
    """ Возвращает рейтинг отеля """
    if not rating:
        return ('Информация о рейтинге отеля отсутствует', msg)
    return '⭐' * int(rating)


def check_in_n_out_dates() -> dict:
    """
    check_in Дата заезда
    check_out Дата отъезда
    Возвращает словарь с датой заезда и отъезда
    """
    dates = {}
    check_in = input('Введите желаемую дату заезда (год-месяц-день): ')
    check_out = input('Введите желаемую дату отъезда (год-месяц-день): ')
    dates['check_in'] = check_in.strftime("%Y-%m-%d")
    dates['check_out'] = check_out.strftime("%Y-%m-%d")
    return dates


def add_user(msg: types.Message) -> None:
    """ Добавляет пользователя в базу """
    logging.info("Пользователь добавлен в базу")
    chat_id = msg.chat.id

def is_user_in_db(msg: types.Message) -> bool:
    """ Проверка есть ли пользователь в базе
    Возвращает булевое значение """
    logging.info('Проверка есть ли пользователь в базе is_user_in_db')
    chat_id = msg.chat.id
    return redis_db.hget(chat_id, 'state')


def extract_search_parameters(msg: types.Message) -> dict:
    """ Извлекает параметры поиска из базы данных """
    logging.info(f"Команда {extract_search_parameters.__name__} была вызвана")
    params = redis_db.hgetall(msg.chat.id)
    logging.info(f"Параметры поиска: {params}")
    return params
