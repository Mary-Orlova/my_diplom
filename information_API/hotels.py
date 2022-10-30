import datetime
import re
import requests
from config_data.config import RAPID_API_KEY
from aiogram.types import Message, MediaGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from loader import dp, bot
from states.status_info import HotelStatus


@logger.catch()
def delete_tags(html_text: str) -> str:
    """Метод удаления тегов - работа с html-текстом
    :param html_text: html
    Возвращает текст из найденной информации API"""
    text = re.sub('<([^<>]*)>', '', html_text)
    return text


@logger.catch()
def request_locations(msg: Message) -> dict:
    """Метод обработки локации
    param msg: сообщение
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
    logger.info(f'Параметры поиска: {querystring}')

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=40)
        data = response.json()
        logger.info(f'Получен ответ API отелей по местоположению: {data}')

        if data.get('message'):
            logger.error(f'Возникли проблемы с API')
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
        await bot.send_message(msg.chat.id, 'Возникло исключение при обработке ответа API по получению локации')
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
    :param dates: словарь сообщения, где содержится code+id города и название
    :param loc_id: id локации
    Возвращает локальное имя
    """
    logger.info(f"Запущена функция exact_location")
    for loc in dates['message']['reply_markup']['inline_keyboard']:
        if loc[0]['callback_data'] == loc_id:
            HotelStatus.city_name = loc[0]['text']
            return loc[0]['text']


@logger.catch()
async def get_hotels(msg: Message, state: FSMContext) -> [list, None]:
    """
    Вызов необходимых функций для получения и обработки данных об отеле
    :param msg: сообщение последнее пользователя (состояние)
    :param state: параметры поиска в формате машины состояний
    Возвращает список (строки) с описанием отеля
    """
    logger.debug(f'Запущен get_hotels')

    async with state.proxy() as state_data:
        parameters = {
            'command': state_data.get('order'),
            'city_id': state_data.get('city'),
            'city_name': state_data.get('city_name'),
            'hotels_count': state_data.get('hotels_count'),
            'get_photo': state_data.get('get_photo'),
            'photo_count': state_data.get('photo_count'),
            'check_in': state_data.get('check_in').strftime("%Y-%m-%d"),
            'check_out': state_data.get('check_out').strftime("%Y-%m-%d"),
            'min_price': state_data.get('min_price'),
            'max_price': state_data.get('max_price'),
            'min_distance': state_data.get('min_distance'),
            'max_distance': state_data.get('max_distance'),
        }
    out_hotel = str(parameters['check_out']).split('-')
    in_hotel = str(parameters['check_in']).split('-')
    out_hotel_day = datetime.date(int(out_hotel[0]), int(out_hotel[1]), int(out_hotel[2]))
    in_hotel_day = datetime.date(int(in_hotel[0]), int(in_hotel[1]), int(in_hotel[2]))
    night = str(out_hotel_day - in_hotel_day).split()[0]  # ночи для расчета общей цены
    logger.info(f'НОЧЕЙ: {night}')
    logger.debug(f'ЗАПИСЬ В СЛОВАРЬ ПАРАМЕТРЫ{parameters}')
    data = request_hotels(parameters)  # возвращается ответ по информации АПИ
    if 'bad_req' in data:
        return ['bad_request']
    command = parameters['command']
    hotel_count, photo = int(parameters['hotels_count']), int(parameters['photo_count'])
    minimum, maximum = parameters['min_distance'], parameters['max_distance']
    data = structure_hotels_info(data, command, minimum, maximum, hotel_count, photo)
    if not data or len(data['results']) < 1:
        return None
    if parameters['command'] == 'DISTANCE_FROM_LANDMARK':
        quantity = int(parameters['hotels_count'])
        data = choose_best_hotels(hotels=data['results'], distance=maximum, limit=quantity)
    else:
        data = data['results']
        logger.debug(f'В блоке ELSE data = {data}')
    await generate_hotels_descriptions(data, night, msg)


