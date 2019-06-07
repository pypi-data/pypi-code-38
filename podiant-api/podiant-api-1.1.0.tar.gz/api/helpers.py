import random
import string


def generate_api_key(length):
    """
    A simple helper to return a randomly-generated string of a given length.

    :param length: The length of string
    :type length: int
    """

    s = ''
    while len(s) < length:
        s += ''.join(
            random.sample(
                string.digits + string.ascii_letters,
                62
            )
        )

    return s[:length]
