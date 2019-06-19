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
Module in charge of dealing with sending and receiving commands for the
/cvmfs/lhcbdev.cern.ch
'''

import datetime
from collections import namedtuple

from lbmessaging.exchanges.Common import Sender, Receiver, Message, \
    check_channel

__author__ = 'Ben Couturier <ben.couturier@cern.ch>'


# Utility class to ease the use of the messages
CommandMessage = namedtuple('CommandBody',
                            ['command', 'arguments', 'trigger_date'])


def _message_to_command(message):
    """ Trivial utility that converts the command from JSON
    :param message: the message that needs to be converted to command
    :returns the converted rabbitMQ message to Message object with payload as
             command message
    """
    ret = None
    if message and message.body:
        body = CommandMessage(*message.body)
        ret = Message(body, message.method_frame, message.header_frame)
    return ret


def command_retry_count(command):
    """ returns the retry_count kept in the headers
    :param command: the command message whose retries needs to be counted
    :returns the value of the retry_count from the header
    """
    return command.header_frame.headers.get('max_retry', None)


class CommandExchange(object):
    """
    Class in charge of dealing with messages to and from the CvmfsDevExchange
    """

    SUFFIX_RETRY = 'retry'
    SUFFIX_ERROR = 'error'

    def __init__(self, channel, exchange, connection=None):
        """
        Specify the exchange to be used
        :param channel: a pikaBlockingConnection channel that should be used in
                        the broker
        :param exchange: the main exchange name used in the broker

        :param error_exchange: the error exchange that should be used to push
                               a command that failed i.e. the retry_count == 0
        :param connection: a pikaBlockingConnection that should be used in
                        the broker
        :param retry_exchange: the exchange use to retry a message sent
        """
        self._channel = check_channel(channel, connection)
        self._exchange = exchange

    def send_command(self, command, arguments, priority=10, max_retry=3,
                     expiration=None):
        """ Formats and sends the command as JSON
        :param command: the command that should be executed on a CVMFS instance
        :param arguments: the command arguments
        :param priority: the priority of the message
        :param max_retry: the max of retries in case of command failure on CVMFS
        :param expiration: the TTL of the message
        """
        now = datetime.datetime.utcnow().isoformat()
        s = Sender(self._exchange, channel=self._channel)
        s.send_message(command, (command, arguments, now), priority,
                       expiration=expiration,
                       max_retry=max_retry)

    def receive_command(self, queue_name, exchange=None):
        """ Receive one message from the queue
        :param queue_name: the queue on which the broker listens for messages
        :param exchange: the exchange name used in the broker
        :returns the last message converted to Message object with payload as
                 command message
        """
        if exchange is None:
            exchange = self._exchange
        r = Receiver(exchange, queue_name,
                     channel=self._channel)
        message = r.receive_message()
        return _message_to_command(message)

    def receive_command_error(self, queue_name):
        """ Receive one error message from the queue
        :param queue_name: the queue on which the broker listens for messages
        :returns the last message converted to Message object with payload as
                 command message
        """
        error_exchange = '%s.%s' % (queue_name, self.SUFFIX_ERROR)
        error_queue = '%s%s' % (queue_name, self.SUFFIX_ERROR)
        return self.receive_command(error_queue, exchange=error_exchange)

    def receive_all(self, queue_name, exchange=None):
        """ Receive all messages from the queue
        :param queue_name: the queue on which the broker listens for messages
        :param exchange: the exchange name used in the broker
        :returns a list of all the messages converted to Message object with
                 payload as command message
        """
        if exchange is None:
            exchange = self._exchange
        r = Receiver(exchange, queue_name,
                     channel=self._channel)
        msglist = r.receive_messages()
        return [_message_to_command(m) for m in msglist]

    def receive_command_error_all(self, queue_name):
        """ Receive all error messages from the queue
        :param queue_name: the queue on which the broker listens for messages
        :returns the last message converted to Message object with payload as
                 command message
        """
        error_exchange = '%s.%s' % (queue_name, self.SUFFIX_ERROR)
        error_queue = '%s%s' % (queue_name, self.SUFFIX_ERROR)
        return self.receive_all(error_queue, exchange=error_exchange)

    def handle_processing_error(self, command, queue_name=None):
        """ Handles the processing error, i.e. resend if retry_count > 0,
        forward to the error queue otherwise
        :param queue_name: the queue on which the broker listens for messages
        :param command: the command that should be executed on a CVMFS instance
        """

        # In order to keep the retrocompatibility and have the code
        # still working. In the past, the signature was (self, command)
        # without queue_name. If an old client calls this function will
        #  end with an exception concerning the number of arguments.
        # Most probably this exception will be try...catched and logged.
        # This particular exception will be more explicit for the developer
        # in the logs.

        if queue_name is None:
            raise Exception("Please specify the queue name on which the "
                            "receiver listens on")
        # Create first the queues and the exchanges

        # Retry is attached to the same queue_name
        retry_exchange = '%s.%s' % (queue_name, self.SUFFIX_RETRY)
        _ = Receiver(retry_exchange, queue_name, channel=self._channel)

        # Error is attached to the a particular error queue
        error_exchange = '%s.%s' % (queue_name, self.SUFFIX_ERROR)
        error_queue = '%s%s' % (queue_name, self.SUFFIX_ERROR)
        _ = Receiver(error_exchange, error_queue, channel=self._channel)

        retry_count = command_retry_count(command)
        if retry_count > 0:
            s = Sender(retry_exchange, channel=self._channel)
            s.resend_message(command)
        else:
            s = Sender(error_exchange, channel=self._channel)
            s.resend_message(command, keep_retry_count=True)
