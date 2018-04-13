import json
from base64 import b64decode
from urllib.parse import unquote

from bottle import route, run, request, post, get, static_file, redirect, abort, response, jinja2_view as view

from db.api import is_valid_pair, is_username_busy, create_user, create_article, get_article_titles_by_login, \
    get_article_by_id, get_users, publish_article
from utils import is_username_valid, is_password_valid, get_table_contents
from webserver.sessions import SessionManager

sm = SessionManager(request, response)


@get("/static/<filepath:re:.*>")
def get_static_files(filepath):
    return static_file(filepath, root="static")


@route('/user/<user_page_name>')
@view('user-page')
def user_page(user_page_name):
    username = request.get_cookie('login')
    if not sm.validate_session():
        redirect('/')
    if not is_username_busy(user_page_name):
        abort(400, "User doesn't exist")
    return {
        'login': username,
        'user_page_name': user_page_name,
        'articles': get_article_titles_by_login(user_page_name, get_drafts=False)
    }


@route('/')
@view('index')
def index():
    if sm.validate_session():
        return {
            'login': request.get_cookie('login'),
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


@route('/registration')
@view('registration')
def rp():
    pass


@route('/search')
@view('users-search')
def us():
    if not sm.validate_session():
        redirect('/')
    else:
        username = request.get_cookie('login')
        sort_by = request.GET.get('sortby', '').strip()
        query = request.GET.get('query', '').strip()
        return {
            'login': username,
            'users': get_users(sort_by, query),
            'current_url': request.fullpath
        }


@route('/publish/<article_id>')
def publish(article_id):
    if not sm.validate_session():
        redirect('/')
    username = request.get_cookie('login')
    if not publish_article(username, article_id):
        abort(400, "Bad article id or username")
    redirect('/my-articles')


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
    user_page_name = request.GET.get('user', '')
    if user_page_name != '':
        if not is_username_busy(user_page_name):
            abort(400, "Suggested user doesn't exist")
    username = request.get_cookie('login')
    return {
        'user_page_name': user_page_name,
        'login': username,
    }


@post('/post-article')
def post_article():
    if not sm.validate_session():
        abort(400, "Invalid session")
    title = request.forms.getunicode('title')
    content = request.forms.getunicode('content')
    username = request.get_cookie('login')
    user_suggestion = request.GET.get('user', None)
    if user_suggestion is not None:
        if not is_username_busy(user_suggestion):
            abort(400, "Suggested user doesn't exist")
    if not create_article(title, content, username, user_suggestion):
        abort(400, "Incorrect article content or title")
    if user_suggestion is None:
        redirect('/my-articles')
    else:
        redirect('/user/' + user_suggestion)


@route('/my-articles')
@view('my-articles')
def my_articles():
    if sm.validate_session():
        username = request.get_cookie('login')
        return {
            'login': username,
            'articles': get_article_titles_by_login(username, get_drafts=False)
        }
    else:
        return {}


@get('/suggestions')
@view('suggestions')
def suggestions():
    if not sm.validate_session():
        redirect('/')
    username = request.get_cookie('login')
    return {
        'login': request.get_cookie('login'),
        'articles': get_article_titles_by_login(username, get_drafts=True)
    }


@route('/article/<art_id>')
@view('view-article')
def view_article(art_id):
    if not sm.validate_session():
        redirect('/')
    username = request.get_cookie('login')
    article = get_article_by_id(art_id, username)
    if article is None:
        abort(400, "Bad article id")
    return {
        'login': username,
        'title': article.title,
        'content': article.content,
        'table_contents': get_table_contents(article.content),
    }


def start_web_server(host='0.0.0.0', port=8080):
    run(host=host, port=port, server='gunicorn', workers=10)

