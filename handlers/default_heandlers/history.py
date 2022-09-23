# import json
# import sqlite3
# import codecs
from aiogram.types import Message
from loader import dp
# from database import base as db_hotels
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from loguru import logger
# from datetime import datetime
# from django.db import DatabaseError, transaction
# from peewee import PrimaryKeyField, IntegerField, CharField, DateTimeField
#
# # @dp.message_handler(commands=["history"])
# # async def history(message: Message, state: FSMContext):
#
#
@logger.catch()
async def history(message: Message):
    logger.info('Команда /history была вызвана.')
    await message.answer('вызвана команда истории')


@logger.catch()
def register_handlers_history(dp: Dispatcher):
    dp.register_message_handler(history, commands=['history'])

#
# class Requests(BaseModel):
#     """Класс хранения истории пользователя"""
#     id = PrimaryKeyField(null=False)
#     user_id = IntegerField()
#     command = CharField()
#     city_name = IntegerField()
#     created_at = DateTimeField(default=datetime.now())
#
#     class Meta:
#         db_hotels = 'requests'
#
# def add_request(parameters: dict):
#     """Внесение данных запроса пользователя в таблицу"""
#     with db_hotels.atomic():
#         try:
#             row = Requests(user_id=parameters.get('user_id'),
#                            command=parameters.get('command'),
#                            city_name=parameters.get('city_name'),
#                            city_id=parameters.get('city_id'),
#                            hotels=json.dump(parameters.get('hotels'), ensure_ascii=False).encode('utf-8'))
#             row.save()
#         except:
#             logger.exception('Произошла ошибка-исключение в add_request')
#
#
# def get_user_history(user_id):
#     """Выаолнения запроса по истории пользователя - запрос в БД"""
#     with db_hotels:
#         try:
#             user_history = Requests.select().where(Requests.user_id == user_id)
#             return True, user_history
#         except DatabaseError:
#             return False, None
