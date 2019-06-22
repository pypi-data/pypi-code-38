# -*- coding: utf-8 -*-

"""
:mod:`taika`
============

The top-level package contain some meta info about the package to be accessible by other tools.

.. data:: __author__ (str)

    The author name.

.. data:: __email__ (str)

    The email of `__author__`.

.. data:: __version__ (str)

    The version of the package.
"""

from taika.taika import Taika

__all__ = ["__author__", "__email__", "__version__"]
__all__ += ["Taika"]


__author__ = """Hector Martinez-Lopez"""
__email__ = "hector.martinez.ub@gmail.com"
__version__ = "0.6.0"
