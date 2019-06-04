""" Module containing VIC cipher """
import logging
import secrets
import string
import numpy as np
from bletchley.ciphers.cipher import Cipher


class VICCipher(Cipher):
    """ Implementation of the VIC cipher """
    def __init__(self):
        logging.info("Created VIC cipher")
        pass

    def encrypt(self, plaintext, checker_board):
        """ Encrypt plain text using VIC cipher """
        logging.info("Attempting to encrypt plain text...")
        ciphertext = ''
        plaintext = self.sanitise(plaintext)
        self.check_checker_board(checker_board)
        row_1, row_2 = self.find_checkerboard_blanks(checker_board)
        for letter in plaintext:
            row, col = np.where(checker_board == letter)
            if row == 0:
                ciphertext += str(col[0])
            if row == 1:
                ciphertext += (str(row_1) + str(col[0]))
            if row == 2:
                ciphertext += (str(row_2) + str(col[0]))
        logging.info("Successfully encrypted plain text.")
        return ciphertext

    def decrypt(self, ciphertext, checker_board):
        """ Decrypt cipher text using VIC cipher """
        logging.info("Attempting to decrypt cipher text...")
        plaintext = ''
        ciphertext = self.sanitise_numerical(ciphertext)
        self.check_checker_board(checker_board)
        row_1, row_2 = self.find_checkerboard_blanks(checker_board)
        print("ROWS:", row_1, row_2)
        iterator = iter(list(ciphertext))
        for value in iterator:
            print("VALUE:", value)
            logging.debug(value)
            if int(value[0]) == int(row_1):
                plaintext += checker_board[1,
                                           int(iterator.__next__()[0])]
            if int(value[0]) == int(row_2):
                plaintext += checker_board[2,
                                           int(iterator.__next__()[0])]
            else:
                plaintext += checker_board[0, int(value[0])]
        logging.info("Successfully decrypted cipher text.")
        return plaintext.replace(' ', '')

    def check_checker_board(self, checker_board):
        """ Checks if the supplied checker board is valid """
        is_valid = True
        if checker_board.shape != (3, 10):  # pragma: no cover
            is_valid = False
            raise Exception('Checkerboard not valid!'
                            ' {} != [3, 10]'.format(checker_board.shape))
        logging.info("Valid checkerboard found.")
        return is_valid

    def find_checkerboard_blanks(self, checker_board):
        """
        Finds the index of blank spaces in the first row of a
        checkerboard
        """
        col = np.where(checker_board[0, :] == " ")
        logging.debug
        logging.debug("Checkerboard has blanks at: {0} and "
                      "{1}".format(col[0][0], col[0][1]))
        return col[0][0], col[0][1]

    def generate_checkerboard(self):
        """ Generates a checkerboard for use with the VIC cipher """
        text = list(string.ascii_uppercase)
        checkerboard = [[], [], []]
        first_row = [' ', ' ']
        for x in range(0, 8):
            choice = secrets.choice(text)
            text.remove(choice)
            first_row.append(choice)
        text.append('.')
        text.append('/')
        for x in range(len(first_row)):
            choice = secrets.choice(first_row)
            first_row.remove(choice)
            checkerboard[0].append(choice)
        for y in range(1, 3):
            for x in range(0, 10):
                choice = secrets.choice(text)
                text.remove(choice)
                checkerboard[y].append(choice)
        checkerboard = np.asarray(checkerboard)
        if self.check_checker_board(checkerboard):
            return checkerboard
