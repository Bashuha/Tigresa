from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from config import DB
from contextlib import asynccontextmanager
from aiogram.filters import Filter
from aiogram.types import Message
from config import TOKEN
from aiogram import Bot


engine = create_async_engine(
   f'postgresql+asyncpg://{DB.get("user")}:{DB.get("password")}@localhost:{DB.get("port")}/{DB.get("database")}',
    echo=DB.get('echo'),
    pool_recycle=3600
)

asyns_connection = sessionmaker(
    expire_on_commit=False,
    class_=AsyncSession,
    bind=engine,
)


bot = Bot(token=TOKEN)


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with asyns_connection() as session:
        yield session


class DBFilter(Filter):
    async def __call__(
        self,
        message: Message,
    ):
        async with get_db() as session:
            return {"session": session}