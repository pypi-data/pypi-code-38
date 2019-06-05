import unittest
import random
import string
from ..string_utils.trie import SimpleTrie


class TestClientMethods(unittest.TestCase):

    @staticmethod
    def _generate_random_string(length):
        return ''.join(
            random.choice(string.ascii_letters) for i in range(length))

    def test_simpletrie(self):
        ptrie = SimpleTrie()
        inputs = ('123456789', 'abcdefghijk', 'lmnopq')
        for x in inputs:
            ptrie.add(x)
        for x in inputs:
            self.assertTrue(ptrie.exact_string_match(x))
            self.assertFalse(ptrie.exact_string_match(x + '1'))
            self.assertFalse(ptrie.exact_string_match(x[:-1]))
        self.assertTrue(ptrie.approximate_string_match('1234567', 2)[0])
        self.assertTrue(ptrie.approximate_string_match('123456712', 2)[0])
        self.assertTrue(ptrie.approximate_string_match('12345678912', 2)[0])
        self.assertFalse(ptrie.approximate_string_match('1234567', 1)[0])
        self.assertFalse(ptrie.approximate_string_match('123456712', 1)[0])
        self.assertFalse(ptrie.approximate_string_match('12345678912', 1)[0])

        inputs = [self._generate_random_string(15) for x in range(100000)]
        for s in inputs:
            ptrie.add(s)
        self.assertTrue(ptrie.exact_string_match(inputs[0]))
        self.assertFalse(ptrie.exact_string_match(inputs[0] + '1'))
        self.assertFalse(ptrie.exact_string_match(inputs[0][:-1]))
        self.assertTrue(ptrie.approximate_string_match(inputs[0], 2)[0])
        self.assertFalse(ptrie.approximate_string_match(inputs[0][-1], 2)[0])
        self.assertFalse(
            ptrie.approximate_string_match(inputs[0] + '!@#', 2)[0])
        self.assertFalse(
            ptrie.approximate_string_match(inputs[0][-3] + '!@#', 2)[0])

    if __name__ == '__main__':
        unittest.main()
