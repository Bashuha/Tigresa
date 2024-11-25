from sqlalchemy.ext.asyncio import AsyncSession
import database.schemas as db_schema
from sqlalchemy import select
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from contextlib import asynccontextmanager


async def make_row_keyboard(
    session: AsyncSession,
    user_id: int,
) -> ReplyKeyboardMarkup:
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
    # map(lambda set_value: id_name_dict.update({set_value.name: set_value.id}), set_name_id)
    # upd_dict = lambda set_value: id_name_dict.update({set_value.name: set_value.id})
    # for i in set_name_id:
        # upd_dict(i)
    set_names = list(name_id_dict.keys())
    keyboard_rows = [[KeyboardButton(text=item)] for item in set_names]
    result_dict = {'reply_keyboard': ReplyKeyboardMarkup(keyboard=keyboard_rows), 'sets_dict': name_id_dict}
    return result_dict


async def create_words_for_challenge(session: AsyncSession, set_id: int):
    word_query = await session.execute(
        select(db_schema.Word.first_word, db_schema.Word.second_word).
        where(db_schema.Word.set_id == set_id)
    )
    words = word_query.all()
    words_dict = {word[0]:word[1] for word in words}
    return words_dict


# @asynccontextmanager
async def word_sender(words_dict: dict):
    for word in words_dict.values():
        yield word
    