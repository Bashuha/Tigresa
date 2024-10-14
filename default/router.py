__all__ = ("router", )

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram import types


router = Router()


@router.message(CommandStart())
async def handle_start_command(message: types.Message):
    await message.answer(
        text="""
Этот бот принимает CSV-файлы и проверяет их структуру.
Команды:
/start - показать эту информацию
<документ> - отправить документ для проверки
"""
    )


@router.message(Command("help"))
async def handle_help(message: types.Message):
    text = """
I'am helping you to learn your words or sentences
And I save your words for you
And I can ask you about them, probably..
"""
    await message.answer(text=text)