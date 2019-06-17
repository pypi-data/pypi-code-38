"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
from unittest import TestCase

from pynetworking.Data import general_pack, general_unpack, ByteStream

from pynetworking.tests.example_functions import DummyPerson


def single_value(test_self, value):
    byte_string = general_pack(value)
    byte_stream = ByteStream(byte_string)
    new_value = general_unpack(byte_stream)[0]
    test_self.assertEqual(value, new_value)


class TestPacking(TestCase):

    def test_int(self):
        single_value(self, -890)

    def test_float(self):
        single_value(self, 212400.7598823849019)

    def test_str_special_chars(self):
        string = "!$Hqä \n}\t."
        single_value(self, string)

    def test_str_long(self):
        # Warning: strings with length more than 2**30 will crash the PC
        string = "W" * 2**20
        single_value(self, string)

    def test_list(self):
        value = [[i for i in range(2)]].append([i for i in range(2)])
        single_value(self, value)

    def test_dict(self):
        value = {"val1": 1, "väl2": "Hä llo", "val3": [((2, 6), 1), 7]}
        single_value(self, value)

    def test_tuple(self):
        single_value(self, ("Hello", 10, [2, 0]))
        single_value(self, ())

    def test_bool(self):
        single_value(self, True)

    def test_bytes(self):
        single_value(self, b"Hello")

    def test_None(self):
        single_value(self, None)

    def test_object(self):
        single_value(self, DummyPerson("John", 90))

    def test_lambda(self):
        byte_string = general_pack(lambda x, y: x + y)
        byte_stream = ByteStream(byte_string)
        new_value = general_unpack(byte_stream)[0]
        self.assertEqual(10, new_value(5, 5))