@logger.catch()
def request_hotels(parameters: dict, page: int = 1):
    """
    Регистрация информауии из API по отелям request information from the hotel api
    :param parameters: В параметры передаются параметры поиска
    :param page: Номер страницы
    Возвращается информация из API
    """
    logger.info(f'Метод request_hotels был вызван с параметрами: {parameters} и номером стр = {page}')
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {
        "adults1": "1",
        "pageNumber": page,
        "destinationId": parameters['city_id'],
        "pageSize": 25,
        "checkOut": parameters['check_out'],
        "checkIn": parameters['check_in'],
        "sortOrder": 'PRICE',
        "currency": "RUB",
        "locale": "ru_RU",
    }
    if parameters['command'] == 'DISTANCE_FROM_LANDMARK':
        querystring['priceMin'] = parameters['min_price']
        querystring['priceMax'] = parameters['max_price']
        querystring['sortOrder'] = 'DISTANCE_FROM_LANDMARK'
        querystring['distance'] = float(parameters['max_distance'])

    logger.info(f'Параметры поиска {querystring}')

    headers = {
        'x-rapidapi-key': RAPID_API_KEY,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=40)
        data = response.json()
        if data.get('message'):
            raise requests.exceptions.RequestException
        logger.info(f'Получен ответ API по отелям REQUESTHOTELS')
        return data

    except requests.exceptions.RequestException as critical_error:
        logger.error(f'Возникла ошибка при получении ответа: {critical_error}')
        return {'bad_req': 'bad_req'}
    except Exception as error:
        logger.exception(f'Ошибка в функции request_hotels: {error}')
        return {'bad_req': 'bad_req'}


@logger.catch()
def structure_hotels_info(data: dict, command: str,
                          minimum: str, maximum: str, hotel_count: int, photo: int) -> dict:
    """
    Структурирование данных по отелям
    :param data: данные по отелям в виде словаря
    :param command: команда пользователя
    :param minimum: минимальное расстояние до центра
    :param maximum: максимальное расстояние до центра
    :param hotel_count: кол-во отелей
    :param photo: кол-во фотографи отеля
    Возвращаются данные в виде словаря по отелям
    """
    logger.info(f'Метод structure_hotels_info был вызван')
    data = data.get('data', {}).get('body', {}).get('searchResults')
    hotels = dict()

    hotels['Общее количество'] = data.get('totalCount', 0)
    logger.info(f"next_page: {data.get('pagination', {}).get('nextPageNumber', 0)}")
    hotels['next_page'] = data.get('pagination', {}).get('nextPageNumber')
    hotels['results'] = []

    try:
        count = 0
        if hotels['Общее количество'] > 0:
            for cur_hotel in data.get('results'):
                if count < hotel_count:
                    hotel = dict()
                    hotel['name'] = cur_hotel.get('name')
                    hotel['star_rating'] = cur_hotel.get('starRating', 0)
                    hotel['price'] = hotel_price(cur_hotel)
                    if not hotel['price']:
                        continue
                    hotel['distance'] = cur_hotel.get('landmarks')[0].get('distance', 'Нет информации по расположению')
                    center = hotel['distance'].strip('').replace(',', '.').split()[0]
                    hotel['address'] = hotel_address(cur_hotel)
                    hotel['ref'] = get_hotel_ref(cur_hotel.get('id'))
                    if photo > 0:
                        hotel['photos'] = photos(cur_hotel, photo)
                    if hotel not in hotels['results'] and command != 'DISTANCE_FROM_LANDMARK':
                        hotels['results'].append(hotel)
                        count += 1
                        logger.debug(f'Был добавлен отель в список отелей {hotels["results"]}')
                    elif hotel not in hotels['results'] and command == 'DISTANCE_FROM_LANDMARK' and \
                            float(minimum) <= float(center) <= float(maximum):
                        hotels['results'].append(hotel)
                        count += 1
                        logger.debug(f'Был добавлен отель в список отелей {hotels["results"]}')
                else:
                    break
            logger.info(f'Отели в функции structure_hotels_info: {hotels}')
            return hotels

    except Exception as error:
        logger.exception(f'Ошибка в функции structure_hotels_info: {error}')


@logger.catch()
def choose_best_hotels(hotels: list[dict], distance: float, limit: int) -> list[dict]:
    """
    Вывод результата отелей в виде списка
    :param hotels: словарь отелей
    :param distance: диапазон расстояния, на котором находится отель от центра.
    :param limit: кол-ва отелей (выбранным пользователь)
    """

    logger.info(f'choose_best_hotels  вызвана с аргументами: дистанция = {distance}, отелей = {limit}\n{hotels}')
    hotels = list(filter(lambda x: float(x["distance"].strip('').replace(',', '.').split()[0]) <= distance, hotels))
    logger.info(f'Отфильтровали отели по дистанции {hotels}')
    # hotels = sorted(hotels, key=lambda k: k["price"])
    # logger.info(f'\nОтели отсортированы: {hotels}')
    return hotels


