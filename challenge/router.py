__all__ = ("router", )

from database.engine import DBFilter
from aiogram import Router, F
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from challenge.functions import make_row_keyboard
from  challenge.states import Challenge


router = Router()


@router.message(
    StateFilter(None),
    Command('challenge'),
    DBFilter(),
)
async def start_challenge(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    # здесь будет запрос на получение сетов пользователя
    user_sets = ["1","2","3","4"]
    set_keyboard_dict: dict = await make_row_keyboard(
        session,
        user_sets,
        message.from_user.id,
    )
    await message.answer(
        text="Выберите, из какого набора сделать тест",
        reply_markup=set_keyboard_dict.get('reply_keyboard')
    )
    await state.set_state(Challenge.choose_set)
    await state.set_data(set_keyboard_dict.get('sets_dict'))
    # await state.clear()


@router.message(
    Challenge.choose_set,
    F.text,
    DBFilter(),
)
async def generate_challenge(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession,
):
    # проверить сообщение
    await message.answer(
        text="Сейчас буду присылать слова, по очереди, секундочку...",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    # поискать навазние сета тут и найти от него id
    set_name_id_dict = state.get_data()
    set_id = set_name_id_dict[message]
    await state.set_state(Challenge.enter_word)

    await message.answer()