#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Fri 20 Sep 14:45:01 2013

from ._library import array, as_blitz
from . import version
from .version import module as __version__
from .version import api as __api_version__

def get_config():
  """Returns a string containing the configuration information.
  """

  import bob.extension
  return bob.extension.get_config(__name__, version.externals, version.api)

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
