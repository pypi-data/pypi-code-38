
from unittest import TestCase

from geneeanlpclient.common.common import isSequential


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


