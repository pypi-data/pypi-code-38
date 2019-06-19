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
"""Interfacing with the path string."""
from . types import from_string_expand


BOOL = {'True': True, 'False': False}


class Util(object):
    """
    Util is a convenience class for safely accessing information from a
    datapointer.
    """

    def __init__(self, datapointer):
        self.datapointer = datapointer

    def file_path(self):
        """Return the pointer url path element."""
        return self.datapointer.path

    def path(self):
        """Return the pointer path fragment."""
        return self.datapointer.fragment("path")

    def mode(self):
        """Return the pointer mode fragment, or r if it does not exist."""
        try:
            mode = self.datapointer.fragment("mode")
            assert(mode in ['r', 'r+', 'w'])
        except KeyError:
            mode = 'r'
        return mode

    def datatype(self):
        """Return the pointer data type fragment."""
        dtype = str(from_string_expand(self.datapointer.fragment("type")))
        dtype = dtype.replace('sytable', 'table')
        dtype = dtype.replace('sytext', 'text')
        return dtype

    def type(self):
        return str(from_string_expand(self.datapointer.fragment("type")))

    def abstype(self):
        return str(self.datapointer.fragment("type"))

    def can_write(self):
        """Returns True if the data source can be written, False otherwise."""
        try:
            return self.mode() == 'w'
        except KeyError:
            return False

    def can_link(self):
        """Returns True if the data source can use links, False otherwise.."""
        try:
            return BOOL[self.datapointer.fragment("link")]
        except KeyError:
            return False


class DataPointer(object):
    """Pointer to data."""
    def __init__(self, url):
        self.url = url
        self.scheme, fullpath = url.split('://')

        fragment_id = None
        if '#' in fullpath:
            self.path, fragment_id = fullpath.rsplit('#', 1)
        try:
            fragment_list = fragment_id.split('&')
            self._fragment_dict = dict([tuple(fragment.split('='))
                                        for fragment in fragment_list])
        except AttributeError:
            self._fragment_dict = {}

    def fragment(self, name):
        """Getter for fragment."""
        return self._fragment_dict[name]

    def set_fragment(self, name, value):
        """Setter for fragment."""
        self._fragment_dict[name] = value

    def del_fragment(self, name):
        """Deleter for fragment."""
        del self._fragment_dict[name]

    def util(self):
        """Returns a Util class instance."""
        return Util(self)

    def copy(self):
        """Copy datapointer."""
        return DataPointer(self.url)
