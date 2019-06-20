#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""A very simple API to query and load data from the COHFACE database.
"""

import os
from .models import *
from .driver import Interface, DATABASE_LOCATION

from pkg_resources import resource_filename

class Database(object):


  def __init__(self, dbdir=DATABASE_LOCATION):
    self.info = Interface()

    self.metadata = []
    for path, dirs, files in os.walk(dbdir):
      if 'data.hdf5' in files: #object directory
        relpath = os.path.relpath(path, dbdir)
        self.metadata.append(os.path.join(relpath, 'data'))


  def objects(self, protocol='all', subset=None):
    """Returns a list of unique :py:class:`.File` objects for the specific
    query by the user.


    Parameters:

      protocol (:py:class:`str`, optional): If set, it should be either
        ``clean``, ``natural`` or ``all``.  All, which is the default,
        considers all the illumination conditions whereas clean retrieves only
        sequences where the spot in on and natural the ones with daylight
        illumination.

      subset (:py:class:`str`, optional): If set, it could be either ``train``,
        ``dev`` or ``test`` or a combination of them (i.e. a list). If not set
        (default), the files from all these sets are retrieved, according to
        the protocol.

    Returns:

      list: A list of :py:class:`File` objects.

    """
    files = []

    proto_basedir = os.path.join('data', 'protocols')

    # clean protocol -> face is illuminated with a spot
    if protocol in ('clean'):

      if not subset:
        d = resource_filename(__name__, os.path.join(proto_basedir, 'clean', 'all.txt'))
        with open(d, 'rt') as f: sessions = f.read().split()
        files += [File(k) for k in self.metadata if k in sessions]
        return files
      else:
        if 'train' in subset:
          d = resource_filename(__name__, os.path.join(proto_basedir, 'clean', 'train.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(k) for k in self.metadata if k in sessions]
        if 'dev' in subset:
          d = resource_filename(__name__, os.path.join(proto_basedir, 'clean', 'dev.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(k) for k in self.metadata if k in sessions]
        if 'test' in subset:
          d = resource_filename(__name__, os.path.join(proto_basedir, 'clean', 'test.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(k) for k in self.metadata if k in sessions]

        return files

    # natural protocol -> no specific illumination (daylight)
    if protocol in ('natural'):

      if not subset:
        d = resource_filename(__name__, os.path.join(proto_basedir, 'natural', 'all.txt'))
        with open(d, 'rt') as f: sessions = f.read().split()
        files += [File(k) for k in self.metadata if k in sessions]
        return files
      else:
        if 'train' in subset:
          d = resource_filename(__name__, os.path.join(proto_basedir, 'natural', 'train.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(k) for k in self.metadata if k in sessions]
        if 'dev' in subset:
          d = resource_filename(__name__, os.path.join(proto_basedir, 'natural', 'dev.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(k) for k in self.metadata if k in sessions]
        if 'test' in subset:
          d = resource_filename(__name__, os.path.join(proto_basedir, 'natural', 'test.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(k) for k in self.metadata if k in sessions]

        return files


    # protocol with both conditions, spot + natural illumination (default)
    if protocol in ('all'):

      if not subset:
        d = resource_filename(__name__, os.path.join(proto_basedir, 'all', 'all.txt'))
        with open(d, 'rt') as f: sessions = f.read().split()
        files += [File(k) for k in self.metadata if k in sessions]
        return files
      else:
        if 'train' in subset:
          d = resource_filename(__name__, os.path.join(proto_basedir, 'all', 'train.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(k) for k in self.metadata if k in sessions]
        if 'dev' in subset:
          d = resource_filename(__name__, os.path.join(proto_basedir, 'all', 'dev.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(k) for k in self.metadata if k in sessions]
        if 'test' in subset:
          d = resource_filename(__name__, os.path.join(proto_basedir, 'all', 'test.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(k) for k in self.metadata if k in sessions]

      return files


# gets sphinx autodoc done right - don't remove it
def __appropriate__(*args):
  """Says object was actually declared here, an not on the import module.

  Parameters:

    *args: An iterable of objects to modify

  Resolves `Sphinx referencing issues
  <https://github.com/sphinx-doc/sphinx/issues/3048>`
  """

  for obj in args: obj.__module__ = __name__

__appropriate__(
    File,
    )

__all__ = [_ for _ in dir() if not _.startswith('_')]
