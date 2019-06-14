import random
import string


def is_empty(s):
    return s is None or s.strip() == ""


def is_not_empty(s):
    return not is_empty(s)


def random_string(length=10):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))
