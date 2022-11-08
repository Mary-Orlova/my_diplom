from loader import dp
from loguru import logger
from aiogram import executor
from utils.set_bot_commands import set_default_commands
# импорт файлов для их дальнейшей регистрации (хэндлеры)
from handlers.default_heandlers import start, help, hello_world, lowprice, highprice, bestdeal, history, echo

# задаем уровень логов
logger.add('debug.log', format='{time} {level} {message}', level='INFO', rotation='1000KB', compression='zip')


# уведомление в терминал при успешном запуске бота + подгружает все команды
@logger.catch()
async def on_startup(_):
    print('\n=== Телеграм-бот вышел в онлайн ===')
    start.register_handlers_start(dp)
    help.register_handlers_help(dp)
    hello_world.register_handlers_hello_world(dp)
    lowprice.register_handlers_lowprice(dp)
    highprice.register_handlers_highprice(dp)
    bestdeal.register_handlers_bestdeal(dp)
    history.register_handlers_history(dp)
    echo.register_handlers_echo(dp)
    await set_default_commands(dp)


@logger.catch()
async def on_shutdown(_):
    await dp.storage.close()
    await dp.storage.wait_closed()


# запускаем лонг поллинг
if __name__ == '__main__':
    try:
        executor.start_polling(dispatcher=dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
        # ответ бота только когда онлайн
    except Exception as error:
        logger.exception(f'Возникла ошибка при попытке запустить бота.', {error})
