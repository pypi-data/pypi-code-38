import re
import string
import secrets

from crypton.crypt_algorithms.password.check import Checker


class Generator:

    def __init__(self):
        self.alphabet = string.ascii_lowercase + string.digits + string.punctuation + string.ascii_uppercase

    def secure_password(self, length):
        password = ''.join(secrets.choice(self.alphabet) for _ in range(length))

        while not re.match(Checker().secure_regex, password):
            password = ''.join(secrets.choice(self.alphabet) for _ in range(length))

        return password
