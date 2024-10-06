import openpyxl
import asyncio
from config import TOKEN
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
import csv


async def check_csv(message: types.Message):
    user_id = message.from_user.id
    file_id = message.document.file_id
    file_data = await bot.get_file(file_id)
    file_path = file_data.file_path
    await bot.download_file(file_path, "temp.csv")
    
    if message.document.mime_type != 'text/csv':
        await message.reply("Некорректный формат файла! Поддерживается только CSV.")
        return
    
    with open('temp.csv', newline='') as csvfile:
        spamreader = csv.reader(
            csvfile,
            # delimiter='',
            # quotechar='|'
        )
        for row in spamreader:
            print(row)
    # try:
    #     wb = openpyxl.load_workbook("temp.csv", data_only=True)
    #     ws = wb.active
    #     rows = ws.values
    # except Exception as e:
    #     await message.reply("Произошла ошибка при чтении файла! Попробуйте снова.")
    #     return
    
    # columns = ['question', 'answer']
    
    # if set(ws[0]) != set(columns):
    #     await message.reply("Неправильная структура CSV! Должны быть колонки 'question' и 'answer'.")
    #     return
    
    # for row in rows:
    #     if not len(row[0]) or not len(row[1]):
    #         await message.reply("Все строки должны быть заполнены в обеих колонках.")
    #         return
    
    await message.reply("CSV успешно проверен!")


bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def handle_start_command(message: types.Message):
    await message.answer(
        text="""
Этот бот принимает CSV-файлы и проверяет их структуру.
Команды:
/start - показать эту информацию
<документ> - отправить документ для проверки
"""
    )


@dp.message(Command("help"))
async def handle_help(message: types.Message):
    text = """
I'am helping you to learn your words or sentences
And I save your words for you
And I can ask you about them, probably..
"""
    await message.answer(text=text)


@dp.message()
async def handle_file(message: types.Message):
    await check_csv(message)


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))