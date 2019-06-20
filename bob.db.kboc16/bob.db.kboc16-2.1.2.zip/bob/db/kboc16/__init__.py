#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""The ATVS Keystroke database
"""

from .query import Database
from .models import Client, File, Protocol, ProtocolPurpose

def get_config():
  """Returns a string containing the configuration information.
  """
  import bob.extension
  return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
