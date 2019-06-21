from .lbps import LBPs
from .ratios import Ratios
from .vectors_ratios import VectorsRatios
from .glcms import GLCMs
from .spectrogram_extended import SpectrogramExtended
from .lbp_histograms import LBPHistograms
from .dummy_tensorflow import DummyTF
from .audio_tensorflow import AudioTFExtractor

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
    Ratios,
    LBPs,
    VectorsRatios,
    GLCMs,
    SpectrogramExtended,
    LBPHistograms,
    DummyTF,
    AudioTFExtractor,
    )
__all__ = [_ for _ in dir() if not _.startswith('_')]
