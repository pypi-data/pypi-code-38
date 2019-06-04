""" File containing unit tests for adfgvx_ciper """
import pytest
import string
import random
from ciphers.adfgvx_cipher import ADFGVXCipher

@pytest.fixture
def cipher():
    return ADFGVXCipher()

def data(lengths):
    words = []
    for length in lengths:
        words.append(key_numeric(length))
    return words

def key(length):
    word = ""
    for x in range(length):
        word += random.choice(list(string.ascii_lowercase))
    return word

def key_numeric(length):
    word = ""
    for x in range(length):
        word += random.choice(list(string.ascii_lowercase + string.digits))
    return word

def keys(lengths):
    words = []
    for length in lengths:
        words.append(key(length))
    return words

@pytest.mark.parametrize("key", keys(range(1, 10)))
@pytest.mark.parametrize("data", data(range(1, 50)))
def test_decryption(cipher, data, key):
    polybius = cipher.generate_polybius()
    cipher_text = cipher.encrypt(data, polybius, key)
    plain_text = cipher.decrypt(cipher_text, polybius, key)
    assert plain_text.upper() == data.upper()

@pytest.mark.parametrize("key", keys(range(1, 10)))
@pytest.mark.parametrize("data", data(range(1, 50)))
def test_encryption(cipher, data, key):
    polybius = cipher.generate_polybius()
    cipher_text = cipher.encrypt(data, polybius, key)
    assert cipher_text.upper() != data.upper()

def test_generate_polybius(cipher):
    polybius = cipher.generate_polybius()
    assert polybius.shape == (6, 6)