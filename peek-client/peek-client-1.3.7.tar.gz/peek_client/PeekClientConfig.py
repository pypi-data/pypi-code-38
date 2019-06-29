"""
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  Synerty Pty Ltd
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
 *
"""
import logging
import os

from jsoncfg.value_mappers import require_integer
from peek_platform.file_config.PeekFileConfigABC import PeekFileConfigABC
from peek_platform.file_config.PeekFileConfigDocBuildMixin import \
    PeekFileConfigDocBuildMixin
from peek_platform.file_config.PeekFileConfigFrontendDirMixin import \
    PeekFileConfigFrontendDirMixin
from peek_platform.file_config.PeekFileConfigOsMixin import PeekFileConfigOsMixin
from peek_platform.file_config.PeekFileConfigPeekServerClientMixin import \
    PeekFileConfigPeekServerClientMixin
from peek_platform.file_config.PeekFileConfigPlatformMixin import \
    PeekFileConfigPlatformMixin

logger = logging.getLogger(__name__)


class PeekClientConfig(PeekFileConfigABC,
                       PeekFileConfigPeekServerClientMixin,
                       PeekFileConfigPlatformMixin,
                       PeekFileConfigOsMixin,
                       PeekFileConfigFrontendDirMixin,
                       PeekFileConfigDocBuildMixin):
    """
    This class creates a basic client configuration
    """

    ### SERVER SECTION ###
    @property
    def mobileSitePort(self) -> int:
        with self._cfg as c:
            return c.server.mobileSitePort(8000, require_integer)

    @property
    def webSocketPort(self) -> int:
        with self._cfg as c:
            return c.server.webSocketPort(8001, require_integer)


    @property
    def desktopSitePort(self) -> int:
        with self._cfg as c:
            return c.server.desktopSitePort(8002, require_integer)


    @property
    def docSitePort(self) -> int:
        with self._cfg as c:
            return c.server.docSitePort(8005, require_integer)

