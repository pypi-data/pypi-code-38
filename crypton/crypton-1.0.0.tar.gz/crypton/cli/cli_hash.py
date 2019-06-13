from termcolor import colored
from crypton import errors
from crypton.cli.cli import Cli
from crypton.crypt_algorithms.hash.sha2 import SHA2


class CliHash(Cli):

    def __init__(self):
        super().__init__()
        self.options = [0, 1, 2, 3]
        self.hash = colored("[CRYPTON::HASHING]> ", 'blue')
        self.sha2_cli = colored("[CRYPTON::HASHING::SHA2]> ", 'blue')
        self.sha3_cli = colored("[CRYPTON::HASHING::SHA3]> ", 'blue')

    def display_menu(self):
        print(colored("\r\n[*] Here you will have to choose between the available options. Select from menu:\n",
                      'green'))
        print(colored("     [1] SHA3 Hash", 'green'))
        print(colored("     [2] SHA2 Hash", 'green'))
        print()
        print(colored("     [0] Exit the Hash Cryptography", 'green'))
        print()

    def get_option(self, prompt):
        return super().get_option(prompt=prompt)

    def get_prompt(self, hash_option):
        cli_prompt = ''
        if hash_option == 1:
            cli_prompt = self.sha3_cli
        elif hash_option == 2:
            cli_prompt = self.sha2_cli

        return cli_prompt

    def display_hash(self, hash_option):
        global input_file_path

        while True:
            try:
                cli_prompt = self.get_prompt(hash_option=hash_option)

                input_file_path = str(input(cli_prompt + colored(' File Path to digest : ', 'green')))
                while not input_file_path:
                    print(errors.empty)
                    input_file_path = str(input(cli_prompt + colored(' File Path to digest : ', 'green')))

                input_bits = int(input(cli_prompt + colored(' Hash size : ', 'green')))
                while input_bits not in SHA2.options:
                    print(errors.sha_key_size)
                    input_bits = int(input(cli_prompt + colored(' Hash size : ', 'green')))

                return input_file_path, input_bits

            except ValueError:
                print(errors.value_type)
            except KeyboardInterrupt:
                quit()
