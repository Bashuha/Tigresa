from aiogram.fsm.state import  StatesGroup, State


class Challenge(StatesGroup):
    choose_set = State()
    enter_word = State()