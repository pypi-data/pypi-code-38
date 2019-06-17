"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
from unittest import TestCase

from pynetworking.Data import ByteStream, pack_int


class TestByteStream(TestCase):

    def test_init(self):
        byte_string = b""
        byte_stream = ByteStream(byte_string)
        self.assertEqual(byte_stream.byte_string, b"")
        self.assertEqual(byte_stream.length, 0)
        self.assertEqual(byte_stream.idx, 0)
        self.assertEqual(byte_stream.remaining_length, 0)
        self.assertEqual(byte_stream.reached_end, True)

    def test_next_int(self):
        first_int = 102
        second_int = 2089
        example_byte_string = pack_int(first_int) + pack_int(second_int)
        byte_stream = ByteStream(example_byte_string)

        next_int = byte_stream.next_int()
        self.assertEqual(next_int, first_int)
        next_int = byte_stream.next_int()
        self.assertEqual(next_int, second_int)

    def test_next_bytes(self):
        example_byte_string = b"Hello World"
        byte_stream = ByteStream(example_byte_string)
        expected = b"Hello"
        actual = byte_stream.next_bytes(5)
        self.assertEqual(expected, actual)

    def test_next_bytes_error(self):
        example_byte_string = b"H"
        byte_stream = ByteStream(example_byte_string)
        self.assertRaises(IndexError, byte_stream.next_bytes, 5)
        self.assertRaises(AssertionError, byte_stream.next_bytes, -2)

    def test_iadd(self):
        byte_stream = ByteStream(b"Hello")
        add = b"Hello"
        byte_stream += add
        expected = b"HelloHello"
        self.assertEqual(byte_stream.byte_string, expected)
        self.assertEqual(byte_stream.reached_end, False)

    def test_remove_consumed_bytes(self):
        byte_stream = ByteStream(b"Hello World")
        byte_stream.next_bytes(len(b"Hello "))
        byte_stream.remove_consumed_bytes()
        expected = b"World"
        self.assertEqual(byte_stream.byte_string, expected)

        byte_stream = ByteStream(b"Hello World")
        byte_stream.next_bytes(len(b"Hello World"))
        byte_stream.remove_consumed_bytes()
        self.assertEqual(byte_stream.reached_end, True)
