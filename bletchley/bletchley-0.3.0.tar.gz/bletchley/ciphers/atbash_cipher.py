""" Module containing Atbash cipher """
import logging
import string
from bletchley.ciphers.cipher import Cipher


class AtbashCipher(Cipher):
    """ Implementation of the Atbash cipher """
    def __init__(self):
        self.alphabet = list(string.ascii_uppercase)
        self.reversed_alphabet = list(reversed(self.alphabet))
        logging.info("Created Atbash cipher")
        pass

    def encrypt(self, plaintext):
        """ Encrypt plain text using Atbash cipher """
        logging.info("Attempting to encrypt plain text...")
        ciphertext = ''
        plaintext = self.sanitise(plaintext)
        for letter in plaintext:
            idx = self.alphabet.index(letter)
            ciphertext += self.reversed_alphabet[idx]
        logging.info("Successfully encrypted plain text...")
        return ciphertext

    def decrypt(self, ciphertext):
        """ Decrypt cipher text using Atbash cipher """
        logging.info("Attempting to decrypt cipher text...")
        plaintext = self.encrypt(ciphertext)
        logging.info("Successfully decrypted cipher text...")
        return plaintext
