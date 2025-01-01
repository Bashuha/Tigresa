__all__ = ("router", )

from database.engine import DBFilter
from aiogram import Router, F
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from challenge.functions import check_word_form_message, make_set_row_keyboard, create_words_for_challenge
from  challenge.states import Challenge


router = Router()
DEFAULT_GEN_VALUE = "The end of your set"


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
    set_keyboard_dict: dict = await make_set_row_keyboard(
        session,
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
    set_name_id_dict = await state.get_data()
    set_id = set_name_id_dict.get(message.text)
    if not set_id:
        return await message.answer("Такого набора нет, надо выбрать из предложенного списка")
    # проверить сообщение
    await message.answer(
        text="Сейчас буду присылать слова, по очереди, секундочку...",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    challenge_dict, send_word = await create_words_for_challenge(session, set_id)
    await state.update_data(challenge_dict)
    await state.set_state(Challenge.enter_word)
    await message.answer(send_word)


@router.message(
    Challenge.enter_word,
    F.text,
)
async def check_incoming_word(
    message: types.Message,
    state: FSMContext,
):
    challenge_dict = await state.get_data()
    updated_dict, result_trigger = await check_word_form_message(
        challenge_dict=challenge_dict.copy(),
        message_text=message.text,
    )
    if not result_trigger:
        answer = ""
        for key, val in  updated_dict.get("dict_with_answers").items():
            answer += f"{key} - {val}\n"
            await state.clear()
        return await message.answer(answer)
    await state.update_data(updated_dict)
    await message.answer(updated_dict["sended_word"])