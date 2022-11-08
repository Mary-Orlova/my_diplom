from aiogram.types import Message
from loader import dp
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from loguru import logger


# Хэндлер на команду /help
# @dp.message_handler(commands=["help"])
@logger.catch()
async def help(message: Message, state: FSMContext) -> None:
    await state.finish()
    logger.info(f'Команда "/help" была вызвана.')
    await message.answer(
        '\n/hello-world — вывод Приветствия'
        '\n/lowprice — вывод самых дешёвых отелей в городе'
        '\n/highprice — вывод самых дорогих отелей в городе'
        '\n/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра'
        '\n/history — вывод истории поиска отелей')


def register_handlers_help(dp: Dispatcher):
    dp.register_message_handler(help, commands=['help'], state='*')
