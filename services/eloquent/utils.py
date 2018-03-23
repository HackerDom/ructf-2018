import re
from hashlib import sha512

USERNAME_TEMPLATE = re.compile('^[a-z0-9_-]{4,16}$')
PASSWORD_TEMPLATE = re.compile('^.{1,20}$')


def is_username_valid(username):
    return USERNAME_TEMPLATE.match(username) is not None


def is_password_valid(password):
    return PASSWORD_TEMPLATE.match(password) is not None


def get_sha512(data):
    return sha512(data).digest()
