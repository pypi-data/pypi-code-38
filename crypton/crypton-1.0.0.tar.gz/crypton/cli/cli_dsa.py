from termcolor import colored
from crypton.cli.cli_asymmetric import CliAsymmetric


class CliDSA(CliAsymmetric):

    def __init__(self):
        super().__init__()
        self.options = [0, 1, 2, 3]

    def display_menu(self):
        print(colored("\r\n[*] Here you will have to choose between the available options. Select from menu:\n",
                      'green'))
        print(colored("     [1] DSA key pair", 'green'))
        print(colored("     [2] DSA sign", 'green'))
        print(colored("     [3] DSA verify", 'green'))
        print()
        print(colored("     [0] Exit the DSA Cryptography", 'green'))
        print()

    def get_option(self, prompt):
        return super().get_option(prompt=prompt)

    def display_key_generator(self, key):
        return super().display_key_generator(key=key)

    def display_sign(self, key):
        return super().display_sign(key=key)

    def display_verify(self, key):
        return super().display_verify(key=key)
