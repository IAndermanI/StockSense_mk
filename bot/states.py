from aiogram.fsm.state import StatesGroup, State

class JOIN(StatesGroup):
    EnterCode = State()
    Added = State()

class ROUND(StatesGroup):
    BuyItem = State()
    SellItem = State()
    Deposit = State()
