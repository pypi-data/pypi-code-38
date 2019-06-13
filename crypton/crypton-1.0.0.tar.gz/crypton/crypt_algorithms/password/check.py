import string
import math
import re
from termcolor import colored
import pkg_resources

list = pkg_resources.resource_filename(__name__, 'wordlist.txt')


class Checker:

    def __init__(self):
        self.uppercase = "(?=.*?[A-Z])"  # 26
        self.lowercase = "(?=.*?[a-z])"  # 26
        self.symbols = "(?=.*?[" + string.punctuation + "])"  # 32
        self.digits = "(?=.*?\d)"  # 10

        self.secure_regex = self.uppercase + self.lowercase + self.symbols + self.digits

        self.wordlist = open(list, 'r').read().split()

    @staticmethod
    def entropy(length):
        return round(math.log2(math.pow(94, length)))

    def dictionary_attacks(self, password):
        if password in self.wordlist:
            return True
        else:
            return False

    def strength(self, password):
        if re.match(self.secure_regex, password):
            result = colored("\nSECURE", 'green')
        else:
            result = colored("\nUNSECURE: ", 'red')

            if self.dictionary_attacks(password):
                result += colored("\n - Vulnerable to dictionary attacks", 'red')
            if len(password) < 15:
                result += colored("\n - It must have a minimum of 15 characters", 'red')
            if not re.match(self.uppercase, password):
                result += colored("\n - It must contain at least one uppercase", 'red')
            if not re.match(self.lowercase, password):
                result += colored("\n - It must contain at least one lowercase", 'red')
            if not re.match(self.symbols, password):
                result += colored("\n - It must contain at least one symbol", 'red')
            if not re.match(self.digits, password):
                result += colored("\n - It must contain at least one digit", 'red')

        return result
