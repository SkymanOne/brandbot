import logging
import os
import telebot
from db_layer import db_access, type_const

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
                'подписанным на наш канал!\n\n👉️ *@BrandPlace* 👈️ '


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
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="😼Подписаться на топ-канал😼", url="https://t.me/brandplace")
    keyboard.add(url_button)
    bot.send_message(message.from_user.id, greeting_text, reply_markup=get_greeting_markup(),
                     parse_mode='Markdown')
    bot.send_message(message.from_user.id, '*Давай*, подписывайся, если не сделал',
                     parse_mode='Markdown', reply_markup=keyboard)


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


@bot.message_handler(func=lambda message: message.text == '💫Бесплатная публикация💫 (free)'
                     or message.text == '💵Закреплённый пост💵 (300 руб.)'
                     or message.text == '💶Пост вне очереди💶 (150 руб.)')
def check_username(message: types.Message):
    nickname = message.from_user.username
    if nickname is None:
        bot.send_message(message.from_user.id, '*У тебя не создан USERNAME❌*\nСоздай его и попробуй снова\n'
                                               'инструкция: http://telegra.ph/1-Sozdayom-nickname-03-06',
                         parse_mode='Markdown')
    else:
        user = db_access.get_user(message.from_user.id)
        if user is None:
            db_access.create_user(message.from_user.first_name,
                                  message.from_user.id,
                                  message.from_user.username)
        bot.send_message(message.from_user.id, nickname)
        bot.send_message(message.from_user.id, str(message.from_user.id) + ' отправь это мне в лс')
        msg = bot.send_message(message.from_user.id, 'Введи информацию о товаре: ',
                               reply_markup=types.ReplyKeyboardRemove())
        if message.text == '💫Бесплатная публикация💫 (free)':
            bot.register_next_step_handler(msg, reg_free_production)
        elif message.text == '💵Закреплённый пост💵 (300 руб.)':
            bot.register_next_step_handler(msg, reg_fixed_publish_production)
        elif message.text == '💶Пост вне очереди💶 (150 руб.)':
            bot.register_next_step_handler(msg, reg_out_of_turn)


def reg_free_production(message: types.Message):
    if message.content_type == 'text':
        post = db_access.get_post_by_text(message.text)
        if post is None:
            result = db_access.create_post(type_const.FREE_PUBLISH, message.text, '', message.from_user.id)
            if result:
                msg = bot.send_message(message.from_user.id, 'Такс😌, супер, теперь отправь несколько фото📷,'
                                                             ' *но по одному* 1️⃣',
                                       parse_mode='Markdown')
                bot.register_next_step_handler(msg, add_photo)
            else:
                bot.send_message(message.from_user.id, 'Упс 🙄, что-то пошло не так😒')
    else:
        msg = bot.send_message(message.from_user.id, 'Ну слушай, первым отправляем текст о товаре, фотки чутка позже 😉')
        bot.register_next_step_handler(msg, reg_free_production)


def reg_out_of_turn(message: types.Message):
    if message.content_type == 'text':
        post = db_access.get_post_by_text(message.text)
        if post is None:
            result = db_access.create_post(type_const.OUT_OF_TURN_PUBLISH, message.text, '', message.from_user.id)
            if result:
                msg = bot.send_message(message.from_user.id, 'Такс😌, супер, теперь отправь несколько фото📷,'
                                                             ' *но по одному* 1️⃣',
                                       parse_mode='Markdown')
                bot.register_next_step_handler(msg, add_photo)
            else:
                bot.send_message(message.from_user.id, 'Упс 🙄, что-то пошло не так😒')
    else:
        msg = bot.send_message(message.from_user.id, 'Ну слушай, первым отправляем текст о товаре, фотки чутка позже 😉')
        bot.register_next_step_handler(msg, reg_free_production)


def reg_fixed_publish_production(message: types.Message):
    if message.content_type == 'text':
        post = db_access.get_post_by_text(message.text)
        if post is None:
            result = db_access.create_post(type_const.FIXED_PUBLISH, message.text, '', message.from_user.id)
            if result:
                msg = bot.send_message(message.from_user.id, 'Такс😌, супер, теперь отправь несколько фото📷,'
                                                             ' *но по одному* 1️⃣',
                                       parse_mode='Markdown')
                bot.register_next_step_handler(msg, add_photo)
            else:
                bot.send_message(message.from_user.id, 'Упс 🙄, что-то пошло не так😒')
    else:
        msg = bot.send_message(message.from_user.id, 'Ну слушай, первым отправляем текст о товаре, фотки чутка позже 😉')
        bot.register_next_step_handler(msg, reg_free_production)


def add_photo(message: types.Message):
    post = db_access.get_latest_post(message.from_user.id)
    markup = types.ReplyKeyboardMarkup()
    markup.row('Закончить добавление фото')
    if not message.text == 'Закончить добавление фото' and message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        link = db_access.upload_photo(file)
        post.links_of_photos += ' {link}'.format(link=link)
        post.save()
        msg = bot.send_message(message.from_user.id, 'Если есть еще фото - присылай👉',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, add_photo)
    else:
        bot.send_message(message.from_user.id, '*Супер!*\n\n'
                                               'ты оставил заявку на публикаицю\nP.S. Фотки классные 😌',
                         parse_mode='Markdown')
        queue = post.queue
        bot.send_message(message.from_user.id, 'Твое место в очереди на публикацию: {n}'.format(n=queue),
                         reply_markup=get_greeting_markup())


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
