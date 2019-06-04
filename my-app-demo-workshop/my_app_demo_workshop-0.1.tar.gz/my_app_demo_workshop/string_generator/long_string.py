from random import choice
from string import ascii_letters

from my_app_demo_workshop.config import LONG_STRING_LEN


def get_long_string():
    """Randomly generate a long string"""

    return ''.join(choice(ascii_letters) for _ in range(LONG_STRING_LEN))
