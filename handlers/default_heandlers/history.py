# import sqlite3
from states.status_info import HotelStatus
from aiogram.types import Message
# from loader import dp
# from database import base as db_hotels
from aiogram import Dispatcher
from loguru import logger
from datetime import datetime
# import requests, json


# @dp.message_handler(commands=["history"])
# async def history(message: Message, state: FSMContext):
@logger.catch()
async def history(message: Message):
    logger.info('Команда /history была вызвана.')
    await message.answer('вызвана команда истории')


@logger.catch()
def register_handlers_history(dp: Dispatcher):
    dp.register_message_handler(history, commands=['history'])


class Requests():
    def __init__(self, user_id, command, city_name=HotelStatus.city_name, city_id=HotelStatus.city):
        self.id = user_id
        self.command = command
        self.city_name = city_name
        self.city_id = city_id
        self.created_at = datetime.now

        class Meta:
            db_hotels = 'requests'
