import argparse
import os
from termcolor import colored

from crypton import errors
from crypton.crypt_algorithms.password.check import Checker
from crypton.crypt_algorithms.password.generate import Generator

checker = Checker()
generator = Generator()
file_path = os.getcwd()


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-v",
                        "--version",
                        dest="version",
                        action="store_true",
                        help="See script version")

    parser.add_argument("-g",
                        "--generate-password",
                        nargs='*',
                        metavar=('length', 'number'),
                        type=int,
                        help="Secure passwords generation"
                             " // Defaults: length (20) - number of passwords (1)")

    parser.add_argument("-c",
                        "--check-password",
                        type=str,
                        metavar='password',
                        help="Passwords strength & security checks")

    parser.add_argument("-i",
                        "--interactive",
                        dest="interactive",
                        action="store_true",
                        help="Run script in interactive mode")

    return parser, parser.parse_args()


def show_passwords(length, number):
    print('\n' + colored('Entropy : ', 'green') + colored(str(checker.entropy(length)) + ' bits', 'white') + '\n')

    for n in range(number):
        print(colored('Password ' + str(n + 1) + ' : ', 'green') + colored(generator.secure_password(length), 'white')
              + '\n')


def generate_password(parser, args):
    if len(args) == 0:
        show_passwords(16, 1)

    elif len(args) == 2:
        length = args[0]
        number = args[1]

        if length < 16 or number < 1:
            print(errors.value)
        else:
            show_passwords(length, number)

    elif len(args) != 2:
        parser.error('expected 2 arguments')


def check_password(args):
    print('\n' + colored('Entropy : ', 'green') + colored(str(checker.entropy(len(args))) + ' bits', 'white'))
    print(checker.strength(args) + '\n')
