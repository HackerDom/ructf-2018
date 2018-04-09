import re
from random import uniform
from collections import defaultdict

r_alphabet = re.compile('[a-zA-Z0-9-]+|[.,:;?!]+')


def gen_lines(corpus):
    for line in open(corpus):
        yield line.lower()


def gen_tokens(lines):
    for line in lines:
        for token in r_alphabet.findall(line):
            yield token


def gen_trigrams(tokens):
    t0, t1 = '$', '$'
    for t2 in tokens:
        yield t0, t1, t2
        if t2 in '.!?':
            yield t1, t2, '$'
            yield t2, '$', '$'
            t0, t1 = '$', '$'
        else:
            t0, t1 = t1, t2


def train(corpus):
    lines = gen_lines(corpus)
    tokens = gen_tokens(lines)
    trigrams = gen_trigrams(tokens)

    bi, tri = defaultdict(float), defaultdict(float)

    for t0, t1, t2 in trigrams:
        bi[t0, t1] += 1
        tri[t0, t1, t2] += 1

    model = {}
    for (t0, t1, t2), freq in tri.items():
        if (t0, t1) in model:
            model[t0, t1].append((t2, freq/bi[t0, t1]))
        else:
            model[t0, t1] = [(t2, freq / bi[t0, t1])]
    return model


def generate_sentence(model, max_length=10000):
    phrase = ''
    t0, t1 = '$', '$'
    while True:
        t0, t1 = t1, unirand(model[t0, t1])
        if (t1 == '$') or (len(phrase) > max_length):
            if phrase[-1] not in ('.', '!', '?'):
                phrase += '.'
            break
        if t1 in '.!?,;:' or t0 == '$':
            phrase += t1
        else:
            phrase += ' ' + t1
    return phrase.capitalize()


def unirand(seq):
    sum_, freq_ = 0, 0
    for item, freq in seq:
        sum_ += freq
    rnd = uniform(0, sum_)
    for token, freq in seq:
        freq_ += freq
        if rnd < freq_:
            return token


war_and_peace_model = train('war_and_peace.txt')


def gen_sentence(max_length=10000):
    return generate_sentence(war_and_peace_model, max_length)
