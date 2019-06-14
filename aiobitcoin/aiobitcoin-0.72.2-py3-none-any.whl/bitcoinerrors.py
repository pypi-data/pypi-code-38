# -*- coding: utf-8 -*-


class BitcoinErrors(Exception):
    def __init__(self, error_msg=''):
        Exception.__init__(self, f'{error_msg}')


class InvalidPrivateKeyEncoding(BitcoinErrors):
    pass


class PrivateKeyForThisAddressAlreadyInWallet(BitcoinErrors):
    pass


class InvalidAddress(BitcoinErrors):
    pass


class InvalidIpOrSubnet(BitcoinErrors):
    pass


class NoConnectionToTheDaemon(BitcoinErrors):
    def __init__(self, error_msg='No connection to the daemon.'):
        super().__init__(error_msg=error_msg)


class IncorrectCreds(BitcoinErrors):
    def __init__(self, uri):
        super().__init__(error_msg=f'RPC on {uri} is alive, but RPC credentials are incorrect.')

