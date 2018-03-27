from db.models import User, Article
from utils import get_sha512


def is_username_busy(username):
    return User.select().where(User.name == username).exists()


def create_user(username, password):
    User.create(name=username, pwd_hash=get_sha512(password.encode())).save()


def is_valid_pair(username, password):
    return User.get(User.name == username).pwd_hash._buffer == get_sha512(password.encode())


def create_article(title, content, owner_login):
    owner_id = User.get(User.name == owner_login).id
    Article.create(title=title, content=content, owner_id=owner_id).save()


def get_articles_by_login(owner_login):
    owner_id = User.get(User.name == owner_login).id
    return Article.select(Article.title, Article.content).where(Article.owner_id == owner_id)
