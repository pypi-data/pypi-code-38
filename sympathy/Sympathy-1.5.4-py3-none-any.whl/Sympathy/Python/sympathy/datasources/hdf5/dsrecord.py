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
"""HDF5 record."""
from . import dsgroup


class Hdf5Record(dsgroup.Hdf5Group):
    """Abstraction of an HDF5-list."""
    def __init__(self, factory, group=None, datapointer=None, can_write=False,
                 can_link=False):
        super(Hdf5Record, self).__init__(
            factory, group, datapointer, can_write, can_link)

    def read_with_type(self, key, content_type):
        """Reads element at key and returns it as a datasource."""
        key = dsgroup.replace_slash(key)
        group = self.group[key]
        try:
            return self.factory(group, content_type, self.can_write,
                                self.can_link)
        except TypeError:
            raise TypeError('Investigating:{} from:{}'.format(
                repr(key), repr(self.group.name)))

    def write_with_type(self, key, value, content_type):
        """Write group at key and returns the group as a datasource."""
        key_group = self._group_get_or_create(dsgroup.replace_slash(key))

        return self.factory(
            key_group, content_type, self.can_write, self.can_link)

    def link_with(self, key, value):
        key = dsgroup.replace_slash(key)

        if key in self.group:
            assert(False)
        else:
            self.group[key] = value.link()

    def keys(self):
        """Return the record keys"""
        return [dsgroup.restore_slash(key) for key in self.group.keys()]
