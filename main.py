import asyncio
from typing import Any, Dict, Optional, Union

from sqlalchemy import insert, select
from config import TOKEN
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command, Filter
import csv
from database.engine import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import database.schemas as db_schema


async def check_csv(
    message: types.Message,
    session: AsyncSession,
):
    tg_user_id = message.from_user.id
    file_id = message.document.file_id
    file_data = await bot.get_file(file_id)
    file_path = file_data.file_path
    await bot.download_file(file_path, "temp.csv")
    
    if message.document.mime_type != 'text/csv':
        await message.reply("Некорректный формат файла! Поддерживается только CSV.")
        return
    
    csv_value = list()
    with open('temp.csv', newline='') as csvfile:
        word_reader = csv.reader(
            csvfile,
            # delimiter='',
            # quotechar='|'
        )
        for row in word_reader:
            csv_value.append(row)

    check_user = await session.execute(
        select(db_schema.User.id).
        where(db_schema.User.tg_id == tg_user_id)
    )
    user_id = check_user.scalar_one_or_none()
    if not user_id:
        insert_user = await session.execute(
            insert(db_schema.User).
            values(tg_id=tg_user_id)
        )
        user_id = insert_user.inserted_primary_key[0]
        await session.commit()

    insert_set_name = await session.execute(
        insert(db_schema.SetName).
        values(
            name='test_csv',
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
    
    await message.reply("CSV успешно проверен!")


bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def handle_start_command(message: types.Message):
    await message.answer(
        text="""
Этот бот принимает CSV-файлы и проверяет их структуру.
Команды:
/start - показать эту информацию
<документ> - отправить документ для проверки
"""
    )


@dp.message(Command("help"))
async def handle_help(message: types.Message):
    text = """
I'am helping you to learn your words or sentences
And I save your words for you
And I can ask you about them, probably..
"""
    await message.answer(text=text)


from aiogram.types import Message, User

class HelloFilter(Filter):
    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name

    async def __call__(
        self,
        message: Message,
        event_from_user: User,
        # Filters also can accept keyword parameters like in handlers
    ) -> Union[bool, Dict[str, Any]]:
        if message.text.casefold() == "hello":
            # Returning a dictionary that will update the context data
            return {"name": event_from_user.mention_html(name=self.name)}
        return False


# @dp.message(HelloFilter())
# async def my_handler(
#     message: Message, name: str  # Now we can accept "name" as named parameter
# ) -> Any:
#     return message.answer("Hello, {name}!".format(name=name))



class DBFilter(Filter):
    def __init__(
        self,
        session: AsyncSession = get_db,
    ):
        self.session = session

    async def __call__(
        self,
        message: types.Message,
    ):
        if message.document:
            conn = [db async for db in self.session()][0]
            return {"session":conn}
        return False


@dp.message(DBFilter())
async def handle_file(
    message: types.Message,
    session: AsyncSession,
):
    await check_csv(message, session)


if __name__ == "__main__":
    # asyncio.run(db_schema.init_models())
    asyncio.run(dp.start_polling(bot))