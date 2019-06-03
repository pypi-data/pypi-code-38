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

from typing import Dict
from .client import _Client


class SessionClient(_Client):
    """
    A client for the Cortex Sessions API.
    """

    URIs = {'start': 'sessions/start', 'get': 'sessions/{session_id}', 'put': 'sessions/{session_id}', 'delete': 'sessions/{session_id}'}

    def start_session(self, ttl=None, instance_id=None, description='No description given') -> str:
        """
        Starts a new session.

        :param ttl: Resets sessions expiration; default is 15 minutes.
        :param instance_id: An optional ID that scopes this session to a deployed agent-instance
        :param description: An optional human readable description for this sessions instance
        :return: The ID of the new Session.
        """
        uri = self.URIs['start']
        params = {}
        if ttl:
            params['ttl'] = ttl
        if instance_id:
            params['instance_id'] = instance_id

        params['description'] = description

        result = self._post_json(uri, params)
        return result.get('sessionId')

    def get_session_data(self, session_id, key=None) -> Dict[str, object]:
        """
        Gets data for a specific session.

        :param session_id: The ID of the session to query.
        :param key: An optional key in the session memory; the entire session memory is returned if a key is not specified.
        :return: A dict containing the requested session data
        """
        uri = self.URIs['get'].format(session_id=session_id)
        if key:
            uri += '?key={key}'.format(key=key)

        result = self._get_json(uri) or {}
        return result.get('state', {})

    def put_session_data(self, session_id, data: Dict):
        """
        Adds data to an existing session.

        :param session_id: The ID of the session to modify.
        :param data: Dict containing the new session keys to set.

        """
        uri = self.URIs['put'].format(session_id=session_id)
        return self._post_json(uri, {'state': data})

    def delete_session(self, session_id):
        """
        Deletes a session.

        :param session_id: The ID of the session to delete.

        """
        uri = self.URIs['delete'].format(session_id=session_id)
        return self._request_json(uri, method='DELETE')
