from termcolor import colored
from crypton.cli.cli_asymmetric import CliAsymmetric
from crypton import errors


class CliRSA(CliAsymmetric):

    def __init__(self):
        super().__init__()
        self.options = [0, 1, 2, 3, 4, 5, 6]

    def display_menu(self):
        print(colored("\r\n[*] Here you will have to choose between the available options. Select from menu:\n",
                      'green'))
        print(colored("     [1] RSA key pair", 'green'))
        print(colored("     [2] RSA key pair for SSH Auth", 'green'))
        print(colored("     [3] RSA sign", 'green'))
        print(colored("     [4] RSA verify", 'green'))
        print(colored("     [5] RSA encryption (PGP principles)", 'green'))
        print(colored("     [6] RSA decryption (PGP principles)", 'green'))
        print()
        print(colored("     [0] Exit the RSA Cryptography", 'green'))
        print()

    def get_option(self, prompt):
        return super().get_option(prompt=prompt)

    def display_key_generator(self, key):
        return super().display_key_generator(key=key)

    def display_sign(self, key):
        return super().display_sign(key=key)

    def display_verify(self, key):
        return super().display_verify(key=key)

    def display_encrypt(self, key):
        return super().display_encrypt(key=key)

    def display_decrypt(self):
        global input_file_path, input_private_key_path, input_aes_key_path
        while True:
            try:

                input_file_path = str(input(self.rsa_cli + colored('File to decrypt path : ', 'green')))
                while not input_file_path:
                    print(errors.empty)
                    input_file_path = str(input(self.rsa_cli + colored('File to decrypt path : ', 'green')))

                input_private_key_path = str(input(self.rsa_cli + colored('RSA Private Key File Path to decrypt : ',
                                                                          'green')))
                while not input_private_key_path:
                    print(errors.empty)
                    input_private_key_path = str(input(self.rsa_cli + colored('RSA Private Key File Path to decrypt : ',
                                                                              'green')))

                input_aes_key_path = str(input(self.rsa_cli + colored('AES Encrypted Key File Path : ',
                                                                      'green')))
                while not input_aes_key_path:
                    print(errors.empty)
                    input_aes_key_path = str(input(self.rsa_cli + colored('AES Encrypted Key File Path : ',
                                                                          'green')))

                return input_file_path, input_private_key_path, input_aes_key_path

            except ValueError:
                print(errors.value_type)
            except KeyboardInterrupt:
                quit()
