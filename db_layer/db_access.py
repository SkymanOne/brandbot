import logging
import my_logger
from db_layer.models import *
from telegraph import Telegraph
import requests

logger = my_logger.get_logger()
logger.setLevel(logging.INFO)


def init_db():
    logger.info('Connect to db')
    db.connect()
    logger.info('Init models')
    db.create_tables([User, QueuePost], safe=True)


def create_user(name: str, telegram_id: int, nickname: str):
    try:
        logger.info('Создание пользователя с nickname {nick} ...'.format(nick=nickname))
        User.create(name=name, telegram_id=telegram_id, nickname=nickname)
    except Exception:
        logger.error('ошибка создания пользователя!')
        return False
    else:
        logger.info('успешное созданием пользователя {nick}'.format(nick=nickname))
        return True


def get_user(telegram_id: int):
    try:
        logger.info('поиск пользователя с id: {id} ...'.format(id=telegram_id))
        user = User.get(User.telegram_id == telegram_id)
    except DoesNotExist:
        logger.error('ошибка поиска пользователя!')
        return None
    else:
        logger.info('успешное получение пользователя c id: {id}'.format(id=telegram_id))
        return user


def get_all_posts():
    logger.info('Вызов метода для получения списка всех постов.')
    try:
        posts = QueuePost.select()
        logger.info('Получение постов из базы данных')
        return posts
    except DoesNotExist:
        logger.error('Ошибка получения постов')
        return None


def create_post(type_of: int, text: str, links: str, seller_id: int):
    seller = get_user(seller_id)
    if seller is not None:
        try:
            logger.info('создание заявки на публикацию')
            new_queue = get_all_posts().count() + 1
            QueuePost.create(type_of=type_of, text=text, links_of_photos=links, seller=seller, queue=new_queue)
        except DoesNotExist:
            logger.error('ошибка создание заявки')
            return False
        else:
            logger.info('успешное создание заявки')
            return True
    else:
        logger.error('ошибка создание заявки')
        return False


def get_post():
    try:
        logger.info('получение первого в очереди поста...')
        post = QueuePost.get(QueuePost.queue == 1)
    except DoesNotExist:
        logger.error('пост НЕ НАЙДЕН в базе данных')
        return None
    else:
        logger.info('успешное получение первого поста')
        return post


def get_post_by_text(text: str):
    try:
        logger.info('получение поста по тексту...')
        post = QueuePost.get(QueuePost.text == text)
    except DoesNotExist:
        logger.error('пост НЕ НАЙДЕН в базе данных')
    else:
        logger.info('успешное получение поста по тексту')
        return post


def get_latest_post(seller_id: int):
    seller = get_user(seller_id)
    if seller is not None:
        logger.info('поиск последнего поста...')
        posts = QueuePost.select().where(QueuePost.seller == seller)
        post = None
        i = 1
        for p in posts:
            if p.queue >= i:
                i = p.queue
                post = p
        logger.info('получение последнего поста post.queue = {q}'.format(q=str(post.queue)))
        return post
    else:
        logger.error('ошибка поиска последнего поста')
        return None


def delete_latest_post(seller_id: int):
    logger.info('даление последнего поста пользователя {id} ...'.format(id=seller_id))
    post = get_latest_post(seller_id)
    if post is not None:
        i = post.queue
        logger.info('изменение порядка очереди следующий постов')
        for p in get_all_posts():
            if p.queue > i:
                p.queue -= 1
                p.save()
        post.delete_instance()
        logger.info('успешное удаление последнего поста пользователя {id}'.format(id=seller_id))
        return True
    else:
        return False


def delete_post_from_queue():
    first_post = get_post()
    if first_post is not None:
        logger.info('удаление первого в очереди поста...')
        first_post.delete_instance()
        logger.info('успешное удаление первого в очереди поста')
        posts = get_all_posts()
        if posts is not None:
            logger.info('смещение номера очереди на -1...')
            for p in posts:
                p.queue -= 1
                p.save()
            logger.info('успешное смещение номера очереди на -1')
            return True
        else:
            logger.error('ошибка смещение постов в очереди')
    else:
        logger.error('ошибка удаление поста из очереди')
        return False


# TODO: получение оплаченных постов и их удаление


def upload_photo(photo):
    logger.info('загрзука фото на сервер telegra.ph...')
    try:
        tel = Telegraph()
        tel.create_account(short_name='brand')
        link = 'http://telegra.ph'
        link += requests.post(link + '/upload',
                              files={'file': ('file', photo, 'image/jpeg')}).json()[0]['src']
    except:
        logger.error('ошибка загрузки фото на сервер telegra.ph')
        return ''
    else:
        logger.info('успешная загрузка фото на сервер: ссылка: {link}'.format(link=link))
        return link


if __name__ == '__main__':
    init_db()
