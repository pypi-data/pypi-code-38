from termcolor import colored
from validate_email import validate_email
from crypton.cli.cli_asymmetric import CliAsymmetric
from crypton.crypt_algorithms.asymmetric.dsa import DSA
from crypton.crypt_algorithms.asymmetric.ecdsa import ECDSA
from crypton.crypt_algorithms.asymmetric.rsa import RSA
from crypton import errors


class CliX509(CliAsymmetric):

    def __init__(self):
        super().__init__()
        self.options = [0, 1, 2]

    def display_menu(self):
        print(colored("\r\n[*] Here you will have to choose between the available options. Select from menu:\n",
                      'green'))
        print(colored("     [1] X509 Self signed certificate", 'green'))
        print(colored("     [2] X509 CSR", 'green'))
        print()
        print(colored("     [0] Exit the Asymmetric Cryptography", 'green'))
        print()

    def get_option(self, prompt):
        return super().get_option(prompt=prompt)

    def display_ss_certificate(self):
        global input_bits
        algorithms = ['RSA', 'DSA', 'ECDSA']

        while True:
            try:

                input_subject_name = str(input(self.x509_cli + colored('Certificate Subject Name : ', 'green')))

                while not input_subject_name:
                    print(errors.empty)
                    input_subject_name = str(input(self.x509_cli + colored('Certificate Subject Name : ',
                                                                           'green')))

                input_alternative_names = 'localhost'

                input_email = str(input(self.x509_cli + colored("Certificate Email : ", 'green')))
                print(colored(' Verifying email existance ...', 'green'))

                while not validate_email(input_email, verify=True):
                    print(errors.gpg_invalid_email)
                    input_email = int(input(self.x509_cli + colored("Certificate Email : ", 'green')))
                print(colored(' Verified!', 'green'))

                input_org = str(input(self.x509_cli + colored('Certificate Organization Name : ', 'green')))

                while not input_org:
                    print(errors.empty)
                    input_org = str(input(self.x509_cli + colored('Certificate Organization Name : ', 'green')))

                input_org_unit = str(input(self.x509_cli + colored('Certificate Organization Unit : ',
                                                                   'green')))
                while not input_org_unit:
                    print(errors.empty)
                    input_org_unit = str(input(self.x509_cli + colored('Certificate Organization Unit : ',
                                                                       'green')))

                input_algorithm = str(input(self.x509_cli + colored('Certificate algorithm (RSA, DSA, ECDSA) : ',
                                                                    'green')))
                while input_algorithm not in algorithms:
                    print(errors.x509_modes)
                    input_algorithm = str(input(self.x509_cli + colored('Certificate algorithm (RSA, DSA, ECDSA) : ',
                                                                        'green')))

                input_bits = int(input(self.x509_cli + colored(input_algorithm + ' Key size : ', 'green')))
                while not input_bits:
                    print(errors.empty)
                    input_bits = int(input(self.x509_cli + colored(input_algorithm + ' Key size : ', 'green')))

                input_path = str(input(self.x509_cli + colored('Certificate Path to export (default current '
                                                               'directory) : ', 'green')))

                if (input_algorithm == 'RSA' and input_bits in RSA.options_key) or \
                        (input_algorithm == 'DSA' and input_bits in DSA.options_key) or \
                        (input_algorithm == 'ECDSA' and input_bits in ECDSA.options_key):

                    return input_bits, input_algorithm, input_subject_name, input_alternative_names, \
                           input_email, input_org, input_org_unit, input_path
                else:
                    if input_algorithm == 'RSA':
                        print(errors.rsa_key_size)
                    elif input_algorithm == 'DSA':
                        print(errors.dsa_key_size)
                    elif input_algorithm == 'ECDSA':
                        print(errors.ecdsa_key_size)

            except ValueError:
                print(errors.value_type)
            except KeyboardInterrupt:
                quit()

    def display_csr(self):
        global input_bits
        algorithms = ['RSA', 'DSA', 'ECDSA']

        while True:
            try:
                input_subject_name = str(input(self.x509_cli + colored('Certificate Subject Name : ', 'green')))

                while not input_subject_name:
                    print(errors.empty)
                    input_subject_name = str(input(self.x509_cli + colored('Certificate Subject Name : ', 'green')))

                input_alternative_names = str(input(self.x509_cli + colored('Certificate Alternative Names ('
                                                                            '- ej. mysite.com, www.mysite.com, '
                                                                            'subdomain.mysite.com : ',
                                                                            'green')))
                while not input_alternative_names:
                    print(errors.empty)
                    input_alternative_names = str(
                        input(self.x509_cli + colored('Certificate Alternative Names ('
                                                      '- ej. mysite.com, www.mysite.com, '
                                                      'subdomain.mysite.com : ',
                                                      'green')))

                input_email = str(input(self.x509_cli + colored("Certificate Email : ", 'green')))
                print(colored(' Verifying email existance ...', 'green'))

                while not validate_email(input_email, verify=True):
                    print(errors.gpg_invalid_email)
                    input_email = int(input(self.x509_cli + colored("Certificate Email : ", 'green')))
                print(colored(' Verified!', 'green'))

                input_org = str(input(self.x509_cli + colored('Certificate Organization Name : ', 'green')))

                while not input_org:
                    print(errors.empty)
                    input_org = str(input(self.x509_cli + colored('Certificate Organization Name : ', 'green')))

                input_org_unit = str(input(self.x509_cli + colored('Certificate Organization Unit : ', 'green')))
                while not input_org_unit:
                    print(errors.empty)
                    input_org_unit = str(input(self.x509_cli + colored('Certificate Organization Unit : ', 'green')))

                input_algorithm = str(input(self.x509_cli + colored('Certificate algorithm (RSA, DSA, ECDSA) : ',
                                                                    'green')))
                while input_algorithm not in algorithms:
                    print(errors.x509_modes)
                    input_algorithm = str(
                        input(self.x509_cli + colored('Certificate algorithm (RSA, DSA, ECDSA) : ', 'green')))

                input_bits = int(input(self.x509_cli + colored(input_algorithm + ' Key size : ', 'green')))
                while not input_bits:
                    print(errors.empty)
                    input_bits = int(input(self.x509_cli + colored(input_algorithm + ' Key size : ', 'green')))

                input_path = str(input(self.x509_cli + colored('Certificate Path to export (default current '
                                                               'directory) : ', 'green')))

                if (input_algorithm == 'RSA' and input_bits in RSA.options_key) or \
                        (input_algorithm == 'DSA' and input_bits in DSA.options_key) or \
                        (input_algorithm == 'ECDSA' and input_bits in ECDSA.options_key):

                    return input_bits, input_algorithm, input_subject_name, input_alternative_names, \
                           input_email, input_org, input_org_unit, input_path
                else:
                    if input_algorithm == 'RSA':
                        print(errors.rsa_key_size)
                    elif input_algorithm == 'DSA':
                        print(errors.dsa_key_size)
                    elif input_algorithm == 'ECDSA':
                        print(errors.ecdsa_key_size)

            except ValueError:
                print(errors.value_type)

            except KeyboardInterrupt:
                quit()
