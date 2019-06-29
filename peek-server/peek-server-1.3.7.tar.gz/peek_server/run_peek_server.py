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
from txhttputil.site.FileUploadRequest import FileUploadRequest
from peek_platform.util.LogUtil import setupPeekLogger

from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_server import importPackages
from peek_server.storage import setupDbConn
from peek_server.storage.DeclarativeBase import metadata
from vortex.DeferUtil import vortexLogFailure
from vortex.VortexFactory import VortexFactory

setupPeekLogger(peekServerName)

from twisted.internet import reactor, defer

from txhttputil.site.SiteUtil import setupSite

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Set the parallelism of the database and reactor

def setupPlatform():
    from peek_platform import PeekPlatformConfig
    PeekPlatformConfig.componentName = peekServerName

    # Tell the platform classes about our instance of the pluginSwInstallManager
    from peek_server.server.sw_install.PluginSwInstallManager import \
        PluginSwInstallManager
    PeekPlatformConfig.pluginSwInstallManager = PluginSwInstallManager()

    # Tell the platform classes about our instance of the PeekSwInstallManager
    from peek_server.server.sw_install.PeekSwInstallManager import PeekSwInstallManager
    PeekPlatformConfig.peekSwInstallManager = PeekSwInstallManager()

    # Tell the platform classes about our instance of the PeekLoaderBase
    from peek_server.plugin.ServerPluginLoader import ServerPluginLoader
    PeekPlatformConfig.pluginLoader = ServerPluginLoader()

    # The config depends on the componentName, order is important
    from peek_server.PeekServerConfig import PeekServerConfig
    PeekPlatformConfig.config = PeekServerConfig()

    # Update the version in the config file
    from peek_server import __version__
    PeekPlatformConfig.config.platformVersion = __version__

    # Set default logging level
    logging.root.setLevel(PeekPlatformConfig.config.loggingLevel)

    if logging.root.level == logging.DEBUG:
        defer.setDebugging(True)

    reactor.suggestThreadPoolSize(PeekPlatformConfig.config.twistedThreadPoolSize)

    # Set paths for the Directory object
    DirSettings.defaultDirChmod = PeekPlatformConfig.config.DEFAULT_DIR_CHMOD
    DirSettings.tmpDirPath = PeekPlatformConfig.config.tmpPath
    FileUploadRequest.tmpFilePath = PeekPlatformConfig.config.tmpPath


def startListening():
    from peek_platform import PeekPlatformConfig

    from peek_server.backend.AdminSiteResource import setupAdminSite, adminSiteRoot
    from peek_server.backend.DocSiteResource import setupDocSite, docSiteRoot

    setupAdminSite()
    setupDocSite()

    setupSite("Peek Admin",
              adminSiteRoot,
              PeekPlatformConfig.config.adminSitePort,
              enableLogin=False)

    setupSite("Peek Admin Docs",
              docSiteRoot,
              PeekPlatformConfig.config.docSitePort,
              enableLogin=False)

    from peek_server.server.PlatformSiteResource import setupPlatformSite
    from peek_server.server.PlatformSiteResource import platformSiteRoot

    setupPlatformSite()

    setupSite("Peek Platform Data Exchange",
              platformSiteRoot,
              PeekPlatformConfig.config.peekServerHttpPort,
              enableLogin=False)

    VortexFactory.createTcpServer(name=PeekPlatformConfig.componentName,
                                  port=PeekPlatformConfig.config.peekServerVortexTcpPort)

    webSocketPort = PeekPlatformConfig.config.webSocketPort
    VortexFactory.createWebsocketServer(PeekPlatformConfig.componentName, webSocketPort)


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
                                  PeekPlatformConfig.pluginLoader.stopOptionalPlugins)
    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.stopCorePlugins)

    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.unloadOptionalPlugins)
    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.unloadCorePlugins)

    # Load all plugins
    d = PeekPlatformConfig.pluginLoader.loadCorePlugins()
    d.addCallback(lambda _: PeekPlatformConfig.pluginLoader.loadOptionalPlugins())
    d.addCallback(lambda _: startListening())
    d.addCallback(lambda _: PeekPlatformConfig.pluginLoader.startCorePlugins())
    d.addCallback(lambda _: PeekPlatformConfig.pluginLoader.startOptionalPlugins())

    def startedSuccessfully(_):
        logger.info('Peek Server is running, version=%s',
                    PeekPlatformConfig.config.platformVersion)
        return _

    d.addErrback(vortexLogFailure, logger, consumeError=True)
    d.addCallback(startedSuccessfully)

    reactor.run()


if __name__ == '__main__':
    main()
