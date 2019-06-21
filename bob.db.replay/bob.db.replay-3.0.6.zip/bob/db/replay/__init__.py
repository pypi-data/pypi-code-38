#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Wed 18 May 09:28:44 2011

"""The Replay-Attack Database accessors for Bob
"""

from .query import Database
from .models import Client, File, Protocol, RealAccess, Attack

def get_config():
  """Returns a string containing the configuration information.
  """
  import bob.extension
  return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
