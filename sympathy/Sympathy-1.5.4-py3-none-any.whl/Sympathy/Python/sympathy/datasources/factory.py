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
"""Factory module for datasources."""
from . hdf5.dstypes import types as hdf5
from . text.dstypes import types as text
import numpy as tmp


class DatasourceFactory(object):
    """Returns a data source object for the required data source."""
    datasource_from_scheme = {
        'hdf5': hdf5,
        'text': text,
        'tmp': tmp
    }

    def __init__(self, datapointer):
        self._datapointer = datapointer
        self.types = self.datasource_from_scheme[datapointer.scheme]

    def create_list(self, container_type):
        """Return a list datasource."""
        return self.from_constructor(container_type, self.types.list_type)

    def create_dict(self, container_type):
        """Return a dict datasource."""
        return self.from_constructor(container_type, self.types.dict_type)

    def create_record(self, container_type):
        """Return a record datasource."""
        return self.from_constructor(container_type, self.types.record_type)

    def create_tuple(self, container_type):
        """Return a tuple datasource."""
        return self.from_constructor(container_type, self.types.record_type)

    def create_text(self, container_type):
        """Return a text datasource."""
        return self.from_constructor(container_type, self.types.text_type)

    def create_table(self, container_type):
        """Return a table datasource."""
        return self.from_constructor(container_type, self.types.table_type)

    def create_lambda(self, container_type):
        """Return a lambda datasource."""
        return self.from_constructor(container_type, self.types.lambda_type)

    def from_constructor(self, container_type, constructor):
        """Return a datasource determined by category."""
        return constructor(self._datapointer, container_type)
