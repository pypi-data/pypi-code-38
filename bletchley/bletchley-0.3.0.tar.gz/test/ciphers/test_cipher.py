""" File containing unit tests for the ciper abstract class """
import pytest
from ciphers.cipher import Cipher

class EmptyCipher(Cipher):
    """ Class for testing the Cipher abstract class """
    def __init__(self):
        pass

    def encrypt(self):
        pass

    def decrypt(self):
        pass

@pytest.fixture
def cipher_implementation():
    return EmptyCipher()

def lower_data():
    return "abcdefghij"

def numerical_data():
    return "123456789"

def mixed_data():
    return "a1b2c3d4e5f6g7h8i9j"

@pytest.mark.parametrize("data, expected", [(lower_data(), lower_data().upper()),
                                            (numerical_data(), ''),
                                            (mixed_data(), lower_data().upper())])
def test_sanitation(cipher_implementation, data, expected):
    sanitsed_text = cipher_implementation.sanitise(data)
    assert sanitsed_text == expected

@pytest.mark.parametrize("data, expected", [(lower_data(), ''),
                                            (numerical_data(), numerical_data()),
                                            (mixed_data(), numerical_data())])
def test_numerical_sanitation(cipher_implementation, data, expected):
    sanitsed_text = cipher_implementation.sanitise_numerical(data)
    assert sanitsed_text == expected

@pytest.mark.parametrize("data, expected", [(lower_data(), lower_data().replace('j', '').upper()),
                                            (numerical_data(), ''),
                                            (mixed_data(), lower_data().replace('j', '').upper())])
def test_sanitation_ij(cipher_implementation, data, expected):
    sanitsed_text = cipher_implementation.sanitise_ij(data)
    assert sanitsed_text == expected

@pytest.mark.parametrize("data, expected", [(lower_data(), lower_data().upper()),
                                            (numerical_data(), numerical_data()),
                                            (mixed_data(), mixed_data().upper())])
def test_sanitation_alphanumeric(cipher_implementation, data, expected):
    sanitsed_text = cipher_implementation.sanitise_alphanumeric(data)
    assert sanitsed_text == expected
