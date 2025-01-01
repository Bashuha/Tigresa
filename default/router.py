__all__ = ("router", )

from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram import types


router = Router()


@router.message(CommandStart())
async def handle_start_command(message: types.Message):
    await message.answer(
        text="""
Привет! Этот бот хранит наборы ваших слов.
Вы можете прислать мне CSV-файл с двумя столбцами,
в первом то, что надо перевести, во втором перевод.
Я сохраню этот набор и когда вы попросите, проверю ваши
знания по любому из выбранных наборов!
Все мои рабочие команды должны быть в меню.
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


@router.message(Command("stop"))
async def clear_context(
    message: types.Message,
    state: FSMContext,
):
    await state.clear()
    await message.answer(text="Мы вернулись в начало")