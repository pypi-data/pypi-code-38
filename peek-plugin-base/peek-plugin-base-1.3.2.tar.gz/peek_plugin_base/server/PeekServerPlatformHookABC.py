from abc import abstractmethod

from peek_plugin_base.PeekPlatformCommonHookABC import PeekPlatformCommonHookABC
from peek_plugin_base.PeekPlatformFileStorageHookABC import PeekPlatformFileStorageHookABC
from peek_plugin_base.server.PeekPlatformServerHttpHookABC import PeekPlatformServerHttpHookABC
from peek_plugin_base.server.PeekPlatformAdminHttpHookABC import \
    PeekPlatformAdminHttpHookABC
from abc import abstractmethod

from peek_plugin_base.PeekPlatformCommonHookABC import PeekPlatformCommonHookABC
from peek_plugin_base.PeekPlatformFileStorageHookABC import PeekPlatformFileStorageHookABC
from peek_plugin_base.server.PeekPlatformAdminHttpHookABC import \
    PeekPlatformAdminHttpHookABC
from peek_plugin_base.server.PeekPlatformServerHttpHookABC import \
    PeekPlatformServerHttpHookABC


class PeekServerPlatformHookABC(PeekPlatformCommonHookABC,
                                PeekPlatformAdminHttpHookABC,
                                PeekPlatformServerHttpHookABC,
                                PeekPlatformFileStorageHookABC):

    @property
    @abstractmethod
    def dbConnectString(self) -> str:
        """ DB Connect String

        :return: The SQLAlchemy database engine connection string/url.

        """