# -*- coding:utf-8 -*-

import six
import unittest
from hypothesis import given
import hypothesis.strategies as st
from knob.crypt import *


KEY_CHARS = u"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz01234567890,./~!@#$%^&*()_+-={}|[];:'<>? " + u'"'

TEXT_CHARS = KEY_CHARS + u"汉字中文"


class TestCrypt(unittest.TestCase):
    @given(st.text(alphabet=KEY_CHARS, min_size=0, max_size=128), st.text(alphabet=TEXT_CHARS, min_size=0, max_size=1024))
    def test_enc_dec(self, key, text):
        encrypted = encrypt(text, key)
        decrypted = decrypt(encrypted, key)
        self.assertEqual(text, decrypted)


if __name__ == '__main__':
    unittest.main()
