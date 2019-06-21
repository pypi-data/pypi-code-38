from .utils import *

from . import database
from . import algorithm
from . import tools

from . import script
from . import test


def padfile_to_label(padfile):
  """Returns an integer presenting the label of the current sample.

  Parameters
  ----------
  padfile : :any:`bob.pad.base.database.PadFile`
      A pad file.

  Returns
  -------
  bool
      True (1) if it is a bona-fide sample, False (O) otherwise.
  """
  return padfile.attack_type is None


def get_config():
  """Returns a string containing the configuration information.
  """
  import bob.extension
  return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
