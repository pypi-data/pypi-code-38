# Copyright (c) 2019. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import json
import time
import uniquid.core.constants as constants
from uniquid.core.ws_reader import WsReader
from collections import namedtuple
from datetime import datetime

class LogWatcher:
    """Implements all commands related to user logs watcher.
    """

    def __init__(self, in_console, in_login_mgr):
        """Initialise an instance of the class."""
        self._console = in_console
        self._login_mgr = in_login_mgr

        # check that user is logged in
        session_key = self._login_mgr.get_session_key()
        if not self._login_mgr.is_session_alive():
            self._console.exception(constants.ERR_LOGGED_OUT)
        
        # prepare URLs to connect to impprinter and orchestrator via WebSocket
        url_mask = 'ws://{0}:{1}/api/v1/log'
        imprinter_url = url_mask.format(self._login_mgr.get_api_ip(), 8070)
        orchestrator_url = url_mask.format(self._login_mgr.get_api_ip(),
                                self._login_mgr.get_api_port())

        # prepare WebSocket readers
        self._imprinter = WsReader(imprinter_url, self.received_log_event)
        self._orchestrator = WsReader(orchestrator_url, self.received_log_event, 
                                jsessionid=session_key)
    
    def start(self):
        """Start log watcher."""
        self._imprinter.start()
        self._orchestrator.start()

        # infinite loop while both WebSocket readers are connected
        while (not self._imprinter.terminated and not self._orchestrator.terminated):
            time.sleep(5)

    def received_log_event(self, logEvent):
        """The handler to receiveing log events"""
        msg = json_to_obj(logEvent)
        timedate = ts_to_timedate(msg.date)
        log_str = '{} [{}] {}'.format(timedate, msg.logLevel, msg.message)
        self._console.nolog(log_str)

def _json_object_hook(d): 
    return namedtuple('X', d.keys())(*d.values())
    
def json_to_obj(data): 
    return json.loads(str(data), object_hook=_json_object_hook)

def ts_to_timedate(timestamp): 
    return datetime.utcfromtimestamp(timestamp / 1000).strftime('%d/%m/%Y %H:%M:%S')
