from .file import PadFile
from .database import PadDatabase
from .filelist.query import FileListPadDatabase
from .filelist.models import Client
from .PadBioFileDB import HighBioDatabase, HighPadDatabase

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
    PadFile,
    PadDatabase,
    FileListPadDatabase,
    Client,
    HighBioDatabase,
    HighPadDatabase
)
__all__ = [_ for _ in dir() if not _.startswith('_')]
