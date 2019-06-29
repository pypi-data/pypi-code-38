import logging
from datetime import datetime
from typing import List

import os
import pytz

from peek_platform.build_common.BuilderOsCmd import runDocBuild
from peek_platform.build_doc.DocBuilderABC import DocBuilderABC
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class DocBuilder(DocBuilderABC):

    def __init__(self, docProjectDir: str, platformService: str,
                 jsonCfg, loadedPlugins: List):
        DocBuilderABC.__init__(self, docProjectDir, platformService,
                               jsonCfg, loadedPlugins)

    @deferToThreadWrapWithLogger(logger, checkMainThread=False)
    def build(self) -> None:
        if not self._jsonCfg.docBuildPrepareEnabled:
            logger.info("%s SKIPPING, Doc build prepare is disabled in config",
                        self._platformService)
            return

        excludeRegexp = (
            r'.*__pycache__.*',
            r'.*[.]py$'
        )

        docLinkDir = os.path.join(self._docProjectDir, "doc_link")
        docConfDir = self._docProjectDir
        docDistDir = os.path.join(self._docProjectDir, "doc_dist")

        if not os.path.isdir(docLinkDir):
            os.mkdir(docLinkDir)

        self._dirSyncMap = list()

        pluginDetails = self._loadPluginConfigs()

        pluginDetails.sort(key=lambda item: item.pluginTitle)

        # --------------------
        # Prepare the table of contents link ins
        self._writePluginsToc(docLinkDir, pluginDetails)
        self._writePluginToc(docLinkDir, pluginDetails)

        # --------------------
        # Prepare the API document loads
        self._writePluginsApiConf(docLinkDir, pluginDetails)
        self._writePluginsApiList(docLinkDir, pluginDetails)

        # --------------------
        # Now sync the plugins documentation directory
        self._syncPluginFiles(docLinkDir,
                              pluginDetails,
                              excludeFilesRegex=excludeRegexp)

        self.fileSync.syncFiles()

        if self._jsonCfg.docSyncFilesForDebugEnabled:
            logger.info("%s starting frontend development file sync",
                        self._platformService)
            self.fileSync.startFileSyncWatcher()

        if self._jsonCfg.docBuildEnabled:
            logger.info("%s starting frontend web build", self._platformService)
            self._compileDocs(docLinkDir)

    def _syncFileHook(self, fileName: str, contents: bytes) -> bytes:
        return contents

    def _compileDocs(self, docLinkDir: str) -> None:
        """ Compile the docs

        this runs `build_html_docs.sh`, after checking if any files have changed.

        """
        startDate = datetime.now(pytz.utc)
        hashFileName = os.path.join(docLinkDir, ".lastHash")

        if not self._recompileRequiredCheck(docLinkDir, hashFileName):
            logger.info("%s Doc has not changed, recompile not required.",
                        self._platformService)
            return

        logger.info("%s Rebuilding docs for ", self._platformService)

        try:
            runDocBuild(self._docProjectDir)

        except Exception as e:
            if os.path.exists(hashFileName):
                os.remove(hashFileName)

            # Update the detail of the exception and raise it
            e.message = "%s sphinx docs failed to build." % self._platformService
            raise

        logger.info("%s sphinx doc rebuild completed in %s",
                    self._platformService, datetime.now(pytz.utc) - startDate)
