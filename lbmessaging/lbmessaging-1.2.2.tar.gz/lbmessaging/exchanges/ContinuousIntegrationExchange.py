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
Module in charge of dealing with sending and receiving nightlies information to
RabbitMQ when a project is done: slot, build id, platform and project
'''

import json
from collections import namedtuple

from lbmessaging.exchanges.Common import Sender, Receiver, Message,\
    check_channel
from lbmessaging.services.Common import ExposedIn


__author__ = 'Stefan-Gabriel Chitic <stefan-gabriel.chitic@cern.ch>'


PHYS_CI_EXCHANGE = "topic.build_ready"
ENVKIT_CI_EXCHANGE = "topic.tar_ready"


# Utility class to ease the use of the messages
PhysBuildReadyMessage = namedtuple('PhysBuildReadyMessage',
                                   sorted(['slot', 'build_id',
                                           'platform', 'project',
                                           'priority',
                                           'deployment']),
                                   rename=True)
EnvkitReadyMessage = namedtuple('EnvkitReadyMessage',
                                sorted(['flavour', 'platform', 'version',
                                        'url']),
                                rename=True)


def _message_to_exchange_type_message(message, type=PhysBuildReadyMessage):
    """ Trivial utility that converts the command from JSON
    :param message: the message that needs to be converted to command
    :param type: the type of message to which the payload is converted.
                 Default is PhysBuildReadyMessage
    :returns the converted rabbitMQ message to Message object with payload as
             ContinuousIntegrationMessage """
    ret = None
    if message and message.body:
        try:
            msg = json.loads(message.body)
        except:
            msg = message.body
        if isinstance(msg, list):
            msg = msg[0]
        try:
            body = type(**msg)
        except TypeError:
            # Add missing fields in the body to None
            for field in type._fields:
                if not msg.get(field, None):
                    msg[field] = None
            body = type(**msg)

        ret = Message(body, message.method_frame, message.header_frame)
    return ret


def message_retry_count(message):
    """ returns the retry_count kepts in the headers
    :param message: the message whose retries needs to be counted
    :returns the value of the retry_count from the header
    """
    return message.header_frame.headers.get('max_retry', None)


@ExposedIn('LbCIService', mapping={
        'send_build_ready': 'send_build_ready',
        'consume_build_ready': 'consume_build_ready',
        'receive_build_ready': 'receive_build_ready',
        'send_envkit_ready': 'send_envkit_ready',
        'consume_envkit_ready': 'consume_envkit_ready',
        'receive_envkit_ready': 'receive_envkit_ready',
    })
@ExposedIn('CVMFSNightliesService', mapping={
        'send_build_ready': 'send_build_ready',
        'receive_build_ready': 'receive_build_ready',
    })
class ContinuousIntegrationExchange(object):
    """
    Class in charge of dealing with messages to and from the
    ContinuousIntegration Exchange
    """

    def __init__(self, channel, connection=None):
        """
        :param channel: a pikaBlockingConnection channel that should be used in
                        the broker
        :param connection: a pikaBlockingConnection that should be used in
                        the broker"""
        self._channel = check_channel(channel, connection)

    def send_envkit_ready(self, flavour, platform, version, url=None):
        """ Formats and sends the information for a tar that was build as JSON
        :param flavour: The flavour of the env_kit (prod/dev)
        :param platform: The platform of the env_kit
        :param version: the version of the env_kit
        :param url: Optional url to override the source of the env_kit
        :return:
        :param priority: the priority of the message
        """
        message = {
            'flavour': flavour,
            'platform': platform,
            'version': version,
            'url': url
        }
        routing_key = "%s.%s.%s.%s" % (flavour, platform, version, url)
        self._send_continuous_integration(ENVKIT_CI_EXCHANGE, message,
                                          routing_key)

    def receive_envkit_ready(self, queue_name):
        """ Receive one tar ready message from the queue
        :param queue_name: the queue on which the broker listens for messages
        :returns the last message converted to Message object with payload as
                 envkitReadyMessage
        """
        return self._receive_continuous_integration(
            queue_name, ENVKIT_CI_EXCHANGE, message_type=
            EnvkitReadyMessage)

    def receive_all_envkit_ready(self, queue_name):
        """ Receive all tar ready messages from the queue
        :param queue_name: the queue on which the broker listens for messages
        :returns a list of all the messages converted to Message object with
                 payload as EnvkitReadyMessage
        """
        return self._receive_continuous_integration_all(
            queue_name, ENVKIT_CI_EXCHANGE,
            message_type=EnvkitReadyMessage)

    def consume_envkit_ready(self, message_processor, queue_name):
        """ Invokes the message_processor on all messages received on
        envkit_CI_EXCHANGE.
         The message processor should:
         - take (message, channel) as arguments
         - return True to ack the messages

         It can interrupt the loop by calling channel.stop_consuming()

         BEWARE: This is not appropriate for long running calls as the
         acknowledgement of the message is done after the processor call.

        :param message_processor: the function that should be called when a new
                                  message is consumed
        :param queue_name: the queue on which the broker listens for messages
        """
        self._consume_continuous_integration(message_processor, queue_name,
                                             ENVKIT_CI_EXCHANGE,
                                             message_type=EnvkitReadyMessage)

    def send_build_ready(self, slot, build_id, platform, project,
                         deployment=[], priority=None):
        """ Formats and sends the a pair of slot-build_id-platform-project
         that was build as JSON
        :param slot: the slot name that was build
        :param build_id: the build id of the slot that was build
        :param platform: the platform of the slot that was build
        :param project: the project of the slot that was build
        :param priority: the priority of the message
        """
        message = {
            'slot': slot,
            'build_id': build_id,
            'project': project,
            'platform': platform,
            'deployment': deployment,
            'priority': priority
        }
        routing_key = "%s.%s.%s.%s" % (slot, build_id, project, platform)
        self._send_continuous_integration(PHYS_CI_EXCHANGE, message,
                                          routing_key)

    def receive_build_ready(self, queue_name):
        """ Receive one build ready message from the queue
        :param queue_name: the queue on which the broker listens for messages
        :returns the last message converted to Message object with payload as
                 PhysBuildReadyMessage
        """
        return self._receive_continuous_integration(queue_name,
                                                    PHYS_CI_EXCHANGE)

    def receive_all_build_ready(self, queue_name):
        """ Receive all build ready messages from the queue
        :param queue_name: the queue on which the broker listens for messages
        :returns a list of all the messages converted to Message object with
                 payload as PhysBuildReadyMessage
        """
        return self._receive_continuous_integration_all(queue_name,
                                                        PHYS_CI_EXCHANGE)

    def consume_build_ready(self, message_processor, queue_name):
        """ Invokes the message_processor on all messages received on
        envkit_CI_EXCHANGE.
         The message processor should:
         - take (message, channel) as arguments
         - return True to ack the messages

         It can interrupt the loop by calling channel.stop_consuming()

         BEWARE: This is not appropriate for long running calls as the
         acknowledgement of the message is done after the processor call.

        :param message_processor: the function that should be called when a new
                                  message is consumed
        :param queue_name: the queue on which the broker listens for messages
        """
        self._consume_continuous_integration(message_processor, queue_name,
                                             PHYS_CI_EXCHANGE)

    def _send_continuous_integration(self, exchange, message, routing_key):
        """ Sends the a continuous integration object metainfo that was build
        as JSON
        :param exchange: the exchange that should be used
        :param message: the actual message that is sent
        :param routing_key: the routing key of the message
         """
        s = Sender(exchange,
                   channel=self._channel)
        s.send_message(routing_key, message, priority=0,
                       max_retry=0)

    def _receive_continuous_integration(self, queue_name, exchange,
                                        message_type=PhysBuildReadyMessage):
        """ Receive one message from the queue
        :param queue_name: the queue on which the broker listens for messages
        :param exchange: the exchange that should be used to map the queue to
        :param type: the type of message to which the payload is converted.
                 Default is PhysBuildReadyMessage
        :returns the last message converted to Message object with payload as
                 message_type
        """
        r = Receiver(exchange, queue_name,
                     channel=self._channel)
        message = r.receive_message(runBeforeAck=None)
        return _message_to_exchange_type_message(message, type=message_type)

    def _receive_continuous_integration_all(self, queue_name, exchange,
                                            message_type=PhysBuildReadyMessage):
        """ Receive all messages from the queue
        :param queue_name: the queue on which the broker listens for messages
        :param exchange: the exchange that should be used to map the queue to
        :param type: the type of message to which the payload is converted.
                 Default is PhysBuildReadyMessage
        :returns a list of all the messages converted to Message object with
                 payload as message_type
        """
        r = Receiver(exchange, queue_name,
                     channel=self._channel)
        msglist = r.receive_messages()
        return [_message_to_exchange_type_message(m, type=message_type)
                for m in msglist]

    def _consume_continuous_integration(self, message_processor, queue_name,
                                        exchange,
                                        message_type=PhysBuildReadyMessage):
        """ Invokes the message_processor on all messages received.
         The message processor should:
         - take (message, channel) as arguments
         - return True to ack the messages

         It can interrupt the loop by calling channel.stop_consuming()

         BEWARE: This is not appropriate for long running calls as the
         acknowledgement of the message is done after the processor call.

        :param message_processor: the function that should be called when a new
                                  message is consumed
        :param queue_name: the queue on which the broker listens for messages
        :param exchange: the exchange that should be used to map the queue to
        :param type: the type of message to which the payload is converted.
                 Default is PhysBuildReadyMessage
         """
        c = Receiver(exchange, queue_name,
                     channel=self._channel)
        # Adding wrapper to convert the messages before processing

        def convert_and_process(message):
            return message_processor(
                _message_to_exchange_type_message(message, type=message_type))
        c.consume_message(convert_and_process)
