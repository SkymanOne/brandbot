import os
from peewee import *
from playhouse.db_url import connect

if 'HEROKU' in list(os.environ.keys()):
    db = connect(os.environ.get('DATABASE_URL'))
else:
    db = SqliteDatabase('develop.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    name = CharField(max_length=100)
    telegram_id = IntegerField()
    nickname = CharField(max_length=100)


# TODO: дописать модель
class QueuePost(BaseModel):
    name = CharField(max_length=50)
    size = CharField(max_length=30)
    state = IntegerField()
    city = CharField(max_length=150)
    price = CharField(max_length=70)
    seller = ForeignKeyField(User)
    type = IntegerField(default=0)


class News(BaseModel):
    text = TextField()
    is_contest = BooleanField(default=False)


if __name__ == '__main__':
    db.connect()
    db.create_tables([User, QueuePost, News], safe=True)
