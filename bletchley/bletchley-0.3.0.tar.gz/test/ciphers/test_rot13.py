""" File containing unit tests for rot13_ciper """
import pytest
import string
import random
from ciphers.rot13_cipher import ROT13Cipher

@pytest.fixture
def cipher():
    return ROT13Cipher()

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

@pytest.mark.parametrize("data", data(range(1, 50)))
def test_decryption(cipher, data):
    cipher_text = cipher.encrypt(data)
    plain_text = cipher.decrypt(cipher_text)
    assert plain_text.upper() == data.upper()

@pytest.mark.parametrize("data", data(range(1, 50)))
def test_encryption(cipher, data):
    cipher_text = cipher.encrypt(data)
    assert cipher_text.upper() != data.upper()
