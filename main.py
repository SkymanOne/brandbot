import logging
import os
import telebot

from telebot import types
from flask import Flask, request

# если в окуржении есть переменная HEROKU, значит получаем токен из переменной окружения
if 'HEROKU' in list(os.environ.keys()):
    TOKEN = str(os.environ.get('TOKEN'))
# иначе импортируем его из скрытого в файлы в папке проекта
else:
    import token_key
    TOKEN = token_key.token

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

greeting_text = '*Добро пожаловать, модник!*😎🤙🏼\n\nДля того, чтобы опубликовать свой рарный айтем нужно быть ' \
                'подписанным на наш канал!\n\n✔️ @BrandPlace ✔️ '


def get_greeting_markup():
    markup = types.ReplyKeyboardMarkup()
    markup.row('💰Опубликовать💰')
    markup.row('🔥Инструкция для публикации🔥')
    markup.row('⚡Правила⚡️', '🌄Модные обои🌄')
    markup.row('🛠Связаться с админами🛠', '💻О разработчике💻')
    markup.resize_keyboard = True
    return markup


def get_types_publishing():
    markup = types.ReplyKeyboardMarkup()
    markup.row('💫Бесплатная публикация💫 (free)')
    markup.row('💵Закреплённый пост💵 (300 руб.)')
    markup.row('💶Пост вне очереди💶 (150 руб.)')
    markup.row('Главное меню📲')
    markup.resize_keyboard = True
    return markup


@bot.message_handler(func=lambda message: message.text == 'Главное меню📲')
@bot.message_handler(commands=['start'])
def greeting(message: types.Message):
    bot.send_message(message.from_user.id, greeting_text, reply_markup=get_greeting_markup())


@bot.message_handler(func=lambda message: message.text == '🔥Инструкция для публикации🔥')
def manual(message: types.Message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('1️⃣ Создаем nickname')
    markup.row('2️⃣ Инструкция публикация поста')
    markup.row('Главное меню📲')
    markup.resize_keyboard = True
    bot.send_message(message.from_user.id, 'Выбери одну из предложенных кнопок🔘',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '💰Опубликовать💰')
def types_of_publish(message: types.Message):
    required = '🔴*ОБЯЗАТЕЛЬНО* надо создать никнейм. Это нужно для того, чтобы с тобой *смог* связаться ' \
               'покупатель🔴\n\n📝В телеграме заходим в Настройки(Settings) ▶️ Имя пользователя(Username)📝 '
    info = 'Создал? Красавчик!\nКаким способом будем публиковать твой айтем❓'
    bot.send_message(message.from_user.id, required, parse_mode='Markdown')
    bot.send_message(message.from_user.id, info, reply_markup=get_types_publishing())


@bot.message_handler(func=lambda message: message.text == '1️⃣ Создаем nickname')
def manual_create_nickname(message: types.Message):
    bot.send_message(message.from_user.id, 'http://telegra.ph/1-Sozdayom-nickname-03-06')


@bot.message_handler(func=lambda message: message.text == '2️⃣ Инструкция публикация поста')
def manual_create_post(message: types.Message):
    # TODO: написать инструкцию
    pass


@bot.message_handler(func=lambda message: message.text == '⚡Правила⚡️')
def rules(message: types.Message):
    rule = '*Дорогие* подписчики и гости канала, спешим донести до вас правила нашей торговой площадки.\nВ целях ' \
           'сохранения актуальности информации, каждый пост будет выходить с интервалом в 1 час, в порядке очереди. ' \
           '*Для того, чтобы опубликовать пост с вашим айтемом*, нужно перейти в главное меню бота и нажать на кнопку ' \
           '\n«💰Опубликовать💰»\n\n❌За попытку продажи/продажу не оригинального предмета - выдаётся *бан*.❌ '
    bot.send_message(message.from_user.id, rule, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == '💻О разработчике💻')
def about_developer(message: types.Message):
    about_me = 'German Nikolishin\n\nPython and .NET developer👨‍💻\nTelegram👉 @german_nikolishin\nGitHub👉 ' \
               'https://github.com/SkymanOne\nVK👉 https://vk.com/german_it\nInst👉 ' \
               'https://www.instagram.com/german.nikolishin/\nTelegram Channel👉 https://t.me/VneUrokaDev '
    bot.send_message(message.from_user.id, about_me)


@bot.message_handler(func=lambda message: message.text == '🛠Связаться с админами🛠')
def connect_to_admins(message: types.Message):
    info = '❓Если возникли какие-то вопросы, то их можно задать одному из администраторов канала❓\n\n📲 @ogan3s\n\n📲 ' \
           '@code1n '
    bot.send_message(message.from_user.id, info)

# если в окуржении есть переменная HEROKU, значит поднимаем сервер
# иначе запускаем прослушку
if 'HEROKU' in list(os.environ.keys()):
    @server.route('/bot', methods=['POST'])
    def get_message():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200


    @server.route('/')
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url='https://brand-bot.herokuapp.com/' + TOKEN)
        return '!', 200


    if __name__ == '__main__':
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 80)))
else:
    bot.remove_webhook()
    bot.polling(True)
