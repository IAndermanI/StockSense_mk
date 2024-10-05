from aiogram import Router
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
            lobby_code = int(split_callback[0])
            if split_callback[1] == 'Start':
                await self._start_round(lobby_code)
                await self._send_admin_panel(lobby_code)
            elif split_callback[1] == 'See players':
                await self._send_players_names(lobby_code)

        elif split_callback[0] == "buy":
            item_to_buy = split_callback[1].split(':')[0]
            await self._buy_item(item_to_buy, state)
        elif split_callback[0] == "admin":
            if split_callback[2] == "Следующий раунд":
                await self._start_new_round(int(split_callback[1]))
            elif split_callback[2] == "Смотреть игроков":
                await self._list_players(int(split_callback[1]))
        elif split_callback[0] == "checkinventory":
            await self._send_inventory()
        elif split_callback[0] == "back":
            await self._send_items_to_buy(self.message.chat.id, edit_text=True)
        elif split_callback[0] == "playerinfo":
            await self._get_player_info(int(split_callback[1]), split_callback[2])

    async def _send_items_to_buy(self, player_id, edit_text=False):
        items_to_pick = get_player(player_id).items_to_buy
        if edit_text:
            await self.message.edit_text(
                text="Выбери, что будешь покупать",
                reply_markup=build_inlineKB_from_list(
                    callback="buy",
                    items=[f"{item}: {items.get_price(item)}"
                           for item in items_to_pick],
                    return_markup=False
                ).button(text="Смотреть инвентарь",
                         callback_data="checkinventory").as_markup()
            )
        else:
            await self.bot.send_message(
                chat_id=player_id,
                text="Выбери, что будешь покупать",
                reply_markup=build_inlineKB_from_list(
                    callback="buy",
                    items=[f"{item}: {items.get_price(item)}"
                           for item in items_to_pick],
                    return_markup=False
                ).button(text="Смотреть инвентарь",
                         callback_data="checkinventory").as_markup()
            )

    async def _send_items_to_buy_everyone(self, lobby_code):
        items_to_pick = get_lobby(lobby_code).round.get_items_to_pick()
        for player_id in items_to_pick.keys():
            await self._send_items_to_buy(player_id)

    async def _start_round(self, lobby_code):
        get_lobby(lobby_code).start_game()
        await self._send_items_to_buy_everyone(lobby_code)

    async def _send_admin_panel(self, lobby_code):
        await self.message.answer(
            text="Control keyboard",
            reply_markup=build_inlineKB_from_list(
                callback=f"admin_{lobby_code}",
                items=["Смотреть игроков", "Следующий раунд"]
            )
        )

    async def _send_players_names(self, lobby_code):
        player_ids = get_lobby(lobby_code).player_ids
        players_names = ""
        for i, player_id in enumerate(player_ids, start=1):
            players_names += f"{i}: @{get_player(player_id).username}\n"
        if players_names == "":
            await self.message.answer("Никто еще не присоединился :(")
        else:
            await self.message.answer(players_names)

    async def _buy_item(self, item_to_buy, state):
        await state.set_state(ROUND.BuyItem)
        get_player(self.message.chat.id).wants_to_buy = item_to_buy
        await self.message.edit_text("Сколько?")

    async def _start_new_round(self, lobby_code):
        if get_lobby(lobby_code).round.round_number > 1:
            await self._get_best_players(lobby_code)
        get_lobby(lobby_code).round.start_new_round()
        await self._send_items_to_buy_everyone(lobby_code)

    async def _get_best_players(self, lobby_code):
        top_players = get_lobby(lobby_code).round.get_top_players()
        top_players_message = "Лучшие игроки по стоимости владений:\n"
        for i in range(min(3, len(top_players))):
            top_players_message += f"{i+1}. @{top_players[i]}"

        for player_id in get_lobby(lobby_code).player_ids:
            await self.bot.send_message(
                chat_id=player_id,
                text=top_players_message
            )

    async def _send_inventory(self):
        await self.message.edit_text(
            text=get_player(self.message.chat.id).check_inventory(),
            reply_markup=build_inlineKB_from_list(
                callback="back",
                items=["Назад к покупкам"]
            )
        )

    async def _list_players(self, lobby_code):
        player_ids = get_lobby(lobby_code).player_ids
        player_usernames = [get_player(player_id).username for player_id in player_ids]
        await self.message.edit_text(
            text="Про кого?",
            reply_markup=build_inlineKB_from_list(
                callback=f"playerinfo_{lobby_code}",
                items=player_usernames
            )
        )

    async def _get_player_info(self, lobby_code, player_username):
        player_ids = get_lobby(lobby_code).player_ids
        for player_id in player_ids:
            if get_player(player_id).username == player_username:
                await self.message.edit_text(f"Все про {player_username}:\n"
                                             f"{get_player(player_id).check_inventory()}")
                await self._send_admin_panel(lobby_code)
