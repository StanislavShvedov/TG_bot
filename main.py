import telebot
from telebot import types
from config import API_TOKEN
from data import check_user, New_user
import random

bot = telebot.TeleBot(API_TOKEN)


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


@bot.message_handler(commands=['start'])
def handle_start(message):
    global user
    id = message.chat.id
    user_name = f'пользователь_{id}'

    if check_user(id):
        user = New_user(id, user_name)
        user._add_user()
        bot.send_message(message.chat.id,
                         'Привет 👋 Давай попрактикуемся в английском языке. Тренировки можешь проходить в '
                         'удобном для себя темпе.\nУ тебя есть возможность использовать тренажёр, как '
                         'конструктор, и собирать свою собственную базу для обучения.\nДля этого воспрользуйся '
                         'инструментами: добавить слово ➕,удалить слово 🔙.Ну что, начнём ⬇️')

    markup = types.ReplyKeyboardMarkup(row_width=2)
    russian_word = user.get_rwords_list()
    target_word = user.get_target_word(russian_word)
    target_word_btn = types.KeyboardButton(target_word)
    other_words = user.get_other_words(target_word)
    other_words_btns = [types.KeyboardButton(word) for word in other_words]

    buttons = [target_word_btn] + other_words_btns
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([add_word_btn, delete_word_btn, next_btn])

    markup.add(*buttons)

    data = {'target': target_word, 'other': other_words}
    user.set_state(data)
    bot.send_message(message.chat.id, f'Угадай слово {russian_word}', reply_markup=markup)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    state = user.get_state()
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
        bot.send_message(message.chat.id, 'Введите новое слово')
        bot.register_next_step_handler(message, add_word)

    if message.text == Command.DELETE_WORD:
        bot.send_message(message.chat.id, 'Введите слово для удаления')
        bot.register_next_step_handler(message, delete_word)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def add_word(message):
    count = user.command_add_word(message.text)
    bot.send_message(message.chat.id, f'Слово "{message.text}" добавлено! В настоящий момент вы изучаете {count} слов.')
    handle_start(message)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def delete_word(message):
    count = user.command_delete_word(message.text)
    bot.send_message(message.chat.id, f'Слово "{message.text}" удалено! В настоящий момент вы изучаете {count} слов.')
    handle_start(message)


if __name__ == '__main__':
    print('Бот запущен')
    bot.polling()
