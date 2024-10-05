from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers import *
from config import config

BOT_TOKEN = config.bot_token

storage = MemoryStorage()
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=storage)

MyCallbackHandler(callback_router, dispatcher=dp, bot=bot)
MyMessageHandler(messages_router, dispatcher=dp, bot=bot)
MyCommandsHandler(commands_router, dispatcher=dp, bot=bot)
dp.include_routers(commands_router, messages_router, callback_router)

if __name__ == '__main__':
    dp.run_polling(bot)
