import logging
import os
import telebot
import token_key

from flask import Flask, request

if 'HEROKU' in list(os.environ.keys()):
    token = os.environ.get('TOKEN')
else:
    token = token_key.token

bot = telebot.TeleBot(token)

if 'HEROKU' in list(os.environ.keys()):
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)
    server = Flask(__name__)


    @server.route('/bot', methods=['POST'])
    def get_message():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200


    @server.route('/')
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url='set url here/' + token)
        return '!', 200

    if __name__ == '__main__':
        server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
else:
    bot.remove_webhook()
    bot.polling(True)
