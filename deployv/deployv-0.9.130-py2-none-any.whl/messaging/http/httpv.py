# coding: utf-8
import json
import logging
from deployv.helpers import configuration_helper
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


_logger = logging.getLogger('deployv')


class BaseHttpConfiguration(object):
    """ As the configuration for the sender can be from various sources this will be the base
    class for that, so there is no need to rewrite or change any code from the sender.
    Just need to be sure that the parameters are fully filled

    :param host: Hostname or ip where the odoo instance is running
    :param token: Token used to authenticate with the controller that returns the messages
    """
    def __init__(self, host, token):
        self.host = host
        self.controller = '{host}/messages_queue'.format(host=self.host)
        self.headers = {'content-type': 'application/json',
                        'http-worker-token': token}


class FileHttpConfiguration(BaseHttpConfiguration):
    """ Reads the configuration from a ini-style file and builds the base configuration

    :param config_object: File or Config parser object where the configuration is going to be read
    """
    def __init__(self, config_object, status=False):
        if isinstance(config_object, ConfigParser):
            self.config = configuration_helper.DeployvConfig(worker_config=config_object)
        elif isinstance(config_object, configuration_helper.DeployvConfig):
            self.config = config_object
        else:
            raise ValueError('No valid config object provided')
        self._config_object = config_object
        host = self.config.http.get('orchest_host')
        token = self.config.http.get('token')
        super(FileHttpConfiguration, self).__init__(host, token)
        self.headers["is_status"] = json.dumps(status)

    def get_result_object(self):
        return FileHttpConfiguration(self._config_object)
