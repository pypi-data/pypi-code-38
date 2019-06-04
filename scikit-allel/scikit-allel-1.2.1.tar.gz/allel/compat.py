# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import absolute_import, print_function, division


import sys
import itertools


PY2 = sys.version_info[0] == 2


if PY2:
    range = xrange
    map = itertools.imap
    string_types = basestring,
    text_type = unicode
    binary_type = str
    integer_types = int, long
    zip = itertools.izip
    zip_longest = itertools.izip_longest
    reduce = reduce
    from urllib import unquote_plus
    FileNotFoundError = IOError
    IsADirectoryError = IOError

    def copy_method_doc(m, n):
        """Copy docstring from `n` to `m`."""
        m.__func__.__doc__ = n.__doc__

else:
    range = range
    map = map
    string_types = str,
    text_type = str
    binary_type = bytes
    integer_types = int,
    zip = zip
    zip_longest = itertools.zip_longest
    import functools
    reduce = functools.reduce
    from urllib.parse import unquote_plus
    FileNotFoundError = FileNotFoundError
    IsADirectoryError = IsADirectoryError

    def copy_method_doc(m, n):
        """Copy docstring from `n` to `m`."""
        m.__doc__ = n.__doc__


def memoryview_safe(x):
    """Make array safe to run in a Cython memoryview-based kernel. These
    kernels typically break down with the error ``ValueError: buffer source
    array is read-only`` when running in dask distributed.

    See Also
    --------
    https://github.com/dask/distributed/issues/1978
    https://github.com/cggh/scikit-allel/issues/206

    """
    if not x.flags.writeable:
        if not x.flags.owndata:
            x = x.copy(order='A')
        x.setflags(write=True)
    return x
