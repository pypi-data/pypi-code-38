#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import pika
import functools

__name__ = "puanchen"
__version__ = '1.0.0'
__author__ = 'ClaireHuang'
__author_email__ = 'clairehf@163.com'


class HeraldMQ(object):
    def __init__(self, host, port, vhost, user, password, heartbeat=60):
        credentials = pika.PlainCredentials(user, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host, port, vhost, credentials, heartbeat=heartbeat
        ))
        self.channel = self.connection.channel()

    def declare_queue(self, queue_name):
        self.channel.queue_declare(queue=queue_name, durable=True)

    def declare_delay_queue(self, queue_name, ttl):
        delay_queue_name = queue_name + "_delay"
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.queue_bind(exchange='amq.direct', queue=queue_name,
                                routing_key=queue_name)
        self.channel.queue_declare(queue=delay_queue_name, durable=True,
                            arguments={
                                'x-message-ttl': ttl,
                                'x-dead-letter-exchange': 'amq.direct',
                                'x-dead-letter-routing-key': queue_name
                            })

    def send_message(self, queue_name, body):
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def send_delay_message(self, queue_name, body):
        delay_queue_name = queue_name + "_delay"
        self.send_message(delay_queue_name, body)

    def close_connection(self):
        self.connection.close()

    def _on_message(self, chan, method_frame, _header_frame, body,
                   consume_func=None):
        """Called when a message is received."""
        result = consume_func(body)
        if result == "complete":
            chan.basic_ack(delivery_tag=method_frame.delivery_tag)
        elif result == "requeue":
            chan.basic_reject(delivery_tag=method_frame.delivery_tag)

    def worker(self, queue_name, func):
        self.channel.basic_qos(prefetch_count=1)
        on_message_callback = functools.partial(self._on_message,
                                                consume_func=func)
        self.channel.basic_consume(queue_name, on_message_callback)
        self.channel.start_consuming()

