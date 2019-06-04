""" Module containing Vigenere cipher """
import logging
from bletchley.ciphers.cipher import Cipher


class VigenereCipher(Cipher):
    """ Implementation of the Vigenere cipher """
    def __init__(self):
        logging.info("Created Vigenere cipher")
        pass

    def encrypt(self, plainttext, key):
        """ Encrypt plain text using Vigenere cipher """
        logging.info("Attempting to encrypt plain text...")
        ciphertext = ''
        plaintext = self.sanitise(plainttext)
        key = self.sanitise(key)
        key_ordinal = [ord(letter) for letter in key]
        plaintext_ordinal = [ord(letter) for letter in plaintext]
        for i in range(len(plaintext)):
            encrypted_value = (plaintext_ordinal[i] +
                               key_ordinal[i % len(key)]) % 26
            ciphertext += chr(encrypted_value + 65)
        logging.info("Successfully encrypted plain text...")
        return ciphertext

    def decrypt(self, ciphertext, key):
        """ Decrypt cipher text using Vigenere cipher """
        logging.info("Attempting to decrypt cipher text...")
        plaintext = ''
        ciphertext = self.sanitise(ciphertext)
        key = self.sanitise(key)
        key_ordinal = [ord(letter) for letter in key]
        ciphertext_ordinal = [ord(letter) for letter in ciphertext]
        for i in range(len(ciphertext)):
            unencrypted_value = (ciphertext_ordinal[i] -
                                 key_ordinal[i % len(key)]) % 26
            plaintext += chr(unencrypted_value + 65)
        logging.info("Successfully decrypted cipher text...")
        return plaintext
