"""
MIT License

Copyright (c) 2019 Lakhya Jyoti Nath (ljnath)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

PyRandomString is a python library to generate N random list of string of M length
Version: 0.0.5
Author: Lakhya Jyoti Nath (ljnath)
Email:  ljnath@ljnath.com
Website: https://www.ljnath.com
"""

import sys
if sys.version_info[0] < 3:
    raise Exception("Python version lower than 3 is not supported")
import re
import random
from enum import Enum

class StringType(Enum):
    """
    Enum for selecting the type of random string
    """
    __ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
    NUMERIC = '0123456789'
    SYMBOLS = '" !#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

    ALPHABET_LOWERCASE = __ALPHABET.lower()
    ALPHABET_LOWERCASE_WITH_SYMBOLS = __ALPHABET.lower() + SYMBOLS
    ALPHABET_UPPERCASE = __ALPHABET.upper()
    ALPHABET_UPPERCASE_WITH_SYMBOLS = __ALPHABET.upper() + SYMBOLS
    ALPHABET_ALL_CASE = ALPHABET_LOWERCASE + ALPHABET_UPPERCASE
    ALPHABET_ALL_CASE_WITH_SYMBOLS = ALPHABET_LOWERCASE + ALPHABET_UPPERCASE + SYMBOLS
    ALPHA_NUMERIC_LOWERCASE = ALPHABET_LOWERCASE + NUMERIC
    ALPHA_NUMERIC_LOWERCASE_WITH_SYMBOLS = ALPHABET_LOWERCASE + NUMERIC + SYMBOLS
    ALPHA_NUMERIC_UPPERCASE = ALPHABET_UPPERCASE + NUMERIC
    ALPHA_NUMERIC_UPPERCASE_WITH_SYMBOLS = ALPHABET_UPPERCASE + NUMERIC + SYMBOLS
    ALPHA_NUMERIC_ALL_CASE = ALPHABET_ALL_CASE + NUMERIC
    ALPHA_NUMERIC_ALL_CASE_WITH_SYMBOLS = ALPHABET_ALL_CASE + NUMERIC + SYMBOLS

class UnsupportedTypeException(Exception):
    """
    Exception class for UnsupportedTypeException. It is supposed to be raised if parameter is not of expected type
    """
    def __init__(self, parameter_name, message = None):
        print('Unsupported type exception for {}. {}'.format(parameter_name, message if message else ''))

class InvalidInputSymbolsException(Exception):
    """
    Exception class for InvalidInputSymbolsException. It is supposed to be when the custom symbol is not a subset of pre-defined symbols
    """
    def __init__(self, input_symbols):
        print('Input symbols "{}" are invalid. Input symbols should be a subset of available symbols {}'.format(input_symbols, StringType.SYMBOLS.value))

class RandomString(object):
    """
    Actual class containing methods to generate random strings
    """
    def __init__(self):
        pass
 
    def get_string(self, max_length=10, random_length=False, string_type=StringType.ALPHA_NUMERIC_ALL_CASE, symbols=None):
        """ Method to generate a random string based on input parameters
            :param max_length : max_length as integer. Maximum length of each generated string
            :param random_length : random_length as boolean - if the length of each word should be random or not. Incase of random length the maximum value is 'max_length'
            :param string_type : string_type as StringType. Type of characters to be used for generating random strings
            :param symbols : symbols as string. Symbols which are to be used during string generation. Applicable only when string_type is set to SYMBOLS or WITH_SYMBOLS
            :return random_string : random_string as a string
        """
        self.__validate_input(1, max_length, random_length, string_type, symbols)
        return self.get_strings(count=1, max_length=max_length, random_length=random_length, string_type=string_type, symbols=symbols)[0] if max_length > 0 else ''

    def get_strings(self, count=10, max_length=10, random_length=False, string_type=StringType.ALPHA_NUMERIC_ALL_CASE, symbols=None):
        """ Method to generate a list of random string based on input parameters
            :param count : count as integer. Total number of strings to be generated 
            :param max_length : max_length as integer. Maximum length of each generated string
            :param random_length : random_length as boolean - if the length of each word should be random or not. Incase of random length the maximum value is 'max_length'
            :param string_type : string_type as StringType. Type of characters to be used for generating random strings
            :param symbols : symbols as string. Symbols which are to be used during string generation. Applicable only when string_type is set to SYMBOLS or WITH_SYMBOLS
            :return list_of_strings : list_of_strings as a list. This is a list containing random strings
        """
        self.__validate_input(count, max_length, random_length, string_type, symbols)
        list_of_strings = []
        if count > 0 and max_length > 0:
            list_of_strings =  list(self.__get_strings(count, max_length, random_length, string_type.value if not symbols else string_type.value.replace(StringType.SYMBOLS.value, symbols)))
        return list_of_strings
 
    def __get_strings(self, count, max_length, random_length, input_characters):
        """ Private method for actual generation of random string
        """
        for _ in range(count):
            current_word = ''
            if not random_length:
                for _ in range(max_length):
                    current_word += random.SystemRandom().choice(input_characters)
            else:
                for _ in range(random.randint(1, max_length)):
                    current_word += random.SystemRandom().choice(input_characters)
            yield(str(current_word))

    def __validate_input(self, count, max_length, random_length, string_type, symbols):
        """ Validation method to chedk the type for input paramters and the symbols
        """
        if not isinstance(count, int):
            raise UnsupportedTypeException(parameter_name='count', message='count should be of integer type instead of current {} type'.format(type(count)))

        if not isinstance(max_length, int):
            raise UnsupportedTypeException(parameter_name='max_length', message='max_length should be of integer type instead of current {} type'.format(type(max_length)))

        if not isinstance(random_length, bool):
            raise UnsupportedTypeException(parameter_name='random_length', message='random_length should be of boolean type instead of current {} type'.format(type(random_length)))

        if not isinstance(string_type, StringType):
            raise UnsupportedTypeException(parameter_name='string_type', message='string_type should be of StringType type instead of current {} type'.format(type(string_type)))

        if symbols and not isinstance(symbols, str):
            raise UnsupportedTypeException(parameter_name='symbols', message='symbols should be either None or of string type instead of current {} type'.format(type(symbols)))
        elif symbols and not re.match(r'[{}]'.format(StringType.SYMBOLS.value), symbols):
            raise InvalidInputSymbolsException(symbols)
