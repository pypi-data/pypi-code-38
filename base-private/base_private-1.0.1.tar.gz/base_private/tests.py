from __future__ import unicode_literals

import unittest

from hypothesis import given
from hypothesis.strategies import binary, integers

from base_private import decode, decode_bits, encode, encode_bits


class AlgoritmTest(unittest.TestCase):
    def test_encode_bits(self):
        for args, encoded in (
                ((b'\x00\x00', 16), '\U000F0000'),
                ((b'\x00', 8), '\U00100100'),
                ((b'\xff\xfe', 16), '\ue8fe'),
                ((b'\xff\xff', 16), '\ue8ff'),
                ((b'\xfe', 8), '\U001001FE'),
                ((b'\xff', 8), '\U001001FF'),
         ):
            with self.subTest(args=args):
                self.assertEqual(encode_bits(*args), encoded)

    def test_decode_bits(self):
        for codepoints, decoded in (
                ('', (b'', 0)),
                ('\U000F0000', (b'\x00\x00', 16)),
                ('\U00100100', (b'\x00', 8)),
                ('\ue8fe', (b'\xff\xfe', 16)),
                ('\ue8ff', (b'\xff\xff', 16)),
        ):
            with self.subTest(codepoints=codepoints):
                self.assertEqual(decode_bits(codepoints), decoded)


class PropertiesTest(unittest.TestCase):
    @given(binary(), integers(0, 7))
    def test_roundtrip_bits(self, data, pad):
        bits = max(len(data) * 8 - pad, 0)
        # 0-out the pad bits
        if data and pad > 0:
            data = bytearray(data)
            data[-1] = ((data[-1] >> pad) << pad)
            data = bytes(data)
        self.assertEqual(
            (data, bits),
            decode_bits(encode_bits(data, bits)),
        )

    @given(binary())
    def test_roundtrip_bytes(self, data):
        self.assertEqual(data, decode(encode(data)))
