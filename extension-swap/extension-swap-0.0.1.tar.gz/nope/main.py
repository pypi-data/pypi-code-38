#!/usr/bin/env python

"""change file extension to nope"""

import argparse
from argparse import RawTextHelpFormatter as rawtxt
import sys
import signal
import os
import json
import subprocess

def signal_handler(sig, frame):
    """handle control c"""
    print('\nuser cancelled')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def query_yes_no(question, default="yes"):
    '''confirm or decline'''
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("\nPlease respond with 'yes' or 'no' (or 'y' or 'n').\n")

class Bcolors:
    """console colors"""
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    GREY = '\033[90m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def main():
    '''change file extension to nope.'''
    parser = argparse.ArgumentParser(
        description='change file extension to nope.',
        prog='nope',
        formatter_class=rawtxt
    )

    #parser.print_help()
    parser.add_argument(
        "file",
        help="""change file extension to nope.\n
    $ nope file.tf\n
    where example is the file you wanna change.""",
        nargs='?',
        default='none'
    )
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.0.7')
    args = parser.parse_args()
    the_file = args.file
    if the_file == "none":
        print(Bcolors.WARNING+"please provide a filename"+Bcolors.ENDC)
        exit()
    else:
        if os.path.exists(the_file):
            print(the_file)
        else: 
            print(Bcolors.WARNING+"file does not exist"+Bcolors.ENDC)
        exit()

if __name__ == "__main__":
    main()
