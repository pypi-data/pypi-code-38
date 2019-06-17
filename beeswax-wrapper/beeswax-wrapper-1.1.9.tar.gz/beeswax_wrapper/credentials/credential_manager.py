#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
For setting and returning beeswax passwords (visible only to current environment user).
"""
from __future__ import unicode_literals

import keyring
import getpass


def store_beeswax_credentials(username, password):
    """
    Store password in environment's keyring

    :param str|unicode username: Beeswax username/email
    :param str|unicode password: Beeswax password
    """
    user = getpass.getuser()
    keyring.set_password("beeswax_username", user, username)
    keyring.set_password("beeswax_password", user, password)


def get_beeswax_credentials():
    """
    Retrieve stored beeswax credentials
    :rtype: dict[str|unicode, str|unicode]
    :return: beeswax credentials, e.g. {"username":"foo", "password":"bar"}
    """
    user = getpass.getuser()
    return {
        'username': keyring.get_password("beeswax_username", user),
        'password': keyring.get_password("beeswax_password", user)
    }
