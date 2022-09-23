from aiogram.types import Message
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from loguru import logger
from loader import dp


# Хэндлер на команду /hello-world
# @dp.message_handler(commands=["hello_world"])
@logger.catch()
async def hello_world(message: Message, state: FSMContext) -> None:
    await state.finish()
    logger.info('Команда /hello_world была вызвана.')
    await message.answer('Привет, это бот для поиска отелей!\nНапиши "/help"')


def register_handlers_hello_world(dp: Dispatcher):
    dp.register_message_handler(hello_world, commands=['hello_world'], state='*')
