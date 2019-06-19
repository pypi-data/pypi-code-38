###############################################################################
# (c) Copyright 2017 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Module grouping the common build functions.
'''

import datetime
import json
import logging
import uuid
from collections import namedtuple

import os
import pika
import uuid

__author__ = 'Ben Couturier <ben.couturier@cern.ch>'


# Utility class to ease the use of the messages
Message = namedtuple('Message', ['body', 'method_frame', 'header_frame'],
                     rename=True)


# Our own exception to signal that the processing was interrupted and
# we shouldn't ack the message
class InterruptedProcessing(Exception):
    pass


# Various utilities for connection management
def _get_pwd_from_sys():
    """
    Get the RabbitMQ password from the environment of from a file on disk
    :returns a username, password tuple for RabbitMQ connection
    """
    # First checking the environment
    res = os.environ.get("RMQPWD", None)

    # Checking for the password in $HOME/private/rabbitmq.txt
    if res is None:
        fname = os.path.join(os.environ["HOME"], "private", "rabbitmq.txt")
        if os.path.exists(fname):
            with open(fname, "r") as f:
                data = f.readlines()
                if len(data) > 0:
                    res = data[0].strip()
    if res is None:
        # At this point we should have found the authentication
        # Otherwise, we throw an exception...
        raise Exception("Could not locate broker credentials")


    # Separate the username/password
    (username, password) = res.split("/")
    return username, password


def get_connection(host=None,
                   username=None, passwd=None,
                   port=5671, vhost='/lhcb', use_ssl=True,
                   heartbeat_interval=None,
                   blocked_connection_timeout=None):
    """
    Create a connection to RabbitMQ
    :param host: the RabbitMQ server hostname
    :param username: the RabbitMQ server username
    :param passwd: the RabbitMQ server password
    :param port: the RabbitMQ server port
    :param vhost: the RabbitMQ virtual host that should be used in the
                  connection
    :param use_ssl: if True, an encrypted connection is created, plain text
                    otherwise
    :returns: a pika BlockingConnection to RabbitMQ generated with the
              arguments
    """

    envhost = os.environ.get("RMQHOST", None)
    if envhost:
        host = envhost
    if host is None:
        host = "lbmessagingbroker.cern.ch"

    envvhost = os.environ.get("RMQVHOST", None)
    if envvhost:
        vhost = envvhost

    if os.environ.get("RMQNOSSL", None):
        use_ssl = False

    if os.environ.get("RMQPORT", None):
        port = int(os.environ.get("RMQPORT"))

    if username is None or passwd is None:
        (username, passwd) = _get_pwd_from_sys()
    credentials = pika.PlainCredentials(username, passwd)
    cpar = " ".join([str(x) for x in [host, use_ssl, port, vhost]])
    logging.debug("Connection paremeters: %s" % cpar)
    conn_params = { "ssl":use_ssl,
                    "port":port,
                    "virtual_host":vhost,
                    "credentials":credentials }
    if heartbeat_interval is not None:
        conn_params["heartbeat_interval"] = heartbeat_interval
    if blocked_connection_timeout is not None:
        conn_params["blocked_connection_timeout"] = blocked_connection_timeout

    params = pika.ConnectionParameters(host, **conn_params )
    return pika.BlockingConnection(params)


def check_channel(channel, connection=None):
    """
    Ugly hack to keep backwards compatibility
    We should receive a pika.Channel, but if we are given a
    pika.BlockingConnection, we just create a new channel from it....

    :param channel: a pikaBlockingConnection channel to verify
    :param connection: a pikaBlockingConnection from which the channel needs
                       to be extracted
    :returns: the correct channel that should be used in the transactions
    """
    checked_channel = None
    if connection is not None:
        checked_channel = connection.channel()
    else:
        if isinstance(channel, pika.BlockingConnection):
            checked_channel = channel.channel()
        else:
            checked_channel = channel
    return checked_channel


class QueueHelper(object):
    """
    Utility class to access the rabbitmq broker
    """

    def __init__(self, channel=None, connection=None):
        """
        Initialize the messenger class
        :param channel: a pikaBlockingConnection channel that should be used in
                        the broker
        :param connection: a pikaBlockingConnection that should be used in
                        the broker
        """

        self._channel = check_channel(channel, connection)
        import lbmessaging
        self.MAX_PRIORITY = lbmessaging.priority(lbmessaging.EMERGENCY)

    def _setup_exchange(self, channel, exchange_name, auto_delete=False):
        """
        Creates an exchange with the desired exchange_type
        :param channel: a pikaBlockingConnection channel that should be used in
                        the exchange declarations
        :param exchange_name: the exchange name used in the broker
        :param auto_delete: option to automatically delete the exchange if no
                            queues is bind to the exchange
        """
        channel.exchange_declare(exchange=exchange_name,
                                 exchange_type='topic',
                                 auto_delete=auto_delete,
                                 durable=True)

    def basic_publish(self, exchange_name, routing_key, body, priority=1,
                      max_retry=3, headers=None, auto_delete=False,
                      expiration=None, extra_properties={}):
        """
        Send a message to the topic defined for the builds
        :param exchange_name: the exchange that should be used
        :param routing_key: the routing (binding) key used to route the message
                            from the exchange to the queue that is bind with
                            this key to the exchange
        :param body: the payload of the message
        :param priority: the priority of the message (0 - 255)
        :param max_retry: the number of retries of sending the message in case
                          of failure
        :param headers: the headers that are included in the message
        :param auto_delete: option to automatically delete the exchange if no
                            queues is bind to the exchange
        :param expiration: TTL for the message. The message will be
                           automatically deleted if this value is reached.
                           The value should be in milliseconds. For non
                           expiring messages, the flag should be set to None
        :param extra_properties: Extra pika BasicProperties to be set.
        """
        channel = self._channel
        self._setup_exchange(channel, exchange_name,
                             auto_delete=auto_delete)
        now = datetime.datetime.utcnow().isoformat()
        ipd = now
        if headers and headers.get('initial_publish_date'):
            ipd = headers.get('initial_publish_date')
        uid = uuid.uuid4().hex
        if headers and headers.get('uid'):
            uid = headers.get('uid')
        props = pika.BasicProperties(delivery_mode=2, priority=priority,
                                     headers={'max_retry': max_retry,
                                              'initial_publish_date': ipd,
                                              'uid': uid,
                                              # make message persistent
                                              'publish_date': now})
        if expiration:
            # It must be a string in milliseconds
            props.expiration = str(expiration)
        for key, value in extra_properties.items():
            setattr(props, key, value)
        channel.basic_publish(exchange=exchange_name,
                              routing_key=routing_key,
                              body=body,
                              properties=props)

    def bind_queue_to_exchange(self, queue_name, exchange_name,
                               routing_keys=None,
                               route_only_to_queue=False,
                               auto_delete=False):
        """
        Binds the queue to an exchange, make sure the queue is persistent
        :param queue_name: the queue on which needs to be bind to the exchange
        :param exchange_name: the exchange to which the queue should be bind to
        :param routing_keys: the routing keys that are used to route a message
                             from the exchange to the queue
        :param route_only_to_queue: if true and no routing keys are defined,
                                    the queue will listen only for the messages
                                    destined for the queue, i.e. the routing
                                    keys in the messages are identical with the
                                    queue name.
        :param auto_delete: option to automatically delete the exchange if no
                            queues is bind to the exchange
        """

        return self._setup_queue(self._channel, exchange_name,
                                 queue_name, routing_keys,
                                 route_only_to_queue=route_only_to_queue,
                                 auto_delete=auto_delete)

    def _setup_queue(self, channel, exchange_name, queue_name=None,
                     routing_keys=None, route_only_to_queue=False,
                     auto_delete=False):
        """
        Setup a queue and binds
        :param channel: a pikaBlockingConnection channel that should be used in
                        the broker
        :param queue_name: the queue on which needs to be bind to the exchange
        :param exchange_name: the exchange to which the queue should be bind to
        :param routing_keys: the routing keys that are used to route a message
                             from the exchange to the queue
        :param route_only_to_queue: if true and no routing keys are defined,
                                    the queue will listen only for the messages
                                    destined for the queue, i.e. the routing
                                    keys in the messages are identical with the
                                    queue name.
        :param auto_delete: option to automatically delete the exchange if no
                            queues is bind to the exchange
        :returns: the queue name. If in the args, the queue name was none,
                  an anonymous queue is created and its name is returned.
        """
        self._setup_exchange(channel, exchange_name,
                             auto_delete=auto_delete)
        if queue_name is None:
            # Anonymous queue is NOT persistent
            logging.info("Declaring anonymous queue")
            result = channel.queue_declare(exclusive=True,
                                           auto_delete=auto_delete,
                                           arguments={
                                               "x-max-priority":
                                                   self.MAX_PRIORITY})
            queue_name = result.method.queue
        else:
            # Named queues are persistent...
            logging.info("Declaring durable queue: %s" % queue_name)
            result = channel.queue_declare(durable=1, queue=queue_name,
                                           auto_delete=auto_delete,
                                           arguments={
                                               "x-max-priority":
                                                   self.MAX_PRIORITY})

        # defaults to the wildcard for topic channels
        if routing_keys is None:
            # If the routing keys list is None, we could listen for all the
            # messages in the exchange using # or we could listen only for the
            # messages for this specific queue. As an example, in the RPC mode,
            # both the client and the server are using the same exchange, but
            # we need to separate the messages for the server queue ( requests)
            # from those for the client anonymous queue (replays)
            if route_only_to_queue:
                routing_keys = [queue_name]
            else:
                routing_keys = ["#"]

        # Now binding the queue to the topic
        for routing_key in routing_keys:
            logging.info("Binding %s to %s for '%s'" % (queue_name,
                                                        exchange_name,
                                                        routing_key))
            channel.queue_bind(exchange=exchange_name,
                               queue=queue_name,
                               routing_key=routing_key)
        return queue_name


class Sender(QueueHelper):
    """
    Class used by cvmfs-lhcbdev.cern.ch to communicate with the outside world
    """

    def __init__(self, exchange, *args, **kwargs):
        """
        Initialize props
        :param exchange_name: the exchange name used in the broker
        """
        super(Sender, self).__init__(*args, **kwargs)
        self._exchange_name = exchange

    def send_message(self, routing_key, payload, priority=1, max_retry=3,
                     auto_delete=False, expiration=None):
        """
        Sends a message to the exchange
        :param routing_keys: the routing keys set in the message in order to
                             route it from the exchange to the queue(s)
        :param payload: the content of the messages send to the exchange
        :param priority: the priority of the message
        :param max_retry: the max of retries in case of command failure on CVMFS
        :param auto_delete: option to automatically delete the exchange if no
                            queues is bind to the exchange
        :param expiration: the TTL of the message
        """
        body = json.dumps(payload)
        self.basic_publish(self._exchange_name, routing_key, body,
                           priority=priority, max_retry=max_retry,
                           expiration=expiration,
                           auto_delete=auto_delete
                           )
        logging.info("Publish done to %s" % (self._exchange_name))

    def resend_message(self, message, keep_retry_count=False):
        """
        Resend a message based on a received header frame payload
        :param message: the message whose consumption failed as Message object
        :param keep_retry_count: if true, the retry count is not decremented.
                                 Otherwise, the retry count is decremented by 1
        """
        routing_key = message.method_frame.routing_key

        bodyjson = json.dumps(message.body)
        new_max_retry = message.header_frame.headers.get('max_retry', 0)
        if not keep_retry_count and 'max_retry' in message.header_frame.\
                headers.keys():
            new_max_retry = message.header_frame.headers['max_retry'] - 1

        self.basic_publish(self._exchange_name, routing_key, bodyjson,
                           priority=message.header_frame.priority,
                           max_retry=new_max_retry,
                           headers=message.header_frame.headers)
        logging.info("resend done to %s" % (self._exchange_name))


class Receiver(QueueHelper):
    """
    Initializes a queue to receive messages
    """

    def __init__(self, exchange, queue, routing_keys=None, auto_delete=False,
                 route_only_to_queue=False, no_bind=False,
                 *args, **kwargs):
        """
        Initialize props
        :param exchange_name: the exchange name used in the broker
        :param queue: the queue on which needs to be bind to the exchange
        :param routing_keys: the routing keys that are used to route a message
                             from the exchange to the queue
        :param auto_delete: option to automatically delete the exchange if no
                            queues is bind to the exchange
        :param route_only_to_queue: if true and no routing keys are defined,
                                    the queue will listen only for the messages
                                    destined for the queue, i.e. the routing
                                    keys in the messages are identical with the
                                    queue name.
        """
        super(Receiver, self).__init__(*args, **kwargs)
        self._exchange_name = exchange
        self._queue_name = queue
        if not no_bind:
            self.bind_queue_to_exchange(
                queue, exchange_name=exchange,
                routing_keys=routing_keys,
                route_only_to_queue=route_only_to_queue,
                auto_delete=auto_delete)

    def receive_messages(self):
        """
        Receive all messages in the queue and returns the list
        :returns a list of Message objects representing
                 all the messages in the queue
        """
        message_list = []
        while True:
            message = self.receive_message()
            if message is None:
                break
            message_list.append(message)
        return message_list

    def receive_message(self, runBeforeAck=None, noAck=False):
        """
        Receive a message from the queue
        :param runBeforeAck: A method to be invoked before sending the ACK back
                             to the message broker
        :param noAck: if True, no ACK is sent back to the message broker
        :return: the message itself as Message object
        """
        message = None
        channel = self._channel
        method_frame, header_frame, body = channel.basic_get(
            queue=self._queue_name)
        if method_frame is not None:
            try:
                t = json.loads(body.decode('UTF-8'))
            except:
                t = body
            message = Message(t, method_frame, header_frame)
            if runBeforeAck:
                runBeforeAck(message)
            if not noAck:
                channel.basic_ack(method_frame.delivery_tag)
        return message

    def consume_message(self, processor):
        """
        Receive a message from the queue
        :param processor: A method to be invoked for each message, it receives
        a message and the channel in parameter and should return True to
        acknowledge the message/ False  to avoid doing so.
        """
        channel = self._channel

        def wrapper(channel, method_frame, header_frame, body):
            t = json.loads(body.decode('UTF-8'))
            message = Message(t, method_frame, header_frame)
            try:
                rc = processor(message)
                if rc:
                    channel.basic_ack(method_frame.delivery_tag)
            except StopIteration as e:
                # This is the normal exit method, we should consume the last
                # message so that it does not stay
                # the queue
                channel.basic_ack(method_frame.delivery_tag)
                channel.stop_consuming()

        channel.basic_consume(wrapper, queue=self._queue_name)
        try:
            channel.start_consuming()
        except InterruptedProcessing:
            channel.stop_consuming()
        except Exception as e:
            channel.stop_consuming()
            raise e


class AdminHelper(QueueHelper):
    """
       Class used for the administration helpers
    """

    def __init__(self, exchange, *args, **kwargs):
        """
        Initialize props
        :param exchange_name: the exchange name used in the broker
        """
        super(AdminHelper, self).__init__(*args, **kwargs)
        self._exchange_name = exchange

    def change_messages(self, queue_name, message_changer,
                        dest_exchange=None):
        """
        Method used to change the payload, the header (priority,
        max_retry_count, etc) or the exchange of message already in the queue

        :param queue_name: the source queue for the messages to change
        :param message_changer: the function called to change the message. It
                                should returned a tuple of (modified, message).
                                If the modified is False, the message is not
                                modified and will be not be ACK, thus from
                                the message broker point of view the message
                                will remain the same. If modified is true,
                                the original message will be consumed and the
                                new one will be re-enqueued.
        :param dest_exchange: if it is not None, the message will be send to
                              this exchange instead of the original one.
        """
        # First we declare the listening and sending brokers.
        # If we what to change the messages in the same queue, the sender
        # exchange is the same as the receiving one
        receive_broker = Receiver(self._exchange_name, queue_name,
                                  channel=self._channel, no_bind=True)
        if dest_exchange:
            sender_broker = Sender(dest_exchange, channel=self._channel)
        else:
            sender_broker = Sender(self._exchange_name, channel=self._channel)
        messages = []
        # We need to look at all the messages in the queue
        while True:
            # We receive each message one by one, but we do not send neither
            # ACK nor NACK ( noAck = true)
            message = receive_broker.receive_message(noAck=True)
            if message is None:
                break
            # We perform the message filtering and change
            (modified, message) = message_changer(message)

            # The messages are added in a list of message tuples that include
            # delivery tag for ACK or NACK, if it was modified (thus NACK is
            # needed) and the new message if modified
            if modified:

                routing_key = message.method_frame.routing_key
                max_retry = message.header_frame.headers.get('max_retry', 3)
                priority = message.header_frame.priority
                logging.info("[Message %s] %s (P:%s) was changed!" % (
                    message.method_frame.delivery_tag,
                    message.body, priority))

                messages.append({
                    'delivery_tag': message.method_frame.delivery_tag,
                    'has_been_modified': modified,
                    'updated_message': {
                        'routing_key': routing_key,
                        'payload': message.body,
                        'priority': priority,
                        'max_retry': max_retry
                    }})

            else:
                logging.info("[Message %s] %s (P:%s) was not changed!" % (
                    message.method_frame.delivery_tag,
                    message.body, message.header_frame.priority))
                messages.append({
                    'delivery_tag': message.method_frame.delivery_tag,
                    'has_been_modified': modified,
                    'updated_message': None
                })
        # If the message was modified, send first the new message into the
        # correct exchange and then ack the old message. If no updates were
        # done, just send a NACK for the existing message to leave it in the
        # queue.
        for message in messages:
            try:
                if message['has_been_modified']:
                    updated_message = message['updated_message']
                    sender_broker.send_message(updated_message['routing_key'],
                                               updated_message['payload'],
                                               priority=updated_message[
                                                   'priority'],
                                               max_retry=updated_message[
                                                   'max_retry'])
                    logging.info(
                        "[Message-%s] Sending ACK!" % message['delivery_tag'])
                    self._channel.basic_ack(message['delivery_tag'])
                else:
                    logging.info(
                        "[Message-%s] Sending NACK!" % message['delivery_tag'])
                    self._channel.basic_nack(message['delivery_tag'])
            except Exception as e:
                logging.error(
                    "Error processing message %s : %s. Sending NACK!" % (
                        message['delivery_tag'], str(e)))
                self._channel.basic_nack(message['delivery_tag'])

    def list_messages_in_queue(self, queue_name):
        """
        Display the messages in the queue
        :param queue_name: the queue whose message should be displayed
        :return: a list of tuples with the message details
        """
        receive_broker = Receiver(self._exchange_name, queue_name,
                                  channel=self._channel,
                                  no_bind=True)
        display = []
        messages = []
        try:
            while True:
                message = receive_broker.receive_message(noAck=True)
                if message is None:
                    break
                messages.append(message.method_frame.delivery_tag)
                routing_key = message.method_frame.routing_key
                max_retry = message.header_frame.headers.get('max_retry', None)
                priority = message.header_frame.priority
                try:
                    expire_in = message.header_frame.expiration
                except:
                    expire_in = None
                uid = message.header_frame.headers.get('uid', None)
                display.append([routing_key, max_retry, priority, expire_in,
                                uid] +
                               [str(x) for x in message.body])
        except Exception as e:
            logging.error("Error gathering messages info: %s" % e)
        finally:
            for message in messages:
                self._channel.basic_nack(message)
        return display


class RPCServer(Receiver):
    """
     RPC Server that is waiting for messages from a RPC Client on a given
     exchange and it replaying to the client anonymous queue.
     """

    def __init__(self, exchange, queue, routing_keys=None, auto_delete=False,
                 *args, **kwargs):
        """

        :param exchange_name: the exchange name used in the broker
        :param queue: the queue on which needs to be bind to the exchange
        :param routing_keys: the routing keys that are used to route a message
                             from the exchange to the queue
        :param auto_delete: option to automatically delete the exchange if no
                            queues is bind to the exchange
        """
        super(RPCServer, self).__init__(exchange, queue, routing_keys,
                                        route_only_to_queue=True,
                                        auto_delete=auto_delete,
                                        *args, **kwargs)
        self.exchange = exchange
        self.auto_delete = auto_delete
        self.counter_messages = 0

    def receive_and_replay_rpc_message(self, processor, limit=None):
        """
        Method to consume a RPC message and to replay using the processor
        :param processor: the function used to process the consumed message
                          and generate the content of the replay message as
                          JSON message
        :param limit: the number of max message exchanges (receive and send)
        """
        def wrapper(message):
            self.counter_messages += 1
            replay_payload = json.dumps(processor(message))
            routing_key = message.header_frame.reply_to
            extra_properties = {
                'correlation_id': message.header_frame.correlation_id
            }
            self.basic_publish(self.exchange, routing_key, replay_payload,
                               priority=self.MAX_PRIORITY,
                               auto_delete=self.auto_delete,
                               extra_properties=extra_properties)
            if limit is not None and limit <= self.counter_messages:
                raise StopIteration
            return replay_payload is not None
        self.consume_message(wrapper)


class RPCClient(QueueHelper):
    """
    RPC Client that is sending messages to a RPC Server on a given exchange
    and it is waiting for the server replay on a anonymous queue.
    """

    def __init__(self, exchange, routing_keys=None, auto_delete=False,
                 *args, **kwargs):
        """
        :param exchange: the exchange name used in the broker
        :param routing_keys: the routing keys that are used to route a message
                             from the exchange to the queue
        :param auto_delete: option to automatically delete the exchange if no
                            queues is bind to the exchange
        """
        super(RPCClient, self).__init__(*args, **kwargs)
        self.auto_delete = auto_delete
        self.exchange_name = exchange
        self.corr_id = str(uuid.uuid4())
        self.queue_name = self.bind_queue_to_exchange(
            None, exchange_name=exchange,
            route_only_to_queue=True,
            routing_keys=routing_keys, auto_delete=auto_delete)
        self.counter_messages = 0

    def send_and_receive_rpc_message(self, routing_key, payload, processor,
                                     limit=None):
        """
        Method to send a RPC message and process the replay using the processor

        :param routing_keys: the routing keys that are used to route a message
                             from the exchange to the queue
        :param payload: the content of the message used in the RPC call
        :param processor: the function used to process the consumed message
        :param limit: the number of max message exchanges (send and receive)
        """
        body = json.dumps(payload)
        channel = self._channel
        extra_properties = {
            'correlation_id': self.corr_id,
            'reply_to': self.queue_name
        }

        def wrapper(channel, method_frame, header_frame, body):
            self.counter_messages += 1
            t = json.loads(body.decode('UTF-8'))
            message = Message(t, method_frame, header_frame)
            if self.corr_id != header_frame.correlation_id:
                channel.basic_ack(method_frame.delivery_tag)
            else:
                rc = processor(message)
                if rc:
                    channel.basic_ack(method_frame.delivery_tag)
                else:
                    channel.basic_nack(method_frame.delivery_tag)
            if limit is not None and limit <= self.counter_messages:
                channel.stop_consuming()

        channel.basic_consume(wrapper, queue=self.queue_name)
        self.basic_publish(self.exchange_name, routing_key, body,
                           priority=self.MAX_PRIORITY,
                           auto_delete=self.auto_delete,
                           extra_properties=extra_properties
                           )
        try:
            channel.start_consuming()
        except InterruptedProcessing:
            channel.stop_consuming()
        except Exception as e:
            channel.stop_consuming()
            raise e
