#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Wed 19 Aug 13:43:50 2015

"""
The AVspoof Database access methods for Bob

"""

from .query import Database
from .models import Client, File, Protocol, ProtocolFiles


def get_config():
    """
    Returns a string containing the configuration information.

    """
    import bob.extension
    return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
