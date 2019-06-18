# coding: utf-8
import logging
import simplejson as json
import requests
import time
from deployv.messaging.http.httpv import BaseHttpConfiguration
from deployv.messaging.basemsg import BasicMessage

_logger = logging.getLogger('deployv')


class HttpSenderV(object):
    """ A simple rabbit mq interface just pass the config parameters
    and send the message

    """
    def __init__(self, sender_configuration, sender_id):
        """
        """
        assert isinstance(sender_configuration, BaseHttpConfiguration)
        self._config = sender_configuration.get_result_object()
        self._id = sender_id

    def send_message(self, message):
        retry = 0
        if isinstance(message, BasicMessage):
            data = message.get_message_str()
        else:
            data = json.dumps(message)
        while retry <= 3:
            try:
                res = requests.post(self._config.controller, data=data,
                                    headers=self._config.headers)
                if res.status_code != 200:
                    _logger.error('Error while sending a message: %s', res.status_code)
            except requests.exceptions.ConnectionError:
                retry += 1
                _logger.error('Failed to connect with the instance, retrying %s', retry)
                time.sleep(5)
            break
