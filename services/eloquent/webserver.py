import json
from base64 import b64decode
from urllib.parse import unquote

import bottle
import redis
from bottle import route, run, view, request, post, get, static_file, redirect, abort, response
from db import is_username_busy, create_user, is_valid_pair
from sessions import SessionManager
from utils import is_username_valid, is_password_valid


sm = SessionManager(request, response)


@get("/static/<filepath:re:.*>")
def get_static_files(filepath):
    return static_file(filepath, root="static")


@get('/')
@view('index')
def index():
    if sm.validate_session():
        return {"login": request.get_cookie('login')}


@get('/sb')
@view('sandbox')
def sandbox():
    pass


@route('/signout')
def logout():
    sm.remove_session()
    redirect('/')


@post('/signin')
def signin():
    username = request.forms.get('username')
    password = request.forms.getunicode('password')
    if username is None or password is None:
        abort(400)
    if not is_username_valid(username) or not is_password_valid(password):
        abort(400)
    if not is_valid_pair(username, password):
        abort(400)
    sm.create_session(username)
    # print(session)
    # session['login'] = username
    # response.set_cookie("login", username)
    redirect('/')


@get('/login')
@view('login')
def login():
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
        abort(400)
    if not is_username_valid(username) or not is_password_valid(password):
        abort(400)
    if not is_username_busy(username):
        create_user(username, password)
        sm.create_session(username)
        redirect('/')
    else:
        abort(400)


@get('/exist/<username>')
def exist(username):
    return json.dumps(is_username_busy(username))


@get('/isvalidpair/<username>/<password>')
def ivp(username, password):
    decoded_password = unquote(b64decode(password, altchars=b'+-').decode())
    return json.dumps(is_valid_pair(username, decoded_password))


@get('/create')
@view('create-title')
def create_title():
    pass

run(host='0.0.0.0', port=8080, server='gunicorn')
