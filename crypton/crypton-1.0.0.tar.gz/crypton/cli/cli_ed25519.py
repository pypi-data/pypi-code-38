from termcolor import colored

from crypton import errors
from crypton.cli.cli_asymmetric import CliAsymmetric


class CliED25519(CliAsymmetric):

    def __init__(self):
        super().__init__()
        self.options = [0, 1, 2, 3]

    def display_menu(self):
        print(colored("\r\n[*] Here you will have to choose between the available options. Select from menu:\n",
                      'green'))
        print(colored("     [1] ED25519 key pair", 'green'))
        print(colored("     [2] ED25519 sign", 'green'))
        print(colored("     [3] ED25519 verify", 'green'))
        print()
        print(colored("     [0] Exit the ED25519 Cryptography", 'green'))
        print()

    def get_option(self, prompt):
        return super().get_option(prompt=prompt)

    def display_key_generator(self, key):
        global input_key_path

        while True:
            try:
                cli_prompt = self.get_prompt(key=key)

                input_key_path = str(input(cli_prompt + colored(key + ' Key File Path to export the 256 bits key ('
                                                                      'default current '
                                                                      'directory) : ', 'green')))
                while not input_key_path:
                    print(errors.empty)
                    input_key_path = str(input(cli_prompt + colored(key + ' Key File Path to export the 256 bits key ('
                                                                          'default current '
                                                                          'directory) : ', 'green')))

                return input_key_path

            except ValueError:
                print(errors.value_type)
            except KeyboardInterrupt:
                quit()

    def display_sign(self, key):
        return super().display_sign(key=key)

    def display_verify(self, key):
        return super().display_verify(key=key)
