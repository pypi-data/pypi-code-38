"""Accounts module."""

#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging

from squid_py.keeper import Keeper

logger = logging.getLogger('account')


class Account:
    """Class representing an account."""

    def __init__(self, address, password=None):
        """
        Hold account address, and update balances of Ether and Ocean token.

        :param address: The address of this account
        :param password: account's password. This is necessary for unlocking account before doing
            a transaction.
        """
        self.address = address
        self.password = password
