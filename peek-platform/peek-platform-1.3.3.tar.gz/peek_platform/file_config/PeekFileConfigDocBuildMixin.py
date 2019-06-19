import logging

from jsoncfg.value_mappers import require_bool

logger = logging.getLogger(__name__)


class PeekFileConfigDocBuildMixin:

    @property
    def docBuildPrepareEnabled(self) -> bool:
        """ Doc Prepare Enabled

        :return True If peek should prepare the build directory

        """
        with self._cfg as c:
            return c.frontend.docBuildPrepareEnabled(True, require_bool)

    @property
    def docSyncFilesForDebugEnabled(self) -> bool:
        """ Sync Files for Debug Enabled

        :return True If peek should watch the build files and sync them as they change

        """
        with self._cfg as c:
            return c.frontend.docSyncFilesForDebugEnabled(False, require_bool)

    @property
    def docBuildEnabled(self) -> bool:
        """ Doc Build Enabled

        :return True If peek should automatically try to build the docs.

        """
        with self._cfg as c:
            return c.frontend.docBuildEnabled(True, require_bool)
