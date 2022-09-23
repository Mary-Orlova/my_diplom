from aiogram.types import Message
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
# from states.status_info import HighpriceStatus
# from information_API import hotels
from loader import dp, bot
# from config_data.config import DEFAULT_COMMANDS
from loguru import logger

lowhighprice_callback_data = CallbackData('lowhighprice', 'action', 'city_id')
# @dp.message_handler(commands=["highprice"])
# async def highprice(message: Message, state: FSMContext):
@logger.catch()
async def highprice(message: Message):
    # await state.finish()
    await message.answer('Вызвана команда высокой цены отеля')
    # if not is_user_in_db(message):
    #     add_user(message)
    # chat_id = message.chat.id
    # redis_db.hset(chat_id, 'state', 1)
    # redis_db.hset(chat_id, 'order', 'PRICE_HIGHEST_FIRST')
    logger.info('Команда "/highprice" была вызвана.')
    # logging.info(redis_db.hget(chat_id, 'order'))
    # state = redis_db.hget(chat_id, 'state')
    # logging.info(f"Current state: {state}")
    # await message.answer(chat_id)


def register_handlers_highprice(dp: Dispatcher):
    dp.register_message_handler(highprice, commands=['highprice'], state='*')
