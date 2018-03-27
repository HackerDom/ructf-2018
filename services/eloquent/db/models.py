from peewee import Model, CharField, BigBitField, SqliteDatabase, TextField, IntegerField

from config import DB_FILE_ABSPATH

db = SqliteDatabase(DB_FILE_ABSPATH)


class User(Model):
    name = CharField(20)
    pwd_hash = BigBitField(64)

    class Meta:
        database = db

if not User.table_exists():
    User.create_table()


class Article(Model):
    title = CharField(256)
    content = TextField()
    owner_id = IntegerField()

    class Meta:
        database = db

if not Article.table_exists():
    Article.create_table()
