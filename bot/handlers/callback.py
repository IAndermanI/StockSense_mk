from aiogram import Router
from aiogram.types import LabeledPrice
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.handlers import CallbackQueryHandler
from backend.lobby import *
from backend.player import get_player
from bot.keyboard import *
from bot.states import *

callback_router = Router()

@callback_router.callback_query()
class MyCallbackHandler(CallbackQueryHandler):
    def __init__(self, event, **kwargs):
        super().__init__(event, **kwargs)
        self.dispatcher = kwargs['dispatcher']

    async def handle(self):
        callback_data = self.callback_data
        message = self.message
        split_callback = callback_data.split('_')
        user_storage_key = StorageKey(self.bot.id, message.chat.id, message.chat.id)
        state = FSMContext(storage=self.dispatcher.storage, key=user_storage_key)

        if split_callback[0].isnumeric() and 100000 <= int(split_callback[0]) <= 999999:
            await self._start_round(int(split_callback[0]))
            await self._send_admin_panel(int(split_callback[0]))
        elif split_callback[0] == "buy":
            item_to_buy = split_callback[1].split(':')[0]
            await self._buy_item(item_to_buy, state)
        elif split_callback[0] == "admin":
            if split_callback[2] == "next":
                await self._start_new_round(int(split_callback[1]))
            elif split_callback[2] == "stop":
                pass

    async def _send_items_to_buy(self, lobby_code):
        items_to_pick = get_lobby(lobby_code).round.get_items_to_pick()
        for player_id in items_to_pick.keys():
            info_txt = f'Твой баланс: {get_player(player_id).check_inventory()}'
            await self.bot.send_message(
                chat_id=player_id,
                text=info_txt + "Выбери, что будешь покупать",
                reply_markup=build_inlineKB_from_list(
                    callback="buy",
                    items=[f"{item}: {items.get_price(item)}"
                           for item in items_to_pick[player_id]]
                )
            )

    async def _start_round(self, lobby_code):
        get_lobby(lobby_code).start_game()
        await self._send_items_to_buy(lobby_code)

    async def _send_admin_panel(self, lobby_code):
        await self.message.edit_text(
            text="Control keyboard",
            reply_markup=build_inlineKB_from_list(
                callback=f"admin_{lobby_code}",
                items=["stop", "next"]
            )
        )

    async def _buy_item(self, item_to_buy, state):
        await state.set_state(ROUND.BuyItem)
        get_player(self.message.chat.id).wants_to_buy = item_to_buy
        await self.message.edit_text("How much?")

    async def _start_new_round(self, lobby_code):
        get_lobby(lobby_code).round.start_new_round()
        await self._send_items_to_buy(lobby_code)
