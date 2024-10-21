import asyncio
from database.engine import bot
from aiogram import Dispatcher
from default.router import router as default_commandas_router
from sets.router import router as set_router
import database.schemas as db_schema


dp = Dispatcher()
dp.include_router(default_commandas_router)
dp.include_router(set_router)


async def main():
    await dp.start_polling(bot)
    await db_schema.init_models()


if __name__ == "__main__":
    # asyncio.run(dp.start_polling(bot))
    asyncio.run(main())
    