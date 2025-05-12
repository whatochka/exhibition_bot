from aiogram.fsm.state import StatesGroup, State


class ItemCreate(StatesGroup):
    title = State()
    description = State()
    image = State()
    voice = State()
