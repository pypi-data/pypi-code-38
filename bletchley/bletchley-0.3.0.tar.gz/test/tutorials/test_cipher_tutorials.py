""" File containing integration tests for cipher tutorials """
import pytest

def test_simple_cipher_tutorial():
        from bletchley.ciphers.rot13_cipher import ROT13Cipher
        my_cipher = ROT13Cipher()
        my_message = "HelloWorld"
        cipher_text = my_cipher.encrypt(my_message)
        plain_text = my_cipher.decrypt(cipher_text)
        assert plain_text.upper() == my_message.upper()

def test_advanced_cipher_tutorial():
        from bletchley.ciphers.vic_cipher import VICCipher
        my_cipher = VICCipher()
        my_checkerboard = my_cipher.generate_checkerboard()
        my_message = "HelloWorld"
        cipher_text = my_cipher.encrypt(my_message, my_checkerboard)
        plain_text = my_cipher.decrypt(cipher_text, my_checkerboard)
        assert plain_text.upper() == my_message.upper()