from aiogram.fsm.state import StatesGroup, State


class ZoneCreate(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_image = State()
    waiting_for_voice = State()
