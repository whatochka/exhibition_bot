from aiogram.fsm.state import State, StatesGroup


class PromoteAdmin(StatesGroup):
    waiting_for_user_id = State()
