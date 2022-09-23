from config_data.config import BOT_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


# инициализация состояния (storage для хранений пользователя внутри сценария)
storage = MemoryStorage()

# инициализация бота
bot = Bot(token=BOT_TOKEN)

# инициализация состояния (storage для хранений пользователя внутри сценария)
dp = Dispatcher(bot, storage=storage)
