from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    Missing_playsers = State()
    Host_selection = State()
    All_players_attended = State()
    On_game = State()

