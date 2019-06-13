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

from cortex_client import SessionClient
from .logger import getLogger
from typing import Dict

log = getLogger(__name__)


class Session:
    """
    Represents a state for a client interaction with Cortex.
    """

    def __init__(self, session_id, client: SessionClient):
        self._session_id = session_id
        self._client = client

    def get(self, key: str) -> object:
        """
        Gets the session data corresponding to the given key.

        :param key: the key to retrieve
        :return: session data corresponding to the given key
        """
        return self._client.get_session_data(self._session_id, key)

    def put(self, key: str, value: Dict):
        """
        Gets the session data corresponding to the given key.

        :param key: the key for the data to be put in the session
        :param value: the value of the data to be put in the session
        :return: a json representation of the data put in the session
        """
        return self._client.put_session_data(self._session_id, value)

    def get_all(self) -> Dict:
        """
        Gets all the data associated with the session.
        """
        return self._client.get_session_data(self._session_id)

    def delete(self):
        """
        Deletes the session from the client.
        """
        return self._client.delete_session(self._session_id)

    @staticmethod
    def start(client: SessionClient, ttl=None, instance_id=None):
        """
        Creates a new session for a given client.

        :param client: The client to associate with this session.
        :param ttl: An optional session time to live.
        :param instance_id: An optional identifier for this session; if not
        provided, the client creates a number.
        :return: A session attached to the given client.
        """
        session_id = client.start_session(ttl, instance_id)
        return Session(session_id, client)
