__all__ = ("router", )

from database.engine import DBFilter
from aiogram import Router, F
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from sets.functions import check_csv, delete_set
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sets.states import SetManager
from challenge.functions import make_set_row_keyboard


router = Router()


@router.message(
    SetManager.sending_csv,
    F.document.mime_type == 'text/csv',
    DBFilter(),
)
async def handle_file(
    message: types.Message,
    session: AsyncSession,
    state: FSMContext,
):
    await check_csv(
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
    await state.set_state(SetManager.sending_csv)


@router.message(SetManager.sending_csv)
async def incorrect_message_sended(message: types.Message):
    await message.answer(
        text="Мне кроме CSV ничего не надо сейчас, попробуйте еще разок"
    )


@router.message(
    Command('del_set'),
    StateFilter(None),
    DBFilter(),
)
async def handle_del_set_command(
    session: AsyncSession,
    message: types.Message,
    state: FSMContext,
):
    kbrd_set_dict = await make_set_row_keyboard(
        session,
        message.from_user.id,
    )
    await message.answer(
        text='Выберите набор, который хотите удалить',
        reply_markup=kbrd_set_dict.get('reply_keyboard'), 
    )
    await state.set_state(SetManager.del_set)
    await state.set_data(kbrd_set_dict.get('sets_dict'))


@router.message(SetManager.del_set, DBFilter())
async def handle_set_name_to_del(
    session: AsyncSession,
    message: types.Message,
    state: FSMContext,
):
    set_name_id_dict = await state.get_data()
    set_id = set_name_id_dict.get(message.text)
    if not set_id:
        return await message.answer('Такого набора нет')
    await delete_set(set_id, session)
    await message.answer(
        text=f'Набор слов {message.text} удален!',
        reply_markup=types.ReplyKeyboardRemove,
    )