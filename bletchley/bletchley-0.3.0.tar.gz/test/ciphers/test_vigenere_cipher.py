""" File containing unit tests for vigenere_ciper """
import pytest
import string
import random
from ciphers.vigenere_cipher import VigenereCipher

@pytest.fixture
def cipher():
    return VigenereCipher()

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

def keys(lengths):
    words = []
    for length in lengths:
        words.append(key(length))
    return words

@pytest.mark.parametrize("key", keys(range(1, 10)))
@pytest.mark.parametrize("data", data(range(1, 50)))
def test_decryption(cipher, data, key):
    cipher_text = cipher.encrypt(data, key)
    plain_text = cipher.decrypt(cipher_text, key)
    assert plain_text.upper() == data.upper()

@pytest.mark.parametrize("key", keys(range(2, 10)))
@pytest.mark.parametrize("data", data(range(2, 50)))
def test_encryption(cipher, data, key):
    cipher_text = cipher.encrypt(data, key)
    if key != data:
        assert cipher_text.upper() != data.upper()

