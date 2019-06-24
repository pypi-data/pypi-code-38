from .haggregate import *  # NOQA

# I'd like to also have "from .regularize import *" here, but because "regularize" is
# in Cython, it causes problems for sphinx and readthedocs, which want to get
# __version__ from this file. When building the docs, "regularize" might not have been
# compiled, which would throw an import error.

__author__ = """Antonis Christofides"""
__email__ = "antonis@antonischristofides.com"
__version__ = "0.1.1"
