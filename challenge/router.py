__all__ = ("router", )

from database.engine import DBFilter
from aiogram import Router, F
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from challenge.functions import check_word_form_message, make_row_keyboard, create_words_for_challenge, word_sender
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
    set_keyboard_dict: dict = await make_row_keyboard(
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
    # разобраться с async_generator, не работает пока        
    words = await create_words_for_challenge(session, set_id)
    first_word_pair = list(words.items())[0]
    # current_words_pair = {first_word_pair[0]}
    challenge_dict = {"words_for_challenge": words, "current_words_pair": None}
    first_word = await anext(word_sender(words), DEFAULT_GEN_VALUE)
    challenge_dict["current_word"] = first_word
    # await state.set_state(Challenge.enter_word)
    await state.update_data(challenge_dict)
    await state.set_state(Challenge.enter_word)
    await message.answer(first_word)


@router.message(
    Challenge.enter_word,
    F.text,
)
async def check_incoming_word(
    message: types.Message,
    state: FSMContext,
):
    challenge_dict = await state.get_data()
    updated_dict = await check_word_form_message(
        challenge_dict=challenge_dict.copy(),
        message_text=message.text,
    )
    updated_dict['current_word'] = await anext(
        word_sender(), DEFAULT_GEN_VALUE)
    await state.update_data(challenge_dict)