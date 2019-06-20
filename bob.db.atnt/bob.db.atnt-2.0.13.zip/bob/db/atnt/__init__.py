#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Fri Apr 20 12:04:44 CEST 2012


"""
The AT&T "Database of Faces" is a small free facial image database to test face
recognition and verification algorithms on. It is also known by its former name
"The ORL Database of Faces". You can download the AT&T database from:
http://www.cl.cam.ac.uk/research/dtg/attarchive/facedatabase.html
"""

from .models import File, Client
from .query import Database


def get_config():
  """Returns a string containing the configuration information.
  """
  import bob.extension
  return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
