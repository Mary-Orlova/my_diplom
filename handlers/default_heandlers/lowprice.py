from aiogram.types import Message
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
# from states.status_info import LowpriceStatus
# from information_API import hotels
# from loader import dp
# from config_data.config import DEFAULT_COMMANDS
from loguru import logger
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

# @dp.message_handler(commands=["lowprice"])
# async def lowprice(message: Message, state: FSMContext) -> None:

lowhighprice_callback_data = CallbackData('lowhighprice', 'action', 'city_id')


@logger.catch()
async def lowprice(message: Message, state: FSMContext) -> None:
    await state.finish()
    # chat_id = message.chat.id
    # redis_db.hset(chat_id, 'state', 1)
    # redis_db.hset(chat_id, 'order', 'PRICE')
    logger.info('Команда "/lowprice" была вызвана.')
    # logging.info(redis_db.hget(chat_id, 'order'))
    # state = redis_db.hget(chat_id, 'state')
    await message.answer('команда поиска дешевых отелей была вызвана')


def register_handlers_lowprice(dp: Dispatcher):
    dp.register_message_handler(lowprice, commands=['lowprice'], state='*')
