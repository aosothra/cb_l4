import json
import random

import redis
import vk_api as vk
from environs import Env
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id


START, QUESTION, GUESS = range(3) 


def start(event, vk_api, persistent_data):
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Мой счет', VkKeyboardColor.PRIMARY)

    vk_api.messages.send(
        user_id=event.user_id,
        message='Добро пожаловать на квиз. Нажмите "Новый вопрос" чтобы начать викторину.',
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard()
    )

    return QUESTION


def new_question(event, vk_api, persistent_data):
    if event.text != 'Новый вопрос':
        vk_api.messages.markAsRead(peer_id=event.user_id)
        return QUESTION
    
    quiz_table = persistent_data['quiz_table']
    redis_connection = persistent_data['redis_connection']

    question = random.choice(list(quiz_table.keys()))
    redis_connection.set(event.user_id, question)

    answer = quiz_table[question]

    if persistent_data['show_answers']:
        question+=f' (ответ: {answer})'

    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=get_random_id()
    )

    return GUESS


def user_guess(event, vk_api, persistent_data):  
    quiz_table = persistent_data['quiz_table']
    redis_connection = persistent_data['redis_connection']

    answer = quiz_table[redis_connection.get(event.user_id)]

    if event.text.lower() == answer:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Правильно! Нажмите "Новый вопрос" чтобы продолжить викторину.',
            random_id=get_random_id()
        )
        return QUESTION
    
    if event.text == 'Сдаться':
        vk_api.messages.send(
            user_id=event.user_id,
            message=f'Правильный ответ - {answer}. Нажмите "Новый вопрос" чтобы продолжить викторину.',
            random_id=get_random_id()
        )
        return QUESTION

    vk_api.messages.send(
        user_id=event.user_id,
        message='Увы, не верно. Может есть другие варианты?',
        random_id=get_random_id()
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

    vk_session = vk.VkApi(token=env('VK_BOT_TOKEN'))
    vk_api = vk_session.get_api()

    users_state = dict()
    persistent_data = {
        'quiz_table': quiz_table,
        'redis_connection': redis_connection,
        'show_answers': env.bool('TEST_ANSWERS', False)
    }

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            state = users_state.get(event.user_id, START)
            if state == START:
                users_state[event.user_id] = start(event, vk_api, persistent_data)
            elif state == QUESTION:
                users_state[event.user_id] = new_question(event, vk_api, persistent_data)
            elif state == GUESS:
                users_state[event.user_id] = user_guess(event, vk_api, persistent_data)


if __name__ == '__main__':
    main()