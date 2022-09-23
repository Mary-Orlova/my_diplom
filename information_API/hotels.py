import re
import requests
from config_data.config import RAPID_API_KEY
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from handlers.default_heandlers import bestdeal
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from loguru import logger
from loader import dp, bot
from states.status_info import BestdealStatus
from keyboards.inline import answer


@logger.catch()
def delete_tags(html_text: str) -> str:
    """Метод удаления тегов - работа с html-текстом
    :param html_text
    Возвращате текст из найденной информации API"""
    text = re.sub('<([^<>]*)>', '', html_text)
    return text


@logger.catch()
def request_locations(msg: Message) -> dict:
    """Метод обработки локации
    :param msg: сообщение
    Возвращает словарь
    """

    url = "https://hotels4.p.rapidapi.com/locations/search"

    querystring = {
        "query": msg.text.strip(),
        "locale": (msg.chat.id, 'locale'),
        }

    headers = {
        'x-rapidapi-key': RAPID_API_KEY,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
        }
    logger.info(f'Параметры поиска локации: {querystring}')

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=40)
        data = response.json()
        logger.info(f'Получен ответ API отелей по местоположению: {data}')

        if data.get('message'):
            logger.error(f'Возникли проблемы с API по местоположению отелей {data}')
            raise requests.exceptions.RequestException
        return data
    except requests.exceptions.RequestException as critical_error:
        logger.exception(f'Ошибка сервера: {critical_error}')
    except Exception as error:
        logger.exception(f'Возникла ошибка: {error}')


@logger.catch()
def make_locations_list(msg: Message) -> dict:
    """
    Получает данные из ответа API отеля и создает словарь
    :param msg: сообщение
    Возвращается словарь локальное имя - локальный ID
    """
    data = request_locations(msg)
    if not data:
        return {'bad_request': 'bad_request'}

    try:
        locations = dict()
        if len(data.get('suggestions')[0].get('entities')) > 0:
            for item in data.get('suggestions')[0].get('entities'):
                location_name = delete_tags(item['caption'])
                locations[location_name] = item['destinationId']
            logger.info('Функция make_locations_list получила ответ - запись в словарь', locations)
            return locations
    except Exception as error:
        logger.error(f'Не удалось проанализировать ответ отеля. {error}')


@logger.catch()
async def get_locations(msg: Message) -> None:
    """
    Получает имя локации и ищет локации с похожим названием и отправляет результат
    :param msg: сообщение c названием искомого города для поиска отеля
    """
    locations = make_locations_list(msg)
    if not locations or len(locations) < 1:
        await bot.send_message(msg.chat.id, 'К сожалению, локация не найдена')
    elif locations.get('bad_request'):
        await bot.send_message('bad_request', msg)
    else:
        menu = InlineKeyboardMarkup()
        for loc_name, loc_id in locations.items():
            menu.add(InlineKeyboardButton(
                text=loc_name,
                callback_data='code' + loc_id)
            )
        menu.add(InlineKeyboardButton(text='cancel', callback_data='cancel'))
        await bot.send_message(msg.chat.id, 'Уточните, пожалуйста:', reply_markup=menu)
        logger.info('Создана клавиатура с городами и отправлена пользователю')


@logger.catch()
async def exact_location(dates: dict, loc_id: str) -> str:
    """
    Получает id выбранной локации и возвращает имя локации из словаря
    :param data: словарь сообщения, где содержится code+id города и название
    :param loc_id: id локации
    Возвращает локальное имя
    """
    logger.info(f"проверка словарь переданный{dates}, айди города {loc_id}")
    for loc in dates['message']['reply_markup']['inline_keyboard']:
        if loc[0]['callback_data'] == loc_id:
            return loc[0]['text']
    logger.info(f"Была вызвана функция exact_location")


