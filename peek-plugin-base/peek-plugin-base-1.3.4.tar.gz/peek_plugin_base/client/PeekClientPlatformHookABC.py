from peek_plugin_base.PeekPlatformCommonHookABC import PeekPlatformCommonHookABC
from peek_plugin_base.PeekPlatformFileStorageHookABC import PeekPlatformFileStorageHookABC
from peek_plugin_base.PeekPlatformServerInfoHookABC import PeekPlatformServerInfoHookABC
from peek_plugin_base.client.PeekPlatformDesktopHttpHookABC import \
    PeekPlatformDesktopHttpHookABC
from peek_plugin_base.client.PeekPlatformMobileHttpHookABC import \
    PeekPlatformMobileHttpHookABC


class PeekClientPlatformHookABC(PeekPlatformCommonHookABC,
                                PeekPlatformMobileHttpHookABC,
                                PeekPlatformDesktopHttpHookABC,
                                PeekPlatformServerInfoHookABC,
                                PeekPlatformFileStorageHookABC):
    pass
