""" File containing unit tests for vic_ciper """
import pytest
import string
import random
import numpy as np
from ciphers.vic_cipher import VICCipher

@pytest.fixture
def cipher():
    return VICCipher()

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
    checkerboard = cipher.generate_checkerboard()
    cipher_text = cipher.encrypt(data, checkerboard)
    plain_text = cipher.decrypt(cipher_text, checkerboard)
    assert plain_text.upper() == data.upper()

@pytest.mark.parametrize("data", data(range(1, 50)))
def test_encryption(cipher, data):
    checkerboard = cipher.generate_checkerboard()
    cipher_text = cipher.encrypt(data, checkerboard)
    assert cipher_text.upper() != data.upper()

def test_invalid_checkerboard():
    checkerboard = np.asarray([])
    with pytest.raises(Exception) as e_info:
        cipher.check_checker_board(checkerboard)

def test_generate_checkerboard(cipher):
    checkerboard = cipher.generate_checkerboard()
    assert checkerboard.shape == (3, 10)
    assert cipher.check_checker_board(checkerboard)

