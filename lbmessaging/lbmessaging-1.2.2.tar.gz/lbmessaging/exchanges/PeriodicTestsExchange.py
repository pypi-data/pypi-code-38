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
Module in charge of dealing with sending and receiving perioding tests messages
 for the PR2
'''

import json
from collections import namedtuple

from lbmessaging.exchanges.Common import Sender, Receiver, Message, \
    check_channel

__author__ = 'Chitic Stefan-Gabriel <stefan-gabriel.chitic@cern.ch>'

PERIODIC_TESTS_EXCHANGE = "topic.periodic_test"

# Utility class to ease the use of the messages
PeriodicTestMessage = namedtuple('PeriodicTestMessage',
                                 ['slot', 'build_id', 'project', 'platform',
                                  'group', 'env', 'runner', 'os_label'])


def _message_to_periodic(message):
    """ Trivial utility that converts the periodic test from JSON
    :param message: the message that needs to be converted to command
    :returns the converted rabbitMQ message to Message object with payload as
             command message
    """
    ret = None
    if message and message.body:
        try:
            msg = json.loads(message.body)
        except:
            msg = message.body
        if isinstance(msg, list):
            msg = msg[0]
        try:
            body = PeriodicTestMessage(**msg)
        except TypeError:
            # Add missing fields in the body to None
            for field in PeriodicTestMessage._fields:
                if not msg.get(field, None):
                    msg[field] = None
            body = PeriodicTestMessage(**msg)

        ret = Message(body, message.method_frame, message.header_frame)
    return ret


def command_retry_count(message):
    """ returns the retry_count kept in the headers
    :param message: the message whose retries needs to be counted
    :returns the value of the retry_count from the header
    """
    return message.header_frame.headers.get('max_retry', None)


class PeriodicTestsExchange(object):
    """
    Class in charge of dealing with messages to and from the PR insance
    """

    def __init__(self, channel, connection=None):
        """
        Specify the exchange to be used
        :param channel: a pikaBlockingConnection channel that should be used in
                        the broker
        :param connection: a pikaBlockingConnection that should be used in
                        the broker
        """
        self._exchange = PERIODIC_TESTS_EXCHANGE

        self._channel = check_channel(channel, connection)

    def request_test(self, slot, buildId, project, config, group, env,
                     runner, os_label, priority=10, max_retry=3,
                     expiration=None):
        """ Formats and sends the command as JSON
        :param command: the command that should be executed on a CVMFS instance
        :param arguments: the command arguments
        :param priority: the priority of the message
        :param max_retry: the max of retries in case of command failure on CVMFS
        :param expiration: the TTL of the message
        """
        params = [slot, project, config, group, env]
        routingKey = ".".join(params)
        body = {
            'slot': slot, 'build_id': buildId, 'project': project,
            'platform': config, 'group': group, 'env': env,
            'runner': runner, 'os_label': os_label}
        s = Sender(self._exchange, channel=self._channel)
        s.send_message(routingKey, body, priority,
                       expiration=expiration,
                       max_retry=max_retry)

    def get_test_to_run(self, queue_name, callback=None):
        """ Receive one message from the queue
        :param queue_name: the queue on which the broker listens for messages
        :param callback: function to run before sending the ack
        :returns the last message converted to Message object with payload as
                 command message
        """
        r = Receiver(self._exchange, queue_name,
                     channel=self._channel)
        message = r.receive_message(runBeforeAck=callback)
        return _message_to_periodic(message)

    def get_tests_to_run(self, queue_name, callback=None):
        """ Receive all message from the queue with callback
        :param queue_name: the queue on which the broker listens for messages
        :param callback: function to run before sending the ack
        :returns the last message converted to Message object with payload as
                 command message
        """
        test_list = []
        while True:
            message = self.get_test_to_run(queue_name, callback=callback)
            if not message:
                break
            test_list.append(message)
        return test_list
