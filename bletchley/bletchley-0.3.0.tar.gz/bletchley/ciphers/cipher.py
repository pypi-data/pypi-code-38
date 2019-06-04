""" Module containing the base class for ciphers """
from abc import ABC
from abc import abstractmethod
import string
import logging


class Cipher(ABC):
    """ Cipher base class providing common functionality and interface """
    def __init__(self, name):  # pragma: no cover
        """ Intialisation function for cipher base class """
        logging.info("Created abstract cipher")
        pass

    def sanitise(self, text):
        """ Parses input to remove all punctuation and only use upper case """
        logging.info('Attempting to sanatise text...')
        sanatised_text = ''
        text = text.upper()
        alphabet = list(string.ascii_uppercase)
        for letter in text:
            if letter in alphabet:
                sanatised_text += letter
        logging.debug('Sanatised: {}'.format(text))
        return sanatised_text

    def sanitise_numerical(self, text):
        """ Parses input to remove all non-numeric characters """
        logging.info('Attempting to numerically sanatise text...')
        sanatised_text = ''
        for letter in text:
            try:
                int(letter)
                sanatised_text += letter
            except ValueError:
                pass
        logging.debug('Sanatised: {}'.format(text))
        return sanatised_text

    def sanitise_ij(self, text):
        """ Parses input to remove all punctuation, and Js and only use upper
        case
        """
        logging.info('Attempting to sanatise text...')
        sanatised_text = ''
        text = text.upper()
        text = text.replace('J', '')
        alphabet = list(string.ascii_uppercase)
        for letter in text:
            if letter in alphabet:
                sanatised_text += letter
        logging.debug('Sanatised: {}'.format(text))
        return sanatised_text

    def sanitise_alphanumeric(self, text):
        """ Parses input to remove all punctuation, and Js and only use upper
        case
        """
        logging.info('Attempting to sanatise text...')
        sanatised_text = ''
        text = text.upper()
        alphabet = list(string.ascii_uppercase + string.digits)
        for letter in text:
            if letter in alphabet:
                sanatised_text += letter
        logging.debug('Sanatised: {}'.format(text))
        return sanatised_text

    @abstractmethod
    def encrypt(self, plaintext):  # pragma: no cover
        """ Encrypts plain text using the cipher """
        pass

    @abstractmethod
    def decrypt(self, ciphertext):  # pragma: no cover
        """ Decrypts cipher text using cipher """
        pass
