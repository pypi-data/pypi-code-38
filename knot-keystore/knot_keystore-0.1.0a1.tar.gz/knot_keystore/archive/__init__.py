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
"""knot_keystore.archive Package."""

import logging

from knot_keystore.archive.azure import ArchiveAzure
from knot_keystore.archive.local import ArchiveLocal

log = logging.getLogger(__name__)

__all__ = ["get_plugins"]


def get_plugins(name=None):
    """Find archive plugins."""
    log.debug("Trying to find available plugins")
    builtin = {"local": ArchiveLocal, "azure": ArchiveAzure}
    plugins = builtin
    log.debug(f"Available plugins: {plugins}")
    if name is not None:
        log.debug(f"Trying to find class for {name} plugin")
        try:
            plugin = plugins[name]
            log.debug(f"Found class for {name} plugin: {plugin.__name__}")
            return plugin
        except KeyError as e:
            raise e
    return plugins.keys()
