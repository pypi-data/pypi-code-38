#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>

"""This is the Bob database entry for the Multi-PIE database.
"""

from .query import Database
from .models import Client, Subworld, File, FileMultiview, Expression, Camera, Protocol, ProtocolPurpose

def get_config():
  """Returns a string containing the configuration information.
  """
  import bob.extension
  return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
