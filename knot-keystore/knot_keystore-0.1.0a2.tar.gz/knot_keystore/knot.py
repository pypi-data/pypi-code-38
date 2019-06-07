# Copyright (c) 2019 Workonline Communications (Pty) Ltd. All rights reserved.
#
# The contents of this file are licensed under the MIT License
# (the "License"); you may not use this file except in compliance with the
# License.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""knot_keystore knot module."""

import contextlib
import logging
import os
import time

import libknot.control

log = logging.getLogger(__name__)


class Knot(object):
    """A knot-dns control object."""

    STORAGE = "/var/lib/knot"
    KASP_DB = "keys"

    def __init__(self, socket=None):
        """Intitialise a new instance."""
        log.debug(f"Initialising knot control instance {self}")
        self.socket = socket
        self.ctl = libknot.control.KnotCtl()

    def __enter__(self):
        """Enter connection context."""
        log.debug(f"Connecting to knot control socket: {self.socket}")
        try:
            self.ctl.connect(self.socket)
        except Exception as e:
            log.error(f"Failed to connect to knot conrol socket: {e}")
            raise e
        log.debug("Connected to knot control socket")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit connection context."""
        log.debug("Disconnecting from knot control socket")
        self.ctl.send(libknot.control.KnotCtlType.END)
        self.ctl.close()
        log.debug("Disconnected from knot control socket")
        return None

    def _cmd(self, cmd=None):
        """Send a control command and return a result."""
        log.debug(f"Sending control command '{cmd}' to knot")
        self.ctl.send_block(cmd)
        resp = self.ctl.receive_block()
        log.debug(f"Got response from knot: {resp}")
        return resp

    @property
    def zone_status(self):
        """Get operational zone status."""
        log.debug("Trying to get knot zone status")
        return self._cmd(cmd="zone-status")

    @property
    def config(self):
        """Read the running config from knot."""
        log.debug("Trying to get knot running config")
        return self._cmd(cmd="conf-read")

    @property
    def kaspdb_path(self):
        """Find the path to the kasp-db directory."""
        log.debug("Trying to find kasp-db location")
        config = self.config
        log.debug("Checking for configured knot storage path")
        try:
            storage = config["template"]["default"]["storage"][0]
        except KeyError:
            log.debug(f"No configured 'storage' in default template: "
                      f"using default value '{self.STORAGE}'")
            storage = self.STORAGE
        log.debug(f"Storage path is {storage}")
        log.debug("Checking for configured kasp-db path")
        try:
            kasp_db = config["template"]["default"]["kasp-db"][0]
        except KeyError:
            log.debug(f"No configured 'kasp-db' in default template: "
                      f"using default value '{self.KASP_DB}'")
            kasp_db = self.KASP_DB
        if not kasp_db.startswith("/"):
            kasp_db = os.path.join(storage, kasp_db)
        log.info(f"Path to kasp-db: {kasp_db}")
        return os.path.split(kasp_db)

    @contextlib.contextmanager
    def freeze(self):
        """Freeze zone operations."""
        log.debug("Trying to freeze knot zone operations")
        self._cmd(cmd="zone-freeze")
        log.debug("Waiting for all zones to become frozen")
        while True:
            time.sleep(1)
            for s in self.zone_status.values():
                if s["freeze"] != "yes":  # pragma: no cover
                    continue
            break
        log.debug("Sucessfully froze zone operations")
        try:
            yield
        finally:
            log.debug("Thawing knot zone operations")
            self._cmd(cmd="zone-thaw")
