from aiogram.fsm.state import  StatesGroup, State


class SetManager(StatesGroup):
    sending_csv = State()
    del_set = State()