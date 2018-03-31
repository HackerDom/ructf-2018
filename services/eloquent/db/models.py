from peewee import Model, CharField, BigBitField, SqliteDatabase, TextField, IntegerField, ForeignKeyField

from config import DB_FILE_ABSPATH

db = SqliteDatabase(DB_FILE_ABSPATH)
MAX_ARTICLE_CONTENT_LENGTH = 1000000
MAX_ARTICLE_PREVIEW_TEXT_LENGTH = 200
MAX_TITLE_LENGTH = 50


class User(Model):
    name = CharField(20)
    pwd_hash = BigBitField(64)

    class Meta:
        database = db

if not User.table_exists():
    User.create_table()


class Article(Model):
    title = CharField(MAX_TITLE_LENGTH)
    content = TextField()
    preview_text = CharField(MAX_ARTICLE_PREVIEW_TEXT_LENGTH)
    owner_id = ForeignKeyField(User)

    class Meta:
        database = db

if not Article.table_exists():
    Article.create_table()
