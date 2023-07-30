from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

import os


storage = MemoryStorage()

bot = Bot(token=os.getenv('TOKEN_TELE'))
dp = Dispatcher(bot, storage=storage)
