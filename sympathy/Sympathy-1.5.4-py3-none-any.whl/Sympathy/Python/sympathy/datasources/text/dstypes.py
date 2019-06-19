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
"""Text type constructor module."""
from . dslist import TextList as list_type
from . dsdict import TextDict as dict_type
from . dsrecord import TextRecord as record_type
from . dstable import TextTable as table_type
from . dstext import TextText as text_type
from . dslambda import TextLambda as lambda_type
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


def create_content(content_type):
    """Return the text group element for the given content type."""
    if isinstance(content_type, TypeList):
        return []
    else:
        return {}


def create_path(container, container_type, path):
    """Create path in file returning the group at container[path]."""

    def create_key(container_type, key):
        """
        Parse string key depending on type.
        Return parsed key.
        """
        if isinstance(container_type, TypeList):
            return int(key)
        else:
            return key

    def set_content(container, container_type, key, value):
        """Set content."""
        if isinstance(container_type, TypeList):
            assert int(key) == container(len)
            container.append(value)
        else:
            container[key] = value

    def update_content(container, container_type, key):
        """
        Get value in container matching key.
        If it does not exist create new value according to type.
        Return tuple of value and its content type.
        """
        key = create_key(container_type, key)
        content_type = container_type[key]

        try:
            content = container[key]
        except KeyError:
            content = create_content(content_type)
            set_content(container, container_type, key, content)
        return (content, content_type)

    root = container

    # Adding other keys.
    for key in [key for key in path.split("/") if key != '']:
        root, container_type = update_content(root, container_type, key)
    return root


class TextFactory(object):
    """
    Returns Text type constructors.
    Creates typed instances.
    """
    def factory(self, datapointer, group, content_type, can_write):
        """Return contained list slice."""
        return factory(content_type)(self.factory,
                                     create_content,
                                     datapointer,
                                     group=group,
                                     can_write=can_write)

    def list_type(self, datapointer, container_type):
        """Return the Text list type constructor."""
        return list_type(self.factory,
                         create_content,
                         datapointer,
                         container_type=container_type,
                         create_path=create_path)

    def dict_type(self, datapointer, container_type):
        """Return the Text dict type constructor."""
        return dict_type(self.factory,
                         create_content,
                         datapointer,
                         container_type=container_type,
                         create_path=create_path)

    def record_type(self, datapointer, container_type):
        """Return the Text record type constructor."""
        return record_type(self.factory,
                           create_content,
                           datapointer,
                           container_type=container_type,
                           create_path=create_path)

    def table_type(self, datapointer, container_type):
        """Return the Text table type constructor."""
        return table_type(self.factory,
                          create_content,
                          datapointer,
                          container_type=container_type,
                          create_path=create_path)

    def text_type(self, datapointer, container_type):
        """Return the Text text type constructor."""
        return text_type(self.factory,
                         create_content,
                         datapointer,
                         container_type=container_type,
                         create_path=create_path)

    def lambda_type(self, datapointer, container_type):
        """Return the Text lambda type constructor."""
        return lambda_type(self.factory,
                           create_content,
                           datapointer,
                           container_type=container_type,
                           create_path=create_path)


types = TextFactory()
