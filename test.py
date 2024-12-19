#@title Полный код бота для самоконтроля
import aiosqlite
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather
API_TOKEN = '7537810130:AAHUN6hdgpa80Sz0dY4mGi3fGwGRimtEdM8'

# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()

# Зададим имя базы данных
DB_NAME = 'quiz_bot.db'


# Структура квиза
quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения текста в Python?',
        'options': ['int', 'list', 'str', 'float'],
        'correct_option': 2
    },
    {
        'question': 'Какой оператор используется для сравнения двух значений?',
        'options': ['=', '==', '!=', '<>'],
        'correct_option': 1
    },
    {
        'question': 'Что вернет функция len("Python")?',
        'options': ['6', '5', '7', 'Ошибка'],
        'correct_option': 0
    },
    {
        'question': 'Какая библиотека используется для работы с числами и массивами в Python?',
        'options': ['NumPy', 'Pandas', 'Matplotlib', 'Flask'],
        'correct_option': 0
    },
    {
        'question': 'Что делает метод append() для списка?',
        'options': ['Добавляет элемент', 'Удаляет элемент', 'Сортирует список', 'Находит индекс элемента'],
        'correct_option': 0
    },
    {
        'question': 'Как называется функция для вывода информации на экран?',
        'options': ['print()', 'input()', 'output()', 'write()'],
        'correct_option': 0
    },
    {
        'question': 'Какой символ используется для обозначения комментариев в Python?',
        'options': ['#', '//', '--', '/*'],
        'correct_option': 0
    },
    {
        'question': 'Какая функция используется для преобразования строки в целое число?',
        'options': ['str()', 'int()', 'float()', 'eval()'],
        'correct_option': 1
    }

]



def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()

async def initialize_results(user_id, total_questions):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO quiz_results (user_id, correct_answers, total_questions) VALUES (?, 0, ?)', (user_id, total_questions))
        await db.commit()

async def update_results(user_id, is_correct):
    async with aiosqlite.connect(DB_NAME) as db:
        if is_correct:
            await db.execute('UPDATE quiz_results SET correct_answers = correct_answers + 1 WHERE user_id = ?', (user_id,))
        await db.commit()
        
@dp.callback_query( F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        
        reply_markup=None
    )
    await update_results(callback.from_user.id, is_correct=True)

    await callback.message.answer(f"Вы выбрали: {callback.message.reply_markup.inline_keyboard[0][0].text}")
    await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)


    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await update_results(callback.from_user.id, is_correct=False)

    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    await callback.message.answer(f"Вы выбрали: {callback.message.reply_markup.inline_keyboard[0][0].text}")
    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)


    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")

async def initialize_results(user_id, total_questions):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO quiz_results (user_id, correct_answers, total_questions) VALUES (?, 0, ?)', (user_id, total_questions))
        await db.commit()

async def update_results(user_id, is_correct):
    async with aiosqlite.connect(DB_NAME) as db:
        if is_correct:
            await db.execute('UPDATE quiz_results SET correct_answers = correct_answers + 1 WHERE user_id = ?', (user_id,))
        await db.commit()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT correct_answers, total_questions FROM quiz_results WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            if result:
                correct, total = result
                await message.answer(f"Ваши результаты:\nПравильных ответов: {correct}\nВсего вопросов: {total}\nУспешность: {correct / total * 100:.2f}%")
            else:
                await message.answer("Вы еще не проходили квиз. Используйте команду /quiz, чтобы начать.")


async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)


async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        # Сохраняем изменения
        await db.commit()


# Хэндлер на команду /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)



async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_results (
                            user_id INTEGER PRIMARY KEY,
                            correct_answers INTEGER,
                            total_questions INTEGER)''')
                           
        # Сохраняем изменения
        await db.commit()




# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())