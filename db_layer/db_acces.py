import logging
import my_logger
from db_layer.models import *

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


def create_post(type_of: int, text: str, links: str, seller: User):
    try:
        logger.info('создание заявки на публикацию')
        new_queue = get_all_posts().count + 1
        QueuePost.create(type_of=type_of, text=text, links_of_photos=links, seller=seller, queue=new_queue)
    except Exception:
        logger.error('ошибка создание заявки')
        return False
    else:
        logger.info('успешное создание заявки')
        return True


def get_post():
    try:
        logger.info('получение первого в очереди поста...')
        post = QueuePost.get(QueuePost.queue == 1)
    except DoesNotExist:
        logger.error('пост НЕ НАЙДЕН в базе данных')
        return None
    else:
        logger.info()
        return post


def delete_post_from_queue():
    first_post = get_post()
    if first_post is not None:
        logging.info('удаление первого в очереди поста...')
        first_post.delete_instance()
        logging.info('успешное удаление первого в очереди поста')
        posts = get_all_posts()
        if posts is not None:
            logging.info('смещение номера очереди на -1...')
            for p in posts:
                p.queue -= 1
                p.save()
            logging.info('успешное смещение номера очереди на -1')
            return True
        else:
            logging.error('ошибка смещение постов в очереди')
    else:
        logging.error('ошибка удаление поста из очереди')
        return False
