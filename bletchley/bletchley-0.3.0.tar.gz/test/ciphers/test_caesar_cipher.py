""" File containing unit tests for caesar_ciper """
import pytest
import string
import random
from ciphers.caesar_cipher import CaesarCipher

@pytest.fixture
def cipher():
    return CaesarCipher()

def data(lengths):
    words = []
    for length in lengths:
        words.append(key(length))
    return words

def key(length):
    word = ""
    for x in range(length):
        word += random.choice(list(string.ascii_lowercase))
    return word

@pytest.mark.parametrize("shift", range(0, 27))
@pytest.mark.parametrize("data", data(range(1, 50)))
def test_decryption(cipher, data, shift):
    cipher_text = cipher.encrypt(data, shift)
    plain_text = cipher.decrypt(cipher_text, shift)
    assert plain_text.upper() == data.upper()

@pytest.mark.parametrize("shift", range(0, 27))
@pytest.mark.parametrize("data", data(range(1, 50)))
def test_encryption(cipher, data, shift):
    cipher_text = cipher.encrypt(data, shift)
    if shift != 26 and shift != 0:
        assert cipher_text.upper() != data.upper()