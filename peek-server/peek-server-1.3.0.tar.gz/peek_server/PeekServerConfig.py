'''
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
'''
import logging
import os

from jsoncfg.value_mappers import require_string, require_integer

from peek_platform.file_config.PeekFileConfigABC import PeekFileConfigABC
from peek_platform.file_config.PeekFileConfigDocBuildMixin import \
    PeekFileConfigDocBuildMixin
from peek_platform.file_config.PeekFileConfigFrontendDirMixin import \
    PeekFileConfigFrontendDirMixin
from peek_platform.file_config.PeekFileConfigOsMixin import PeekFileConfigOsMixin
from peek_platform.file_config.PeekFileConfigPlatformMixin import \
    PeekFileConfigPlatformMixin
from peek_platform.file_config.PeekFileConfigSqlAlchemyMixin import \
    PeekFileConfigSqlAlchemyMixin
from peek_platform.file_config.PeekFileConfigWorkerMixin import PeekFileConfigWorkerMixin
from peek_server.PeekServerConfigLicMixin import PeekServerConfigLicMixin

logger = logging.getLogger(__name__)


class PeekServerConfig(PeekFileConfigABC,
                       PeekFileConfigOsMixin,
                       PeekFileConfigPlatformMixin,
                       PeekFileConfigSqlAlchemyMixin,
                       PeekServerConfigLicMixin,
                       PeekFileConfigFrontendDirMixin,
                       PeekFileConfigDocBuildMixin,
                       PeekFileConfigWorkerMixin):
    """
    This class creates a server configuration
    """

    import peek_admin
    _frontendProjectDir = os.path.dirname(peek_admin.__file__)

    ### USER SECTION ###
    @property
    def adminPass(self):
        with self._cfg as c:
            return c.user.admin["pass"]("peeking", require_string)

    @property
    def adminUser(self):
        with self._cfg as c:
            return c.user.admin.user("backend", require_string)

    ### SERVER SECTION ###
    @property
    def adminSitePort(self) -> int:
        """ Site Port

        The port used to serve the admin web page on
        """
        with self._cfg as c:
            return c.server.adminSitePort(8010, require_integer)

    @property
    def webSocketPort(self) -> int:
        with self._cfg as c:
            return c.server.webSocketPort(8013, require_integer)

    @property
    def docSitePort(self) -> int:
        """ Admin Documentation Site Port

        The port used to serve the admin documentation
        """
        with self._cfg as c:
            return c.server.docSitePort(8015, require_integer)

    ### SERVER SECTION ###
    @property
    def peekServerHttpPort(self):
        """ Peek Server HTTP Port

        This port serves resources for the plugins, as well as a HTTP vortex.
        """
        with self._cfg as c:
            return c.peekServer.httpPort(8011, require_integer)

    @property
    def peekServerVortexTcpPort(self):
        """ Peek Server Vortex TCP Port

        This port serves a raw vortex over TCP (No HTTP).

        It remains open perminently until either side disconnects.
        """
        with self._cfg as c:
            return c.peekServer.tcpVortexPort(8012, require_integer)
