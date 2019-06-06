import importlib
import logging

from celery.signals import worker_process_init, worker_process_shutdown, worker_init, \
    task_postrun

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_base.worker.CeleryDbConn import getDbSession

logger = logging.getLogger(__name__)


class __WorkerInit:
    # Store the data for the worker processes to initialise with
    dbConnectString = None
    dbEngineArgs = None


@worker_init.connect
def initWorkerConnString(sender, **kwargs):
    logger.info("Setting worker process database connection string")
    __WorkerInit.dbConnectString = sender.app.peekDbConnectString
    __WorkerInit.dbEngineArgs = sender.app.peekDbEngineArgs


@worker_process_init.connect
def initWorkerProcessDbConn(**kwargs):
    logger.debug('Creating unique database connection for worker process')

    # The next call to CeleryDbConn.dbEngine property will create a new engine
    # with this connection string
    from peek_plugin_base.worker import CeleryDbConn
    CeleryDbConn = importlib.reload(CeleryDbConn)

    CeleryDbConn._dbConnectString = __WorkerInit.dbConnectString
    CeleryDbConn._dbEngineArgs = __WorkerInit.dbEngineArgs
    logger.info('Created unique database connection for worker process')


@worker_process_shutdown.connect
def shutdownWorkerProcessDbConn(**kwargs):
    logger.debug('Closing database connectionn for worker.')

    if CeleryDbConn.__ScopedSession:
        getDbSession()  # Ensure we have a session maker
        CeleryDbConn.__ScopedSession.close_all()

    if CeleryDbConn.__dbEngine:
        CeleryDbConn.__dbEngine.dispose()

    logger.info('Closed database connectionn for worker.')


@task_postrun.connect
def taskEndCloseSession(**kwargs):
    CeleryDbConn.getDbSession().close()
