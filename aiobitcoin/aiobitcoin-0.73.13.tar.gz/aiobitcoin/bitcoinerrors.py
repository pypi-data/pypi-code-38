# -*- coding: utf-8 -*-


class _BitcoinErrors(Exception):
    def __init__(self, error_msg=''):
        Exception.__init__(self, f'{error_msg}')


class InvalidPrivateKeyEncoding(_BitcoinErrors):
    """
    Invalid private key encoding.
    """
    pass


class PrivateKeyForThisAddressAlreadyInWallet(_BitcoinErrors):
    """
    Private key for address is already in wallet.
    """
    pass


class InvalidAddress(_BitcoinErrors):
    """
    Invalid address.
    """
    pass


class InvalidIpOrSubnet(_BitcoinErrors):
    """
    Invalid ip or subnet.
    """
    pass


class NoConnectionToTheDaemon(_BitcoinErrors):
    """
    There is no connection to the daemon.
    """
    def __init__(self, error_msg):
        super().__init__(error_msg=error_msg)


class IncorrectCreds(_BitcoinErrors):
    """
    Login or password in URI is incorrect.
    """
    def __init__(self, uri):
        super().__init__(error_msg=f'RPC on {uri} is alive, but RPC credentials are incorrect.')