@logger.catch()
async def center_distance_correct(hotel_info: dict, parameters: dict) -> bool:
    """Проверка соответствия введеных параметров отеля до центра города
    :param hotel_info информация по отелю
    :param  parameters мин/макс дистанция
    Возвращает булевое значение
    """
    valid = False
    if hotel_info.get('price') and hotel_info.get('center_distance'):
        parts = hotel_info['center_distance'].split()
        if len(parts) > 0:
            try:
                valid = parameters['min_distance'] <= float(re.sub(',', '.', parts[0])) <= parameters['max_distance']
            except ValueError:
                valid = False
    return valid


@logger.catch()
async def get_hotels(message: Message, state: FSMContext):
    """"Выполнение запроса для получения данных по отелям от пользователя
    param: message сообщение-запросы
    param: state состояние пользователя по запросам"""
    async with state.proxy() as state_data:
        parameters = {
            'user_id': state_data.get('user_id'),
            'command': state_data.get('command'),
            'message_id': state_data.get('message_id'),
            'city_name': state_data.get('city_name'),
            'city_id': state_data.get('city_id'),
            'hotels_count': state_data.get('hotels_count'),
            'get_photo': state_data.get('get_photo'),
            'photo_count': state_data.get('photo_count'),
            'check_in': state_data.get('check_in'),
            'check_out': state_data.get('check_out'),
            'min_price': state_data.get('min_price'),
            'max_price': state_data.get('max_price'),
            'min_distance': state_data.get('min_distance'),
            'max_distance': state_data.get('max_distance'),
            'locale': state_data.get('currency'),
            'currency': state_data.get('currency'),
            'distance_unit': state_data.get('distance_unit')
            }
    url = "https://hotels4.p.rapidapi.com" + 'property/list'
    headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': RAPID_API_KEY
        }


@logger.catch()
def get_parameters_information(msg: Message) -> str:
    """ Формирует сообщение о текущих параметрах поиска
    :param msg сообщение-поиск по параметру
    Возвращает строку по минимальной/максимальной цене"""
    logger.info(f'Функция {get_parameters_information.__name__} была вызвана с параметрами: {msg}')
    parameters = msg.chat.id
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
    logger.info(f'Поиск с параметрами: {message}')
    return message


@logger.catch()
def make_message(msg: Message, prefix: str) -> str:
    """ Формирует и возвращает сообщение об недопустимом вводе информации или вопросе
    :param msg: запрос сообщение
    :param prefix недопустимый ввод
    Возвращает сообщение об ошибке ввода"""
    state = msg.chat.id
    message = (prefix, msg)
    return message


@logger.catch()
def extract_search_parameters(msg: Message) -> dict:
    """ Извлекает параметры поиска из базы данных
    :param msg: сообщение-запрос
    Возвращает параметры поиска"""
    logger.info(f"Команда {extract_search_parameters.__name__} была вызвана")
    params = msg.chat.id
    logger.info(f"Параметры поиска: {params}")
    return params


@logger.catch()
def hotels_list(msg: Message) -> None:
    """
    Отображение результатов по отелям
    :param msg: сообщение
    """
    chat_id = msg.chat.id
    wait_msg = bot.send_message(chat_id, ('wait', msg))
    params = extract_search_parameters(msg)
    hotels = get_hotels(msg, params)
    logger.info(f'Метод {get_hotels.__name__} вернул: {hotels}')
    bot.delete_message(chat_id, wait_msg.id)
    if not hotels or len(hotels) < 1:
        bot.send_message(chat_id, ('hotels_not_found', msg))
    elif 'bad_request' in hotels:
        bot.send_message(chat_id, ('bad_request', msg))
    else:
        quantity = len(hotels)
        bot.send_message(chat_id, get_parameters_information(msg))
        bot.send_message(chat_id, f"{('hotels_found', msg)}: {quantity}")
        for hotel in hotels:
            bot.send_message(chat_id, hotel)

