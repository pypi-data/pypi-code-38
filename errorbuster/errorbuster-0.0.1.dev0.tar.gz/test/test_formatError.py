from unittest import TestCase
from errorbuster import formatError


class A(object):
    def func_add(self, x, y):
        print x, "/", y, "=", x/y

class B(object):
    def __init__(self, a):
        self.a = a

    def process(self, a, b):
        self.a.func_add(a, b)

class TestFormatError(TestCase):
    def test_formatError(self):
        b = B(A())
        try:
            b.process(1, 0)
        except Exception as e:
            print formatError(e)
        self.assertTrue(True)
