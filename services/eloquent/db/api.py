from db.models import User
from utils import get_sha512


def is_username_busy(username):
    return User.select().where(User.name == username).exists()


def create_user(username, password):
    User.create(name=username, pwd_hash=get_sha512(password.encode())).save()


def is_valid_pair(username, password):
    return User.get(User.name == username).pwd_hash._buffer == get_sha512(password.encode())
