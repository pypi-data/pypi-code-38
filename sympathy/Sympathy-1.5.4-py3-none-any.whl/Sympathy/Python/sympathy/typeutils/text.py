# Copyright (c) 2013, Combine Control Systems AB
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
API for working with the Text type.

Import this module like this::

    from sympathy.api import text

Class :class:`text.File`
------------------------
.. autoclass:: File
   :members:
   :special-members:

"""
import numpy as np
from .. utils import filebase
from .. utils.context import inherit_doc


def is_text(scheme, filename):
    return File.is_type(filename, scheme)


def is_texts(scheme, filename):
    return FileList.is_type(filename, scheme)


@filebase.typeutil('sytypealias text = sytext')
@inherit_doc
class File(filebase.TypeAlias):
    """
    A Text type containing arbitrary text, be it Hamlet or some json encoded
    data structure.

    Any node port with the *Text* type will produce an object of this kind.
    """

    def set(self, text_data):
        """Set text data."""
        self._data.set(text_data)

    def get(self):
        """Return text data."""
        return self._data.get()

    def update(self, other):
        """Copy the contents from ``other`` :class:`text.File`.
        Equivalent to :meth:`source`.
        """
        self._data.update(other._data)

    def source(self, other, shallow=False):
        """Copy the contents from ``other`` :class:`text.File`.
        Equivalent to :meth:`update`.
        """
        self.set(other.get())

    def names(self, kind=None, **kwargs):
        """Return a formatted list with a name and type of the data.
        columns."""
        if kind == 'calc':
            return ['.get()']
        return []

    def types(self, kind=None, **kwargs):
        """Return types associated with names."""
        if kind == 'calc':
            return [np.dtype('U')]
        return []

    @classmethod
    def viewer(cls):
        from .. platform import text_viewer
        return text_viewer.TextViewer

    @classmethod
    def icon(cls):
        return 'ports/text.svg'


@inherit_doc
class FileList(filebase.FileListBase):
    """
    FileList has been changed and is now just a function which creates
    generators to sybase types.

    Old documentation follows:

    The :class:`FileList` class is used when working with lists of Texts.

    The main interfaces in :class:`FileList` are indexing or iterating for
    reading (see the :meth:`__getitem__()` method) and the :meth:`append()`
    method for writing.
    """

    sytype = '[text]'
    scheme = 'hdf5'
