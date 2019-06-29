

from celery import Celery

from peek_platform import PeekPlatformConfig
from peek_platform.ConfigCeleryApp import configureCeleryApp
from peek_platform.file_config.PeekFileConfigWorkerMixin import PeekFileConfigWorkerMixin

celeryApp = Celery('celery')


def start(workerConfig:PeekFileConfigWorkerMixin):
    configureCeleryApp(celeryApp, workerConfig)

    pluginIncludes = PeekPlatformConfig.pluginLoader.celeryAppIncludes

    celeryApp.conf.update(
        # DbConnection MUST BE FIRST, so that it creates a new connection
        include=[
            'peek_platform.ConfigCeleryApp', # Load the vortex serialisation
            'peek_plugin_base.worker.CeleryDbConnInit'
            ] + pluginIncludes,
    )

    # Create and set this attribute so that the CeleryDbConn can use it
    # Worker is passed as sender to @worker_init.connect
    celeryApp.peekDbConnectString = PeekPlatformConfig.config.dbConnectString
    celeryApp.peekDbEngineArgs = PeekPlatformConfig.config.dbEngineArgs

    celeryApp.worker_main()
