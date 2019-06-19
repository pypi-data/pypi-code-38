
from .constants import CHAR_LOWERCASE, CHAR_NUMERIC, CHAR_UPPERCASE

def check_input(variable, expected_type, or_none=False):
    """Checks if a given variable is of the expected type. May also be
    NoneType is or_none is True. Raises an exception is unexpected type is
    present"""

    if not variable and expected_type is not bool and or_none is False:
        raise Exception('\'variable\' %s was not given' % variable)

    if not expected_type:
        raise Exception('\'expected_type\' %s was not given' % expected_type)

    if not or_none:
        if not isinstance(variable, expected_type):
            raise Exception('Expected %s type was %s, got %s'
                            % (variable, expected_type, type(variable)))
    else:
        if not isinstance(variable, expected_type) \
                and not isinstance(variable, type(None)):
            raise Exception('Expected %s type was %s or None, got %s'
                            % (variable, expected_type, type(variable)))


def valid_string(string):
    check_input(string, str)

    valid_chars = CHAR_NUMERIC + CHAR_UPPERCASE + CHAR_LOWERCASE + '-_'

    for char in string:
        if char not in valid_chars:
            raise Exception('Invalid character %s in string %s. Only valid characters are %s' % (char, string, valid_chars))