from time import strftime, gmtime

from peewee import Model, CharField, BigBitField, SqliteDatabase, TextField, IntegerField, ForeignKeyField, \
    DateTimeField, BooleanField

from config import DB_FILE_ABSPATH

db = SqliteDatabase(DB_FILE_ABSPATH)
MAX_ARTICLE_CONTENT_LENGTH = 1000000
MAX_ARTICLE_PREVIEW_TEXT_LENGTH = 150
MAX_TITLE_LENGTH = 50


def get_current_time():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


class User(Model):
    name = CharField(20)
    pwd_hash = BigBitField(64)
    registration_date = DateTimeField(default=get_current_time)
    articles_count = IntegerField()

    class Meta:
        database = db

if not User.table_exists():
    User.create_table()


SORT_MAP = {
    'username': User.name,
    'rtime': User.registration_date.desc(),
    'pac': User.articles_count.desc(),
}


class Article(Model):
    title = CharField(MAX_TITLE_LENGTH)
    content = TextField()
    preview_text = CharField(MAX_ARTICLE_PREVIEW_TEXT_LENGTH)
    owner = ForeignKeyField(User)
    is_draft = BooleanField()

    class Meta:
        database = db

if not Article.table_exists():
    Article.create_table()

