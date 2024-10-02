import logging
from typing import Any
from aiogram.types import Message
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import Router
from datetime import datetime, timedelta
from aiogram.handlers import MessageHandler, MessageHandlerCommandMixin
from aiogram.fsm.storage.base import StorageKey
from backend.player import get_player
from bot.keyboard import build_inlineKB_from_list
from bot.states import *
from config import config
from backend.lobby import *

messages_router = Router()

@messages_router.message()
class MyMessageHandler(MessageHandler):
    def __init__(self, event, **kwargs):
        super().__init__(event, **kwargs)
        self.dispatcher = kwargs['dispatcher']

    async def handle(self):
        message = self.event
        user_storage_key = StorageKey(self.bot.id, message.chat.id, message.chat.id)
        state = FSMContext(storage=self.dispatcher.storage, key=user_storage_key)
        cur_state = await state.get_state()
        if cur_state == JOIN.EnterCode:
            await self._enter_code(message)
        elif cur_state == ROUND.BuyItem:
            await self._buy_item(message)

    async def _enter_code(self, message):
        if not message.text.isnumeric():
            await message.answer(f'Code is 6-digit integer. Try again!')
        elif int(message.text) in get_lobby.get_all_lobbies():
            get_lobby(int(message.text)).add_player(message.from_user.id)
            await message.answer(f'Successfully added. Now wait for the start')
        else:
            await message.answer(f'Mistake in the lobby code. Try again!')

    async def _buy_item(self, message):
        if not message.text.isnumeric():
            await message.answer(f'Введи число')
        else:
            buy_item = get_player(message.from_user.id).buy_item(
                get_player(message.from_user.id).wants_to_buy, int(message.text))
            if buy_item:
                await message.answer('Успешно куплено')
            else:
                await message.answer("Что-то пошло не так. Попробуй купить товар заново")
            await message.answer(text="Выбери, что будешь покупать",
                                 reply_markup=build_inlineKB_from_list(
                                    callback="buy",
                                    items=[f"{item}: {items.get_price(item)}"
                                           for item in get_player(message.chat.id).items_to_buy]
                                 ))
            get_player(message.from_user.id).wants_to_buy = None
