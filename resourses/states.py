from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    missing_playsers = State()
    host_selection = State()
    enter_remaining_balance = State()

