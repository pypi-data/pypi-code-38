from random import choice
from string import ascii_letters

from my_app_demo_workshop.config import SHORT_STRING_LEN


def get_short_string():
    """Randomly generate a short string"""

    return ''.join(choice(ascii_letters) for _ in range(SHORT_STRING_LEN))




