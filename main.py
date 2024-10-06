import openpyxl
import asyncio
from config import TOKEN
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command


async def check_csv(message: types.Message):
    file = message.document
    await file.download("temp.csv")
    
    if file.mime_type != 'text/csv':
        await message.reply("Некорректный формат файла! Поддерживается только CSV.")
        return
    
    try:
        wb = openpyxl.load_workbook("temp.csv", data_only=True)
        ws = wb.active
        rows = ws.values
    except Exception as e:
        await message.reply("Произошла ошибка при чтении файла! Попробуйте снова.")
        return
    
    columns = ['question', 'answer']
    
    if set(ws[0]) != set(columns):
        await message.reply("Неправильная структура CSV! Должны быть колонки 'question' и 'answer'.")
        return
    
    for row in rows:
        if not len(row[0]) or not len(row[1]):
            await message.reply("Все строки должны быть заполнены в обеих колонках.")
            return
    
    await message.reply("CSV успешно проверен!")


async def start_command(message: types.Message):
    await message.reply("Этот бот принимает CSV-файлы и проверяет их структуру.\n\nКоманды:\n/start - показать эту информацию\n<документ> - отправить документ для проверки")


bot = Bot(token=TOKEN)
dp = Dispatcher()


async def start_polling(bot):
    await dp.start_polling(bot)


@dp.message(CommandStart())
async def handle_start_command(message: types.Message):
    if message.text == '/start':
        await start_command(message)


@dp.message(Command("help"))
async def handle_help(message: types.Message):
    text = """
    I'am helping you to learn your words or sentences\n
    And I save your words for you\n
    And I can ask you about them, probably..
    """
    await message.answer(text=text)


# @dp.message
# async def handle_file(message: types.Message):
#     await check_csv(message)


if __name__ == "__main__":
    asyncio.run(start_polling(bot))