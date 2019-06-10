"""
Based on http://pika.readthedocs.org/en/latest/examples/asynchronous_consumer_example.html

Changes include, but not limited to, removal of Exchange binding, doing
the consumption in a separate thread and adding wait and time to live
timeouts.
"""

import functools
import logging
import time
import pika

import threading
import traceback

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

import xml.etree.ElementTree as ET


class _Worker(threading.Thread):
    def __init__(self,
                 consumer,
                 basic_deliver,
                 properties,
                 body):
        threading.Thread.__init__(self)
        self._basic_deliver = basic_deliver
        self._consumer = consumer
        self._consumption = None
        document = ET.fromstring(body)
        action = document.get('action')
        if 'stop_listening' == action:
            LOGGER.info('A "stop listening" message has been received')
            self._consumer.add_timeout(0,
                                       self.stop_listening)
        elif 'stop_worker' == action:
            LOGGER.info('A "stop Worker" message has been received')
            self._consumer.add_timeout(0,
                                       self.request_stop)
        elif 'ignore' == action:
            LOGGER.info('An "Ignore this message" message has been received')
            self._consumer.add_timeout(0,
                                       self.acknowledge_message)
        else:
            self.__consumption_instance = self._consumer._consumption(properties,
                                                                      body,
                                                                      basic_deliver.redelivered)


    def run(self):
        if None == self.__consumption_instance:
            return
        try:
            self.__consumption_instance.consume()
        except Consumption.StopListeningException as s:
            LOGGER.info('Worker requested a stop to listening')
            self._consumer.add_timeout(0,
                                       self.stop_listening)
            return
        except Consumption.StopWorkerException as s:
            LOGGER.info('Worker requested a stop of itself')
            self._consumer.add_timeout(0,
                                       self.request_stop)
            return
        except Exception as e:
            traceback.print_exc()
        self._consumer.add_timeout(0,
                                   self.acknowledge_message)


    def acknowledge_message(self):
        """Binds this object's deliver tag to the consumers
        'acknowledge_message' method
        
        """
        self._consumer.acknowledge_message(self._basic_deliver.delivery_tag)


    def request_stop(self):
        """Binds this object's 'acknowledge_message' to the consumers
        'request_stop' method
        
        """
        self._consumer.request_stop(self.acknowledge_message)


    def stop_listening(self):
        """Binds this object's 'acknowledge_message' to the consumers
        'request_stop' method
        
        """
        self._consumer.stop_listening()
        self._consumer.acknowledge_message(self._basic_deliver.delivery_tag)


import sys

def get_implementation(target):
    end = target.rfind('.')
    start = end + 1
    if -1 == end:
        target_module = target
        target_class = target
    elif start == len(target):
        target_module = target[:end]
        target_class = target[:end]
    else:
        target_module = target[:end]
        target_class = target[start:]
    try:
        exec('from ' + target_module + ' import ' + target_class + ' as ConsumptionImpl')
        LOGGER.info('Using class "' + target_module + '.' + target_class + '" to execute the consumption')
        return ConsumptionImpl
    except ImportError:
        LOGGER.critical('Failed to import "' + target_module + '.' + target_class + '"')
        sys.exit(3)


