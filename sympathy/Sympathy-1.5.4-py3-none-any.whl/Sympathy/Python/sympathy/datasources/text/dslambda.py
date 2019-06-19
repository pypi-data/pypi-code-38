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
"""Text Data source module."""
from . import dsgroup


class TextLambda(dsgroup.TextGroup):
    """Abstraction of an Text-lambda."""
    def __init__(self,
                 factory,
                 create_content,
                 datapointer,
                 group=None,
                 can_write=False,
                 container_type=None,
                 create_path=None,):
        super(TextLambda, self).__init__(
            factory, create_content, datapointer, group, can_write,
            container_type, create_path)

    def read(self):
        """
        Return stored pair of flow and list of port assignments or None if
        nothing is stored.
        """
        if 'lambda' in self.group:
            column = self.group['lambda']
            return (column[0], column[1])
        return None

    def write(self, value):
        """
        Stores lambda in the hdf5 file, at path,
        with data from the given text
        """
        self.group['lambda'] = (value[0],) + value[1]

    def transferable(self, other):
        return False

    def transfer(self, other):
        self.group['lambda'] = other.group['lambda']
