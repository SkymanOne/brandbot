from db_layer.models import *


def init_db():
    db.connect()
    db.create_tables([User, QueuePost, News], safe=True)
