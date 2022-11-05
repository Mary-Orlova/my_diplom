from aiogram.types import Message
from database import base as db_hotels
from aiogram import Dispatcher
from loguru import logger


@logger.catch()
def register_handlers_history(dp: Dispatcher):
    dp.register_message_handler(history, commands=['history'])
    dp.register_message_handler(history, commands=['delete_history'])


@logger.catch()
async def history(message: Message) -> None:
    """ Метод вывода истории из БД пользователю в телеграм-бот.
    :param message: сообщение пользователя."""
    logger.info(f'Команда /history была вызвана, id = {message.from_user.id}')
    user_id = int(message.from_user.id)
    limit = '10'
    history_info = db_hotels.show_history(user_id, limit)
    await message.answer(str(history_info))


@logger.catch()
async def delete_history(message: Message) -> None:
    """ Метод удаления истории из БД.
    :param message: сообщение пользователя."""
    logger.info(f'Команда /delete_history была вызвана, id = {message.from_user.id}')
    id_string = int(message.from_user.id)
    db_hotels.delete_history(id_string)
