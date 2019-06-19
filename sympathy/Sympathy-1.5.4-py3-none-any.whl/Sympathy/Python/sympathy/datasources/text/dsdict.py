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
"""Text dict."""
import six
from . import dsgroup


class TextDict(dsgroup.TextGroup):
    """Abstraction of an Text-dict."""
    def __init__(self,
                 factory,
                 create_content,
                 datapointer,
                 group=None,
                 can_write=False,
                 container_type=None,
                 create_path=None,):
        super(TextDict, self).__init__(
            factory, create_content, datapointer, group, can_write,
            container_type, create_path)

    def read_with_type(self, key, content_type):
        """Reads element at key and returns it as a datasource."""
        return self.factory(
            self.datapointer, self.group[key], content_type, self.can_write)

    def write_with_type(self, key, value, content_type):
        """Write group at key and returns the group as a datasource."""
        if key in self.group:
            key_group = self.group[key]
        else:
            key_group = self.create_content(content_type)
            self.group[key] = key_group

        return self.factory(
            self.datapointer, key_group, content_type, self.can_write)

    def items(self, content_type):
        return [(key, self.factory(
            self.datapointer, value, content_type, self.can_write))
            for key, value in six.iteritems(self.group)]

    def contains(self, key):
        return key in self.group

    def keys(self):
        """Return the keys."""
        return self.group.keys()

    def size(self):
        """Return the dict size."""
        return len(self.group)

    def delete(self, key):
        if self.contains(key):
            raise ValueError("Trying to delete stored value.")
