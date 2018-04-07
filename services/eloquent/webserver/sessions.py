import os
from copy import copy
from base64 import b64encode
from time import time

import redis

from utils import get_sha512

COOKIE_EXPIRATION_TIME = 60 * 60


class SessionManager:
    def __init__(self, request, response):
        self.request = request
        self.response = response
        self.storage = redis.StrictRedis(host='localhost', port=6379, db=0)

    def create_session(self, login):
        login = copy(login).encode()
        salt = os.urandom(10)
        sid = b64encode(get_sha512(login + salt)).decode()
        self.storage.set(login, salt)
        self.response.set_cookie('login', login.decode(), expires=time() + COOKIE_EXPIRATION_TIME)
        self.response.set_cookie('sid', sid, expires=time() + COOKIE_EXPIRATION_TIME)

    def validate_session(self):
        login = self.request.get_cookie('login')
        sid = self.request.get_cookie('sid')
        if login is None or sid is None:
            return False
        login = login.encode()
        salt = self.storage.get(login)
        if salt is None:
            return False
        return b64encode(get_sha512(login + salt)).decode() == sid

    def remove_session(self):
        if self.validate_session():
            login = self.request.get_cookie('login').encode()
            self.storage.delete(login)
            self.response.delete_cookie('login')
            self.response.delete_cookie('sid')
            return True
        return False
