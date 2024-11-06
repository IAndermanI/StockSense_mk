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
from bot.states import *
from config import config
from backend.lobby import *
from bot.keyboard import *
from backend.items import sceneries

commands_router = Router()

@commands_router.message(Command(commands=['start', 'create_lobby']))
class MyCommandsHandler(MessageHandler, MessageHandlerCommandMixin):
    def __init__(self, event: Message, **kwargs: Any):
        super().__init__(event, **kwargs)
        self.dispatcher = kwargs['dispatcher']

    async def handle(self):
        command = self.command.command
        message = self.event
        user_storage_key = StorageKey(self.bot.id, message.chat.id, message.chat.id)
        state = FSMContext(storage=self.dispatcher.storage, key=user_storage_key)

        if command == 'start':
            await self._handle_start(message, state)
        elif command == 'create_lobby':
            await self._handle_create_lobby(message)

    async def _handle_start(self, message, state):
        if message.from_user.id in config.admin_ids:
            await message.answer(f'Привет, создай лобби: /create_lobby')
        else:
            await message.answer(f'Привет, это игра Копилка. Дождись, пока учитель не назовет номер лобби, '
                                 f'а затем введи его')
            await state.set_state(JOIN.EnterCode)

    async def _handle_create_lobby(self, message):
        if message.from_user.id in config.admin_ids:
            new_lobby = get_lobby()
            await message.answer(f'Назови детям номер лобби: {new_lobby.lobby_code}',
                                 reply_markup=build_inlineKB_from_list(new_lobby.lobby_code, ['Начать',
                                                                                              'Смотреть участников',
                                                                                              'Выбрать сценарий']))
