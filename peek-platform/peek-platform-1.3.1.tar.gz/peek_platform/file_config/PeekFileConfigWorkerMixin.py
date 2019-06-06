import logging
import multiprocessing

from jsoncfg.value_mappers import require_string, require_integer

logger = logging.getLogger(__name__)


class PeekFileConfigWorkerMixin:
    @property
    def celeryBrokerUrl(self) -> str:
        # for BROKER_URL
        default = 'amqp://guest:guest@localhost:5672//'
        with self._cfg as c:
            return c.celery.brokerUrl(default, require_string)

    @property
    def celeryResultUrl(self) -> str:
        # for CELERYD_CONCURRENCY
        default = 'redis://localhost:6379/0'
        with self._cfg as c:
            return c.celery.resultUrl(default, require_string)

    @property
    def celeryWorkerCount(self) -> str:
        # for CELERYD_CONCURRENCY

        # By default, we assume a single server setup.
        # So leave half the CPU threads for the database
        default = int(multiprocessing.cpu_count() / 2)
        with self._cfg as c:
            return c.celery.workerCount(default, require_integer)

    @property
    def celeryTaskPrefetch(self) -> str:
        # for CELERYD_PREFETCH_MULTIPLIER

        default = 2

        with self._cfg as c:
            return c.celery.taskPrefetch(default, require_integer)
