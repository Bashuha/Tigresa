from aiogram.fsm.state import  StatesGroup, State


class SendCSV(StatesGroup):
    sending_csv = State()