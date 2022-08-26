import os
import re
import requests
from aiogram import types
import logging
from dotenv import load_dotenv
from bot_redis import redis_db

load_dotenv()

X_RAPIDAPI_KEY = os.getenv('RAPID_API_KEY')


def exact_location(data: dict, loc_id: str) -> str:
    """
    Получает id выбранной локации и возвращает имя локации из словаря
    data: словарь сообщения
    loc_id: id локации
    Возвращает локальное имя
    """
    for loc in data['reply_markup']['inline_keyboard']:
        if loc[0]['callback_data'] == loc_id:
            return loc[0]['text']


def delete_tags(html_text: str) -> str:
    """Метод удаления тегов - работа с html-текстом"""
    text = re.sub('<([^<>]*)>', '', html_text)
    return text


def request_locations(msg: types.Message) -> dict:
    """Метод обработки локации"""
    url = "https://hotels4.p.rapidapi.com/locations/search"

    querystring = {
        "query": msg.text.strip(),
        "locale": redis_db.hget(msg.chat.id, 'locale'),
    }

    headers = {
        'x-rapidapi-key': X_RAPIDAPI_KEY,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }
    logging.info(f'Параметры поиска локации: {querystring}')

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
        data = response.json()
        logging.info(f'Получен ответ API отелей по местоположению: {data}')

        if data.get('message'):
            logging.error(f'Возникли проблемы с API по местоположению отелей {data}')
            raise requests.exceptions.RequestException
        return data
    except requests.exceptions.RequestException as critical_error:
        logging.error(f'Ошибка сервера: {critical_error}')
    except Exception as error:
        logging.error(f'Error: {error}')


def make_locations_list(msg: types.Message) -> dict:
    """
    Получает данные из ответа API отеля и создает словарь
    msg: сообщение
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
            logging.info(locations)
            return locations
    except Exception as error:
        logging.error(f'Не удалось проанализировать ответ отеля. {error}')