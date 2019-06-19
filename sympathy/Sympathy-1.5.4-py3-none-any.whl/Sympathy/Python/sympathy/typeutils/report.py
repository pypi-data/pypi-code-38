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

from sympathy.utils import filebase
from sympathy.utils import port
from .. utils.context import inherit_doc


def is_report(scheme, filename):
    return File.is_type(filename, scheme)


def is_reports(scheme, filename):
    return FileList.is_type(filename, scheme)


@filebase.typeutil('sytypealias report = sytext')
@inherit_doc
class File(filebase.TypeAlias):
    """Report type."""

    def set(self, report_data):
        self._data.set(report_data)

    def get(self):
        # If data is not set return an empty (json-encoded) dictionary instead
        # of empty string so the result can always be json decoded.
        return self._data.get() or '{}'

    def update(self, other):
        self._data.update(other._data)

    def source(self, other, shallow=False):
        self.set(other.get())

    @classmethod
    def viewer(cls):
        from .. platform import report_viewer
        return report_viewer.ReportViewer

    @classmethod
    def icon(cls):
        return 'ports/report.svg'


@inherit_doc
class FileList(filebase.FileListBase):
    """List of reports type."""

    sytype = '[report]'
    scheme = 'text'


def Report(description, name=None):
    return port.PortType(description, 'report', scheme='text', name=name)


def Reports(description, name=None):
    return port.PortType(description, '[report]', scheme='text', name=name)
