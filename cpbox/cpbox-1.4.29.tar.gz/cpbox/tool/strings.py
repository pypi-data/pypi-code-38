import string
import random

def random_str(count=10):
    return ''.join(random.choice(string.ascii_letters) for i in range(count))
