from _sha512 import sha512

from peewee import SqliteDatabase, Model, CharField, BigBitField


def get_sha512(data: bytes):
    return sha512(data).digest()


db = SqliteDatabase('test.db')


class User(Model):
    name = CharField(20)
    pwd_hash = BigBitField(64)

    class Meta:
        database = db

User.create_table()


def is_username_busy(username):
    return User.select().where(User.name == username).exists()


def create_user(username, password):
    print("CREATION:({})".format(password))
    User.create(name=username, pwd_hash=get_sha512(password.encode())).save()


def is_valid_pair(username, password):
    print("CHECKING:({})".format(password))
    result = User.get(User.name == username).pwd_hash._buffer == get_sha512(password.encode())
    print('db API:', result)
    return result
