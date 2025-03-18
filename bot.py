from dotenv import load_dotenv
import os
import json
import asyncio
import time

from aiogram import Dispatcher, Bot
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton



load_dotenv()

bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()

with open('questions.json', 'r', encoding='utf-8') as file:
    questions = json.load(file)['questions']


class QuizStates(StatesGroup):
    ASKING = State()
    ANSWERING = State()

@dp.message(Command('start'))
async def start_command(message: Message, state: FSMContext):
    image = FSInputFile('images/main.jpg')
    start_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
        ],
        resize_keyboard=True
    )
    await message.answer_photo(photo = image,
                               caption = 'Добро пожаловать в викторину на тему истории! Готов проверить свои знания?', reply_markup=start_kb)
    await state.set_state(QuizStates.ASKING)


@dp.message(QuizStates.ASKING)
async def asking(message: Message, state: FSMContext):
    if message.text.lower() == 'да':
        await state.update_data(question_index=0, correct_answers=0)
        await ask_question(message, state)
    elif message.text.lower() == 'нет':
        await message.answer('Хорошо, если передумаешь, просто напиши /start.')
        await state.clear()
    else:
        await message.answer('Пожалуйста, нажми "Да" чтобы начать тест или "Нет" чтобы отказаться.')

# Функция для задания вопроса
async def ask_question(message: Message, state: FSMContext):
    data = await state.get_data()
    question_index = data['question_index']
    question = questions[question_index]

    options_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=option, callback_data=str(i))] for i, option in enumerate(question["options"])
        ]
    )
    image = FSInputFile(question["image"])
    await message.answer_photo(image, f'{question["question"]}', reply_markup=options_kb)
    await state.set_state(QuizStates.ANSWERING)

# Обработка ответа на вопрос
@dp.callback_query(QuizStates.ANSWERING)
async def answering(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question_index = data['question_index']
    question = questions[question_index]

    user_answer_index = int(callback_query.data)
    user_answer = question["options"][user_answer_index]

    if user_answer == question["correct_answer"]:
        await callback_query.message.answer('Верно✅')
        time.sleep(1)
        await state.update_data(correct_answers=data['correct_answers'] + 1)
    else:
        await callback_query.message.answer(f'Неверно.❌\nПравильный ответ: *{questions[question_index]["correct_answer"]}*', parse_mode="Markdown")
        time.sleep(1)

    if question_index + 1 < len(questions):
        await state.update_data(question_index=question_index + 1)
        await ask_question(callback_query.message, state)
    else:
        score = data['correct_answers']
        await callback_query.message.answer(f'Тест завершен!')
        await state.clear()

    await callback_query.answer()

    if score<=5:
            imeg = FSInputFile("images/vvv.jpg")
            await callback_query.message.answer_photo(imeg,f"Вы правильно ответили на {score} из {len(questions)} вопросов.А ты точно живешь в России и изучаешь ЕЁ историю? Если да, то стоит взять за правило читать учебник перед сном 😊 Все получиться! Что бы пройти ещё раз, нажми /start")

    elif score<=10:
            imeg = FSInputFile("images/loox.jpg")
            await callback_query.message.answer_photo(imeg,f"Вы правильно ответили на {score} из {len(questions)} вопросов.Тебе стоит вспомнить некоторые темы, они прошли мимо тебя. Но все поправимо! Не сдавайся! Что бы пройти ещё раз, нажми /start")

    elif score<=15:
            imeg = FSInputFile("images/lxl.jpg")
            await callback_query.message.answer_photo(imeg,f"Вы правильно ответили на {score} из {len(questions)} вопросов.Вау, Вау, Вау… приятно видеть столь образованного человека! Так держать! Что бы пройти ещё раз, нажми /start")

        #await callback_query.message.answer(f'Тест завершен! Вы пра-вильно ответили на {score} из {len(questions)} вопросов. Что бы пройти тест повторно, введите /start')
    await state.clear()

    await callback_query.answer()



async def main():
    print('Бот запущен')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())