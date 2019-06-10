# Common methods for loading RabbitMQ parameters/

from __future__ import print_function

DEFAULT_INI_FILE = '.rabbitMQ.ini'
DEFAULT_INI_SECTION = 'RabbitMQ'

import pika
import sys

from rabbitmq_consume import LOGGER

def _read_config(file,
                 section):
    """Reads the config.ini file for login information, host, etc."""

    try:
        from ConfigParser import SafeConfigParser as ConfigParser
    except ModuleNotFoundError as e:
        from configparser import ConfigParser
    import os
    import sys

    config_parser = ConfigParser()
    if None == file:
        if 'HOME' in os.environ:
            filepath = os.path.join(os.environ['HOME'],
                                    DEFAULT_INI_FILE)
        else:
            LOGGER.critical('Can not find INI file "' + DEFAULT_INI_FILE + '", make sure HOME envar is defined')
            sys.exit(1)
    else:
        filepath = file
    if not os.path.exists(filepath):
        LOGGER.critical('Can not find INI file "' + filepath + '"')
        sys.exit(1)

    config_parser.read(filepath)
    config = {}
    for option in config_parser.options(section):
        try:
            if option == 'channel_max' or \
               option == 'connection_attempts' or \
               option == 'frame_max' or \
               option == 'heartbeat_interval' or \
               option == 'retry_delay' or \
               option == 'socket_timeout':
                config[option] = config_parser.getint(section,
                                                      option)
            elif option == 'backpressure_detection' or \
                 option == 'ssl':
                config[option] = config_parser.getboolean(section,
                                                          option)
            else: 
                config[option] = config_parser.get(section,
                                                   option)
        except:
            config[option] = None

    return config


def get_parameters(file,
                   section):
    """
    Read the config file and creates an appropriate ConnectionParameter instance
    """
    config = _read_config(file,
                          section)
    username = config.pop('username', None)
    password = config.pop('password', None)
    credentials = pika.PlainCredentials(username,
                                        password)
    config['credentials'] = credentials
    if 'port' not in config:
        config['port']=5672
    if 'heartbeat_interval' not in config:
        config['heartbeat_interval']=580
    parameters = pika.ConnectionParameters()
    parameters.host = config['host']
    parameters.credentials = credentials
    parameters.virtual_host = config['virtual_host']
    return parameters
