#!/usr/bin/env python3

import logging
from time import sleep

import click


@click.command()
@click.argument('ip')
@click.option('-v', 'verbose', is_flag=True, default=False, help='Verbose output')
def cmd_bruteforce(ip, protocol, userfile, passfile):
    """
    Brute force compatible with various protocols

    Example:

    \b
    # habu.bruteforce -m ftp -u users.txt -p passwords.txt 192.168.0.100
    """

    if verbose:
        logging.basicConfig(level=logging.INFO, format='%(message)s')


if __name__ == '__main__':
    cmd_bruteforce()

