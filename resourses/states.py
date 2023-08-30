from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    missing_playsers = State()
    enter_remaining_balance = State()
    add_admin = State()
    delete_admin = State()
