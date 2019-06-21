from .crop import Cropper, FixedCrop, NoCrop
from .mask import Padder, Masker, FixedMask, NoMask, AnnotatedRoIMask
from .mask import KonoMask, LeeMask, TomesLeeMask, WatershedMask
from .normalize import Normalizer, NoNormalization, HuangNormalization
from .filters import Filter, NoFilter, HistogramEqualization
from .preprocessor import Preprocessor

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
    Cropper,
    FixedCrop,
    NoCrop,
    Padder,
    Masker,
    FixedMask,
    NoMask,
    AnnotatedRoIMask,
    KonoMask,
    LeeMask,
    TomesLeeMask,
    WatershedMask,
    Normalizer,
    NoNormalization,
    HuangNormalization,
    Filter,
    NoFilter,
    HistogramEqualization,
    Preprocessor,
    )
__all__ = [_ for _ in dir() if not _.startswith('_')]
