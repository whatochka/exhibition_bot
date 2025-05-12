from aiogram.fsm.state import StatesGroup, State


class SubzoneCreate(StatesGroup):
    title = State()
    description = State()
    image = State()
    voice = State()


class SubzoneEdit(StatesGroup):
    title = State()
    description = State()
    image = State()
    voice = State()
