import html
import json
from base64 import b64decode
from urllib.parse import unquote

import markdown
from bottle import route, run, request, post, get, static_file, redirect, abort, response, jinja2_view as view
from markdown.extensions.toc import TocExtension

from db.api import is_valid_pair, is_username_busy, create_user, create_article, get_article_titles_by_login, \
    get_article_by_id
from utils import is_username_valid, is_password_valid
from webserver.sessions import SessionManager

sm = SessionManager(request, response)


@get("/static/<filepath:re:.*>")
def get_static_files(filepath):
    return static_file(filepath, root="static")


@route('/<username>')
@view('user-page')
def user_page(username):
    return {'username': username}


@route('/')
@view('index')
def index():
    if sm.validate_session():
        username = request.get_cookie('login')
        return {
            'login': request.get_cookie('login'),
            'articles': get_article_titles_by_login(username)
        }
    else:
        return {}


@route('/signout')
def logout():
    sm.remove_session()
    redirect('/')


@post('/signin')
def signin():
    username = request.forms.get('username')
    password = request.forms.getunicode('password')
    if username is None or password is None:
        abort(400, "Request form doesn't contain username or password")
    if not is_username_valid(username) or not is_password_valid(password):
        abort(400, "Incorrect login or password")
    if not is_valid_pair(username, password):
        abort(400, "Incorrect login or password")
    sm.create_session(username)
    redirect('/')


@get('/login')
@view('login')
def login_func():
    pass


@route('/sb')
@view('sandbox')
def sandbox():
    pass


@route('/registration')
@view('registration')
def rp():
    pass


@post('/register')
def register():
    username = request.forms.get('username')
    password = request.forms.getunicode('password')
    if username is None or password is None:
        abort(400, "Request form doesn't contain username or password")
    if not is_username_valid(username) or not is_password_valid(password):
        abort(400, "Incorrect login or password")
    if is_username_busy(username):
        abort(400, "Username is busy")
    create_user(username, password)
    sm.create_session(username)
    redirect('/')


@get('/exist/<username>')
def exist(username):
    return json.dumps(is_username_busy(username))


@get('/isvalidpair/<username>/<password>')
def ivp(username, password):
    decoded_password = unquote(b64decode(password, altchars=b'+-').decode())
    return json.dumps(is_valid_pair(username, decoded_password))


@get('/create')
@view('create-article')
def create_article_func():
    if not sm.validate_session():
        redirect('/')


@post('/post-article')
def post_article():
    if not sm.validate_session():
        abort(400, "Invalid session")
    title = request.forms.getunicode('title')
    content = request.forms.getunicode('content')
    username = request.get_cookie('login')
    if not create_article(title, content, username):
        abort(400, "Incorrect article content or title")
    redirect('/')


@route('/article/<art_id>')
@view('view-article')
def view_article(art_id):
    if not sm.validate_session():
        redirect('/')
    username = request.get_cookie('login')
    article = get_article_by_id(art_id)
    return {
        'login': username,
        'title': article.title,
        'content': article.content,
    }


def start_web_server(host='0.0.0.0', port=8080):
    run(host=host, port=port, server='gunicorn')
