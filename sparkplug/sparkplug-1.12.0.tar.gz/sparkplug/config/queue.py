"""Queue configuration
======================

.. highlight:: cfg

Sparkplug can automatically declare and configure queues on startup::

    [queue:events]
    # Will the queue be declared as durable, and survive broker restarts?
    durable = True
    # Will the queue be declared as auto-deleted, and be removed if all
    # consumers exit?
    auto_delete = False
    # Is the queue exclusive to this program?
    exclusive = False

Queues that are used by a consumer__ must be part of sparkplug's configuration.
However, if the queue is expected to already exist, it's sufficient to mark
the queue as passive::

    [queue:expected]
    passive = True

__ `Consumer configuration`_
"""

from sparkplug.config import DependencyConfigurer
from sparkplug.config.types import convert, parse_bool, parse_dict
from sparkplug.logutils import LazyLogger

_log = LazyLogger(__name__)


class QueueConfigurer(DependencyConfigurer):
    def __init__(self, name, **kwargs):
        DependencyConfigurer.__init__(self)

        self.queue = name

        create_args = dict(kwargs)
        convert(create_args, 'durable', parse_bool)
        convert(create_args, 'auto_delete', parse_bool)
        convert(create_args, 'exclusive', parse_bool)
        convert(create_args, 'passive', parse_bool)
        convert(create_args, 'arguments', parse_dict)
        self.create_args = create_args

        dlx = create_args \
            .get('arguments', {}) \
            .get('x-dead-letter-exchange', None)
        if dlx:
            self.depends_on(dlx)

    def start(self, channel):
        _log.debug("Declaring queue %s (%r)", self.queue, self.create_args)

        channel.queue_declare(queue=self.queue, **self.create_args)

    def __repr__(self):
        return "Queue(queue={0.queue})".format(self)
