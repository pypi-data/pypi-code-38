from .database import PadVoiceFile, VoicePadFile
from .asvspoof import ASVspoofPadDatabase
from .asvspoof2017 import ASVspoof2017PadDatabase
from .avspoof import AVspoofPadDatabase
from .voicepa import VoicePAPadDatabase

# gets sphinx autodoc done right - don't remove it
def __appropriate__(*args):
  """Says object was actually declared here, and not in the import module.
  Fixing sphinx warnings of not being able to find classes, when path is shortened.
  Parameters:

    *args: An iterable of objects to modify

  Resolves `Sphinx referencing issues
  <https://github.com/sphinx-doc/sphinx/issues/3048>`
  """

  for obj in args: obj.__module__ = __name__

__appropriate__(
    PadVoiceFile,
    VoicePadFile,
    ASVspoofPadDatabase,
    AVspoofPadDatabase,
    VoicePAPadDatabase,
    ASVspoof2017PadDatabase,
    )
__all__ = [_ for _ in dir() if not _.startswith('_')]
