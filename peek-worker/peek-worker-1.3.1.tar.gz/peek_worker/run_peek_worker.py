#!/usr/bin/env python
"""

  Copyright Synerty Pty Ltd 2013

  This software is proprietary, you are not free to copy
  or redistribute this code in any format.

  All rights to this software are reserved by
  Synerty Pty Ltd

"""

import logging
import threading
from threading import Thread

from pytmpdir.Directory import DirSettings
from twisted.internet import reactor, defer

from peek_platform import PeekPlatformConfig
from peek_plugin_base.PeekVortexUtil import peekWorkerName, peekServerName
from txhttputil.site.FileUploadRequest import FileUploadRequest
from peek_platform.util.LogUtil import setupPeekLogger
from vortex.DeferUtil import vortexLogFailure
from vortex.VortexFactory import VortexFactory

setupPeekLogger(peekWorkerName)

logger = logging.getLogger(__name__)


def setupPlatform():
    from peek_platform import PeekPlatformConfig
    PeekPlatformConfig.componentName = peekWorkerName

    # Tell the platform classes about our instance of the pluginSwInstallManager
    from peek_worker.sw_install.PluginSwInstallManager import PluginSwInstallManager
    PeekPlatformConfig.pluginSwInstallManager = PluginSwInstallManager()

    # Tell the platform classes about our instance of the PeekSwInstallManager
    from peek_worker.sw_install.PeekSwInstallManager import PeekSwInstallManager
    PeekPlatformConfig.peekSwInstallManager = PeekSwInstallManager()

    # Tell the platform classes about our instance of the PeekLoaderBase
    from peek_worker.plugin.WorkerPluginLoader import WorkerPluginLoader
    PeekPlatformConfig.pluginLoader = WorkerPluginLoader()

    # The config depends on the componentName, order is important
    from peek_worker.PeekWorkerConfig import PeekWorkerConfig
    PeekPlatformConfig.config = PeekWorkerConfig()

    # Update the version in the config file
    from peek_worker import __version__
    PeekPlatformConfig.config.platformVersion = __version__

    # Set default logging level
    logging.root.setLevel(PeekPlatformConfig.config.loggingLevel)

    if logging.root.level == logging.DEBUG:
        defer.setDebugging(True)

    # The worker doesn't need any threads
    reactor.suggestThreadPoolSize(1)

    # Initialise the txhttputil Directory object
    DirSettings.defaultDirChmod = PeekPlatformConfig.config.DEFAULT_DIR_CHMOD
    DirSettings.tmpDirPath = PeekPlatformConfig.config.tmpPath
    FileUploadRequest.tmpFilePath = PeekPlatformConfig.config.tmpPath


def twistedMain():
    # defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    # Make the agent restart when the server restarts, or when it looses connection
    def restart(status):
        from peek_platform import PeekPlatformConfig
        PeekPlatformConfig.peekSwInstallManager.restartProcess()

    (VortexFactory.subscribeToVortexStatusChange(peekServerName)
        .filter(lambda online: online == False)
        .subscribe(on_next=restart)
        )

    # First, setup the VortexServer Worker
    from peek_platform import PeekPlatformConfig
    d = VortexFactory.createTcpClient(PeekPlatformConfig.componentName,
                                      PeekPlatformConfig.config.peekServerHost,
                                      PeekPlatformConfig.config.peekServerVortexTcpPort)
    d.addErrback(vortexLogFailure, logger, consumeError=True)


    # Software update check is not a thing any more
    # Start Update Handler,
    # Add both, The peek client_fe_app might fail to connect, and if it does, the payload
    # sent from the peekSwUpdater will be queued and sent when it does connect.
    # d.addBoth(lambda _: peekSwVersionPollHandler.start())

    # Load all Plugins

    d.addBoth(lambda _: logger.info("Loading all Peek Plugins"))
    d.addBoth(lambda _: PeekPlatformConfig.pluginLoader.loadCorePlugins())
    d.addBoth(lambda _: PeekPlatformConfig.pluginLoader.loadOptionalPlugins())

    d.addBoth(lambda _: logger.info("Starting all Peek Plugins"))
    d.addBoth(lambda _: PeekPlatformConfig.pluginLoader.startCorePlugins())
    d.addBoth(lambda _: PeekPlatformConfig.pluginLoader.startOptionalPlugins())

    # Log Exception, convert the errback to callback
    d.addErrback(vortexLogFailure, logger, consumeError=True)

    # Log that the reactor has started
    d.addCallback(lambda _:
                  logger.info('Peek Worker is running, version=%s',
                              PeekPlatformConfig.config.platformVersion))

    # Unlock the mutex
    d.addCallback(lambda _: twistedPluginsLoadedMutex.release())

    d.addErrback(vortexLogFailure, logger, consumeError=True)

    # Run the reactor in a thread
    reactor.callLater(0, logger.info, "Reactor started")

    reactor.run(installSignalHandlers=False)


def celeryMain():
    from peek_platform import PeekPlatformConfig

    # Load all Plugins
    logger.info("Starting Celery")
    from peek_worker import CeleryApp
    CeleryApp.start(PeekPlatformConfig.config)


# Create the startup mutex, twisted has to load the plugins before celery starts.
twistedPluginsLoadedMutex = threading.Lock()
assert twistedPluginsLoadedMutex.acquire()


def setPeekWorkerRestarting():
    global peekWorkerRestarting
    peekWorkerRestarting = True


def main():
    setupPlatform()

    # Initialise and run all the twisted stuff in another thread.
    twistedMainLoopThread = Thread(target=twistedMain)
    twistedMainLoopThread.start()

    # Block until twisted has released it's lock
    twistedPluginsLoadedMutex.acquire()

    # Start the celery blocking main thread
    celeryMain()
    logger.info("Celery has shutdown")

    # Shutdown the Vortex
    VortexFactory.shutdown()

    if PeekPlatformConfig.peekSwInstallManager.restartTriggered:
        logger.info("Restarting Peek Worker")
        PeekPlatformConfig.peekSwInstallManager.realyRestartProcess()

    else:
        # Tell twisted to stop
        logger.info("Shutting down twisted reactor.")
        reactor.callFromThread(reactor.stop)

    # Wait for twisted to stop
    twistedMainLoopThread.join()
    logger.info("Reactor shutdown complete.")

    PeekPlatformConfig.pluginLoader.stopCorePlugins()
    PeekPlatformConfig.pluginLoader.stopOptionalPlugins()

    PeekPlatformConfig.pluginLoader.unloadCorePlugins()
    PeekPlatformConfig.pluginLoader.unloadOptionalPlugins()
    logger.info("Worker Service shutdown complete.")


if __name__ == '__main__':
    main()
