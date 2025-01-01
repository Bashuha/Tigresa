from sqlalchemy.ext.asyncio import AsyncSession
import database.schemas as db_schema
from sqlalchemy import select
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from contextlib import asynccontextmanager


async def make_set_row_keyboard(
    session: AsyncSession,
    user_id: int,
) -> dict:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    set_query = await session.execute(
        select(db_schema.SetName.name, db_schema.SetName.id).
        where(db_schema.SetName.user_id == str(user_id))
    )
    set_name_id = set_query.all()
    await session.close()
    name_id_dict = {key:value for (key, value) in set_name_id}
    set_names = list(name_id_dict.keys())
    keyboard_rows = [[KeyboardButton(text=item)] for item in set_names]
    result_dict = {'reply_keyboard': ReplyKeyboardMarkup(keyboard=keyboard_rows), 'sets_dict': name_id_dict}
    return result_dict


async def create_words_for_challenge(session: AsyncSession, set_id: int) -> dict:
    word_query = await session.execute(
        select(db_schema.Word.first_word, db_schema.Word.second_word).
        where(db_schema.Word.set_id == set_id)
    )
    words = word_query.all()
    await session.close()
    words_dict = {word[0]:word[1] for word in words[1:]}
    # send_word, = list(words_dict.items())[0]
    send_word, correct_word = words[0]
    challenge_dict = {
        "correct_word": correct_word,
        "sended_word": send_word,
        "dict_with_answers": {},
    }
    challenge_dict["words_for_challenge"] = words_dict
    return challenge_dict, send_word


async def check_word_form_message(
    challenge_dict: dict,
    message_text: str,
) -> dict:
    dict_with_answers = challenge_dict.get("dict_with_answers")
    sended_word = challenge_dict["sended_word"]
    if challenge_dict["correct_word"] == message_text:
        dict_with_answers[sended_word] = 1
    else:
        dict_with_answers[sended_word] = f'**{challenge_dict["correct_word"]}**'
    words_for_challenge = challenge_dict.get("words_for_challenge")
    if not words_for_challenge:
        return challenge_dict, False
    send_word = list(words_for_challenge.items())[0][0]
    challenge_dict.update(
        sended_word=send_word,
        correct_word=words_for_challenge.pop(send_word),
        words_for_challenge=words_for_challenge,
    )
    challenge_dict["dict_with_answers"] = dict_with_answers
    return challenge_dict, True
    