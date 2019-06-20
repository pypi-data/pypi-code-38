#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""
The MNIST Database is a database of handwritten digits, which has a training
set of 60,000 examples, and a test set of 10,000 examples. It is a subset of
a larger set available from NIST. The digits have been size-normalized and
centered in a fixed-size image.
"""


from .query import Database


def get_config():
  """Returns a string containing the configuration information.
  """

  import bob.extension
  return bob.extension.get_config(__name__)


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
    Database,
    )

__all__ = [_ for _ in dir() if not _.startswith('_')]
