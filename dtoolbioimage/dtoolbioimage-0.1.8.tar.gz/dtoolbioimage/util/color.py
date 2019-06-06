"""Module for generating RGB tuples for use as colors in images."""

import sys
import random
import hashlib
import itertools


def _extract_8_bits(long_value, shift=1):
    """Return an integer in the range 0, 255 by extracting 8 bits from the
    input long value. shift determines which 8 bits are taken, by default
    the first 8 bits."""

    bitmask = (1 << 8 * shift) - 1

    return (long_value & bitmask) >> (8 * (shift-1))


def _md5_hash_as_long(input_value):
    """Return the hash of the input value converted to a long."""

    hex_hash = hashlib.md5(str(input_value).encode('utf-8')).hexdigest()

    return int(hex_hash, 16)


def _generate_rgb_tuple(long_hash):
    """Return an RGB tuple with the following ranges:

    0 <= blue < 128
    128 <= green < 256
    0 <= red < 256"""

    blue = _extract_8_bits(long_hash, 1) & 127
    green = 128 + (_extract_8_bits(long_hash, 2) & 127)
    red = _extract_8_bits(long_hash, 3)

    return map(int, (red, green, blue))


def unique_color_from_identifier(identifier):
    """Return unique color as RGB tuple.

    Useful for creating PNG images where each color is used as an identifier.

    Raises TypeError if the identifier is not an integer.

    Raises ValueError if the identifier is not in the range 0 to 16777215
    inclusive.

    :param identifier: positive integer in range from 0 to 16777215 inclusive
    :raises: TypeError, ValueError
    :returns: RGB tuple
    """
    if not isinstance(identifier, int):
        raise(TypeError("Identifier is not an integer {}".format(identifier)))
    if identifier < 0:
        raise(ValueError("Negative identifier not allowed"))
    if identifier >= 256*256*256:
        raise(ValueError("Identifier {} >= {}".format(identifier,
                                                      256*256*256)))
    blue = identifier % 256
    green = (identifier // 256) % 256
    red = (identifier // (256*256)) % 256
    return (red, green, blue)


def identifier_from_unique_color(unique_color):
    """Return identifier from unique RGB tuple.

    :param unique_color: RGB tuple
    :returns: positive integer in range from 0 to 16777215 inclusive
    """
    red, green, blue = unique_color
    red_factor = 256 * 256
    green_factor = 256
    return red * red_factor + green * green_factor + blue


def pretty_color_from_identifier(identifier):
    """Return deterministic aesthetically pleasing RGB tuple.

    :returns: RGB tuple
    """
    long_hash = _md5_hash_as_long(identifier)
    tuple_as_integers = _generate_rgb_tuple(long_hash)
    tuple_permutations = list(itertools.permutations(tuple_as_integers))
    selected_permutation = _extract_8_bits(long_hash, 4) % 6
    return tuple_permutations[selected_permutation]


def random_pretty_color():
    """Return random aesthetically pleasing RGB tuple.

    :returns: RGB tuple
    """
    try:
        identifier = random.randint(0, sys.maxint)
    except AttributeError:
        # Python3 has no sys.maxint
        identifier = random.randint(0, sys.maxsize)
    return pretty_color_from_identifier(identifier)


def pretty_color_palette(identifiers, keep_zero_black=True):
    """Return dictionary with pretty colors.

    :param identifiers: set of unique identifiers
    :param keep_zero_black: whether or not the background should be black
    :returns: dictionary
    """

    color_dict = {}
    for i in identifiers:
        if keep_zero_black and i == 0:
            color_dict[0] = (0, 0, 0)
            continue
        value = pretty_color_from_identifier(i)
        color_dict[i] = value

    return color_dict


def unique_color_palette(identifiers):
    """Return dictionary with unique colors.

    :param identifiers: set of unique identifiers
    :returns: dictionary
    """
    color_dict = {}
    for i in identifiers:
        i = int(i)  # Force np.int64 to int for py3.3 compatibility.
        color_dict[i] = unique_color_from_identifier(i)
    return color_dict
