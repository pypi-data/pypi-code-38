""" Module containing ROT13 cipher """
import logging
from bletchley.ciphers.cipher import Cipher


class ROT13Cipher(Cipher):
    """ Implementation of the ROT13 cipher """
    def __init__(self):
        logging.info("Created ROT13 cipher")
        pass

    def encrypt(self, plaintext):
        """ Encrypt plain text using ROT13 cipher """
        logging.info("Attempting to encrypt plain text...")
        ciphertext = ''
        plaintext = self.sanitise(plaintext)
        plaintext_ordinal = [(ord(letter)-65) for letter in plaintext]
        for i in range(len(plaintext)):
            encrypted_value = (plaintext_ordinal[i] + 13) % 26
            ciphertext += chr(encrypted_value + 65)
        logging.info("Successfully encrypted plain text...")
        return ciphertext

    def decrypt(self, ciphertext):
        """ Decrypt cipher text using ROT13 cipher """
        logging.info("Attempting to decrypt cipher text...")
        plaintext = ''
        ciphertext = self.sanitise(ciphertext)
        ciphertext_ordinal = [(ord(letter)-65) for letter in ciphertext]
        for i in range(len(ciphertext)):
            unencrypted_value = (ciphertext_ordinal[i] - 13) % 26
            plaintext += chr(unencrypted_value + 65)
        logging.info("Successfully decrypted cipher text...")
        return plaintext
