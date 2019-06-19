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
Provides means to get FileInfo objects with the following interface.
These provide information usable to distinguish the file format.

>>> class FileInfo(object):
>>>     def __init__(self, filepath):
>>>         # ...
>>>         pass
>>>
>>>     def is_file(self):
>>>         # ...
>>>         pass
>>>
>>>     def header(self):
>>>         # ...
>>>         pass
>>>
>>>     def version(self):
>>>         # ...
>>>         pass
>>>
>>>     def datatype(self):
>>>         # ...
>>>         pass
"""
import re
from . hdf5.dsinfo import FileInfo as Hdf5FileInfo
from . text.dsinfo import FileInfo as TextFileInfo

retype = re.compile(b"^SFD ([A-Z0-9]*)")


INFO_FROM_SCHEME = {
    'hdf5': Hdf5FileInfo,
    'text': TextFileInfo,
}


def get_fileinfo_from_scheme(scheme):
    """Return the FileInfo class associated with scheme."""
    return INFO_FROM_SCHEME[scheme]


def get_fileinfo_from_file(filename):
    """Return the FileInfo class associated with filename."""
    return INFO_FROM_SCHEME[get_scheme_from_file(filename)]


def get_scheme_from_file(filename):
    """Return the scheme associated with filename."""
    res = None
    with open(filename, 'rb') as f:
        match = retype.match(
            f.readline().split(b'{')[0])
        if match:
            res = match.groups()[0].decode('ascii').lower()
    return res
