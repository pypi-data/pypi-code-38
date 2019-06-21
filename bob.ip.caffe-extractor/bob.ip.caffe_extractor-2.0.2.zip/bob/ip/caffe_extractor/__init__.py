#!/usr/bin/env python


def download_file(url, out_file):
  """Downloads a file from a given url

  Parameters
  ----------
  url : str
      The url to download form.
  out_file : str
      Where to save the file.
  """
  import sys
  if sys.version_info[0] < 3:
    # python2 technique for downloading a file
    from urllib2 import urlopen
    with open(out_file, 'wb') as f:
      response = urlopen(url)
      f.write(response.read())

  else:
    # python3 technique for downloading a file
    from urllib.request import urlopen
    from shutil import copyfileobj
    with urlopen(url) as response:
      with open(out_file, 'wb') as f:
        copyfileobj(response, f)

from .Extractor import Extractor
from .VGGFace import VGGFace
from .LightCNN import LightCNN


def get_config():
  """Returns a string containing the configuration information.
  """
  import bob.extension
  return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
def __appropriate__(*args):
  """Says object was actually declared here, and not in the import module.
  Fixing sphinx warnings of not being able to find classes, when path is shortened.
  Parameters:

    *args: An iterable of objects to modify

  Resolves `Sphinx referencing issues
  <https://github.com/sphinx-doc/sphinx/issues/3048>`
  """

  for obj in args:
    obj.__module__ = __name__

__appropriate__(
    Extractor,
    VGGFace,
)

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
