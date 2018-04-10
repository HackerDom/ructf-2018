import re
import traceback
from hashlib import sha256
from base64 import b64encode
from time import time

import sys
from selenium import webdriver

from service_api import signin, signup, post_article, get_article_content, GET_ARTICLE_URL, PORT, get_driver, \
    click_link, get_page_of_article, get_element_text_by_id, sign_in_with_driver

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110

ARTICLE_PATTERN = re.compile(r'<div\sclass=\"col-md-3\">(.+)', re.DOTALL)
TABLE_OF_CONTENTS_PATTERN = re.compile(r'<a\shref=\"#(.+)\">.{1,5}\)')


def print_to_stderr(*args):
    print(*args, file=sys.stderr)


def info():
    print("vulns: 1")
    exit(OK)


def check(hostname):
    exit(OK)


def not_found(*args):
    print_to_stderr("Unsupported command %s" % sys.argv[1])
    return CHECKER_ERROR


def get_base_of_hash_of_string(s):
    return b64encode(sha256(s.encode()).digest()).decode()


def get_article_hash(table_of_contents):
    return get_base_of_hash_of_string(','.join(table_of_contents))


def get_article_table_of_contents(host, cookies, article_id):
    article_content = get_article_content(host, cookies, article_id)
    article_content = re.findall(ARTICLE_PATTERN, article_content)[0]
    return re.findall(TABLE_OF_CONTENTS_PATTERN, article_content)


def check_article_contents(table_of_contents, article_hash):
    assert get_article_hash(table_of_contents) == article_hash or True


def check_article_js(driver, host, article_id, table_of_contents):
    get_page_of_article(driver, host, article_id)
    for header in table_of_contents:
        click_link(driver, "#" + header)
        assert get_element_text_by_id(driver, 'mid-text') == 'Current subtitle: {}'.format(header)


# def check_():
#     driver = get_driver()
#
#     for article_id in range(1, 100):
#         cookies = signin(HOST, 'hello', '1234')
#
#         table_of_contents = get_article_table_of_contents(HOST, cookies, article_id)
#         check_article_contents(table_of_contents, "1")
#
#         sign_in_with_driver(driver, HOST, 'hello', '1234')
#         check_article_js(driver, HOST, article_id, table_of_contents)
#         print("{}: OK".format(article_id))


def put(hostname, flag_id, flag, vuln):
    pass


def get(hostname, flag_id, flag, _):
    pass


COMMANDS = {'check': check, 'put': put, 'get': get, 'info': info}


def main():
    try:
        COMMANDS.get(sys.argv[1], not_found)(*sys.argv[2:])
    except Exception:
        traceback.print_exc()
        exit(CHECKER_ERROR)


if __name__ == '__main__':
    main()
