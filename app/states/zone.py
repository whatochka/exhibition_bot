from aiogram.fsm.state import StatesGroup, State


class ZoneCreate(StatesGroup):
    title = State()
    description = State()
    image = State()
    voice = State()


class ZoneEdit(StatesGroup):
    title = State()
    description = State()
    image = State()
    voice = State()
