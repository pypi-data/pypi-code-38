# Copyright (c) 2019. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import json
from ws4py.client.threadedclient import WebSocketClient
from collections import namedtuple
from datetime import datetime

# WebSocket reader build on ws4py. More info you can find:
#   https://ws4py.readthedocs.io/en/latest/sources/clienttutorial/
#   https://github.com/Lawouach/WebSocket-for-Python

class WsReader(WebSocketClient):
    """Implements all commands to read messages from WebSocket.
    """

    def __init__(self, url, callback, jsessionid=None):
        """Initialise an instance of the class."""
        self._callback = callback

        # prepare session id as cookie in headers
        cookie=None
        if jsessionid is not None:
            session_cookie = 'JSESSIONID={0}'.format(jsessionid)
            cookie=[('Cookie', session_cookie)]

        # init web socket client
        super(WsReader, self).__init__(url, headers=cookie, heartbeat_freq=1)

    def start(self):
        """Start log watcher."""
        self.connect()

    def opened(self):
        """WS open connection handler"""
        pass

    def closed(self, code, reason=None):
        """WS close connection handler"""
        pass

    def received_message(self, message):
        """WS received message handler"""
        self._callback(message)

