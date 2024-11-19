import json
from pprint import pprint

import telebot
from telebot import types
from config import API_TOKEN
from data import *
import random


bot = telebot.TeleBot(API_TOKEN)

class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'

@bot.message_handler(commands=['start'])
def handle_start(message):
    id = message.chat.id
    user_name = f'пользователь_{id}'

    if check_user(id):
        add_new_user(id, user_name)
        bot.send_message(message.chat.id,
                         'Привет 👋 Давай попрактикуемся в английском языке. Тренировки можешь проходить в '
                         'удобном для себя темпе.\nУ тебя есть возможность использовать тренажёр, как '
                         'конструктор, и собирать свою собственную базу для обучения.\nДля этого воспрользуйся '
                         'инструментами: добавить слово ➕,удалить слово 🔙.Ну что, начнём ⬇️')

    markup = types.ReplyKeyboardMarkup(row_width=2)
    russian_word = get_rwords_list(id)
    target_word = get_target_word(russian_word)
    target_word_btn = types.KeyboardButton(target_word)
    other_words = get_other_words(target_word)
    other_words_btns = [types.KeyboardButton(word) for word in other_words]

    buttons = [target_word_btn] + other_words_btns
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([add_word_btn, delete_word_btn, next_btn])

    markup.add(*buttons)

    data = {'target': target_word, 'other': other_words}
    set_state(id, data)
    bot.send_message(message.chat.id, f'Угадай слово {russian_word}', reply_markup=markup)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
        state = get_state(message.chat.id)
        target_word = state['target']
        other_words = state['other']
        if message.text == target_word:
            bot.send_message(message.chat.id, 'Правильно')
            handle_start(message)
        elif message.text in other_words:
            bot.send_message(message.chat.id, 'Не правильно, попробуй еще')

        if message.text == Command.NEXT:
            handle_start(message)

        if message.text == Command.ADD_WORD:
            print('Here - if message.text == Command.ADD_WORD')
            bot.send_message(message.chat.id, 'Введите новое слово')
            bot.register_next_step_handler(message, get_text)



@bot.message_handler(func=lambda message: True, content_types=['text'])
def get_text(message):
    command_add_word(message.chat.id, message.text)
    bot.send_message(message.chat.id, f'Слово "{message.text}" добавлено!')
    handle_start(message)

if __name__ == '__main__':
    print('Бот запущен')
    bot.polling()