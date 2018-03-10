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
