# Copyright (c) 2015, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Utility functionality for working with the fundamental data types in sympathy.
"""
import collections

import six
import numpy as np


_KINDS = {'b': 'bool',
          'i': 'integer',
          'u': 'integer',
          'f': 'float',
          'c': 'complex',
          'S': 'bytes',
          'U': 'text',
          'M': 'datetime',
          'm': 'timedelta'}


_DTYPES = collections.OrderedDict([
    ('bool', np.dtype(bool)),
    ('integer', np.dtype(int)),
    ('float', np.dtype(float)),
    ('complex', np.dtype(complex)),
    ('text', np.dtype(six.text_type)),
    ('bytes', np.dtype(six.binary_type)),
    ('datetime', np.dtype('datetime64[us]')),
    ('timedelta', np.dtype('timedelta64[us]'))])


def typename_from_kind(kind):
    """Return typename assocated with kind."""
    return _KINDS[kind]


def dtype(name):
    """
    Return dtype from name.

    Supports typenames, our special interpretation for some numpy.dtype.kinds,
    as well as regular numpy.dtype strings.
    """
    if name in _KINDS:
        return _DTYPES[_KINDS[name]]
    elif name in _DTYPES:
        return _DTYPES[name]
    else:
        return np.dtype(name)


def typenames():
    """Return list of all handled typenames."""
    return list(_DTYPES.keys())
