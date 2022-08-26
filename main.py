from aiogram import Bot, Dispatcher, executor
import config
import logging
import requests
from aiogram import types
import handlers
import bot_redis
import information_API.hotels
import information_API.locations
import check.checking
# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализация бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

async def on_startup(_):
    print('\n=== Телеграм-бот вышел в онлайн ===')


# Хэндлер на команду /hello-world
@dp.message_handler(commands=["hello-world"])
async def hello_world(message: types.Message):
    # if not is_user_in_db(message):
    #     add_user(message)
    # logging.info(f'Команда "/hello-world" была вызвана')
    await message.answer('Привет, это бот для поиска отелей!\nНапиши "/help" и познакомлю Вас с моими командами')


# Хэндлер на команду /help
@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    # if not is_user_in_db(message):
    #     add_user(message)
    # logging.info(f'Команда "/help" была вызвана')
    await message.answer(
        '\n/lowprice — вывод самых дешёвых отелей в городе'
        '\n/highprice — вывод самых дорогих отелей в городе'
        '\n/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра'
        '\n/history — вывод истории поиска отелей')

# Хэндлер на сообщение приветствия
@dp.message_handler(content_types=['text'])
async def hello(message: types.Message):
    if message.text == 'Привет, Journey Hotels':
        await message.answer('Привет, это бот для поиска отелей!\nНапиши "/help" и познакомлю с моими командами')
    else:
        await message.answer('Привет, к сожалению, не понял запрос!\nНапиши "/help" и познакомлю с моими командами')

# запускаем лонг поллинг
if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)  # ответ бота только когда онлайн
    except Exception as error:
        logging.error(f'Возникла ошибка: {error}')

