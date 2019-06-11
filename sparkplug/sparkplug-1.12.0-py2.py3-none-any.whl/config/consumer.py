"""Consumer configuration
=========================

.. highlight:: ini

To add consumers to a sparkplug instance, include one or more ``[consumer:*]``
sections in your configuration::

    [consumer:echo]
    # Entry point identifier
    use = sparkplug#echo
    # Queue to consume against
    queue = events
    # Other parameters will be passed passed to the entry point
    format = %%(body)s
    # If set, indicates the time_reporters to use; comma-separated for >1
    time_reporters = mylogger, myotherlogger

The ``use`` parameter is used to find a ``pkg_resources`` entry point. For the
example above, an entry point named ``echo`` in the ``sparkplug.consumers``
group for a distribution (usually, an ``egg`` file) named ``sparkplug`` will
be loaded and used to create message consumers.

---------------------
The consumer protocol
---------------------

.. highlight:: python

Once sparkplug finds an entry point, it uses something equivalent to::

    callback = entry_point(channel, **config)
    channel.basic_consume(queue=queue, callback=callback)

to configure each channel. When sparkplug shuts down, the callback is
also unregistered cleanly.

To register entry points in your own egg files, use ``setuptools``'
``entry_points`` mechanism::

    setup(
        # ...
        entry_points = {
            # ...
            'sparkplug.consumers': [
                'echo = sparkplug.examples:EchoConsumer'
            ]
        }
    )

A complete example is included in the sparkplug source.
"""

from multiprocessing.pool import ThreadPool
from multiprocessing import TimeoutError

import pkg_resources
from sparkplug.config import DependencyConfigurer
from sparkplug.logutils import LazyLogger
import sparkplug.config.timer
from .connection import MultiThreadedConnection

_log = LazyLogger(__name__)


def parse_use(group, use, load_entry_point=pkg_resources.load_entry_point):
    """Parses and loads the entry point for a 'use' directive. The ``use``
    string is expected to look like ``dist#name`` and will be split on the
    first ``'#'`` into a ``dist, name`` pair. Then we pass the whole lot
    to the ``load_entry_point`` callback (using the same protocol as
    ``pkg_resources.load_entry_point``) and return whatever we get back.

    :param group: the entry point group to load from.
    :param use: the un-parsed ``use`` string.
    :param load_entry_point: the function that will actually load entry points.
    """
    dist, entry_point = use.split('#', 1)
    return load_entry_point(dist, group, entry_point)


class ConsumerThread(object):
    def __init__(self, connection, consumer):
        self._consumer = consumer
        self._connection = connection
        self._pool = ThreadPool(1)

    def __call__(self, msg):
        timeout = self._connection.heartbeat * 0.4 or None
        result = self._pool.apply_async(self._consumer, (msg,))
        while not result.ready():
            try:
                result.get(timeout=timeout)
            except TimeoutError:
                _log.debug("Busy heartbeat")
                self._connection.send_heartbeat()
        return


class ConsumerConfigurer(DependencyConfigurer):
    """Handles per-channel setup and teardown for consumer blocks in the
    sparkplug config file.

    :param name: the name of the consumer section.
    :param configurer: the configuration builder to configure with
        callbacks.
    :param use: the consumer entry point to look up.
    :param queue: the queue to bind to.
    :param **kwargs: other configuration parameters, which will be
        passed along to the ``use`` callback.
    """
    def __init__(self, name, use, queue, **kwargs):
        DependencyConfigurer.__init__(self)
        self.entry_point = self.parse_use('sparkplug.consumers', use)
        self.queue = queue

        self.consumer_params = kwargs

        # timerreporters are optional, but calling this is not optional:
        self._init_reporters()

        self.depends_on(queue)


    def _init_reporters( self ):
        self.time_reporters = []
        if 'time_reporters' in self.consumer_params:
            self.time_reporters = [ x.strip() for x in self.consumer_params['time_reporters'].split(',') ]
            for name in self.time_reporters:
                self.depends_on(name)
            # We want to avoid sending extra parameters to consumer
            # entry points that are not expecting them:
            del self.consumer_params['time_reporters']

    def start(self, channel):
        _log.debug("Creating consumer from %r", self.entry_point)
        consumer = self.entry_point(channel, **self.consumer_params)

        with MultiThreadedConnection(channel.connection):
            # Wrap the original consumer with a callable to
            # report timing information:
            consumer = sparkplug.config.timer.Timer(consumer, self.time_reporters)

            # Wrap again to run in a separate thread, allow main thread to handle heartbeats
            executer = ConsumerThread(channel.connection, consumer)

            _log.debug("Consuming from queue %s", self.queue)
            channel.basic_consume(callback=executer, queue=self.queue)

    def stop(self, channel):
        pass

    parse_use = staticmethod(parse_use)

    def __repr__(self):
        return "Consumer(queue={0.queue}, consumer={0.entry_point}".format(self)
