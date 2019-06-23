#!/usr/bin/env python
"""

  Copyright Synerty Pty Ltd 2013

  This software is proprietary, you are not free to copy
  or redistribute this code in any format.

  All rights to this software are reserved by
  Synerty Pty Ltd

"""

import logging

from pytmpdir.Directory import DirSettings
from twisted.internet import defer
from twisted.internet import reactor
from txhttputil.site.FileUploadRequest import FileUploadRequest
from txhttputil.util.DeferUtil import printFailure
from peek_platform.util.LogUtil import setupPeekLogger

from peek_plugin_base.PeekVortexUtil import peekAgentName, peekServerName
from vortex.DeferUtil import vortexLogFailure
from vortex.VortexFactory import VortexFactory

setupPeekLogger(peekAgentName)

logger = logging.getLogger(__name__)


def setupPlatform():
    from peek_platform import PeekPlatformConfig
    PeekPlatformConfig.componentName = peekAgentName

    # Tell the platform classes about our instance of the PluginSwInstallManager
    from peek_agent.sw_install.PluginSwInstallManager import PluginSwInstallManager
    PeekPlatformConfig.pluginSwInstallManager = PluginSwInstallManager()

    # Tell the platform classes about our instance of the PeekSwInstallManager
    from peek_agent.sw_install.PeekSwInstallManager import PeekSwInstallManager
    PeekPlatformConfig.peekSwInstallManager = PeekSwInstallManager()

    # Tell the platform classes about our instance of the PeekLoaderBase
    from peek_agent.plugin.AgentPluginLoader import AgentPluginLoader
    PeekPlatformConfig.pluginLoader = AgentPluginLoader()

    # The config depends on the componentName, order is important
    from peek_agent.PeekAgentConfig import PeekAgentConfig
    PeekPlatformConfig.config = PeekAgentConfig()

    # Update the version in the config file
    from peek_agent import __version__
    PeekPlatformConfig.config.platformVersion = __version__

    # Set default logging level
    logging.root.setLevel(PeekPlatformConfig.config.loggingLevel)

    if logging.root.level == logging.DEBUG:
        defer.setDebugging(True)

    reactor.suggestThreadPoolSize(PeekPlatformConfig.config.twistedThreadPoolSize)

    # Initialise the txhttputil Directory object
    DirSettings.defaultDirChmod = PeekPlatformConfig.config.DEFAULT_DIR_CHMOD
    DirSettings.tmpDirPath = PeekPlatformConfig.config.tmpPath
    FileUploadRequest.tmpFilePath = PeekPlatformConfig.config.tmpPath


def main():
    defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    setupPlatform()

    # Make the agent restart when the server restarts, or when it looses connection
    def restart(status):
        from peek_platform import PeekPlatformConfig
        PeekPlatformConfig.peekSwInstallManager.restartProcess()

    (VortexFactory.subscribeToVortexStatusChange(peekServerName)
        .filter(lambda online: online == False)
        .subscribe(on_next=restart)
        )

    # First, setup the VortexServer Agent

    from peek_platform import PeekPlatformConfig
    d = VortexFactory.createTcpClient(PeekPlatformConfig.componentName,
                                      PeekPlatformConfig.config.peekServerHost,
                                      PeekPlatformConfig.config.peekServerVortexTcpPort)

    d.addErrback(printFailure)

    # Software update check is not a thing any more
    # Start Update Handler,
    from peek_platform.sw_version.PeekSwVersionPollHandler import peekSwVersionPollHandler
    # Add both, The peek client might fail to connect, and if it does, the payload
    # sent from the peekSwUpdater will be queued and sent when it does connect.
    # d.addBoth(lambda _: peekSwVersionPollHandler.start())

    # Load all Plugins
    d.addBoth(lambda _: PeekPlatformConfig.pluginLoader.loadCorePlugins())
    d.addBoth(lambda _: PeekPlatformConfig.pluginLoader.loadOptionalPlugins())
    d.addBoth(lambda _: PeekPlatformConfig.pluginLoader.startCorePlugins())
    d.addBoth(lambda _: PeekPlatformConfig.pluginLoader.startOptionalPlugins())

    def startedSuccessfully(_):
        logger.info('Peek Agent is running, version=%s',
                    PeekPlatformConfig.config.platformVersion)
        return _

    d.addCallback(startedSuccessfully)

    d.addErrback(vortexLogFailure, logger, consumeError=True)

    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.stopOptionalPlugins)
    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.stopCorePlugins)

    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.unloadOptionalPlugins)
    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.unloadCorePlugins)
    reactor.addSystemEventTrigger('before', 'shutdown', VortexFactory.shutdown)

    reactor.run()


if __name__ == '__main__':
    main()

