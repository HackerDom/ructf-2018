import os

from peewee import Model, CharField, BigBitField, SqliteDatabase

from config import DB_FILE_ABSPATH

db = SqliteDatabase(DB_FILE_ABSPATH)


class User(Model):
    name = CharField(20)
    pwd_hash = BigBitField(64)

    class Meta:
        database = db

User.create_table()

print(list(User.select()))
