__all__ = ("router", )

from database.engine import DBFilter
from aiogram import Router
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from sets.functions import check_csv


router = Router()


@router.message(DBFilter())
async def handle_file(
    message: types.Message,
    session: AsyncSession,
):
    await check_csv(message, session)