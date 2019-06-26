"""
Python3 Module

Summary:
    User Input Manipulation

"""
import os
import sys
import re
import logging
from string import ascii_lowercase
from pyaws import __version__

logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)


def bool_assignment(arg, patterns=None):
    """
    Summary:
        Enforces correct bool argment assignment
    Arg:
        :arg (*): arg which must be interpreted as either bool True or False
    Returns:
        bool assignment | TYPE:  bool
    """
    arg = str(arg)    # only eval type str
    try:
        if patterns is None:
            patterns = (
                (re.compile(r'^(true|false)$', flags=re.IGNORECASE), lambda x: x.lower() == 'true'),
                (re.compile(r'^(yes|no)$', flags=re.IGNORECASE), lambda x: x.lower() == 'yes'),
                (re.compile(r'^(y|n)$', flags=re.IGNORECASE), lambda x: x.lower() == 'y')
            )
        if not arg:
            return ''    # default selected
        else:
            for pattern, func in patterns:
                if pattern.match(arg):
                    return func(arg)
    except Exception as e:
        raise e


def bool_convert(variable):
    """
    Convert user input from string, int to bool
    """
    try:
        if re.search('True', variable, re.IGNORECASE):
            return True
        elif re.search('False', variable, re.IGNORECASE):
            return False
    except TypeError as e:
        logger.error("Error: {} not interpreted. Return false. Error: {}".format(str(variable), str(e)))
        return False
    return bool(int(variable))


def range_bind(min_value, max_value, value):
    """ binds number to a type and range """
    if value not in range(min_value, max_value + 1):
        value = min(value, max_value)
        value = max(min_value, value)
    return int(value)


def range_test(min, max, value):
    """
    Summary.

        Tests value to determine if in range (min, max)

    Args:
        :min (int):  integer representing minimum acceptable value
        :max (int):  integer representing maximum acceptable value
        :value (int): value tested

    Returns:
        Success | Failure, TYPE: bool

    """
    if isinstance(value, int):
        if value in range(min, max + 1):
            return True
    return False


def userchoice_mapping(choice):
    """
    Summary:
        Maps the number of an option presented to the user to the
        correct letters in sequential a-z series when choice parameter
        is provided as a number.

        When given a letter as an input parameter (choice is a single
        letter), returns the integer number corresponding to the letter
        in the alphabet (a-z)

        Examples:
            - userchoice_mapping(3) returns 'c'
            - userchoice_mapping('z') returns 26 (integer)
    Args:
        choice, TYPE: int or str
    Returns:
        ascii (lowercase), TYPE: str OR None
    """
    # prepare mapping dict containing all 26 letters
    map_dict = {}
    letters = [x for x in ascii_lowercase]
    extend_a = ['a' + x for x in letters]
    extend_b = ['b' + x for x in letters]

    # combine all
    letters.extend(extend_a)
    letters.extend(extend_b)
    max_index = len(letters)

    # build lookup table (dict)
    for index, key in enumerate(letters):
        map_dict[index] = letters[index]

    try:

        # process user input
        if isinstance(choice, str):
            if choice.lower() in letters:
                for k, v in map_dict.items():
                    if v == choice.lower():
                        return k

            elif int(choice) in range(1, max_index + 1):
                # integer string provided
                return map_dict[int(choice)]

            else:
                # not in letters or integer string outside range
                return None
        elif choice not in range(0, max_index + 1):
            return None

    except KeyError:
        # integer outside range provided
        return None
    except ValueError:
        # string outside range provided
        return None
    return map_dict[choice]