@logger.catch()
async def generate_hotels_descriptions(hotels: dict, night: str, msg: Message) -> list[str]:
    """
    Метод получения описания отеля
    :param hotels: информация об отеле
    :param night: кол-во ночей в отеле
    Возвращает список (строки) с описанием отеля
    """
    logger.info(f'Метод generate_hotels_descriptions был вызван')

    chat_id = msg.chat.id
    if not hotels or len(hotels) < 1:
        await bot.send_message(chat_id, 'Отель не найден')
    elif 'bad_request' in hotels:
        await bot.send_message(chat_id, 'bad_request')
    else:
        quantity = len(hotels)
        await bot.send_message(chat_id, f"{'Найденные отели'}: {quantity}")

    for hotel in hotels:
        current_day = str(hotel.get('price'))
        all_current = str(int(current_day) * int(night))
        logger.info(f'ЗА НОЧЬ{current_day} ОБЩАЯ ЦЕНА{all_current}')

        message = str(
            f" Отель: {hotel.get('name')}\n"
            f" Рейтинг: {hotel_rating(hotel.get('star_rating'))}\n"
            f" Адрес: {hotel.get('address')}\n"
            f" Расположенность от центра: {hotel.get('distance')}\n"
            f" Цена за 1 ночь: {current_day}\n"
            f" Цена за все время: {all_current}\n"
            f" Ссылка: {hotel.get('ref')}\n"
        )

        if hotel.get('photos') is not None:
            media = MediaGroup()
            for num, photo in enumerate(hotel['photos']):
                if num == 0:
                    media.attach_photo(photo, caption=message)
                else:
                    media.attach_photo(photo)
            await bot.send_media_group(chat_id=chat_id, media=media)

        elif hotel.get('photos') is None:
            await bot.send_message(chat_id, 'У Отеля нет фотографий', message)


@logger.catch()
def hotel_price(hotel: dict) -> int:
    """ Возвращает стоимость отеля
    :param hotel: словарь по отелю
    Возвращает стоимость за отель"""
    price = 0
    try:
        if hotel.get('ratePlan').get('price').get('exactCurrent'):
            price = hotel.get('ratePlan').get('price').get('exactCurrent')
            price = round(price)
        else:
            price = hotel.get('ratePlan').get('price').get('current')
            price = int(re.sub(r'[^0-9]', '', price))
            price = round(price)
    except Exception as exception:
        logger.exception(f'Возникла ошибка при обработке запроса получения цены отеля {exception}')
    return price


@logger.catch()
def hotel_address(hotel: dict) -> str:
    """ Метод получения адреса отеля
    :param hotel: словарь по отелю
    Возвращает адрес отеля"""
    message = f'Информация об адресе отеля отсутствует'
    if hotel.get('address'):
        message = hotel.get('address').get('streetAddress', message)
    return message


@logger.catch()
def get_hotel_ref(hotel_id) -> str:
    """Возвращает ссылку на отель """
    return f'https://hotels.com/ho{hotel_id}'


@logger.catch()
def hotel_rating(rating: float) -> str:
    """ Метод поиска рейтинга отеля
    :param rating: рейтинг из информации по отелю
    Возвращает рейтинг отеля """
    if not rating:
        return 'Информация о рейтинге отеля отсутствует'
    return '⭐' * int(rating)


def photos(hotel: dict, photo_count: int):
    """ Получение фото отеля"""
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": hotel.get('id')}
    headers = {
        'x-rapidapi-key': RAPID_API_KEY,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    photos = response.json()
    hotel['photos'] = []

    # Проверка наличия фото отеля
    try:
        photos_list = photos["hotelImages"]
        for photo in photos_list:
            if len(hotel['photos']) < photo_count:
                photo = photo['baseUrl'][0:-11] + '.jpg'
                hotel['photos'].append(photo)
            elif len(hotel['photos']) == photo_count:
                return hotel['photos']
            else:
                break
    except KeyError:
        print('К сожалению, фотографий меньше.')
    except TypeError:
        print('В методе photos Сервер не отвечает.')
