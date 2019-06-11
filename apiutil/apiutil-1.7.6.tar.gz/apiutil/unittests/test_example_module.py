
import unittest
import apiutil
from apiutil import _metadata


class TestExample(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # Instantiation
    def test_version(self):
        self.assertEqual(apiutil.__version__, _metadata.__version__, u'Version is incorrect')


if __name__ == u'__main__':
    unittest.main()
