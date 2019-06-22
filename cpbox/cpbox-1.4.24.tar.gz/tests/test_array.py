import unittest
from cpbox.tool import array

class TestArray(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_merge(self):
        a = {'first': {'all_rows': {'pass': 'dog', 'number': '1'}}}
        b = {'first': {'all_rows': {'fail': 'cat', 'number': '5'}}}
        self.assertEqual(array.merge(a, b), {'first': {'all_rows': {'pass': 'dog', 'fail': 'cat', 'number': '5'}}})

        a = {'first': {}}
        b = {'first': {'name': 'Maya'}}
        self.assertEqual(array.merge(a, b), b)

        a = {'first': {}}
        b = {'first': {'name': 'Maya'}}
        self.assertEqual(array.merge(b, a), b)

if __name__ =='__main__':
    unittest.main()
