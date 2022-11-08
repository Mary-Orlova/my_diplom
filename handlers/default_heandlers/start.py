from aiogram.types import Message
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from loader import dp, bot
from loguru import logger


# @dp.message_handler(commands=['start'])
@logger.catch()
async def start(message: Message, state: FSMContext) -> None:
    await state.finish()
    try:
        await bot.send_message(message.from_user.id, f"Привет, {message.from_user.full_name}!")
        logger.info('Команда /start была вызвана.')
    except Exception as error:
        logger.exception(f'При вызове команды /start произошла ошибка, {error}')
        await message.reply('Общение с ботом через ЛС, напишите ему: \nhttps://t.me/Journey Hotels')


def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'], state='*')