class SelectConsumer(object):
    """This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.
    If RabbitMQ closes the connection, this class will stop and indicate
    that reconnection is necessary. You should look at the output, as
    there are limited reasons why the connection may be closed, which
    usually are tied to permission related issues or socket timeouts.
    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.
    """
    EXCHANGE = 'amq.direct'
    EXCHANGE_TYPE = 'direct'

    def __init__(self, host, port, vhost, user, password, queue,
                 consume_func, heartbeat=60):
        """
           Create a new instance of the consumer class
        """
        self.should_reconnect = False
        self.was_consuming = False

        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._consuming = False
        # In production, experiment with higher prefetch values
        # for higher consumer throughput
        self._prefetch_count = 1

        credentials = pika.PlainCredentials(user, password)
        self.connection_parameters = pika.ConnectionParameters(
            host, port, vhost, credentials, heartbeat=heartbeat)

        self.queue = queue
        self.routing_key = queue

        self.consume_func = consume_func

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.
        :rtype: pika.SelectConnection
        """
        logging.info('Connecting to : SelectConnection')
        return pika.SelectConnection(
            parameters=self.connection_parameters,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            logging.info('Connection is closing or already closed')
        else:
            logging.info('Closing connection')
            self._connection.close()

    def on_connection_open(self, _unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :param pika.SelectConnection _unused_connection: The connection
        """
        logging.info('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.
        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error
        """
        logging.error('Connection open failed: %s', err)
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
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logging.warning('Connection closed, reconnect necessary: %s', reason)
            self.reconnect()

    def reconnect(self):
        """Will be invoked if the connection can't be opened or is
        closed. Indicates that a reconnect is necessary then stops the
        ioloop.
        """
        self.should_reconnect = True
        self.stop()

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.
        """
        logging.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.
        Since the channel is now open, we'll declare the exchange to use.
        :param pika.channel.Channel channel: The channel object
        """
        logging.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        logging.info('Adding channel close callback')
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
        logging.warning('Channel %i was closed: %s', channel, reason)
        self.close_connection()

    def setup_exchange(self, exchange_name):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.
        :param str|unicode exchange_name: The name of the exchange to declare
        """
        logging.info('Declaring exchange: %s', exchange_name)
        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(
            self.on_exchange_declareok, userdata=exchange_name)
        self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=self.EXCHANGE_TYPE,
            durable=True,
            callback=cb)

    def on_exchange_declareok(self, _unused_frame, userdata):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.
        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
        :param str|unicode userdata: Extra user data (exchange name)
        """
        logging.info('Exchange declared: %s', userdata)
        self.setup_queue(self.queue)

    def setup_queue(self, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.
        :param str|unicode queue_name: The name of the queue to declare.
        """
        logging.info('Declaring queue %s', queue_name)
        cb = functools.partial(self.on_queue_declareok, userdata=queue_name)
        self._channel.queue_declare(queue=queue_name, durable=True, callback=cb)

    def on_queue_declareok(self, _unused_frame, userdata):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.
        :param pika.frame.Method _unused_frame: The Queue.DeclareOk frame
        :param str|unicode userdata: Extra user data (queue name)
        """
        queue_name = userdata
        logging.info('Binding %s to %s with %s', self.EXCHANGE, queue_name,
                    self.routing_key)
        cb = functools.partial(self.on_bindok, userdata=queue_name)
        self._channel.queue_bind(
            queue_name,
            self.EXCHANGE,
            routing_key=self.routing_key,
            callback=cb)

    def on_bindok(self, _unused_frame, userdata):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will set the prefetch count for the channel.
        :param pika.frame.Method _unused_frame: The Queue.BindOk response frame
        :param str|unicode userdata: Extra user data (queue name)
        """
        logging.info('Queue bound: %s', userdata)
        self.set_qos()

    def set_qos(self):
        """This method sets up the consumer prefetch to only be delivered
        one message at a time. The consumer must acknowledge this message
        before RabbitMQ will deliver another one. You should experiment
        with different prefetch values to achieve desired performance.
        """
        self._channel.basic_qos(
            prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok)

    def on_basic_qos_ok(self, _unused_frame):
        """Invoked by pika when the Basic.QoS method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.
        :param pika.frame.Method _unused_frame: The Basic.QosOk response frame
        """
        logging.info('QOS set to: %d', self._prefetch_count)
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
        logging.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        on_message_call = functools.partial(self.on_message,
                                            consume_func=self.consume_func)
        self._consumer_tag = self._channel.basic_consume(
            self.queue, on_message_call)
        self.was_consuming = True
        self._consuming = True

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.
        """
        logging.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.
        :param pika.frame.Method method_frame: The Basic.Cancel frame
        """
        logging.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, _unused_channel, basic_deliver, properties, body,
                   consume_func=None):
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
        :param funcobj consume_func: Real consumer function on app
        """
        logging.info('Received message # delivery tag %s: %s',
                    basic_deliver.delivery_tag, body)

        result = consume_func(body)
        if result == "complete":
            self.acknowledge_message(basic_deliver.delivery_tag)
        elif result == "requeue":
            self.not_acknowledge_message(basic_deliver.delivery_tag)
        else:
            raise Exception("Unknown return value of consume function.")

    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.
        :param int delivery_tag: The delivery tag from the Basic.Deliver frame
        """
        logging.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def not_acknowledge_message(self, delivery_tag):
        logging.info('Not Acknowledging message %s', delivery_tag)
        self._channel.basic_nack(delivery_tag)

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.
        """
        if self._channel:
            logging.info('Sending a Basic.Cancel RPC command to RabbitMQ')
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
        logging.info(
            'RabbitMQ acknowledged the cancellation of the consumer: %s',
            userdata)
        self.close_channel()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.
        """
        logging.info('Closing the channel')
        self._channel.close()

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.
        """
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
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
            logging.info('Stopping')
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            logging.info('Stopped')


class ReconnectingSelectConsumer(object):
    """This is an example consumer that will reconnect if the nested
    ExampleConsumer indicates that a reconnect is necessary.
    """

    def __init__(self, host, port, vhost, user, password, queue, consume_func,
                 heartbeat=60):
        self._reconnect_delay = 0

        self.host = host
        self.port = port
        self.vhost = vhost
        self.user = user
        self.password = password
        self.queue = queue
        self.consume_func = consume_func
        self.heartbeat = heartbeat

        self._consumer = SelectConsumer(self.host, self.port, self.vhost,
                                        self.user, self.password, self.queue,
                                        self.consume_func, self.heartbeat)

    def run(self):
        while True:
            try:
                self._consumer.run()
            except KeyboardInterrupt:
                self._consumer.stop()
                break
            self._maybe_reconnect()

    def _maybe_reconnect(self):
        if self._consumer.should_reconnect:
            self._consumer.stop()
            reconnect_delay = self._get_reconnect_delay()
            logging.info('Reconnecting after %d seconds', reconnect_delay)
            time.sleep(reconnect_delay)
            self._consumer = SelectConsumer(self.host, self.port, self.vhost,
                                        self.user, self.password, self.queue,
                                        self.consume_func, self.heartbeat)

    def _get_reconnect_delay(self):
        if self._consumer.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1
        if self._reconnect_delay > 30:
            self._reconnect_delay = 30
        return self._reconnect_delay