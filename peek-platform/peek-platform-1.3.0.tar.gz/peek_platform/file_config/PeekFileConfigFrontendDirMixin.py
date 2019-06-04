import logging
import os

from jsoncfg.value_mappers import require_bool, require_string

logger = logging.getLogger(__name__)


class PeekFileConfigFrontendDirMixin:
    # --- Platform Logging


    @property
    def feNativescriptBuildPrepareEnabled(self) -> bool:
        """ Nativescript Frontend Build Enabled

        :return True If peek should prepare the build directory

        """
        with self._cfg as c:
            return c.frontend.nativescriptBuildPrepareEnabled(False, require_bool)

    @property
    def feFrontendSrcOverlayDir(self) -> bool:
        """ Frontend Src Overlay Directory

        :return The path of the directory that will override any frontend SRC
            file with customers customisations.

        """
        default = os.path.join(self._homePath, 'frontendSrcOverlayDir')
        with self._cfg as c:
            return self._chkDir(c.frontend.frontendSrcOverlayDir(default, require_string))

    @property
    def feFrontendNodeModuleOverlayDir(self) -> bool:
        """ Frontend node_modules Overlay Directory

        :return The path of the directory that will override any frontend node_module
            file with customers customisations.

        """
        default = os.path.join(self._homePath, 'frontendNodeModuleOverlayDir')
        with self._cfg as c:
            return self._chkDir(c.frontend.frontendNodeModuleOverlayDir(default, require_string))

    @property
    def feSyncFilesForDebugEnabled(self) -> bool:
        """ Sync Files for Debug Enabled

        :return True If peek should watch the build files and sync them as they change

        """
        with self._cfg as c:
            return c.frontend.syncFilesForDebugEnabled(False, require_bool)


    @property
    def feWebBuildPrepareEnabled(self) -> bool:
        """ Frontend Build Enabled

        :return True If peek should automatically try to build the frontend.

        """
        with self._cfg as c:
            return c.frontend.webBuildPrepareEnabled(True, require_bool)



    @property
    def feWebBuildEnabled(self) -> bool:
        """ Frontend Build Enabled

        :return True If peek should automatically try to build the frontend.

        """
        with self._cfg as c:
            return c.frontend.webBuildEnabled(True, require_bool)