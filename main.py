import asyncio
from database.engine import bot
from aiogram import Dispatcher
from default.router import router as default_commandas_router
from default.router import router as set_router


dp = Dispatcher()
dp.include_router(default_commandas_router)
dp.include_router(set_router)


if __name__ == "__main__":
    # asyncio.run(db_schema.init_models())
    asyncio.run(dp.start_polling(bot))