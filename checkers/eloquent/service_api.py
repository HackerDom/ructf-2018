import json
from time import sleep

import requests
from requests.cookies import RequestsCookieJar
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

PORT = 8080


SIGNUP_URL = "http://{host}:{port}/registration"
SIGNIN_URL = "http://{host}:{port}/login"
CREATE_ARTICLE_URL = "http://{host}:{port}/create"
REGISTER_URL = "http://{host}:{port}/register"
LOGIN_URL = "http://{host}:{port}/signin"
POST_ARTICLE_URL = "http://{host}:{port}/post-article"
GET_ARTICLE_URL = "http://{host}:{port}/article/{article_id}"
SET_VAL_BY_NAME_SCRIPT_TEMPLATE = """$('[name="{}"]').val("{}")"""


def get_driver():
    driver = webdriver.PhantomJS(service_log_path='/dev/null')
    driver.set_window_size(1600, 900)
    return driver


def signup(host, login, password):
    r = requests.post(
        url=REGISTER_URL.format(host, PORT),
        data={'username': login, 'password': password},
        timeout=15
    )
    return r.request._cookies


def signin(host, login, password):
    r = requests.post(
        url=LOGIN_URL.format(host=host, port=PORT),
        data={'username': login, 'password': password},
        timeout=15
    )
    return r.request._cookies


def post_article(host, cookies, title, content):
    requests.post(
        url=POST_ARTICLE_URL.format(host, PORT),
        cookies=cookies,
        data={'title': title, 'content': content},
        timeout=15
    )


def get_article_content(host, cookies, article_id):
    r = requests.get(
        url=GET_ARTICLE_URL.format(host=host, port=PORT, article_id=article_id),
        cookies=cookies,
        timeout=15
    )
    return r.content.decode()


def sign_in_with_driver(driver, host, login, password):
    driver.get(SIGNIN_URL.format(host=host, port=PORT))
    send_keys_to_field(driver, 'username', login)
    send_keys_to_field(driver, 'password', password)
    send_keys_to_field(driver, 'password', Keys.ENTER)


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
