from termcolor import colored
from crypton.cli.cli import Cli
from crypton.crypt_algorithms.asymmetric.dsa import DSA
from crypton.crypt_algorithms.asymmetric.rsa import RSA
from crypton.crypt_algorithms.asymmetric.ecdsa import ECDSA
from crypton import errors


class CliAsymmetric(Cli):

    def __init__(self):
        super().__init__()
        self.asymm_cli = colored("[CRYPTON::ASYMMETRIC]> ", 'blue')
        self.rsa_cli = colored("[CRYPTON::ASYMMETRIC::RSA]> ", 'blue')
        self.dsa_cli = colored("[CRYPTON::ASYMMETRIC::DSA]> ", 'blue')
        self.ecdsa_cli = colored("[CRYPTON::ASYMMETRIC::ECDSA]> ", 'blue')
        self.ed25519_cli = colored("[CRYPTON::ASYMMETRIC::ED25519]> ", 'blue')
        self.x25519_cli = colored("[CRYPTON::ASYMMETRIC::X25519]> ", 'blue')
        self.x509_cli = colored("[CRYPTON::ASYMMETRIC::X509]> ", 'blue')
        self.options = [0, 1, 2, 3, 4, 5, 6]

    def display_menu(self):
        print(colored("\r\n[*] Here you will have to choose between the available options. Select from menu:\n",
                      'green'))
        print(colored("     [1] RSA", 'green'))
        print(colored("     [2] DSA", 'green'))
        print(colored("     [3] ECDSA", 'green'))
        print(colored("     [4] ED25519", 'green'))
        print(colored("     [5] X25519", 'green'))
        print(colored("     [6] X.509 Certificate", 'green'))
        print()
        print(colored("     [0] Exit the Asymmetric Cryptography", 'green'))
        print()

    def get_option(self, prompt):
        return super().get_option(prompt=prompt)

    def get_prompt(self, key):
        cli_prompt = ''
        if key == 'RSA':
            cli_prompt = self.rsa_cli
        elif key == 'DSA':
            cli_prompt = self.dsa_cli
        elif key == 'ECDSA':
            cli_prompt = self.ecdsa_cli
        elif key == 'ED25519':
            cli_prompt = self.ed25519_cli
        elif key == 'X25519':
            cli_prompt = self.x25519_cli

        return cli_prompt

    def display_key_generator(self, key):
        global input_bits, input_key_path

        while True:
            try:
                cli_prompt = self.get_prompt(key=key)

                input_bits = int(input(cli_prompt + colored(key + ' Key size : ', 'green')))
                while not input_bits:
                    print(errors.empty)
                    input_bits = int(input(cli_prompt + colored(key + ' Key size : ', 'green')))

                input_key_path = str(input(cli_prompt + colored(key + ' Key File Path to export (default current '
                                                                      'directory) : ', 'green')))

                if (key == 'RSA' or key == 'SSH' and input_bits in RSA.options_key) or \
                        (key == 'DSA' and input_bits in DSA.options_key) or \
                        (key == "ECDSA" and input_bits in ECDSA.options_key):
                    return input_bits, input_key_path
                else:
                    if key == 'RSA' or key == 'SSH':
                        print(errors.rsa_key_size)
                    elif key == 'DSA':
                        print(errors.dsa_key_size)
                    elif key == 'ECDSA':
                        print(errors.ecdsa_key_size)

            except ValueError:
                print(errors.value_type)
            except KeyboardInterrupt:
                quit()

    def display_encrypt(self, key):
        global input_file_path, input_public_key_path
        while True:
            try:
                cli_prompt = self.get_prompt(key=key)

                input_file_path = str(input(cli_prompt + colored('File to encrypt path : ', 'green')))
                while not input_file_path:
                    print(errors.empty)
                    input_file_path = str(input(cli_prompt + colored('File to encrypt path : ', 'green')))

                input_public_key_path = str(input(cli_prompt + colored(key + ' Public Key File Path to encrypt : ',
                                                                       'green')))
                while not input_public_key_path:
                    print(errors.empty)
                    input_public_key_path = str(input(cli_prompt + colored(key + ' Public Key File Path to encrypt : ',
                                                                           'green')))
                return input_file_path, input_public_key_path

            except ValueError:
                print(errors.value_type)
            except KeyboardInterrupt:
                quit()

    def display_sign(self, key):
        global input_file_path, input_private_key_path

        while True:
            try:
                cli_prompt = self.get_prompt(key=key)

                input_file_path = str(input(cli_prompt + colored('File to sign path : ', 'green')))
                while not input_file_path:
                    print(errors.empty)
                    input_file_path = str(input(cli_prompt + colored('File to sign path : ', 'green')))

                input_private_key_path = str(input(cli_prompt + colored(key + ' Private Key File Path to sign : ',
                                                                        'green')))
                while not input_private_key_path:
                    print(errors.empty)
                    input_private_key_path = str(input(cli_prompt + colored(key + ' Private Key File Path to sign : '
                                                                            , 'green')))

                return input_file_path, input_private_key_path
            except ValueError:
                print(errors.value_type)
            except KeyboardInterrupt:
                quit()

    def display_verify(self, key):
        global input_file_path, input_public_key_path, input_signature_path

        while True:
            try:
                cli_prompt = self.get_prompt(key=key)

                input_file_path = str(input(cli_prompt + colored('File to verify path : ', 'green')))
                while not input_file_path:
                    print(errors.empty)
                    input_file_path = str(input(cli_prompt + colored('File to verify path : ', 'green')))

                input_public_key_path = str(input(cli_prompt + colored(key + ' Public Key File Path to verify : ',
                                                                       'green')))
                while not input_public_key_path:
                    print(errors.empty)
                    input_public_key_path = str(input(cli_prompt + colored(key + 'Public Key File Path to verify '
                                                                                 ': ', 'green')))

                input_signature_path = str(input(cli_prompt + colored('Signature File Path : ', 'green')))
                while not input_signature_path:
                    print(errors.empty)
                    input_signature_path = str(input(cli_prompt + colored('Signature File Path : ', 'green')))

                return input_file_path, input_public_key_path, input_signature_path
            except ValueError:
                print(errors.value_type)
            except KeyboardInterrupt:
                quit()
