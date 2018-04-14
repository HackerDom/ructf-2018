from json import loads, dumps
from base64 import b64decode
from EC import EC
from csv import DictReader
from random import randint

import re

def decode_cookie(cookie):
    data = loads(b64decode(cookie).decode())
    return {x:int(y, 16) for x,y in data.items()}

def check_curve(cookie):
    curve = decode_cookie(cookie)
    ec = EC(*tuple(map(curve.get, 'abp')))

    if (4 * pow(ec.a, 3) + 27 * pow(ec.b, 2)) % ec.p == 0:
        return False
    
    g = curve['gX'], curve['gY']
    return ec.order(g, curve['n'])

def check_journal(bs, cookie):
    pattern = re.compile("\d+\) ([a-z0-9]+).+\.\( ([a-f0-9]{4,}), ([a-f0-9]{4,}) \).+\( ([a-f0-9]{4,}),? ?([a-f0-9]{4,})? \)")
    curve = decode_cookie(cookie)
    ec = EC(*tuple(map(curve.get, 'abp')))

    arr = []
    res = (x.text for x in bs.find_all("p", {"class":"card-text"}))
    for tag in res:
        name, pub_x, pub_y, s, r = pattern.search(tag).groups()
        arr.append(r)
        pub_x, pub_y = map(lambda x:int(x,16), (pub_x, pub_y))
        pub_point = ec.point(pub_x, pub_y)
        if not ec.is_valid(pub_point):
            return False
    
    return any(arr)

    
def get_book():
    r = randint(0, 1000)
    with open('result.csv', 'r') as f:
        for i, book in enumerate(DictReader(f)):
            if i == r:
                return book