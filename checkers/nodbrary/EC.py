from collections import namedtuple
from Crypto.Util.number import inverse

Point = namedtuple("Point", ["x", "y"])

class EC(object):
    """System of Elliptic Curve"""
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p
        self.zero = Point(0, 0)

    def is_valid(self, p):
        if p == self.zero: 
            return True
        l = (p.y ** 2) % self.p
        r = ((p.x ** 3) + self.a * p.x + self.b) % self.p
        return l == r

    def add(self, p1, p2):
        if p1 == self.zero: 
            return p2
        if p2 == self.zero: 
            return p1
        if p1.x == p2.x and (p1.y != p2.y or p1.y == 0):
            return self.zero
        if p1.x == p2.x:
            l = (3 * p1.x * p1.x + self.a) * inverse(2 * p1.y, self.p) % self.p
        else:
            l = (p2.y - p1.y) * inverse(p2.x - p1.x, self.p) % self.p
        x = (l * l - p1.x - p2.x) % self.p
        y = (l * (p1.x - x) - p1.y) % self.p
        return Point(x, y)

    def mul(self, p, n):
        r = self.zero
        while 0 < n:
            if n & 1 == 1:
                r = self.add(r, p)
            n, p = n >> 1, self.add(p, p)
        return r

    def order(self, g, n):
        g = Point(*g)
        if not (self.is_valid(g) and g != self.zero):
            return False
        return self.mul(g, n) == self.zero

    def point(self, x, y):
        return Point(x, y)