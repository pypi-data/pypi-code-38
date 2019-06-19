"""Binding configuration
========================

.. highlight:: cfg

Sparkplug can automatically bind queues to exchanges on startup::

    [binding:postoffice/events]
    # The name of the queue to bind
    queue = events
    # The exchange to bind to.
    exchange = postoffice
    # The routing key to bind under (optional for some exchange types)
    routing_key = events

The queue_ and exchange_ listed for a binding must be present in sparkplug's
configuration.

.. _queue: `Queue configuration`_
.. _exchange: `Exchange configuration`_
"""

from sparkplug.config import DependencyConfigurer
from sparkplug.logutils import LazyLogger

_log = LazyLogger(__name__)


class BindingConfigurer(DependencyConfigurer):
    def __init__(self, name, queue, exchange, routing_key=''):
        DependencyConfigurer.__init__(self)
        self.queue = queue
        self.exchange = exchange
        self.routing_key = routing_key
        
        self.depends_on(queue)
        self.depends_on(exchange)
    
    def start(self, channel):
        _log.debug(
            "Binding queue %s to exchange %s using key %s",
            self.queue,
            self.exchange,
            self.routing_key
        )
        
        channel.queue_bind(
            queue=self.queue,
            exchange=self.exchange,
            routing_key=self.routing_key
        )

    def __repr__(self):
        return ("Binding(queue={0.queue}, exchange={0.exchange},"
                "routing_key={0.routing_key})".format(self))
