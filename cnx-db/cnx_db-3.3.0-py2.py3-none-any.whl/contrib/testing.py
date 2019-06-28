# -*- coding: utf-8 -*-
"""\
These are functions that are useful in testing. They deal with testing
configuration discovery, setting defaults, and inspect the environment.

"""
import os
import sys


__all__ = (
    'get_settings',
    'is_py3',
    'is_venv',
    'is_venv_importable',
)


_DEFAULT_DB_URL = 'postgresql://tester:tester@localhost:5432/testing'


def get_settings():
    """Lookup database connection settings. This provides similar results
    to that of :func:`cnxdb.config.discover_settings`.

    :return: A dictionary of settings
    :rtype: dict

    """
    common_url = os.environ.get('DB_URL', _DEFAULT_DB_URL)
    super_url = os.environ.get('DB_SUPER_URL', common_url)

    settings = {
        'db.common.url': common_url,
        'db.readonly.url': common_url,
        'db.super.url': super_url,
    }
    return settings


def is_venv():
    """Tells whether the application is running within a virtualenv
    (aka venv).

    :rtype: bool

    """
    return hasattr(sys, 'real_prefix')


def is_venv_importable():
    """Determines whether the tests should be run with virtualenv
    (aka venv) database import features enabled.

    By default this will be true if the process is running within a venv.
    This can be overridden by setting the `AS_VENV_IMPORTABLE` environment
    variable to anything other than the string 'true'.

    :return: enable venv features
    :rtype: bool

    """
    x = os.environ.get('AS_VENV_IMPORTABLE', 'true') == 'true'
    return is_venv() and x


def is_py3():
    """Returns a boolean value if running under python3.x

    :rtype: bool

    """
    return sys.version_info > (3,)
