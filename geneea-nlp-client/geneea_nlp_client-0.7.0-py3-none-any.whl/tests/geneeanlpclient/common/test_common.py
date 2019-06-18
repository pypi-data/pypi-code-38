
from unittest import TestCase

from geneeanlpclient.common.common import isSequential, toBool


class TestCommon(TestCase):

    def test_isSequential(self):
        self.assertTrue(isSequential([1, 2, 3, 4, 5]))
        self.assertTrue(isSequential([-1, 0, 1]))
        self.assertTrue(isSequential([0]))
        self.assertTrue(isSequential([5]))
        self.assertTrue(isSequential([]))

        self.assertFalse(isSequential([1, 2, 3, 5]))
        self.assertFalse(isSequential([1, 1]))
        self.assertFalse(isSequential([1, 0]))

    def test_toBool(self):
        self.assertTrue(toBool(True))
        self.assertTrue(toBool(' TRUE '))
        self.assertTrue(toBool('true'))
        self.assertTrue(toBool('1'))
        self.assertTrue(toBool(1))

        self.assertFalse(toBool(None))
        self.assertFalse(toBool(False))
        self.assertFalse(toBool('Yes'))
        self.assertFalse(toBool('anything'))
        self.assertFalse(toBool(0))
        self.assertFalse(toBool(2))
        self.assertFalse(toBool([True]))
        self.assertFalse(toBool({'my': 'dict'}))
