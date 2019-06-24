# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import functools
import time
from anyblok_bus.status import MessageStatus
from logging import getLogger
from pika import SelectConnection, URLParameters

logger = getLogger(__name__)


class Worker:
    """Define consumers to consume the queue défined in the AnyBlok registry
    by the bus_consumer decorator

    ::

        worker = Worker(anyblokregistry, profilename)
        worker.start()  # blocking loop
        worker.is_ready()  # return True if all the consumer are started
        worker.stop()  # stop the loop and close the connection with rabbitmq

    This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, this class will stop and indicate
    that reconnection is necessary. You should look at the output, as
    there are limited reasons why the connection may be closed, which
    usually are tied to permission related issues or socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    :param registry: anyblok registry instance
    :param profile: the name of the profile which give the url of rabbitmq
    :param consumers: list of the consumer to consum
    :param withautocommit: default True, commit all the transaction
    """

    def __init__(self, registry, profile, consumers, withautocommit=True):
        self.registry = registry
        self.profile = self.registry.Bus.Profile.query().filter_by(
            name=profile
        ).one()
        self.consumers = consumers
        self.withautocommit = withautocommit
        self._consumer_tags = []

        self.should_reconnect = False
        self.was_consuming = False

        self._connection = None
        self._channel = None
        self._closing = False
        self._consuming = False
        # In production, experiment with higher prefetch values
        # for higher consumer throughput
        self._prefetch_count = 1

    def get_url(self):
        """ Retrieve connection url """
        connection = self.profile
        if connection:
            return connection.url.url

        raise Exception("Unknown profile")

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        url = self.get_url()
        logger.info('Connecting to %s', url)
        return SelectConnection(
            parameters=URLParameters(url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            logger.info('Connection is closing or already closed')
        else:
            logger.info('Closing connection')
            self._connection.close()

    def on_connection_open(self, _unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :param pika.SelectConnection _unused_connection: The connection

        """
        logger.info('Connection opened')
        self.profile.state = 'connected'
        if self.withautocommit:
            self.registry.commit()

        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.

        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error

        """
        logger.error('Connection open failed: %s', err)
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
            logger.warning('Connection closed, reconnect necessary: %s', reason)
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
        logger.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        logger.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.set_qos()

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        logger.info('Adding channel close callback')
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
        logger.warning('Channel %i was closed: %s', channel, reason)
        self.close_connection()

    def on_bindok(self, _unused_frame, userdata):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will set the prefetch count for the channel.

        :param pika.frame.Method _unused_frame: The Queue.BindOk response frame
        :param str|unicode userdata: Extra user data (queue name)

        """
        logger.info('Queue bound: %s', userdata)

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
        logger.info('QOS set to: %d', self._prefetch_count)
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
        logger.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        for queue, model, method in self.consumers:
            self.declare_consumer(queue, model, method)

        self.was_consuming = True
        self._consuming = True

    def declare_consumer(self, queue, model, method):

        def on_message(_unused_channel, basic_deliver, properties, body):
            """Invoked by pika when a message is delivered from RabbitMQ. The
            channel is passed for your convenience. The basic_deliver object
            that is passed in carries the exchange, routing key, delivery tag
            and a redelivered flag for the message. The properties passed in is
            an instance of BasicProperties with the message properties and the
            body is the message that was sent.

            :param pika.channel.Channel _unused_channel: The channel object
            :param pika.Spec.Basic.Deliver: basic_deliver method
            :param pika.Spec.BasicProperties: properties
            :param bytes body: The message body

            """
            logger.info(
                'Received message on %r # %s from %s',
                queue, basic_deliver.delivery_tag, properties.app_id)
            logger.debug(
                'Received message on %r # %s from %s: %s',
                queue, basic_deliver.delivery_tag, properties.app_id, body)
            self.registry.rollback()
            error = ""
            try:
                Model = self.registry.get(model)
                status = getattr(Model, method)(body=body.decode('utf-8'))
                logger.debug('Message delivery_tag=%r and app_id=%r '
                             'is consumed with status=%r',
                             basic_deliver.delivery_tag, properties.app_id,
                             status)
            except Exception as e:
                logger.exception('Error during consumation of queue %r' % queue)
                self.registry.rollback()
                status = MessageStatus.ERROR
                error = str(e)

            if status is MessageStatus.ACK:
                self._channel.basic_ack(basic_deliver.delivery_tag)
                logger.info('ack queue %s tag %r',
                            queue, basic_deliver.delivery_tag)
            elif status is MessageStatus.NACK:
                self._channel.basic_nack(basic_deliver.delivery_tag)
                logger.info('nack queue %s tag %r',
                            queue, basic_deliver.delivery_tag)
            elif status is MessageStatus.REJECT:
                self._channel.basic_reject(basic_deliver.delivery_tag)
                logger.info('reject queue %s tag %r',
                            queue, basic_deliver.delivery_tag)
            elif status is MessageStatus.ERROR or status is None:
                self.registry.Bus.Message.insert(
                    content_type=properties.content_type, message=body,
                    queue=queue, model=model, method=method,
                    error=error, sequence=basic_deliver.delivery_tag,
                )
                self._channel.basic_ack(basic_deliver.delivery_tag)
                logger.info('save message of the queue %s tag %r',
                            queue, basic_deliver.delivery_tag)

            if self.withautocommit:
                self.registry.commit()

        self._consumer_tags.append(
            self._channel.basic_consume(
                queue, on_message,
                arguments=dict(model=model, method=method)
            )
        )
        return True

    def is_ready(self):
        return self._consuming

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """
        logger.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        logger.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        self.profile.state = 'disconnected'
        if self.withautocommit:
            self.registry.commit()

        if self._channel:
            logger.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            for consumer_tag in self._consumer_tags:
                cb = functools.partial(self.on_cancelok, userdata=consumer_tag)
                self._channel.basic_cancel(consumer_tag, cb)

    def on_cancelok(self, _unused_frame, userdata):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method _unused_frame: The Basic.CancelOk frame
        :param str|unicode userdata: Extra user data (consumer tag)

        """
        self._consuming = False
        logger.info(
            'RabbitMQ acknowledged the cancellation of the consumer: %s',
            userdata)
        self._consumer_tags.remove(_unused_frame.method.consumer_tag)
        if not len(self._consumer_tags):
            self.close_channel()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        logger.info('Closing the channel')
        self._channel.close()

    def start(self):
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
            logger.info('Stopping')
            if self._consuming:
                self.stop_consuming()
                try:
                    self._connection.ioloop.start()
                except RuntimeError:
                    self._connection.ioloop.stop()
            else:
                self._connection.ioloop.stop()

            logger.info('Stopped')


class ReconnectingWorker:

    def __init__(self, *args):
        self.args = args
        self._reconnect_delay = 0
        self._consumer = Worker(*args)

    def start(self):
        while True:
            try:
                logger.debug('Start to consume for %r', self.args)
                self._consumer.start()
            except KeyboardInterrupt:
                self._consumer.stop()
                break

            self._maybe_reconnect()

    def _maybe_reconnect(self):
        logger.debug('Check if the consumer must be restarted %r', self.args)
        if self._consumer.should_reconnect:
            self._consumer.stop()
            reconnect_delay = self._get_reconnect_delay()
            logger.info('Reconnecting after %d seconds', reconnect_delay)
            time.sleep(reconnect_delay)
            self._consumer = Worker(*self.args)

    def _get_reconnect_delay(self):
        if self._consumer.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1

        if self._reconnect_delay > 30:
            self._reconnect_delay = 30

        return self._reconnect_delay
