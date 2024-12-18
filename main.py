import asyncio
from database.engine import bot
from aiogram import Dispatcher
import database.schemas as db_schema

from default.router import router as default_commandas_router
from sets.router import router as set_router
from challenge.router import router as challenge_router


dp = Dispatcher()
dp.include_router(default_commandas_router)
dp.include_router(set_router)
dp.include_router(challenge_router)


async def start_polling():
    await dp.start_polling(bot)


async def main():
    # await start_polling()
    # await db_schema.init_models()
    await asyncio.gather(
        db_schema.init_models(),
        start_polling(),
    )


if __name__ == "__main__":
    # asyncio.run(dp.start_polling(bot))
    asyncio.run(main())
    