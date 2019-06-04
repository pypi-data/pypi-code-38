""" Module containing Caesar cipher """
import logging
from bletchley.ciphers.cipher import Cipher


class CaesarCipher(Cipher):
    """ Implementation of the Caesar cipher """
    def __init__(self):
        logging.info("Created Caesar cipher")
        pass

    def encrypt(self, plaintext, shift):
        """ Encrypt plain text using Caesar cipher """
        logging.info("Attempting to encrypt plain text...")
        ciphertext = ''
        plaintext = self.sanitise(plaintext)
        plaintext_ordinal = [(ord(letter)-65) for letter in plaintext]
        for i in range(len(plaintext)):
            encrypted_value = (plaintext_ordinal[i] + shift) % 26
            ciphertext += chr(encrypted_value + 65)
        logging.info("Successfully encrypted plain text...")
        return ciphertext

    def decrypt(self, ciphertext, shift):
        """ Decrypt cipher text using Caesar cipher """
        logging.info("Attempting to decrypt cipher text...")
        plaintext = ''
        ciphertext = self.sanitise(ciphertext)
        ciphertext_ordinal = [(ord(letter)-65) for letter in ciphertext]
        for i in range(len(ciphertext)):
            unencrypted_value = (ciphertext_ordinal[i] - shift) % 26
            plaintext += chr(unencrypted_value + 65)
        logging.info("Successfully decrypted cipher text...")
        return plaintext
