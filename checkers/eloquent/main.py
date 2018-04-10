from time import sleep, time

import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


from generators import gen_article_title, gen_article_content, gen_login, gen_password

PORT = 8080
HOST = "0.0.0.0"


SIGNUP_URL = "http://%s:%d/registration" % (HOST, PORT)
SIGNIN_URL = "http://%s:%d/login" % (HOST, PORT)
CREATE_ARTICLE_URL = "http://%s:%d/create" % (HOST, PORT)

REGISTER_URL = "http://%s:%d/register" % (HOST, PORT)
LOGIN_URL = "http://%s:%d/signin" % (HOST, PORT)
POST_ARTICLE_URL = "http://%s:%d/post-article" % (HOST, PORT)


SET_VAL_BY_NAME_SCRIPT_TEMPLATE = """$('[name="{}"]').val("{}")"""


def get_driver():
    return webdriver.PhantomJS(service_log_path='/dev/null')


def send_keys_to_field(driver, field_name, keys):
    field = driver.find_element_by_name(field_name)
    field.send_keys(keys)


def set_field_val_by_name(driver, field_name, value):
    driver.execute_script(SET_VAL_BY_NAME_SCRIPT_TEMPLATE.format(field_name, value))


def signup_(login, password):
    r = requests.post(REGISTER_URL, data={'username': login, 'password': password})
    return r.request._cookies


def signin_(login, password):
    r = requests.post(LOGIN_URL, data={'username': login, 'password': password})
    return r.request._cookies


def post_article_(cookies, title, content):
    requests.post(POST_ARTICLE_URL, cookies=cookies, data={'title': title, 'content': content})


def signup(driver, login, password):
    driver.get(SIGNUP_URL)
    send_keys_to_field(driver, "username", login)
    send_keys_to_field(driver, "password", password)
    send_keys_to_field(driver, "password", Keys.ENTER)


def signin(driver, login, password):
    driver.get(SIGNIN_URL)
    send_keys_to_field(driver, "username", login)
    send_keys_to_field(driver, "password", password)
    send_keys_to_field(driver, "password", Keys.ENTER)


def post_article(driver, title, content):
    driver.get(CREATE_ARTICLE_URL)
    send_keys_to_field(driver, 'title', title)
    set_field_val_by_name(driver, 'content', content.replace('\n', r'\n'))
    post_btn = driver.find_element_by_id('post-btn')
    post_btn.click()


def main():
    driver = get_driver()
    start = time()
    signup(driver, gen_login(), gen_password())
    post_article(driver, gen_article_title(), gen_article_content())
    print(time() - start)
    driver.close()

    start = time()
    cookies = signup_(gen_login(), gen_password())
    post_article_(cookies, gen_article_title(), gen_article_content())
    print(time() - start)


if __name__ == '__main__':
    main()


"""
chrome  3857477632
phantom 2831765504
firefox 5664231424
"""
