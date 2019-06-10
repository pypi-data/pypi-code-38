#
# Module: consume
#
# Description: Command to start consumtion of a RabbitMQ queue by the specified Pytohn class.
#

def main():
    import logging
    import sys
    import os
    import argparse

    from rabbitmq_consume import Consumption, Consumer, parameter_utils, LOGGER

    LOGGER.setLevel(logging.DEBUG)
    
    parser = argparse.ArgumentParser(description='Generic Client to consume a RabbitMQ queue.')
    parser.add_argument('-d',
                        '--debug',
                        dest='DEBUG',
                        help='print out detail information to stdout.',
                        action='store_true',
                        default=False)
    parser.add_argument('--live_time',
                        dest='LIVE_TIME',
                        help='The number of seconds that this client should listen for new messages.' + 
                        ' After this time, and once any consumption that was in progress when it expired, the client with gracefully exit.',
                        type=float,
                        default=0.0)
    parser.add_argument('--log_file',
                        dest='LOG_FILE',
                        help='The file, as opposed to stdout, into which to write log messages')
    parser.add_argument('-i',
                        '--rabbit_ini',
                        dest='RABBITMQ_INI',
                        help='The path to the file contains the RabbitMQ INI file, the default is $HOME/.rabbitMQ.ini')
    parser.add_argument('-r',
                        '--restart',
                        dest='RESTART',
                        help='The number of seconds to wait before attempting to reconnect after a lost connection.' + 
                             ' Zero or less means no reconnect will be attempted.',
                        type=int,
                        default=0)
    parser.add_argument('-s',
                        '--ini_section',
                        dest='INI_SECTION',
                        help='The section of the INI file to use for this execution, the default is "RabbitMQ"',
                        default='RabbitMQ')
    parser.add_argument('-t',
                      '--transient',
                      dest='TRANSIENT',
                      help='true if the specified queue is transient rather than durable.',
                      action='store_true',
                      default=False)
    parser.add_argument('-w',
                        '--workers',
                        dest='WORKERS',
                        help='The maximum number of workers that will run in parallel',
                        type=int,
                        default=1)
    parser.add_argument('--wait_time',
                        dest='WAIT_TIME',
                        help='The number of seconds that this client should wait with no message after which the client with gracefully exit.',
                        type=float,
                        default=0.0)
    parser.add_argument('queue',
                        help='The rabbitMQ queue which this client should consume')
    parser.add_argument('consumption_class',
                        help='The module.class of the class that will consumer the messages of the queue')
    options = parser.parse_args()

    if options.DEBUG:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    if options.LOG_FILE:
        logging.basicConfig(filename=options.LOG_FILE,
                            level=log_level)
    else:
        logging.basicConfig(stream=sys.stdout,
                            level=log_level)

    parameters = parameter_utils.get_parameters(options.RABBITMQ_INI,
                                                options.INI_SECTION)
    consumer = Consumer(parameters,
                        options.queue,
                        target=options.consumption_class,
                        prefetch=options.WORKERS,
                        restart=options.RESTART,
                        durable=not options.TRANSIENT,
                        live_time=options.LIVE_TIME,
                        wait_time=options.WAIT_TIME)
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()
