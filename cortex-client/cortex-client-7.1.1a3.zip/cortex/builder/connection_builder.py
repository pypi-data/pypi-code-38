"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from cortex.logger import getLogger
from cortex_client import ConnectionClient
from cortex.connection import Connection

log = getLogger(__name__)


class ConnectionBuilder:

    """
    A builder utility to aid in programmatic creation of Cortex Connections.  Not meant to be directly instantiated by
    clients.
    """

    def __init__(self, name: str, client: ConnectionClient, camel='1.0.0'):
        self._camel = camel
        self._name = name
        self._title = None
        self._description = None
        self._client = client
        self._connection_type = None
        self._allow_write = None
        self._params = {}
        self._tags = {}

    def title(self, title: str):
        """
        Sets the title property of the Connection.

        :param title: the human friendly name of the Connection
        :return: the builder instance
        """
        self._title = title
        return self

    def description(self, description: str):
        """
        Sets the description property of the Connection.

        :param description: the human friendly long description of the Connection
        :return: the builder instance
        """
        self._description = description
        return self

    def connection_type(self, connection_type: str):
        """
        Sets the connection_type property of a connection.

        :param connection_type: Type of a connection
        :return: the builder instance
        """
        self._connection_type = connection_type
        return self


    def allow_write(self, allow_write: bool = True):
        """
        Sets the allow_write property of the connection.

        :param description: boolean value for the coonection to allow_write
        :return: the builder instance
        """
        self._allow_write = allow_write
        return self

    def params(self, name: str, value: str):
        """
        Adds a Connection parameter.

        :param name: Parameter Name
        :param value: Parameter Value
        :return:
        """
        params = {
            'name': name,
            'value': value
        }

        self._params[name] = params

        return self

    def tags(self, label: str, value: str):
        """
        Adds a Connection tags.

        :param label:Parameter Label
        :param value
        :return:
        """
        tags = {
            'label': label,
            'value': value
        }

        self._params[label] = tags

        return self

    def to_camel(self):
        connection = {
            'camel': self._camel,
            'name': self._name,
            'title': self._title or self._name,
            'connectionType' :self._connection_type
        }

        if len(self._params) > 0:
            connection['params'] = list(self._params.values())

        if len(self._tags) > 0:
            connection['tags'] = list(self._tags.values())

        if self._description:
            connection['description'] = self._description

        if self._allow_write:
            connection['allowWrite'] = self._allow_write

        return connection

    def build(self) -> Connection:
        """
        Builds and saves a Connection using the properties configured on the builder

        :return: the resulting Connection
        """
        connection = self.to_camel()
        self._client.save_connection(connection)

        return Connection.get_connection(self._name, self._client)
