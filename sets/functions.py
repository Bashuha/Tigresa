import csv
from sqlalchemy.ext.asyncio import AsyncSession
import database.schemas as db_schema
from sqlalchemy import insert, select
from aiogram import types
from database.engine import bot
from aiogram.fsm.state import  StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def make_row_keyboard(
    session: AsyncSession,
    items: list[str],
    user_id: int,
) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    # переделать так, чтобы список кнопок был бесконечный
    # и их можно было листать
    set_query = await session.execute(
        select(db_schema.SetName.name, db_schema.SetName.id).
        where(db_schema.SetName.user_id == 1)
    )
    set_name_id = set_query.all()
    await session.close()
    id_name_dict = {key:value for (key, value) in set_name_id}
    # map(lambda set_value: id_name_dict.update({set_value.name: set_value.id}), set_name_id)
    # upd_dict = lambda set_value: id_name_dict.update({set_value.name: set_value.id})
    # for i in set_name_id:
        # upd_dict(i)
    set_names = list(id_name_dict.keys())
    set_names.append("12345")
    set_names.extend(['11111111111', '11111111111' ,'11111111111', '11111111111', '11111111111', '11111111111', '11111111111', '11111111111'])
    # row = [KeyboardButton(text=item) for item in items]
    row = [KeyboardButton(text=item) for item in set_names]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


async def check_csv(
    # document: types.Message,
    message: types.Message,
    session: AsyncSession,
):
    # потом проверим и добавим (если надо) пользователя
    # tg_user_id = document.from_user.id
    tg_user_id = str(message.from_user.id)
    check_user = await session.execute(
        select(db_schema.User.id).
        where(db_schema.User.tg_id == tg_user_id)
    )
    # user_id = check_user.one_or_none()
    user_id = check_user.scalar_one_or_none()
    if not user_id:
        insert_user = await session.execute(
            insert(db_schema.User).
            values(tg_id=tg_user_id)
        )
        user_id = insert_user.inserted_primary_key[0]
        await session.commit()

    # проверить существование сета с текущим названием
    file_name = message.document.file_name[:-4]
    check_set_name_query = await session.execute(
        select(db_schema.SetName.id).
        where(
            db_schema.SetName.name == file_name,
            db_schema.SetName.user_id == user_id
        )
    )
    check_set_name = check_set_name_query.scalar_one_or_none()
    if check_set_name:
        await message.reply("У вас уже есть набор слов с таким названием")
        # await bot.send_message(
        #     chat_id=tg_user_id,
        #     text='У вас уже есть набор слов с таким названием',
        # )
        return
    
    # дальше обработаем данные файла
    file_id = message.document.file_id
    # file_id = document.file_id
    file_data = await bot.get_file(file_id)
    file_path = file_data.file_path
    await bot.download_file(file_path, "temp.csv")
    csv_value = list()
    with open('temp.csv', newline='') as csvfile:
        word_reader = csv.reader(
            csvfile,
            # delimiter='',
            # quotechar='|'
        )
        for row in word_reader:
            csv_value.append(row)


    insert_set_name = await session.execute(
        insert(db_schema.SetName).
        values(
            name=file_name,
            user_id=user_id,
        )
    )
    await session.commit()
    set_id = insert_set_name.inserted_primary_key
    insert_word = [
        {
            'first_word': word[0],
            'second_word': word[1],
            'set_id': set_id[0],
        }
        for word in csv_value
    ]

    await session.execute(
        insert(db_schema.Word).
        values(insert_word)
    )
    await session.commit()
    await session.close()
    
    await message.reply("CSV успешно проверен!")
    # await bot.send_message(
    #     chat_id=tg_user_id,
    #     text='CSV успешно проверен!',
    # )


class Challenge(StatesGroup):
    choose_set = State()
    enter_word = State()


class SendCSV(StatesGroup):
    sending_csv = State()
