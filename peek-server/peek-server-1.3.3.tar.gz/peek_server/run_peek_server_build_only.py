#!/usr/bin/env python
""" 
 * synnova.py
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This sw_upload is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this sw_upload are reserved by
 *  Synerty Pty Ltd
 *
"""

import logging
import os

from pytmpdir.Directory import DirSettings

from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_server import importPackages
from peek_server.storage import setupDbConn
from peek_server.storage.DeclarativeBase import metadata
from txhttputil.site.FileUploadRequest import FileUploadRequest
from peek_platform.util.LogUtil import setupPeekLogger
from vortex.DeferUtil import vortexLogFailure

setupPeekLogger(peekServerName)

from twisted.internet import reactor

logger = logging.getLogger(__name__)


def setupPlatform():
    from peek_platform import PeekPlatformConfig
    PeekPlatformConfig.componentName = peekServerName

    # Tell the platform classes about our instance of the PeekLoaderBase
    from peek_server.plugin.ServerPluginLoader import ServerPluginLoader
    PeekPlatformConfig.pluginLoader = ServerPluginLoader()

    # The config depends on the componentName, order is important
    from peek_server.PeekServerConfig import PeekServerConfig
    PeekPlatformConfig.config = PeekServerConfig()

    # Set default logging level
    logging.root.setLevel(PeekPlatformConfig.config.loggingLevel)

    # Set paths for the Directory object
    DirSettings.defaultDirChmod = PeekPlatformConfig.config.DEFAULT_DIR_CHMOD
    DirSettings.tmpDirPath = PeekPlatformConfig.config.tmpPath
    FileUploadRequest.tmpFilePath = PeekPlatformConfig.config.tmpPath


def main():
    setupPlatform()
    from peek_platform import PeekPlatformConfig
    import peek_server

    # Configure sqlalchemy
    setupDbConn(
        metadata=metadata,
        dbEngineArgs=PeekPlatformConfig.config.dbEngineArgs,
        dbConnectString=PeekPlatformConfig.config.dbConnectString,
        alembicDir=os.path.join(os.path.dirname(peek_server.__file__), "alembic")
    )

    # Force model migration
    from peek_server.storage import dbConn
    dbConn.migrate()

    # Import remaining components
    importPackages()

    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.unloadOptionalPlugins)
    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.unloadCorePlugins)

    # Load all plugins
    d = PeekPlatformConfig.pluginLoader.loadCorePlugins()
    d.addCallback(lambda _: PeekPlatformConfig.pluginLoader.loadOptionalPlugins())
    d.addErrback(vortexLogFailure, logger, consumeError=True)

    reactor.run()


if __name__ == '__main__':
    main()
