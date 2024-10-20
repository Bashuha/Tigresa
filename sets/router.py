__all__ = ("router", )

# from magic_filter import F
from database.engine import DBFilter
from aiogram import Router, F
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from sets.functions import check_csv
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sets.functions import Challenge, SendCSV
from sets.functions import make_row_keyboard


router = Router()


@router.message(
    SendCSV.sending_csv,
    F.document.mime_type == 'text/csv',
    DBFilter(),
)
async def handle_file(
    # document,
    message: types.Message,
    session: AsyncSession,
    state: FSMContext,
):
    await check_csv(
        # document,
        message,
        session
    )
    await state.clear()


@router.message(StateFilter(None), Command('add_set'))
async def handle_add_set_command(
    message: types.Message,
    state: FSMContext,
):
    await message.answer(
        text='Отправьте мне CSV файл с вашими словами'
    )
    await state.set_state(SendCSV.sending_csv)


@router.message(SendCSV.sending_csv)
async def incorrect_message_sended(message: types.Message):
    await message.answer(
        text="Мне кроме CSV ничего не надо сейчас, попробуйте еще разок"
    )


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
    await message.answer(
        text="Выберите, из какого набора сделать тест",
        reply_markup=await make_row_keyboard(
            session,
            user_sets,
            message.from_user.id,
        )
    )
    await state.set_state(Challenge.choose_set)
    await state.clear()
