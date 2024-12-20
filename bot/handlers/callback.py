from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.handlers import CallbackQueryHandler
from backend.lobby import *
from backend.items import *
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
        print(f'Callback data: {callback_data}')
        message = self.message
        split_callback = callback_data.split('_')
        user_storage_key = StorageKey(self.bot.id, message.chat.id, message.chat.id)
        state = FSMContext(storage=self.dispatcher.storage, key=user_storage_key)

        if split_callback[0].isnumeric() and 100000 <= int(split_callback[0]) <= 999999:
            lobby_code = int(split_callback[0])
            if split_callback[1] == 'Начать':
                await self._start_game(lobby_code)
                await self._send_admin_panel(lobby_code)
            elif split_callback[1] == 'Смотреть участников':
                await self._send_players_names(lobby_code)
            elif split_callback[1] == 'Выбрать сценарий':
                await self._send_choose_scenery(lobby_code, message)
        elif split_callback[0] == "scenery":
            await self._set_scenery(int(split_callback[1]), split_callback[2])
        elif split_callback[0] == "options":
            if split_callback[2] == "Купить":
                await self._send_items_to_buy(int(split_callback[1]), self.message.chat.id, edit_text=True)
            elif split_callback[2] == "Продать":
                await self._send_items_to_sell(int(split_callback[1]), self.message.chat.id, edit_text=True)
            elif split_callback[2] == "Смотреть инвентарь":
                await self._send_inventory(int(split_callback[1]), "options")
        elif split_callback[0] == "buy":
            item_to_buy = split_callback[2].split(':')[0]
            await self._buy_item(int(split_callback[1]), item_to_buy, state)
        elif split_callback[0] == "sell":
            item_to_sell = split_callback[2].split(':')[0]
            await self._sell_item(int(split_callback[1]), item_to_sell, state)
        elif split_callback[0] == "admin":
            if split_callback[2] == "Следующий раунд":
                await self._start_new_round(int(split_callback[1]))
                await self._send_admin_panel(int(split_callback[1]), True)
            elif split_callback[2] == "Завершить игру":
                await self._end_game(int(split_callback[1]))
            elif split_callback[2] == "Смотреть игроков":
                await self._list_players(int(split_callback[1]))
        elif split_callback[0] == "back":
            if split_callback[2] == "options":
                await self._send_options_kb(int(split_callback[1]), self.message.chat.id, edit_text=True)
            elif split_callback[2] == "buy":
                await self._send_items_to_buy(int(split_callback[1]), self.message.chat.id, edit_text=True)
        elif split_callback[0] == "checkinventory":
            await self._send_inventory(int(split_callback[1]), "buy")
        elif split_callback[0] == "playerinfo":
            await self._get_player_info(int(split_callback[1]), split_callback[2])
        elif split_callback[0] == "deposit":
            await self._buy_item(int(split_callback[1]), "deposit", state)
        

    async def _set_scenery(self, lobby_code, scenery_name):
        await self.message.delete()
        get_items(lobby_code).set_scenery(scenery_name)

    async def _send_items_to_buy(self, lobby_code, player_id, edit_text=False):
        items_to_pick = get_player(player_id).items_to_buy
        reply_markup = build_inlineKB_from_list(
                        callback=f"buy_{lobby_code}",
                        items=[f"{item}: {get_items(lobby_code).get_price(item)}"
                               for item in items_to_pick],
                        return_markup=False
                       ).button(text="Вклад: 10%",
                                callback_data=f"deposit_{lobby_code}")
        if get_items(lobby_code).round_number == 1:
            reply_markup = reply_markup.button(text="Смотреть инвентарь",
                                               callback_data=f"checkinventory_{lobby_code}")
        reply_markup = reply_markup.adjust(2).as_markup()
        if edit_text:
            await self.message.edit_text(
                text="Выбери, что будешь покупать",
                reply_markup=reply_markup
            )
        else:
            await self.bot.send_message(
                chat_id=player_id,
                text="Выбери, что будешь покупать",
                reply_markup=reply_markup
            )

    async def _send_items_to_sell(self, lobby_code, player_id, edit_text=False):
        items_to_sell = list(get_player(player_id).inventory.keys())
        if edit_text:
            await self.message.edit_text(
                text="Выбери, что хочешь продать",
                reply_markup=build_inlineKB_from_list(
                    callback=f"sell_{lobby_code}",
                    items=[f"{item}: {get_items(lobby_code).get_price(item, False)}"
                           for item in items_to_sell]
                )
            )
        else:
            await self.bot.send_message(
                chat_id=player_id,
                text="Выбери, что хочешь продать",
                reply_markup=build_inlineKB_from_list(
                    callback=f"sell_{lobby_code}",
                    items=[f"{item}: {get_items(lobby_code).get_price(item, False)}"
                           for item in items_to_sell]
                )
            )

    async def _send_options_kb(self, lobby_code, player_id, edit_text=False):
        if edit_text:
            await self.message.edit_text(
                text="Что хочешь сделать?",
                reply_markup=build_inlineKB_from_list(
                    callback=f"options_{lobby_code}",
                    items=["Купить", "Продать", "Смотреть инвентарь"]
                )
            )
        else:
            await self.bot.send_message(
                chat_id=player_id,
                text="Что хочешь сделать?",
                reply_markup=build_inlineKB_from_list(
                    callback=f"options_{lobby_code}",
                    items=["Купить", "Продать", "Смотреть инвентарь"]
                )
            )

    async def _send_items_to_buy_everyone(self, lobby_code):
        items_to_pick = get_lobby(lobby_code).round.get_items_to_pick()
        for player_id in items_to_pick.keys():
            await self._send_items_to_buy(lobby_code, player_id)

    async def _send_options_kb_to_everyone(self, lobby_code):
        items_to_pick = get_lobby(lobby_code).round.get_items_to_pick()
        for player_id in items_to_pick.keys():
            await self._send_options_kb(lobby_code, player_id)

    async def _send_choose_scenery(self, lobby_code, message):
        await message.answer(f'Выбери сценарий',
                                reply_markup=build_inlineKB_from_list(f'scenery_{lobby_code}', sceneries))

    async def _start_game(self, lobby_code):
        get_lobby(lobby_code).start_game()
        await self._send_items_to_buy_everyone(lobby_code)

    async def _send_admin_panel(self, lobby_code, to_change=False):
        next_round_text = "Следующий раунд" if get_lobby(lobby_code).round.round_number < get_items(lobby_code).max_rounds else "Завершить игру"
        if to_change:
            await self.message.edit_text(
                text=f"Панель управления. Раунд №{get_lobby(lobby_code).round.round_number}",
                reply_markup=build_inlineKB_from_list(
                    callback=f"admin_{lobby_code}",
                    items=["Смотреть игроков", next_round_text]
                )
            )
        else:
            await self.message.answer(
                text=f"Панель управления. Раунд №{get_lobby(lobby_code).round.round_number}",
                reply_markup=build_inlineKB_from_list(
                    callback=f"admin_{lobby_code}",
                    items=["Смотреть игроков", next_round_text]
                )
            )

    async def _send_players_names(self, lobby_code):
        player_ids = get_lobby(lobby_code).player_ids
        players_names = ""
        for i, player_id in enumerate(player_ids, start=1):
            players_names += f"{i}: {get_player(player_id).username}\n"
        if players_names == "":
            await self.message.answer("Никто еще не присоединился :(")
        else:
            await self.message.answer(players_names)

    async def _buy_item(self, lobby_code, item_to_buy, state):
        if item_to_buy == "deposit":
            await state.set_state(ROUND.Deposit)
        else:
            await state.set_state(ROUND.BuyItem)
            get_player(self.message.chat.id).wants_to_buy = item_to_buy
        await self.message.edit_text("Сколько?")

    async def _sell_item(self, lobby_code, item_to_sell, state):
        await state.set_state(ROUND.SellItem)
        get_player(self.message.chat.id).wants_to_sell = item_to_sell
        await self.message.edit_text("Сколько?")

    async def _start_new_round(self, lobby_code):
        await self._get_best_players(lobby_code)
        get_lobby(lobby_code).round.start_new_round()
        await self._send_options_kb_to_everyone(lobby_code)

    async def _end_game(self, lobby_code):
        top_players = get_lobby(lobby_code).round.get_top_players()
        final_message = f"Поздравляем, вы прошли наш мастеркласс! Надеемся, вы многому научились.\nФинальный топ игроков:\n"
        for i in range(len(top_players)):
            final_message += f"{i+1}. {top_players[i]}"

        for player_id in get_lobby(lobby_code).player_ids:
            await self.bot.send_message(
                chat_id=player_id,
                text=final_message
            )
    
    async def _get_best_players(self, lobby_code):
        top_players = get_lobby(lobby_code).round.get_top_players()
        top_players_message = "Лучшие игроки по стоимости владений:\n"
        for i in range(min(3, len(top_players))):
            top_players_message += f"{i+1}. {top_players[i]}"

        for player_id in get_lobby(lobby_code).player_ids:
            await self.bot.send_message(
                chat_id=player_id,
                text=top_players_message
            )

    async def _send_inventory(self, lobby_code, back_to):
        await self.message.edit_text(
            text=get_player(self.message.chat.id).check_inventory(),
            reply_markup=build_inlineKB_from_list(
                callback=f"back_{lobby_code}_{back_to}",
                items=["Назад"]
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
