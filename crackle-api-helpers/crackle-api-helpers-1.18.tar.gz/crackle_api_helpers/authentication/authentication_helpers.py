''' API related helper module '''
import string
import random


def generate_username(prefix, length=20):
    """
    Generates a string that can be used for a username
    returns string
    """
    chars = string.ascii_uppercase + string.digits
    return prefix + ''.join(random.choice(chars) for _ in range(length))
