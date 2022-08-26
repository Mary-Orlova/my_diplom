import os

import requests
from dotenv import load_dotenv
import logging
from aiogram import types
from check.checking import check_in_n_out_dates, hotel_price,  hotel_address, hotel_rating
from bot_redis import redis_db

load_dotenv()

X_RAPIDAPI_KEY = os.getenv('RAPID_API_KEY')


def get_hotels(msg: types.Message, parameters: dict) -> [list, None]:
    """
    Вызов необходимых функций для получения и обработки данных об отеле
    msg: сообщение состояние
    parameters: параметры поиска
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
                logging.warning('bad_request')
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


def request_hotels(parameters: dict, page: int = 1):
    """
    Регистрация информауии из API по отелям request information from the hotel api
    В параметры передаются параметры поиска
    Номер страницы
    Возвращается информация из API
    """
    logging.info(f'Метод {request_hotels.__name__} был вызван с параметрами: номер = {page}, '
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

    logging.info(f'Параметры поиска {querystring}')

    headers = {
        'x-rapidapi-key': X_RAPIDAPI_KEY,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
        data = response.json()
        if data.get('message'):
            raise requests.exceptions.RequestException

        logging.info(f'Получен ответ API по отелям: {data}')
        return data

    except requests.exceptions.RequestException as critical_error:
        logging.error(f'Возникла ошибка при получении ответа: {critical_error}')
        return {'bad_req': 'bad_req'}
    except Exception as error:
        logging.info(f'Ошибка в функции {request_hotels.__name__}: {error}')
        return {'bad_req': 'bad_req'}


def structure_hotels_info(msg: types.Message, data: dict) -> dict:
    """
    Структурирование данных по отелям
    msg: сообщение пользователя
    data: данные по отелям в виде словаря
    Возвращаются данные в виде словаря по отелям
    """
    logging.info(f'Метод {structure_hotels_info.__name__} был вызван с параметрами: msd = {msg}, data = {data}')
    data = data.get('data', {}).get('body', {}).get('searchResults')
    hotels = dict()
    hotels['Общее количество'] = data.get('totalCount', 0)

    logging.info(f"Следующая страница: {data.get('pagination', {}).get('nextPageNumber', 0)}")
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
                hotel['distance'] = cur_hotel.get('landmarks')[0].get('distance', _('no_information', msg))
                hotel['address'] = hotel_address(cur_hotel, msg)

                if hotel not in hotels['results']:
                    hotels['results'].append(hotel)
        logging.info(f'Отели в функции {structure_hotels_info.__name__}: {hotels}')
        return hotels

    except Exception as error_in_structure_hotels:
        logging.info(f'Ошибка в функции {structure_hotels_info.__name__}: {error_in_structure_hotels}')


def choose_best_hotels(hotels: list[dict], distance: float, limit: int) -> list[dict]:
    """
    Вывод результата отелей в виде списка
    hotels: словарь отелей
    distance: диапазон расстояния, на котором находится отель от центра.
    limit: кол-ва отелей (выбранным пользователь)
    """
    logging.info(f'Функция {choose_best_hotels.__name__} была вызвана с аргументами: '
                f'дистанция = {distance}, количество отелей = {limit}\n{hotels}')
    hotels = list(filter(lambda x: float(x["distance"].strip().replace(',', '.').split()[0]) <= distance, hotels))
    logging.info(f'Отфильтрованы отели: {hotels}')
    hotels = sorted(hotels, key=lambda k: k["price"])
    logging.info(f'Отели отсортированы: {hotels}')
    if len(hotels) > limit:
        hotels = hotels[:limit]
    return hotels


def generate_hotels_descriptions(hotels: dict, msg: types.Message) -> list[str]:
    """
    Метод получения описания отеля
    hotels: информация об отеле
    msg: сообщение пользователя
    Возвращает список (строки) с описанием отеля
    """
    logging.info(f'Метод {generate_hotels_descriptions.__name__} был вызван с параметрами {hotels}')
    hotels_info = []

    for hotel in hotels:
        message = (
            f"{('Отель', msg)}: {hotel.get('name')}\n"
            f"{('Рейтинг', msg)}: {hotel_rating(hotel.get('star_rating'), msg)}\n"
            f"{('Адресс', msg)}: {hotel.get('address')}\n"
            f"{('Расположенность от центра', msg)}: {hotel.get('distance')}\n"
            f"{('Цена', msg)}: {hotel['price']} {redis_db.hget(msg.chat.id)}\n"
            f"{('Фотографии отеля', msg)}: {hotel.get('photos')} {redis_db.send_photo}\n"
        )
        hotels_info.append(message)
    return hotels_info
