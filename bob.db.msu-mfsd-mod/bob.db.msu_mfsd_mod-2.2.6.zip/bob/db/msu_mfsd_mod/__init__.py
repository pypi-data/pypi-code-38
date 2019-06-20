#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Wed 18 May 09:28:44 2011

"""The msu_mfsd_mod face-spoof Database accessors for Bob
"""

from .query import Database
from .verificationprotocol import Database as VerificationDatabase, File as VerificationFile
from .models import Client, File

def get_config():
  """Returns a string containing the configuration information.
  """
  import bob.extension
  return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
