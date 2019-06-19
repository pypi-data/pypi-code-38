# import Libraries of other lib packages
import bob.core

# import our own Library
import bob.extension
bob.extension.load_bob_library('bob.sp', __file__)

from ._library import *
from . import version
from .version import module as __version__


def extrapolate_zero(src, dst):
  """Extrapolates the values in ``src`` to ``dst`` with zeros.

  Input ``src`` (and ``dst``) arrays can be 1 or 2-dimensional. For more
  details, read the help for :py:func:`extrapolate`.

  Parameters:

  src
    (array) A 1 or 2D array that is going to be extrapolated

  dst
    (array) A pre-allocated array, with the same number of dimensions
    as in ``src``, where the extrapolation results will be placed.

  Returns ``None``, raises in case of errors.
  """

  return extrapolate(src, dst, BorderType.Zero)


def extrapolate_mirror(src, dst):
  """Extrapolates the values in ``src`` to ``dst``, mirroring ``src``.

  Input ``src`` (and ``dst``) arrays can be 1 or 2-dimensional. For more
  details, read the help for :py:func:`extrapolate`.

  Parameters:

  src
    (array) A 1 or 2D array that is going to be extrapolated

  dst
    (array) A pre-allocated array, with the same number of dimensions
    as in ``src``, where the extrapolation results will be placed.

  Returns ``None``, raises in case of errors.
  """

  return extrapolate(src, dst, BorderType.Mirror)


def extrapolate_nearest(src, dst):
  """Extrapolates the values in ``src`` to ``dst``, with nearest values.

  Input ``src`` (and ``dst``) arrays can be 1 or 2-dimensional. For more
  details, read the help for :py:func:`extrapolate`.

  Parameters:

  src
    (array) A 1 or 2D array that is going to be extrapolated

  dst
    (array) A pre-allocated array, with the same number of dimensions
    as in ``src``, where the extrapolation results will be placed.

  Returns ``None``, raises in case of errors.
  """

  return extrapolate(src, dst, BorderType.NearestNeighbour)


def extrapolate_constant(src, dst, constant):
  """Extrapolates the values in ``src`` to ``dst``, with a constant value.

  Input ``src`` (and ``dst``) arrays can be 1 or 2-dimensional. For more
  details, read the help for :py:func:`extrapolate`.

  Parameters:

  src
    (array) A 1 or 2D array that is going to be extrapolated

  dst
    (array) A pre-allocated array, with the same number of dimensions
    as in ``src``, where the extrapolation results will be placed.

  constant
    (scalar) A scalar with matching type of ``src`` and ``dst``,
    containing the value that will be used to extrapolate ``src`` into
    ``dst``.

  Returns ``None``, raises in case of errors.
  """

  return extrapolate(src, dst, BorderType.Constant, constant)


def extrapolate_circular(src, dst):
  """Extrapolates the values in ``src`` to ``dst``, using circular
  extrapolation.

  Input ``src`` (and ``dst``) arrays can be 1 or 2-dimensional. For more
  details, read the help for :py:func:`extrapolate`.

  Parameters:

  src
    (array) A 1 or 2D array that is going to be extrapolated

  dst
    (array) A pre-allocated array, with the same number of dimensions
    as in ``src``, where the extrapolation results will be placed.

  Returns ``None``, raises in case of errors.
  """

  return extrapolate(src, dst, BorderType.Circular)


def get_config():
  """Returns a string containing the configuration information.
  """
  return bob.extension.get_config(__name__, version.externals, version.api)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
