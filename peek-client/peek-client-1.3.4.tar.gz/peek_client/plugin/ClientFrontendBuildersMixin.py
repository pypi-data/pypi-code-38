import logging

import os

from peek_platform.build_doc.DocBuilder import DocBuilder
from peek_platform.build_frontend.NativescriptBuilder import NativescriptBuilder
from peek_platform.build_frontend.WebBuilder import WebBuilder

logger = logging.getLogger(__name__)


class ClientFrontendBuildersMixin:

    def _buildMobile(self, loadedPlugins):
        # --------------------
        # Prepare the Peek Mobile

        from peek_platform import PeekPlatformConfig

        try:
            import peek_mobile
            mobileProjectDir = os.path.dirname(peek_mobile.__file__)

        except:
            logger.warning("Skipping builds of peek-mobile"
                           ", the package can not be imported")
            return

        nsBuilder = NativescriptBuilder(mobileProjectDir,
                                        "peek-mobile",
                                        PeekPlatformConfig.config,
                                        loadedPlugins)
        yield nsBuilder.build()

        mobileWebBuilder = WebBuilder(mobileProjectDir,
                                      "peek-mobile",
                                      PeekPlatformConfig.config,
                                      loadedPlugins)
        yield mobileWebBuilder.build()

    def _buildDesktop(self, loadedPlugins):
        # --------------------
        # Prepare the Peek Desktop
        from peek_platform import PeekPlatformConfig

        try:
            import peek_desktop
            desktopProjectDir = os.path.dirname(peek_desktop.__file__)

        except:
            logger.warning("Skipping builds of peek-desktop"
                           ", the package can not be imported")
            return

        desktopWebBuilder = WebBuilder(desktopProjectDir,
                                       "peek-desktop",
                                       PeekPlatformConfig.config,
                                       loadedPlugins)
        yield desktopWebBuilder.build()

    def _buildDocs(self, loadedPlugins):
        # --------------------
        # Prepare the User Docs
        from peek_platform import PeekPlatformConfig

        try:
            import peek_doc_user
            docProjectDir = os.path.dirname(peek_doc_user.__file__)

        except:
            logger.warning("Skipping builds of peek_doc_user"
                           ", the package can not be imported")
            return

        docBuilder = DocBuilder(docProjectDir,
                                "peek-doc-user",
                                PeekPlatformConfig.config,
                                loadedPlugins)
        yield docBuilder.build()