class Consumer(object):
    """This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, this class will stop and indicate
    that reconnection is necessary. You should look at the output, as
    there are limited reasons why the connection may be closed, which
    usually are tied to permission related issues or socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    """

    def __init__(self, parameters, queue, target = 'NullConsumption', prefetch=1,
                 restart=0, durable=True, live_time=0.0, wait_time=0.0):
        """Create a new instance of the consumer class, passing in the
        parameters used to connect to RabbitMQ.

        :param str amqp_url: The AMQP url to connect with

        """
        self.should_reconnect = False
        self.was_consuming = False

        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._consuming = False
        # Exdended attributes
        self._active = 0
        self._consumption = get_implementation(target)
        self._durable = durable
        self._listening = True
        self._parameters = parameters
        self._prefetch = prefetch
        self._queue = queue
        self._restart = restart
        self._wait_time = wait_time
        if live_time > 0:
            self._live = threading.Timer(live_time,
                                         self.expired_live)
            self._live.start()
        self.start_waiting()
        LOGGER.info('Worker count set to ' + str(self._prefetch))


    def add_timeout(self, deadline, callback_method):
        """Requests that the specified callback be executed in the thread
        monitoring the connection after the requested number of seconds"""
        self._connection.ioloop.call_later(deadline, callback_method)


    def expired_live(self):
        self.add_timeout(0,
                         self.stop_listening)


    def stop_listening(self):
        """This method is called to gracefully shut down the connection when
        the 'live_time' parameters has been exceeded.
        
        """
        changed = False
        if self._prefetch != self._active:
            # Reduce the pre-fetch to the number of currently active
            # connections.
            self._prefetch = self._active
            changed = True
            self._channel.basic_qos(prefetch_count = self._prefetch)
        if 0 == self._prefetch :
            LOGGER.info('Stopping as there no Workers and no longer listening')
            cb = functools.partial(self.stop, internal_stop=True)
            self.add_timeout(0,
                             cb)
        else:
            self._listening = False
            if changed:
                LOGGER.info('Worker count changed to ' + str(self._prefetch)
                    + ' as no longer listening')



    def close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            LOGGER.info('Connection is closing or already closed')
        else:
            LOGGER.info('Closing connection')
            self._connection.close()


    def request_stop(self, request):
        self._prefetch -= 1
        self._channel.basic_qos(prefetch_count = self._prefetch)
        request()
        if 0 == self._prefetch :
            LOGGER.info('Stopping as there are not more Workers')
            cb = functools.partial(self.stop, internal_stop=True)
            self.add_timeout(0,
                             cb)
        else:
            LOGGER.info('Worker count changed to ' + str(self._prefetch))


    def start_waiting(self):
        if self._wait_time > 0:
            self._wait = threading.Timer(self._wait_time,
                                         self.expired_wait)
            self._wait.start()
        else:
            self._wait = None


    def expired_wait(self):
        self.add_timeout(0,
                         self.stop_waiting)


    def stop_waiting(self):
        """This method is called to gracefully shut down the connection when
        it's waiting time has been exceeded and no message received.

        """
        if 0 != self._active:
            return
        self._channel.basic_qos(prefetch_count = 0)
        LOGGER.info('Stopping as the wait time has been exceeded and no'
                     + ' message received')
        self.add_timeout(0,
                         self.stop)


    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        LOGGER.info('Connecting to %s', self._parameters)
        return pika.SelectConnection(
            parameters=self._parameters,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)


    def on_connection_open(self, _unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :param pika.SelectConnection _unused_connection: The connection

        """
        LOGGER.info('Connection opened')
        self.open_channel()


    def on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.

        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error

        """
        LOGGER.error('Connection open failed: %s', err)
        self.reconnect()


    def on_connection_closed(self, _unused_connection, reason):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.

        """
        self._channel = None
        if self._closing or 0 >= self._restart:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('Connection closed, reconnect necessary: %s', reason)
            self.reconnect()


    def reconnect(self):
        """Will be invoked if the connection can't be opened or is
        closed. Indicates that a reconnect is necessary then stops the
        ioloop.

        """
        if not self._closing:
            self.should_reconnect = True
            self.stop()


    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)


    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll set up the queue (skipping the
        exchange steps).

        :param pika.channel.Channel channel: The channel object

        """
        LOGGER.info('Channel opened')
        self._channel = channel
        self._channel.basic_qos(prefetch_count = self._prefetch)
        self.add_on_channel_close_callback()
        self.setup_queue(self._queue)


    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        LOGGER.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param Exception reason: why the channel was closed

        """
        LOGGER.warning('Channel %i was closed: %s', channel, reason)
        self.close_connection()


    def setup_queue(self, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.

        """
        LOGGER.info('Declaring queue %s', queue_name)
        cb = functools.partial(self.on_queue_declareok, userdata=queue_name)
        self._channel.queue_declare(queue=queue_name, callback=cb, durable=self._durable)


    def on_queue_declareok(self, _unused_frame, userdata):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we start the consumption
        of the queue.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        LOGGER.info('Starting consumption')
        self.start_consuming()


    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.

        """
        LOGGER.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self._queue,
                                                         self.on_message)
        self.was_consuming = True
        self._consuming = True


    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """
        LOGGER.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)


    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        LOGGER.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel _unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param bytes body: The message body

        """
        LOGGER.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        self._active += 1
        if None != self._wait:
            self._wait.cancel()
            self._wait = None
        runner = _Worker(self,
                         basic_deliver,
                         properties,
                         body);
        runner.start();


    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame

        """
        LOGGER.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)
        self._active -= 1
        if 0 == self._active:
            self.start_waiting()
        if not self._listening:
            self._prefetch -= 1
            self._channel.basic_qos(prefetch_count = self._prefetch)
            if 0 == self._prefetch :
                LOGGER.info('Stopping as there no Workers and no longer listening')
                cb = functools.partial(self.stop, internal_stop=True)
                self.add_timeout(0,
                                 cb)
            else:
                LOGGER.info('Worker count changed to ' + str(self._prefetch)
                    + ' as no longer listening')


    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self._channel:
            LOGGER.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            cb = functools.partial(
                self.on_cancelok, userdata=self._consumer_tag)
            self._channel.basic_cancel(self._consumer_tag, cb)


    def on_cancelok(self, _unused_frame, userdata):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method _unused_frame: The Basic.CancelOk frame
        :param str|unicode userdata: Extra user data (consumer tag)

        """
        self._consuming = False
        LOGGER.info(
            'RabbitMQ acknowledged the cancellation of the consumer: %s',
            userdata)
        self.close_channel()


    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        LOGGER.info('Closing the channel')
        self._channel.close()


    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        self._connection = self.connect()
        self._connection.ioloop.start()


    def stop(self, internal_stop = False):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        if not self._closing:
            self._closing = True
            LOGGER.info('Stopping')
            if self._consuming:
                self.stop_consuming()
                if not internal_stop:
                    self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            LOGGER.info('Stopped')
