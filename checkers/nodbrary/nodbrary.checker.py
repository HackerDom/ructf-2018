#!/usr/bin/env python3

import traceback
import sys
import os

from utils import check_curve, decode_cookie, get_book, check_journal
from string import digits, ascii_letters
from json import loads, dumps
from bs4 import BeautifulSoup
from requests import Session
from faker import Faker


OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "nodbrary"
PORT = 3000

SIGN_UP   = "http://{}:{}/signup"
ADD_BOOK  = "http://{}:{}/add"
ADD_TAG   = "http://{}:{}/tag"
SIGN_IN   = "http://{}:{}/signin"
READ_BOOK = "http://{}:{}/book/"
JOURNAL   = "http://{}:{}/journal"

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
DIR = os.path.join(CUR_DIR, 'flags')

def generate_login():
    return ''.join(Faker().name().split())

def make_request(method, addr, team_addr, data=None):
    try:
        URL = addr.format(team_addr, PORT)
        r = method(URL, data=data) if data else method(URL)
        
        if r.status_code == 502:
            close(DOWN, "Service is down")
        if r.status_code != 200:
            r = method(URL, data=data) if data else method(URL)
            if r.status_code == 502:
                close(DOWN, "Service is down")
            if r.status_code != 200:
                close(MUMBLE, "Invalid HTTP response", "Invalid status code: {} {}".format(URL, r.status_code))	
    except Exception as ex:
        close(DOWN, "Service is down")
    return r

def store_user_data(flag_id, data):
    if not os.path.exists(DIR):
        os.makedirs(DIR)
    
    try:
        with open(os.path.join(DIR, flag_id), 'w') as f:
            f.write(dumps(data))
    except Exception as ex:
        close(CHECKER_ERROR, "Checker can't write files", "Can't write {}".format(flag_id))

def read_user_data(flag_id):
    path = os.path.join(DIR, flag_id)
    
    if not os.path.exists(path):
        close(CHECKER_ERROR, "Checker can't see file", "{} isn't exist".format(flag_id))
    
    try:
        with open(path, 'r') as f:
            data = loads(f.read())
    except Exception:
        close(CHECKER_ERROR, "Checker can't read file", "Can't read {}".format(flag_id))
    
    try:
        os.remove(path)
    except Exception:
        close(CHECKER_ERROR, "Checker can't delete file", "Can't delete {}".format(flag_id))
    return data['login'], data['password'], data['book_id']
        

def close(code, public="", private=""):
	if public:
		print(public)
	if private:
		print(private, file=sys.stderr)
	print('Exit with code {}'.format(code, file=sys.stderr))
	exit(code)

def info(*args):
    close(OK, "vulns: 1")

def check(*args):
    team_addr = args[0]
    login = generate_login()
    s = Session()

    r = make_request(s.post, SIGN_UP, team_addr, {"login":login})

    session = r.cookies.get('session', None)
    if not session:
        close(MUMBLE, "Invalid cookie", "No cookie. {}".format(team_addr))
    
    if not check_curve(session):
        close(MUMBLE, "Wrong curve", "Wrong curve. {}".format(team_addr))

    r = make_request(s.get, JOURNAL, team_addr)

    if not check_journal(BeautifulSoup(r.text, 'html.parser'), session):
        close(MUMBLE, "Breaked journal", "Bad journal. {}".format(team_addr))

    close(OK)

def put(*args):
    team_addr, flag_id, flag = args[:3]
    login = generate_login()
    s = Session()

    r = make_request(s.post, SIGN_UP, team_addr, {"login":login})
    
    session = r.cookies.get('session', None)
    if not session:
        close(MUMBLE, "Invalid cookie", "No cookie. {}".format(team_addr))
    password = hex(decode_cookie(session).get('priv_key'))[2:]

    book = get_book(CUR_DIR)
    r = make_request(s.post, ADD_BOOK, team_addr, book)

    book_id = r.url.split('/')[-1]
    make_request(s.post, ADD_TAG, team_addr, {"bookId":book_id,"tag":flag})

    store_user_data(flag_id, {"login": login, "password": password, "book_id": book_id})
    close(OK)

def get(*args):
    team_addr, flag_id, flag = args[:3]
    login, password, book_id = read_user_data(flag_id)
    s = Session()

    make_request(s.post, SIGN_IN, team_addr, {"login":login,"key":password})
    
    r = make_request(s.get, READ_BOOK+book_id, team_addr)
    res = [x.text for x in BeautifulSoup(r.text, 'html.parser').find_all('span', {'class':'badge badge-pill badge-info'})]
    if flag in res:
        close(OK)
    close(CORRUPT, "Service corrupted", "Flag '{}' not in {}".format(flag, res))


def error_arg(*args):
    close(CHECKER_ERROR, "Wrong command {}".format(sys.argv[1]))

COMMANDS = {
    'check': check, 
    'put': put, 
    'get': get, 
    'info': info
}

if __name__ == '__main__':
    try:
        COMMANDS.get(sys.argv[1], error_arg)(*sys.argv[2:])
    except Exception as ex:
        close(CHECKER_ERROR, "Checker error", "INTERNAL ERROR: {}".format(ex))