#
# Module: consume
#
# Description: Command to start consumtion of a RabbitMQ queue by the specified Pytohn class.
#

import sys
import pika

import xml.etree.ElementTree as ET

from rabbitmq_consume import parameter_utils, LOGGER

def get_channel(parameters,
                task_queue):
    """
    Gets the channel that will be supplying the processing requests.
    """
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue = task_queue,
                          durable=True)
    return connection, channel

def default_message():
    return ET.ElementTree(ET.fromstring("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<default_message/>
"""))


def getIgnoreMessage(message, attr='action'):
    message.getroot().set(attr,'ignore')
    return message


def getStopListeningMessage(message, attr='action'):
    message.getroot().set(attr,'stop_listening')
    return message


def getStopWorkerMessage(message, attr='action'):
    message.getroot().set(attr,'stop_worker')
    return message


def main():
    import os
    import argparse

    parser = argparse.ArgumentParser(description='Command to inject simple messages into a RabbitMQ queue.')
    parser.add_argument('-d',
                      '--debug',
                      dest='DEBUG',
                      help='print out detail information to stdout.',
                      action='store_true',
                      default=False)
    parser.add_argument('-i',
                        '--rabbit_ini',
                        dest='RABBITMQ_INI',
                        help='The path to the file contains the RabbitMQ INI file, the default is $HOME/.rabbitMQ.ini')
    parser.add_argument('--ignore',
                        dest='IGNORE',
                        help='injects an "ignore" message onto the stream (this is the default behaviour, unless -l or -w are specified)',
                        action='store_true',
                        default=True)
    parser.add_argument('-l',
                        '--stop_listening',
                        dest='STOP_LISTENING',
                        help='injects a "stop listening" message onto the stream (overrides both --ignore and -w)',
                        action='store_true',
                        default=False)
    parser.add_argument('-s',
                        '--ini_section',
                        dest='INI_SECTION',
                        help='The section of the INI file to use for this execution, the default is "RabbitMQ"',
                        default='RabbitMQ')
    parser.add_argument('-w',
                        '--stop_worker',
                        dest='STOP_WORKER',
                        help='injects a "stop worker" message onto the stream, (overrides both --ignore)',
                        action='store_true',
                        default=False)
    parser.add_argument('queue',
                        help='The rabbitMQ queue which this client should consume',
                        default=None)
    options = parser.parse_args()

    if None == options.queue:
        LOGGER.critical("RabbitMQ queue must be supplied")
        sys.exit(-1)

    parameters = parameter_utils.get_parameters(options.RABBITMQ_INI,
                                                options.INI_SECTION)
    (connection, channel) = get_channel(parameters,
                                        options.queue)
    message = default_message();

    if options.STOP_LISTENING:
        message = getStopListeningMessage(message)
    elif options.STOP_WORKER:
        message = getStopWorkerMessage(message)
    else:
        message = getIgnoreMessage(message)
    channel.basic_publish(exchange = '',
                          routing_key = options.queue,
                          body = ET.tostring(message.getroot()),
                          properties=pika.BasicProperties(delivery_mode = 2,))

    connection.close()
