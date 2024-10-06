from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.handlers import MessageHandler
from aiogram.fsm.storage.base import StorageKey
from backend.player import get_player
from bot.keyboard import build_inlineKB_from_list
from bot.states import *
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
        elif cur_state == ROUND.Deposit:
            await self._buy_item(message, is_deposit=True)
        elif cur_state == ROUND.SellItem:
            await self._sell_item(message)

    async def _enter_code(self, message):
        if not message.text.isnumeric():
            await message.answer(f'Код - строка из 6 цифр. Попробуй снова!')
        elif int(message.text) in get_lobby.get_all_lobbies():
            get_player(message.from_user.id)
            get_player(message.from_user.id).username = message.from_user.username
            get_lobby(int(message.text)).add_player(message.from_user.id)
            await message.answer(f'Успешно добавили в лобби. Теперь жди начала')
        else:
            await message.answer(f'Ошибка при подключении к лобби. Попробуй снова!')

    async def _buy_item(self, message, is_deposit=False):
        if not message.text.isnumeric():
            await message.answer(f'Введи целое положительное число')
        else:
            successful = False
            if is_deposit:
                successful = get_player(message.from_user.id).deposit(int(message.text))
            else:
                successful = get_player(message.from_user.id).buy_item(
                    get_player(message.from_user.id).wants_to_buy, int(message.text))
            if successful:
                await message.answer('Успешно куплено')
            else:
                await message.answer("Что-то пошло не так. Попробуй заново")

            if items.round_number == 1:
                await message.answer(text="Выбери, что будешь покупать",
                                     reply_markup=build_inlineKB_from_list(
                                      callback="buy",
                                      items=[f"{item}: {items.get_price(item)}"
                                             for item in get_player(message.from_user.id).items_to_buy],
                                      return_markup=False
                                       ).button(
                                       text="Вклад: 10%", callback_data="deposit").button(
                                       text="Cмотреть инвентарь", callback_data="checkinventory").adjust(2).as_markup()
                                     )
            else:
                await message.answer(
                    text="Что хочешь сделать?",
                    reply_markup=build_inlineKB_from_list(
                        callback="options",
                        items=["Купить", "Продать", "Смотреть инвентарь"]
                    )
                )

            get_player(message.from_user.id).wants_to_buy = None

    async def _sell_item(self, message):
        if not message.text.isnumeric():
            await message.answer(f'Введи число')
        if not float(message.text).is_integer():
            await message.answer(f'Введи целое число')
        else:
            sell_item = get_player(message.from_user.id).sell_item(
                get_player(message.from_user.id).wants_to_sell, int(message.text))
            if sell_item:
                await message.answer('Успешно продано')
            else:
                await message.answer("Что-то пошло не так. Попробуй заново")

            await message.answer(
                text="Что хочешь сделать?",
                reply_markup=build_inlineKB_from_list(
                    callback="options",
                    items=["Купить", "Продать", "Смотреть инвентарь"]
                )
            )

            get_player(message.from_user.id).wants_to_sell = None
