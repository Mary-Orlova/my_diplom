from aiogram.types import BotCommand
from config_data.config import DEFAULT_COMMANDS
from loader import dp, bot
from loguru import logger
from aiogram import Dispatcher


@logger.catch()
async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands(
        [BotCommand(*command) for command in DEFAULT_COMMANDS]
    )
