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

from .logger import getLogger
from cortex_client import ConnectionClient
from cortex_client.serviceconnector import ServiceConnector
from .camel import CamelResource

log = getLogger(__name__)


class Connection(CamelResource):

    """
    Defines the connection for a dataset.
    """

    def __init__(self, connection, connector: ServiceConnector):
        super().__init__(connection, True)
        self._connector = connector


    @staticmethod
    def get_connection(name, client: ConnectionClient):
        """
        Fetches a Connection to work with.

        :param client: The client instance to use.
        :param name: The name of the connection to retrieve.
        :return: A Connection object.
        """
        uri = 'connections/{name}'.format(name=name)
        log.debug('Getting connection using URI: %s' % uri)
        r = client._serviceconnector.request('GET', uri)
        r.raise_for_status()

        return Connection(r.json(), client._serviceconnector)
