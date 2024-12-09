from aiogram.filters.state import StatesGroup, State


class States(StatesGroup):
    wait_for_themes = State()
    wait_for_comfirm_themes = State()
    wait_for_deleting_theme = State()
    wait_for_suggest = State()
