import json
import random

import redis
from environs import Env
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler

QUESTION, GUESS, GIVE_UP = range(3) 


def start(update, context):
    quiz_keyboard_layout = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    quiz_keyboard_markup = ReplyKeyboardMarkup(quiz_keyboard_layout)

    update.message.reply_text(
        text='Добро пожаловать на квиз. Нажмите "Новый вопрос" чтобы начать викторину.',
        reply_markup=quiz_keyboard_markup
    )

    return QUESTION


def stop(update, context):
    update.message.reply_text(
        text='Спасибо за участие! Будем рады видеть Вас снова!',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def new_question(update, context):
    quiz_table = context.bot_data['quiz_table']
    redis_connection = context.bot_data['redis_connection']
    
    question = random.choice(list(quiz_table.keys()))
    redis_connection.set(update.effective_chat.id, question)

    answer = quiz_table[question]
    
    if context.bot_data['show_answers']:
        question+=f' (ответ: {answer})'

    update.message.reply_text(
        text=question
    )
        
    return GUESS


def user_gave_up(update, context):
    quiz_table = context.bot_data['quiz_table']
    redis_connection = context.bot_data['redis_connection']
    
    answer = quiz_table[redis_connection.get(update.effective_chat.id)]

    update.message.reply_text(
        text=f'Правильный ответ - {answer}. Нажмите "Новый вопрос" чтобы продолжить викторину.'
    )
        
    return QUESTION


def user_guess(update, context):
    quiz_table = context.bot_data['quiz_table']
    redis_connection = context.bot_data['redis_connection']

    answer = quiz_table[redis_connection.get(update.effective_chat.id)]

    if update.message.text.lower() == answer:
        update.message.reply_text(
            text='Правильно! Нажмите "Новый вопрос" чтобы продолжить викторину.'
        )
        return QUESTION

    update.message.reply_text(
        text='Увы, не верно. Может есть другие варианты?'
    )
    return GUESS


def main():
    env = Env()
    env.read_env()

    with open(env('QUIZ_JSON_PATH'), mode='r', encoding='utf-8') as quiz_file:
        quiz_table = json.load(quiz_file)

    redis_connection = redis.Redis(
        host=env('REDIS_HOST'), 
        port=env('REDIS_PORT'),
        db=0,
        password=env('REDIS_PASSWORD'),
        decode_responses=True)

    updater = Updater(env('TG_BOT_TOKEN'))
    dispatcher = updater.dispatcher

    quiz_conversation = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)
        ],
        states={
            QUESTION: [
                MessageHandler(Filters.regex('Новый вопрос'), new_question)
            ],
            GUESS: [
                MessageHandler(Filters.regex('Сдаться'), user_gave_up),
                MessageHandler(Filters.text & (~Filters.command), user_guess)
            ]
        },
        fallbacks=[
            CommandHandler('stop', stop)
        ]
    )

    dispatcher.add_handler(quiz_conversation)

    dispatcher.bot_data['quiz_table'] = quiz_table
    dispatcher.bot_data['redis_connection'] = redis_connection
    dispatcher.bot_data['show_answers'] = env.bool('TEST_ANSWERS', False)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()