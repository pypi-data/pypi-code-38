#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 18 Nov 21:38:19 2013

"""Extension building for using this package
"""

import numpy
from pkg_resources import resource_filename
from bob.extension import Extension as BobExtension
# forward the build_ext command from bob.extension
from bob.extension import build_ext, Library as BobLibrary
from distutils.version import LooseVersion

class Extension(BobExtension):
  """Extension building with pkg-config packages and blitz.array.

  See the documentation for :py:class:`distutils.extension.Extension` for more
  details on input parameters.
  """

  def __init__(self, *args, **kwargs):
    """Initialize the extension with parameters.

    This extension adds ``blitz>=0.10`` as a requirement for extensions derived
    from this class.

    See the help for :py:class:`bob.extension.Extension` for more details on
    options.
    """

    require = ['blitz>=0.10', 'boost']

    kwargs.setdefault('packages', []).extend(require)

    self_include_dir = resource_filename(__name__, 'include')
    kwargs.setdefault('system_include_dirs', []).append(numpy.get_include())
    kwargs.setdefault('include_dirs', []).append(self_include_dir)

    macros = [
          ("PY_ARRAY_UNIQUE_SYMBOL", "BOB_NUMPY_C_API"),
          ("NO_IMPORT_ARRAY", "1"),
          ]

    if LooseVersion(numpy.__version__) >= LooseVersion('1.7'):
      macros.append(("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"))

    kwargs.setdefault('define_macros', []).extend(macros)

    # Run the constructor for the base class
    BobExtension.__init__(self, *args, **kwargs)


class Library (BobLibrary):
  """Pure C++ library building with blitz array.

  See the documentation for :py:class:`bob.extension.Extension` for more
  details on input parameters.
  """

  def __init__(self, *args, **kwargs):
    """Initialize the library with parameters.

    This library adds ``blitz>=0.10`` as a requirement for library derived
    from this class.

    See the help for :py:class:`bob.extension.Library` for more details on
    options.
    """

    require = ['blitz>=0.10', 'boost']

    kwargs.setdefault('packages', []).extend(require)

    self_include_dir = resource_filename(__name__, 'include')
    kwargs.setdefault('system_include_dirs', []).append(numpy.get_include())
    kwargs.setdefault('include_dirs', []).append(self_include_dir)

    # TODO: are these macros required for pure C++ builds?
    macros = [
          ("PY_ARRAY_UNIQUE_SYMBOL", "BOB_NUMPY_C_API"),
          ("NO_IMPORT_ARRAY", "1"),
          ]

    if LooseVersion(numpy.__version__) >= LooseVersion('1.7'):
      macros.append(("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"))

    kwargs.setdefault('define_macros', []).extend(macros)

    # Run the constructor for the base class
    BobLibrary.__init__(self, *args, **kwargs)
