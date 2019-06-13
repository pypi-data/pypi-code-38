from termcolor import colored
from crypton import errors
from crypton.cli.cli import Cli
from crypton.crypt_algorithms.symmetric.aes import Aes


class CliSymmetric(Cli):

    def __init__(self):
        super().__init__()
        self.symm_cli = colored("[CRYPTON::SYMMETRIC]> ", 'blue')
        self.aes_cli = colored("[CRYPTON::SYMMETRIC::AES]> ", 'blue')

    def display_menu(self):
        print(colored("\r\n[*] Here you will have to choose between the available options. Select from menu:\n",
                      'green'))
        print(colored("     [1] AES Key generation", 'green'))
        print(colored("     [2] AES Encryption", 'green'))
        print(colored("     [3] AES Decryption", 'green'))
        print()
        print(colored("     [0] Exit the Symmetric Cryptography", 'green'))
        print()

    def get_option(self, prompt):
        return super().get_option(prompt=prompt)

    def display_key_generator(self):
        global input_bits

        while True:
            try:
                input_bits = int(input(self.aes_cli + colored("AES Key size : ", 'green')))

                while input_bits not in Aes.options_key:
                    print(errors.aes_key_size)
                    input_bits = int(input(self.aes_cli + colored("AES Key size : ", 'green')))

                input_passphrase = str(input(self.aes_cli + colored("AES passphrase : ", 'green')))

                while not input_passphrase:
                    print(errors.aes_empty)
                    input_passphrase = str(input(self.aes_cli + colored("AES passphrase : ", 'green')))

                return input_bits, input_passphrase

            except ValueError:
                print(errors.value_type)
            except KeyboardInterrupt:
                quit()

    def display_encrypt(self):
        global input_bits
        aes_modes = ['CBC', 'CTR']

        while True:
            try:
                input_key = str(input(self.aes_cli + colored("AES Key : ", 'green')))

                while not input_key:
                    print(errors.aes_key_size)
                    input_key = int(input(self.aes_cli + colored("AES Key : ", 'green')))

                input_mode = str(input(self.aes_cli + colored("AES mode (CBC or CTR) : ", 'green')))

                while input_mode not in aes_modes:
                    print(errors.aes_modes)
                    input_mode = str(input(self.aes_cli + colored("AES mode (CBC or CTR) : ", 'green')))

                input_file_path = str(input(self.aes_cli + colored("File to encrypt path : ", 'green')))

                while not input_file_path:
                    print(errors.aes_empty)
                    input_file_path = str(input(self.aes_cli + colored("Text to encrypt : ", 'green')))

                return input_key, input_mode, input_file_path

            except ValueError:
                print(errors.value_type)
            except KeyboardInterrupt:
                quit()

    def display_decrypt(self):
        global input_bits
        aes_modes = ['CBC', 'CTR']

        while True:
            try:
                input_key = str(input(self.aes_cli + colored("AES Key : ", 'green')))

                while not input_key:
                    print(errors.aes_key_size)
                    input_key = int(input(self.aes_cli + colored("AES Key : ", 'green')))

                input_mode = str(input(self.aes_cli + colored("AES mode (CBC or CTR) : ", 'green')))

                while input_mode not in aes_modes:
                    print(errors.aes_modes)
                    input_mode = str(input(self.aes_cli + colored("AES mode (CBC or CTR) : ", 'green')))

                input_file_path = str(input(self.aes_cli + colored("File to decrypt path : ", 'green')))

                while not input_file_path:
                    print(errors.aes_empty)
                    input_file_path = str(input(self.aes_cli + colored("Text to decrypt : ", 'green')))

                return input_key, input_mode, input_file_path

            except ValueError:
                print(errors.value_type)
            except KeyboardInterrupt:
                quit()
