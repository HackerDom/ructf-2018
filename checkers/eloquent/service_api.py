import json
from enum import Enum
from time import sleep

import re
import requests
from requests.cookies import RequestsCookieJar
from requests.exceptions import ConnectTimeout, ConnectionError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

PORT = 8080


SIGNUP_URL = "http://{host}:{port}/registration"
SIGNIN_URL = "http://{host}:{port}/login"
CREATE_ARTICLE_URL = "http://{host}:{port}/create"
REGISTER_URL = "http://{host}:{port}/register"
LOGIN_URL = "http://{host}:{port}/signin"
POST_ARTICLE_URL = "http://{host}:{port}/post-article"
SUGGEST_ARTICLE_URL = "http://{host}:{port}/post-article?user={user}"
GET_ARTICLE_URL = "http://{host}:{port}/article/{article_id}"
SET_VAL_BY_NAME_SCRIPT_TEMPLATE = """$('[name="{}"]').val("{}")"""
MY_SUGGESTIONS = "http://{host}:{port}/suggestions"
MY_ARTICLES = "http://{host}:{port}/my-articles"
TABLE_OF_CONTENTS_PATTERN = re.compile(r'<a\shref=\"#(.+)\">.{1,5}\)')

ARTICLE_BTN_TEMPLATE = re.compile(r'<a\shref=\"/article/(\d+)\"\sclass=\"btn\sbtn-primary\sbottom-btn\"')
ARTICLE_ID_TEMPLATE = re.compile(r"/article/(\d+)")

TIMEOUT = 2


class ExceptionType(Enum):
    MUMBLE = 103
    DOWN = 104


class ApiException(Exception):
    def __init__(self, exc_type, exc_message):
        self.exc_type = exc_type
        self.exc_message = exc_message


def api_method(func):
    def patched_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.ConnectionError as e:
            raise ApiException(ExceptionType.DOWN, 'in function {}, exception: {}'.format(func, e))
        except requests.HTTPError as e:
            raise ApiException(ExceptionType.MUMBLE, 'in function {}, exception: {}'.format(func, e))
    return patched_func


def get_driver():
    # driver = webdriver.PhantomJS(service_log_path='/dev/null')
    # driver.set_window_size(1600, 900)
    # return driver
    return webdriver.Chrome()


@api_method
def signup(host, login, password):
    r = requests.post(
        url=REGISTER_URL.format(host=host, port=PORT),
        data={'username': login, 'password': password},
        timeout=TIMEOUT
    )
    r.raise_for_status()
    return r.request._cookies


@api_method
def signin(host, login, password):
    r = requests.post(
        url=LOGIN_URL.format(host=host, port=PORT),
        data={'username': login, 'password': password},
        timeout=TIMEOUT
    )
    r.raise_for_status()
    return r.request._cookies


@api_method
def post_article(host, cookies, title, content):
    r = requests.post(
        url=POST_ARTICLE_URL.format(host=host, port=PORT),
        cookies=cookies,
        data={'title': title, 'content': content},
        timeout=TIMEOUT
    )
    r.raise_for_status()


@api_method
def suggest_article(host, cookies, title, content, user):
    r = requests.post(
        url=SUGGEST_ARTICLE_URL.format(host=host, port=PORT, user=user),
        cookies=cookies,
        data={'title': title, 'content': content},
        timeout=TIMEOUT
    )
    r.raise_for_status()
    return True


@api_method
def get_article_content(host, cookies, article_id):
    r = requests.get(
        url=GET_ARTICLE_URL.format(host=host, port=PORT, article_id=article_id),
        cookies=cookies,
        timeout=TIMEOUT
    )
    r.raise_for_status()
    return r.content.decode()


def sign_in_with_driver(driver, host, login, password):
    driver.get(SIGNIN_URL.format(host=host, port=PORT))
    send_keys_to_field(driver, 'username', login)
    send_keys_to_field(driver, 'password', password)
    send_keys_to_field(driver, 'password', Keys.ENTER)


@api_method
def get_article_id_by_cookies(host, cookies, from_suggestions=True):
    pattern = MY_SUGGESTIONS if from_suggestions else MY_ARTICLES
    r = requests.get(
        url=pattern.format(host=host, port=PORT),
        cookies=cookies,
        timeout=TIMEOUT
    )
    r.raise_for_status()
    content = r.content.decode()
    article_id = ARTICLE_ID_TEMPLATE.search(content).group(1)
    return article_id


@api_method
def get_suggestions_by_cookies(host, cookies):
    r = requests.get(
        url=MY_SUGGESTIONS.format(host=host, port=PORT),
        cookies=cookies,
        timeout=TIMEOUT
    )
    r.raise_for_status()
    return r.content.decode()


def get_page_of_article(driver, host, article_id):
    driver.get(url=GET_ARTICLE_URL.format(host=host, port=PORT, article_id=article_id))


def click_link(driver, href):
    driver.find_element_by_css_selector('a[href="{}"]'.format(href)).click()


def get_element_text_by_id(driver, element_id):
    return driver.find_element_by_id(element_id).text


def send_keys_to_field(driver, field_name, keys):
    field = driver.find_element_by_name(field_name)
    field.send_keys(keys)


def set_field_val_by_name(driver, field_name, value):
    driver.execute_script(SET_VAL_BY_NAME_SCRIPT_TEMPLATE.format(field_name, value))


def emulate_articles_view(driver, host, username, password):
    sign_in_with_driver(driver, host, username, password)
    sleep(10)
    driver.get(MY_SUGGESTIONS.format(host=host, port=PORT))
    source = driver.page_source
    for article_id in re.findall(ARTICLE_BTN_TEMPLATE, source):
        driver.get(GET_ARTICLE_URL.format(host=host, port=PORT, article_id=article_id))
        for href in re.findall(TABLE_OF_CONTENTS_PATTERN, driver.page_source):
            click_link(driver, '#' + href)
