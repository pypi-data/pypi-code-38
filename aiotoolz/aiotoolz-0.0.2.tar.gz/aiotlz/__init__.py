"""``aiotlz`` mirrors the ``aiotoolz`` API and uses ``cytoolz`` if possible.

The ``aiotlz`` package is installed when ``aiotoolz`` is installed.
It provides a convenient way to use functions from ``cytoolz``--a faster
Cython implementation of ``aiotoolz``--if it is installed, otherwise it uses
functions from ``aiotoolz``.
"""

from . import _build_tlz
