# coding: utf-8
from deployv.helpers.utils import get_error_message
from deployv.base.errors import GracefulExit
import logging
import pika
from random import randint
from time import sleep


_logger = logging.getLogger(__name__)


class ReconnectionException(Exception):
    def __init__(self, message, *args, **kwargs):
        super(ReconnectionException, self).__init__(message, *args, **kwargs)


class RabbitReceiverV(object):
    """ This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    """
    EXCHANGE_TYPE = 'topic'

    def __init__(self, listener_configuration, worker_id):
        """ Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param str amqp_url: The AMQP url to connect with

        """
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._consuming = False
        self._config = listener_configuration
        if self._config.result_config:
            self._binding_key = self._config.route
        else:
            self._binding_key = '{base}.{wid}'.format(base=self._config.route, wid=worker_id)

    def connect(self):
        """ This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        _logger.info('Connecting to %s:%s',
                     self._config.parameters.host,
                     self._config.parameters.port)
        return pika.SelectConnection(
                self._config.parameters, self.on_connection_open,
                stop_ioloop_on_close=True)

    def on_connection_open(self, unused_connection):
        """ This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection

        """
        _logger.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        """ This method adds an on close callback that will be invoked by pika
        when RabbitMQ closes the connection to the publisher unexpectedly.

        """
        _logger.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """ This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            _logger.warning('Connection closed, reopening in %s seconds: (%s) %s',
                            self._config.parameters.socket_timeout, reply_code, reply_text)
            self.reconnect()

    def reconnect(self):
        """ Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        # This is the old connection IOLoop instance, stop its ioloop
        self.stop()

    def open_channel(self):
        """ Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """
        _logger.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """ This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        _logger.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self._config.exchange_name)

    def add_on_channel_close_callback(self):
        """ This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        _logger.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """ Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        _logger.warning('Channel %i was closed: (%s) %s',
                        channel, reply_code, reply_text)
        self.close_connection()

    def setup_exchange(self, exchange_name):
        """ Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param str|unicode exchange_name: The name of the exchange to declare

        """
        _logger.info('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self.EXCHANGE_TYPE)

    def on_exchange_declareok(self, unused_frame):
        """ Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame

        """
        _logger.info('Exchange declared')
        self.setup_queue(self._binding_key)

    def setup_queue(self, queue_name):
        """ Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.

        """
        _logger.info('Declaring queue %s', queue_name)
        self._channel.queue_declare(self.on_queue_declareok, queue=queue_name, durable=True)

    def on_queue_declareok(self, method_frame):
        """ Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        _logger.info('Binding %s to %s with %s',
                     self._config.exchange_name, self._config.queue_name, self._binding_key)
        self._channel.queue_bind(self.on_bindok, queue=self._binding_key,
                                 exchange=self._config.exchange_name,
                                 routing_key=self._binding_key)
        _logger.info('Binding %s to %s with %s',
                     self._config.exchange_name, self._config.queue_name, self._config.route)
        self._channel.queue_bind(self.on_bindok, queue=self._config.queue_name,
                                 exchange=self._config.exchange_name,
                                 routing_key=self._config.route)

    def on_bindok(self, unused_frame):
        """ Invoked by pika when the Queue.Bind method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.

        :param pika.frame.Method unused_frame: The Queue.BindOk response frame

        """
        _logger.info('Queue bound')
        self.start_consuming()

    def start_consuming(self):
        """ This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming.
        """
        _logger.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self._callback_funct,
                                                         self._binding_key)
        self._consuming = True

    def add_on_cancel_callback(self):
        """ Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """
        _logger.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """ Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        _logger.info('Consumer was cancelled remotely, shutting down: %r',
                     method_frame)
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        """ Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame

        """
        _logger.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        """ Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self._channel:
            _logger.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):
        """ This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame

        """
        self._consuming = False
        _logger.info('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):
        """ Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        _logger.info('Closing the channel')
        if self._connection.is_closing or self._connection.is_closed:
            _logger.info('Connection already closed')
            return
        self._channel.close()

    def run(self, callback_funct):
        """ Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        if self._connection and self._connection.is_open:
            return
        self._callback_funct = callback_funct
        while not self._closing:
            try:
                self._connection = self.connect()
                self._connection.ioloop.start()
            except (KeyboardInterrupt, GracefulExit):
                self._closing = True
                self.stop()
            except Exception as error:  # pylint: disable=W0703
                _logger.error('Error connecting to Rabbit server')
                error_msg = get_error_message(error)
                _logger.exception(error_msg)
                wait = randint(3, 7)
                _logger.error('Waiting %s seconds before retry', wait)
                sleep(wait)

    def stop(self):
        """ Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        _logger.info('Stopping')
        if not self._connection or self._connection.is_closing or self._connection.is_closed:
            _logger.info('Connection already closed')
            return
        if self._consuming:
            self.stop_consuming()
            self._connection.ioloop.start()
        else:
            self._connection.ioloop.stop()
        _logger.info('Stopped')

    def close_connection(self):
        """ This method closes the connection to RabbitMQ."""
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            _logger.info('Connection already closed')
            return
        _logger.info('Closing connection')
        self._connection.close()
