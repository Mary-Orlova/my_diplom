from aiogram.types import Message
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from loguru import logger
from loader import dp


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
# @dp.message_handler(state=None)
# @dp.message_handler()
@logger.catch()
async def bot_echo(message: Message, state: FSMContext):
    await state.finish()
    if message.text == 'Привет, Journey Hotels':
        await message.answer('Привет, это бот для поиска отелей!\nНапиши "/help" и познакомлю с моими командами')
        logger.info('Команда "Привет, Journey Hotels" была вызвана.')
    else:
        await message.answer('Привет, к сожалению, не понял запрос!\nНапиши "/help" и познакомлю с моими командами')
        logger.error('Пользователь ввел не корректную команду', message.text)


def register_handlers_echo(dp: Dispatcher):
    dp.register_message_handler(bot_echo, state='*')
