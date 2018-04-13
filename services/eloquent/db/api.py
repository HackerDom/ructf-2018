import markdown
import html
from markdown.extensions.toc import TocExtension
from peewee import DoesNotExist

from db.models import User, Article, MAX_ARTICLE_PREVIEW_TEXT_LENGTH, MAX_ARTICLE_CONTENT_LENGTH, MAX_TITLE_LENGTH, \
    SORT_MAP
from utils import get_sha512, strip_html_tags


MAX_USERS_COUNT_TO_SEARCH = 40


def is_username_busy(username):
    return User.select().where(User.name == username).exists()


def create_user(username, password):
    User.create(name=username, pwd_hash=get_sha512(password.encode()), articles_count=0).save()


def is_valid_pair(username, password):
    if not is_username_busy(username):
        return False
    return User.get(User.name == username).pwd_hash._buffer == get_sha512(password.encode())


def create_article(title, content, owner_login, user_suggestion):
    if len(content) > MAX_ARTICLE_CONTENT_LENGTH or len(title) > MAX_TITLE_LENGTH:
        return False
    user = User.get(User.name == owner_login)
    if user_suggestion is None:
        owner = user
    else:
        owner = User.get(User.name == user_suggestion)
    articles_count = user.articles_count
    html_content = markdown.markdown(content, safe_mode='escape', extensions=[TocExtension(baselevel=3)])
    stripped_text = strip_html_tags(html_content)
    preview_text = stripped_text[:MAX_ARTICLE_PREVIEW_TEXT_LENGTH]
    if len(stripped_text) > MAX_ARTICLE_PREVIEW_TEXT_LENGTH:
        preview_text += '...'
    Article.create(
        title=html.escape(title),
        content=html_content,
        preview_text=preview_text,
        owner=owner,
        is_draft=user_suggestion is not None
    ).save()
    if user_suggestion is None:
        User\
            .update({User.articles_count: articles_count + 1})\
            .where(User.id == owner)\
            .execute()
    return True


def get_article_titles_by_login(owner_login, get_drafts):
    if not is_username_busy(owner_login):
        return None
    owner = User.get(User.name == owner_login)
    return Article\
        .select(Article.id, Article.preview_text, Article.title)\
        .where(Article.owner == owner, Article.is_draft == get_drafts)


def get_article_by_id(art_id, username):
    try:
        article = Article.get_by_id(int(art_id))
        if User.get(User.name == username).id != article.owner.id and article.is_draft:
            return None
        return article
    except (ValueError, DoesNotExist):
        return None


def get_users(sort_by=None, query=''):
    search_query = User.select(User.name, User.registration_date, User.articles_count)
    if sort_by is not None:
        search_query = search_query.order_by(SORT_MAP.get(sort_by, ''))
    if query is not None:
        search_query = search_query.where(User.name.contains(query))
    search_query = search_query.limit(MAX_USERS_COUNT_TO_SEARCH)
    return list(search_query)


def publish_article(username, article_id):
    article = Article.get_by_id(article_id)
    user = article.owner
    if user.name != username:
        return False
    Article\
        .update({Article.is_draft: False})\
        .where(Article.id == article_id)\
        .execute()
    User\
        .update({User.articles_count: user.articles_count + 1})\
        .where(User.id == user.id)\
        .execute()
    return True

