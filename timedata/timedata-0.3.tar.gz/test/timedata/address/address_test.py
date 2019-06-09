import unittest
from timedata.address.address import Address


class AddressTest(unittest.TestCase):
    def _address(self, desc, expected=None):
        address = Address(desc)
        self.assertEqual(str(address), expected or desc)
        return address

    def test_empty(self):
        address = self._address('')
        self.assertFalse(address)
        self.assertFalse(address.segments)
        self.assertFalse(address.assignment)
        self.assertEqual(address.get(23), 23)
        with self.assertRaises(ValueError):
            address.set(self, 23)
        self.assertEqual(str(address), '')

    def test_error(self):
        with self.assertRaises(ValueError):
            Address('ab[cd()]')
        BAD = (
            '.a.b.',
            '.a.bar() = 3',
            'a.',
            'a..b',
            'a.()',
            'a.[2]',
            'a[2]b',
            'a()b',
            'a[()cd]',
            '!',
            '?',
        )
        for i in BAD:
            with self.assertRaises(ValueError):
                Address(i)

    def test_attrib(self):
        address = self._address('attr', '.attr')
        self.assertEqual(str(address), '.attr')
        self.assertEqual(len(address.segments), 1)
        self.attr = 'bingo'
        self.assertIs(address.get(self), 'bingo')
        address.set(self, 'bang')
        self.assertIs(address.get(self), 'bang')

    def test_attrib_error(self):
        address = self._address('.attr')
        self.assertEqual(str(address), '.attr')
        with self.assertRaises(AttributeError):
            address.get(AddressTest)

        with self.assertRaises(AttributeError):
            address.get(0)

    def test_array(self):
        address = self._address('[1]')
        self.assertEqual(str(address), '[1]')
        self.assertEqual(len(address.segments), 1)
        data = [2, 4, 6]
        self.assertEqual(address.get(data), 4)
        address.set(data, 3)
        self.assertEqual(data, [2, 3, 6])

    def test_array_error(self):
        address = self._address('[1]')
        with self.assertRaises(IndexError):
            address.get([0])

        with self.assertRaises(IndexError):
            address.set([0], 5)

        with self.assertRaises(TypeError):
            address.get(0)

    def test_compound(self):
        self.attr1 = [{'test': [None, {'heck': self}]}, 'x', 'y']
        self.attr2 = self
        self.attr3 = 'bingo'

        desc = '.attr1[0][test][1][heck].attr2.attr3'
        address = self._address(desc)
        self.assertEqual(str(address), desc)
        self.assertEqual(len(address.segments), 7)
        self.assertEqual(address.get(self), 'bingo')
        address.set(self, 'bang')
        self.assertEqual(self.attr3, 'bang')

    def call(self, x):
        self.call_result = 23

    def test_trivial_call(self):
        address = self._address('()')
        self.assertEqual(len(address.segments), 1)
        result = []

        address.set(result.append, 'value')
        self.assertEqual(result, ['value'])

    def test_call(self):
        address = self._address('.call()')
        self.assertEqual(len(address.segments), 2)
        address.set(self, 23)
        self.assertEqual(self.call_result, 23)

    def call2(self):
        return None, lambda: self

    def test_call_complex(self):
        self.results = []
        address = self._address('.call2()[1]().call()')
        self.assertEqual(len(address.segments), 6)
        address.set(self, 23)
        self.assertEqual(self.call_result, 23)
        del self.call_result

    def test_compound_error(self):
        address = self._address('.attr1[0][test][1][heck].attr2.attr3')

        with self.assertRaises(AttributeError):
            address.get(self)

        self.attr1 = None
        with self.assertRaises(TypeError):
            address.get(self)

        with self.assertRaises(TypeError):
            address.set(self, 2)

    def test_segment_start_with_index(self):
        self._address('[1]')
        with self.assertRaises(ValueError):
            self._address('foo.[1]')

    def test_assignment(self):
        self.attr = None
        self._address('.attr = 1').set(self)
        self.assertEqual(self.attr, 1)

        self.attr = None
        self._address('.attr = 1, 2.5, 3').set(self)
        self.assertEqual(self.attr, (1, 2.5, 3))

        self.attr = None
        self._address('.attr = 1, bugs, this is 32').set(self)
        self.assertEqual(self.attr, (1, 'bugs', 'this is 32'))