@logger.catch()
def get_hotels(msg: Message, parameters: dict) -> [list, None]:
    """
    Вызов необходимых функций для получения и обработки данных об отеле
    :param msg: сообщение состояние
    :param parameters: параметры поиска
    Возвращает список (строки) с описанием отеля
    """
    data = request_hotels(parameters)
    if 'bad_req' in data:
        return ['bad_request']
    data = structure_hotels_info(msg, data)
    if not data or len(data['results']) < 1:
        return None
    if parameters['order'] == 'DISTANCE_FROM_LANDMARK':
        next_page = data.get('next_page')
        distance = float(parameters['distance'])
        while next_page and next_page < 5 \
                and float(data['results'][-1]['distance'].replace(',', '.').split()[0]) <= distance:
            add_data = request_hotels(parameters, next_page)
            if 'bad_req' in data:
                logger.error('bad_request')
                break
            add_data = structure_hotels_info(msg, add_data)
            if add_data and len(add_data["results"]) > 0:
                data['results'].extend(add_data['results'])
                next_page = add_data['next_page']
            else:
                break
        quantity = int(parameters['quantity'])
        data = choose_best_hotels(data['results'], distance, quantity)
    else:
        data = data['results']

    data = generate_hotels_descriptions(data, msg)
    return data


@logger.catch()
def request_hotels(parameters: dict, page: int = 1):
    """
    Регистрация информауии из API по отелям request information from the hotel api
    :param parameters: В параметры передаются параметры поиска
    :param page: Номер страницы
    Возвращается информация из API
    """
    logger.info(f'Метод {request_hotels.__name__} был вызван с параметрами: номер = {page}, '
                f'параметры поиска = {parameters}')
    url = "https://hotels4.p.rapidapi.com/properties/list"
    dates = check_in_n_out_dates()

    querystring = {
        "adults1": "1",
        "pageNumber": page,
        "destinationId": parameters['destination_id'],
        "pageSize": parameters['quantity'],
        "checkOut": dates['check_out'],
        "checkIn": dates['check_in'],
        "sortOrder": parameters['order'],
        "locale": parameters['locale']
    }
    if parameters['order'] == 'DISTANCE_FROM_LANDMARK':
        querystring['priceMax'] = parameters['max_price']
        querystring['priceMin'] = parameters['min_price']
        querystring['pageSize'] = '25'

    logger.info(f'Параметры поиска {querystring}')

    headers = {
        'x-rapidapi-key': RAPID_API_KEY,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
        data = response.json()
        if data.get('message'):
            raise requests.exceptions.RequestException

        logger.info(f'Получен ответ API по отелям: {data}')
        return data

    except requests.exceptions.RequestException as critical_error:
        logger.error(f'Возникла ошибка при получении ответа: {critical_error}')
        return {'bad_req': 'bad_req'}
    except Exception as error:
        logger.exception(f'Ошибка в функции {request_hotels.__name__}: {error}')
        return {'bad_req': 'bad_req'}


@logger.catch()
def structure_hotels_info(msg: Message, data: dict) -> dict:
    """
    Структурирование данных по отелям
    :param msg: сообщение пользователя
    :param data: данные по отелям в виде словаря
    Возвращаются данные в виде словаря по отелям
    """
    logger.info(f'Метод {structure_hotels_info.__name__} был вызван с параметрами: msd = {msg}, data = {data}')
    data = data.get('data', {}).get('body', {}).get('searchResults')
    hotels = dict()
    hotels['Общее количество'] = data.get('totalCount', 0)

    logger.info(f"Следующая страница: {data.get('pagination', {}).get('nextPageNumber', 0)}")
    hotels['Следующая страница'] = data.get('pagination', {}).get('nextPageNumber')
    hotels['results'] = []

    try:
        if hotels['Общее количество'] > 0:
            for cur_hotel in data.get('results'):
                hotel = dict()
                hotel['name'] = cur_hotel.get('name')
                hotel['star_rating'] = cur_hotel.get('starRating', 0)
                hotel['price'] = hotel_price(cur_hotel)
                if not hotel['price']:
                    continue
                hotel['distance'] = cur_hotel.get('landmarks')[0].get('distance', ('no_information', msg))
                hotel['address'] = hotel_address(cur_hotel, msg)

                if hotel not in hotels['results']:
                    hotels['results'].append(hotel)
        logger.info(f'Отели в функции {structure_hotels_info.__name__}: {hotels}')
        return hotels

    except Exception as error:
        logger.exception(f'Ошибка в функции {structure_hotels_info.__name__}: {error}')


@logger.catch()
def choose_best_hotels(hotels: list[dict], distance: float, limit: int) -> list[dict]:
    """
    Вывод результата отелей в виде списка
    :param hotels: словарь отелей
    :param distance: диапазон расстояния, на котором находится отель от центра.
    :param limit: кол-ва отелей (выбранным пользователь)
    """
    logger.info(f'Функция {choose_best_hotels.__name__} была вызвана с аргументами: '
                f'дистанция = {distance}, количество отелей = {limit}\n{hotels}')
    hotels = list(filter(lambda x: float(x["distance"].strip().replace(',', '.').split()[0]) <= distance, hotels))
    logger.info(f'Отфильтрованы отели: {hotels}')
    hotels = sorted(hotels, key=lambda k: k["price"])
    logger.info(f'Отели отсортированы: {hotels}')
    if len(hotels) > limit:
        hotels = hotels[:limit]
    return hotels


@logger.catch()
def generate_hotels_descriptions(hotels: dict, msg: Message) -> list[str]:
    """
    Метод получения описания отеля
    :param hotels: информация об отеле
    :param msg: сообщение пользователя
    Возвращает список (строки) с описанием отеля
    """
    logger.info(f'Метод {generate_hotels_descriptions.__name__} был вызван с параметрами {hotels}')
    hotels_info = []

    for hotel in hotels:
        message = (
            f"{('Отель', msg)}: {hotel.get('name')}\n"
            f"{('Рейтинг', msg)}: {hotel_rating(hotel.get('star_rating'), msg)}\n"
            f"{('Адресс', msg)}: {hotel.get('address')}\n"
            f"{('Расположенность от центра', msg)}: {hotel.get('distance')}\n"
            f"{('Цена', msg)}: {hotel['price']} \n"
            f"{('Фотографии отеля', msg)}: {hotel.get('photos')}\n"
        )
        hotels_info.append(message)
    return hotels_info


@logger.catch()
def hotel_price(hotel: dict) -> int:
    """ Возвращает стоимость отеля
    :param hotel: словарь по отелю
    Возвращает стоимость за отель"""
    price = 0
    try:
        if hotel.get('ratePlan').get('price'):
            price = hotel.get('ratePlan').get('price')
        else:
            price = hotel.get('ratePlan').get('price')
            price = int(re.sub(r'[^0-9]', '', price))
    except Exception as exception:
        logger.exception(f'Возникла ошибка при обработке запроса получения цены отеля {exception}')
    return price


@logger.catch()
def hotel_address(hotel: dict, msg: Message) -> str:
    """ Метод получения адреса отеля
    :param hotel: словарь по отелю
    :param msg: адрес отеля
    Возвращает адрес отеля"""
    message = ('Информация об адресе отеля отсутствует', msg)
    if hotel.get('address'):
        message = hotel.get('address').get('streetAddress', message)
    return message


@logger.catch()
def hotel_rating(rating: float, msg: Message) -> str:
    """ Метод поиска рейтинга отеля
    :param rating: рейтинг из информации по отелю
    :param msg: сообщение-запрос
    Возвращает рейтинг отеля """
    if not rating:
        return 'Информация о рейтинге отеля отсутствует'
    return '⭐' * int(rating)


@logger.catch()
def check_in_n_out_dates() -> dict:
    """
    :param heck_in Дата заезда
    :param check_out Дата отъезда
    Возвращает словарь с датой заезда и отъезда
    """
    dates = {}
    dates['check_in'] = BestdealStatus.check_in()
    dates['check_out'] = BestdealStatus.check_out()
    return dates
