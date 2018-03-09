import logging
import os
import telebot

from flask import Flask, request

if 'HEROKU' in list(os.environ.keys()):
    TOKEN = str(os.environ.get('TOKEN'))
else:
    import token_key
    TOKEN = token_key.token

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)


@bot.message_handler(content_types=['text'])
def echo(message):
    bot.reply_to(message, 'Hello, world')


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

if 'HEROKU' in list(os.environ.keys()):
    @server.route('/bot', methods=['POST'])
    def get_message():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200


    @server.route('/')
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url='https://brand-bot.herokuapp.com/' + 'bot')
        return '!', 200


    if __name__ == '__main__':
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
else:
    bot.remove_webhook()
    bot.polling(True)
