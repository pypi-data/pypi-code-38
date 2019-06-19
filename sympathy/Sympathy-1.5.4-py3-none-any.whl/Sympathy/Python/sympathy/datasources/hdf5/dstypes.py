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
"""HDF5 type constructor module."""
from . dslist import Hdf5List as list_type
from . dsdict import Hdf5Dict as dict_type
from . dsrecord import Hdf5Record as record_type
from . dstable import Hdf5Table as table_type
from . dstext import Hdf5Text as text_type
from . dslambda import Hdf5Lambda as lambda_type
from ... types.types import (TypeList,
                             TypeDict,
                             TypeRecord,
                             TypeTuple,
                             TypeTable,
                             TypeText,
                             TypeFunction,
                             TypeAlias)


def factory(content_type):
    """Return datasource constructor according to content_type."""
    # Construct the child element.
    if isinstance(content_type, TypeList):
        return list_type
    elif isinstance(content_type, TypeDict):
        return dict_type
    elif isinstance(content_type, TypeRecord):
        return record_type
    elif isinstance(content_type, TypeTuple):
        return record_type
    elif isinstance(content_type, TypeTable):
        return table_type
    elif isinstance(content_type, TypeText):
        return text_type
    elif isinstance(content_type, TypeFunction):
        return lambda_type
    elif isinstance(content_type, TypeAlias):
        while isinstance(content_type, TypeAlias):
            content_type = content_type.get()
        return factory(content_type)
    else:
        raise Exception('Unknown content type: {}'.format(type(content_type)))


class Hdf5Factory(object):
    """
    Returns HDF5 type constructors.
    Creates typed instances.
    """
    def factory(self, group, content_type, can_write, can_link):
        """Return contained list slice."""
        return factory(content_type)(self.factory,
                                     group=group,
                                     can_write=can_write,
                                     can_link=can_link)

    def list_type(self, datapointer, container_type):
        """Return the HDF5 list type constructor."""
        return list_type(self.factory,
                         datapointer=datapointer)

    def dict_type(self, datapointer, container_type):
        """Return the HDF5 dict type constructor."""
        return dict_type(self.factory,
                         datapointer=datapointer)

    def record_type(self, datapointer, container_type):
        """Return the HDF5 record type constructor."""
        return record_type(self.factory,
                           datapointer=datapointer)

    def table_type(self, datapointer, container_type):
        """Return the HDF5 table type constructor."""
        return table_type(self.factory,
                          datapointer=datapointer)

    def text_type(self, datapointer, container_type):
        """Return the HDF5 text type constructor."""
        return text_type(self.factory,
                         datapointer=datapointer)

    def lambda_type(self, datapointer, container_type):
        """Return the HDF5 lambda type constructor."""
        return lambda_type(self.factory,
                           datapointer=datapointer)


types = Hdf5Factory()
