from aiogram.fsm.state import StatesGroup, State

class JOIN(StatesGroup):
    EnterCode = State()
    Added = State()

class ROUND(StatesGroup):
    BuyItem = State()

class ROUNDS(StatesGroup):
    Round1 = State()
    AddStocks = State()
    DeleteStock = State()
    StockNews = State()
    AddedStocks = State()

class FIELDS(StatesGroup):
    Fields = State()
    AddField = State()
    DeleteField = State()
