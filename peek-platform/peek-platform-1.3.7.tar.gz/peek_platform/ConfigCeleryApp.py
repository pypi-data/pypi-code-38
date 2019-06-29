import logging
import typing

import celery
from celery import signals as celery_signals
from kombu import serialization
from peek_platform.file_config.PeekFileConfigWorkerMixin import PeekFileConfigWorkerMixin
from vortex.DeferUtil import noMainThread
from vortex.Payload import Payload

logger = logging.getLogger(__name__)


def vortexDumps(arg: typing.Tuple) -> str:
    noMainThread()
    # startTime = datetime.now(pytz.utc)
    try:
        return Payload(tuples=[arg])._toJson()
    except Exception as e:
        logger.exception(e)
        raise
    # finally:
    #     logger.debug("vortexDumps took %s", (datetime.now(pytz.utc) - startTime))


def vortexLoads(jsonStr: str) -> typing.Tuple:
    noMainThread()
    # startTime = datetime.now(pytz.utc)
    try:
        return Payload()._fromJson(jsonStr).tuples[0]
    except Exception as e:
        logger.exception(e)
        raise
    # finally:
    #     logger.debug("vortexLoads took %s", (datetime.now(pytz.utc) - startTime))


serialization.register(
    'vortex', vortexDumps, vortexLoads,
    content_type='application/x-vortex',
    content_encoding='utf-8',
)


class BackendMixin:

    def exception_to_python(self, exc):
        """Convert serialized exception to Python exception."""
        import sys
        from kombu.utils.encoding import from_utf8
        from celery.utils.serialization import (create_exception_cls,
                                                get_pickled_exception)

        EXCEPTION_ABLE_CODECS = frozenset({'pickle'})

        if not exc:
            return exc

        if not isinstance(exc, BaseException):
            exc_module = exc.get('exc_module')
            if exc_module is None:
                cls = create_exception_cls(
                    from_utf8(exc['exc_type']), __name__)
            else:
                exc_module = from_utf8(exc_module)
                exc_type = from_utf8(exc['exc_type'])
                try:
                    cls = getattr(sys.modules[exc_module], exc_type)
                except KeyError:
                    cls = create_exception_cls(exc_type,
                                               celery.exceptions.__name__)
            exc_msg = exc['exc_message']
            args = exc_msg if isinstance(exc_msg, tuple) else [exc_msg]
            try:
                exc = cls(*args)
            except TypeError:
                exc = Exception("%s\n%s" % (cls, args))

            if self.serializer in EXCEPTION_ABLE_CODECS:
                exc = get_pickled_exception(exc)

        return exc


from celery.backends.base import Backend

Backend.exception_to_python = BackendMixin.exception_to_python


def configureCeleryApp(app, workerConfig: PeekFileConfigWorkerMixin):
    # Optional configuration, see the application user guide.
    app.conf.update(
        # On peek_server, the thread limit is set to 10, these should be configurable.
        broker_pool_limit=15,

        # Set the broker and backend URLs
        broker_url=workerConfig.celeryBrokerUrl,
        result_backend=workerConfig.celeryResultUrl,

        # Leave the logging to us
        worker_hijack_root_logger=False,

        # The time results will stay in redis before expiring.
        # I believe they are cleared when the results are obtained
        # from txcelery._DeferredTask
        result_expires=3600,

        # The number of tasks each worker will prefetch.
        worker_prefetch_multiplier=workerConfig.celeryTaskPrefetch,

        # The number of workers to have at one time
        worker_concurrency=workerConfig.celeryWorkerCount,

        # The maximum number or results to keep for the client
        # We could have backlog of 1000 results waiting for the client to pick up
        # This would be a mega performance issue.
        result_cache_max=1000,  # Default is 100

        task_serializer='vortex',
        # accept_content=['vortex'],  # Ignore other content
        accept_content=['pickle', 'json', 'msgpack', 'yaml', 'vortex'],
        result_serializer='vortex',
        enable_utc=True,

        # Default time in seconds before a retry of the task should be executed.
        # 3 minutes by default.
        default_retry_delay=2
    )


from peek_platform.file_config.PeekFileConfigABC import PeekFileConfigABC
from peek_platform.file_config.PeekFileConfigPlatformMixin import \
    PeekFileConfigPlatformMixin


class _WorkerTaskConfigMixin(PeekFileConfigABC,
                             PeekFileConfigPlatformMixin):
    pass


@celery_signals.after_setup_logger.connect
def configureCeleryLogging(*args, **kwargs):
    from peek_plugin_base.PeekVortexUtil import peekWorkerName

    # Fix the loading problems windows has
    # from peek_platform.util.LogUtil import setupPeekLogger
    # setupPeekLogger(peekWorkerName)

    from peek_platform import PeekPlatformConfig
    PeekPlatformConfig.componentName = peekWorkerName
    config = _WorkerTaskConfigMixin()

    # Set default logging level
    logging.root.setLevel(config.loggingLevel)

    if config.loggingLevel != "DEBUG":
        for name in ("celery.worker.strategy", "celery.app.trace", "celery.worker.job"):
            logging.getLogger(name).setLevel(logging.WARNING)
