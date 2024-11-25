import csv
from sqlalchemy.ext.asyncio import AsyncSession
import database.schemas as db_schema
from sqlalchemy import insert, select
from aiogram import types
from database.engine import bot


async def check_csv(
    # document: types.Message,
    message: types.Message,
    session: AsyncSession,
):
    tg_user_id = str(message.from_user.id)
    # проверить существование сета с текущим названием
    file_name = message.document.file_name[:-4]
    check_set_name_query = await session.execute(
        select(db_schema.SetName.id).
        where(
            db_schema.SetName.name == file_name,
            db_schema.SetName.user_id == tg_user_id
        )
    )
    check_set_name = check_set_name_query.scalar_one_or_none()
    if check_set_name:
        await message.reply("У вас уже есть набор слов с таким названием")
        return
    
    # дальше обработаем данные файла
    file_id = message.document.file_id
    file_data = await bot.get_file(file_id)
    file_path = file_data.file_path
    await bot.download_file(file_path, "temp.csv")

    insert_set_name = await session.execute(
        insert(db_schema.SetName).
        values(
            name=file_name,
            user_id=tg_user_id,
        )
    )
    await session.commit()
    set_id = insert_set_name.inserted_primary_key
    csv_value = list()
    with open('temp.csv', newline='') as csvfile:
        word_reader = csv.reader(
            csvfile,
            # delimiter='',
            # quotechar='|'
        )
        for row in word_reader:
            csv_value.append(
                {
                    'first_word': row[0],
                    'second_word': row[1],
                    'set_id': set_id[0],
                }
            )
    await session.execute(
        insert(db_schema.Word).
        values(csv_value)
    )
    await session.commit()
    await session.close()
    await message.reply("CSV успешно проверен!")
