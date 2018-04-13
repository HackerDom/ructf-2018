from random import choice, randint
from string import digits, ascii_letters

from bullshit_generator import gen_sentence


MAX_ARTICLE_CONTENT_LENGTH = 1000000


with open("NAMES") as names_file:
    NAMES = names_file.read().split('\n')


with open("user-agents") as user_agents_file:
    USER_AGENTS = user_agents_file.read().split('\n')


def gen_login():
    return '{}-{}'.format(choice(NAMES), "".join(choice(digits) for _ in range(9)))


def gen_password():
    return "".join(choice(ascii_letters + digits) for _ in range(20))


def gen_flag():
    return '==' + ''.join(choice(digits + ascii_letters) for _ in range(10))


def gen_user_agent():
    return choice(USER_AGENTS)


def gen_headers():
    return {'User-Agent': gen_user_agent()}


def gen_article_title():
    return gen_sentence(40)[:50]


def gen_article_content():
    sentences = [gen_sentence() for _ in range(20)]
    i = randint(0, 9)
    sentences.insert(i, "\n#{}\n".format(sentences[i].split()[0]))
    i = randint(10, 19)
    sentences.insert(i, "\n#{}\n".format(sentences[i].split()[0]))
    return ' '.join(sentences)[:1000000]
