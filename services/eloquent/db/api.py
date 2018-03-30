import markdown
import html
from markdown.extensions.toc import TocExtension

from db.models import User, Article, MAX_ARTICLE_PREVIEW_TEXT_LENGTH, MAX_ARTICLE_CONTENT_LENGTH
from utils import get_sha512, strip_html_tags


def is_username_busy(username):
    return User.select().where(User.name == username).exists()


def create_user(username, password):
    User.create(name=username, pwd_hash=get_sha512(password.encode())).save()


def is_valid_pair(username, password):
    return User.get(User.name == username).pwd_hash._buffer == get_sha512(password.encode())


def create_article(title, content, owner_login):
    if len(content) > MAX_ARTICLE_CONTENT_LENGTH:
        return False
    owner_id = User.get(User.name == owner_login).id
    html_content = markdown.markdown(content, safe_mode='escape', extensions=[TocExtension(baselevel=3)])
    stripped_text = strip_html_tags(html_content)
    preview_text = stripped_text[:MAX_ARTICLE_PREVIEW_TEXT_LENGTH]
    if len(stripped_text) > MAX_ARTICLE_PREVIEW_TEXT_LENGTH:
        preview_text += '...'
    Article.create(
        title=html.escape(title),
        content=html_content,
        preview_text=preview_text,
        owner_id=owner_id
    ).save()
    return True


def get_article_titles_by_login(owner_login):
    owner_id = User.get(User.name == owner_login).id
    return Article.select(Article.id, Article.preview_text, Article.title).where(Article.owner_id == owner_id)


def get_article_by_id(art_id):
    return Article.get_by_id(int(art_id))
