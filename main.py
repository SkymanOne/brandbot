import logging
import os
import telebot

from telebot import types
from flask import Flask, request

if 'HEROKU' in list(os.environ.keys()):
    TOKEN = str(os.environ.get('TOKEN'))
else:
    import token_key
    TOKEN = token_key.token

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

greeting_text = '*Добро пожаловать, модник!*😎🤙🏼\n\nДля того, чтобы опубликовать свой рарный айтем нужно быть ' \
                'подписанным на наш канал!\n\n✔️ @BrandPlace ✔️ '


def get_greeting_markup():
    markup = types.ReplyKeyboardMarkup()
    markup.row('🚀Конкурс🚀')
    markup.row('🔥Инструкция для публикации🔥', '🚀Конкурс🚀')
    markup.row('⚡Правила⚡️', '🌄Модные обои🌄')
    markup.row('🛠Связаться с админами🛠', '💻О разработчике💻')
    return markup


@bot.message_handler(func=lambda message: message.text == 'Главное меню📲')
@bot.message_handler(commands=['start'])
def echo(message: types.Message):
    bot.send_message(message.from_user.id, greeting_text, reply_markup=get_greeting_markup())


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
