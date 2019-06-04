""" Module containing ADFGX cipher """
import logging
import math
import secrets
import string
import numpy as np
from bletchley.ciphers.cipher import Cipher


class ADFGXCipher(Cipher):
    """ Implementation of the ADFGX cipher """
    def __init__(self):
        logging.info("Created ADFGX cipher")
        self.header = ['A', 'D', 'F', 'G', 'X']
        pass

    def encrypt(self, plaintext, polybius, key):
        """ Encrypt plain text using ADFGX cipher """
        logging.info("Attempting to encrypt plain text...")
        ciphertext = ''

        plaintext = self.sanitise_ij(plaintext)
        key = np.asarray(list(key), dtype='S10')
        inter_text = []
        for letter in plaintext:
            x, y = np.where(polybius == letter)
            inter_text.append(self.header[x[0]])
            inter_text.append(self.header[y[0]])

        number_of_rows = int(math.ceil(len(inter_text) / len(key)))
        while (len(inter_text) / len(key)) < number_of_rows:
            inter_text.append('')
        trans_col = np.array(inter_text).reshape(number_of_rows, len(key))

        cipher_array = []
        for row in range(number_of_rows):
            cipher_array.append(trans_col[row, :][key.argsort()[:]].tolist())
        for x in range(len(key)):
            for y in range(number_of_rows):
                ciphertext += cipher_array[y][x]
            ciphertext += ' '

        logging.info("Successfully encrypted plain text...")
        return ciphertext

    def decrypt(self, ciphertext, polybius, key):
        """ Decrypt cipher text using ADFGX cipher """
        logging.info("Attempting to decrypt cipher text...")
        plaintext = ''
        key = np.asarray(list(key), dtype='S10')
        split_ciphertext = ciphertext.split(' ')
        ciphertext = ciphertext.replace(' ', '')
        number_of_rows = int(math.ceil(len(ciphertext) / len(key)))
        cipher_array = np.full([number_of_rows, len(key)], '', dtype='S10')
        row = 0
        for block in split_ciphertext:
            block = self.sanitise(block)
            for letter in range(len(block)):
                cipher_array[letter, row] = block[letter]
            row += 1
        trans_col = np.full([number_of_rows, len(key)], '', dtype='S10')
        for row in range(number_of_rows):
            for letter in range(len(cipher_array[row])):
                key_sort = key.argsort()
                trans_col[row][key_sort[letter]] = (cipher_array[row][letter])
        inter_text = ''
        for x in range(trans_col.shape[0]):
            for y in range(trans_col.shape[1]):
                inter_text += str(trans_col[x, y].decode('UTF-8'))
        for i in range(0, len(inter_text), 2):
            x = self.header.index(inter_text[i])
            y = self.header.index(inter_text[i + 1])
            plaintext += str(polybius[x, y])
        logging.info("Successfully decrypted cipher text...")
        return plaintext

    def generate_polybius(self):
        """ Generates a polybius for use with the ADFGX cipher """
        text = list(string.ascii_uppercase)
        polybius = [[], [], [], [], []]
        text.remove('J')
        for y in range(0, 5):
            for x in range(0, 5):
                choice = secrets.choice(text)
                text.remove(choice)
                polybius[y].append(choice)
        polybius = np.asarray(polybius)
        return polybius
