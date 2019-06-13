"""
PyRandomString is a python library to generate a list of string. 

Author: Lakhya Jyoti Nath (ljnath)
Email:  ljnath@ljnath.com
Website: https://www.ljnath.com
"""

import random
from enum import Enum

class StringType(Enum):
    """
    Enum for selecting the type of random string
    """
    __ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
    NUMERIC = '0123456789'
    ALPHABET_LOWERCASE = __ALPHABET.lower()
    ALPHABET_UPPERCASE = __ALPHABET.upper()
    ALPHABET_ALL_CASE = ALPHABET_LOWERCASE + ALPHABET_UPPERCASE
    ALPHA_NUMERIC_LOWERCASE = ALPHABET_LOWERCASE + NUMERIC
    ALPHA_NUMERIC_UPPERCASE = ALPHABET_UPPERCASE + NUMERIC
    ALPHA_NUMERIC_ALL_CASE = ALPHABET_ALL_CASE + NUMERIC


class RandomString(object):
    """
    Actual class containing methods to generate random strings
    """
    def __init__(self):
        pass
 
    def get_strings(self, string_count:int = 10, max_length:int = 10, random_length:bool = False, string_type:StringType = StringType.ALPHA_NUMERIC_ALL_CASE):
        """ Method to generate random string based on input parameters
            :param string_count : string_count as integer. Total number of strings to be generated 
            :param max_length : max_length as integer. Maximum length of each generated string
            :param random_length : random_length as boolean - if the length of each word should be random or not. Incase of random length the maximum value is 'max_length'
            :param string_type : string_type as StringType. Type of characters to be used for generating random strings
        """
        string_collection = []
        if string_count > 0 and max_length > 0:
            string_collection =  list(self.__get_strings(string_count, max_length, random_length, string_type))
        return string_collection
 
    def __get_strings(self, string_count, max_length, random_length, input_characters):
        """ Private method for actual generation of random string
        """
        for _ in range(string_count):
            current_word = ''
            if not random_length:
                for _ in range(max_length):
                    current_word += random.SystemRandom().choice(input_characters.value)
            else:
                for _ in range(random.randint(1, max_length)):
                    current_word += random.SystemRandom().choice(input_characters.value)
            yield(str(current_word))
 