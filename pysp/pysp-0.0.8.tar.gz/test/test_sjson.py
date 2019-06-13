
import unittest

from pysp.sjson import SJson


class InnerL2:
    def __init__(self, *args, **kwargs):
        self.msgs = ['hahaha', 'hohoho']
        self.dict = {
            'hello': 'hi'
        }


class InnerL1:
    def __init__(self, *args, **kwargs):
        self.msg = 'This is message.'
        self.nums = [1, 2]
        self.inner = InnerL2()


class OuterCls:
    def __init__(self, *args, **kwargs):
        self.a = 1.1
        self.b = 2.2
        self.c = 'text'
        self.inner = InnerL1()


class JsonSerialTest(unittest.TestCase):

    def test_json_serial(self):
        ocls = OuterCls()
        jstr = SJson.to_serial(ocls, indent=2)
        ojson = SJson.to_deserial(jstr, globals=globals())

        self.assertTrue(
            ocls.inner.inner.dict['hello'] == ojson.inner.inner.dict['hello'])
        self.assertTrue(
            str(ocls.inner.inner.msgs) == str(ojson.inner.inner.msgs))
        # print(globals())
