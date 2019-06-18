# coding: utf-8
import logging
import requests
from requests import exceptions
import time
import simplejson as json


_logger = logging.getLogger('deployv')


class HttpReceiverV(object):

    def __init__(self, listener_configuration, worker_id):
        self.active = True
        self.worker_id = worker_id
        self._config = listener_configuration

    def run(self, callback_funct):
        self.active = True
        while self.active:
            self.get_message(callback_funct)
            time.sleep(5)

    def get_message(self, callback):
        data = {'params': {'worker_id': self.worker_id}}
        try:
            res = requests.get(self._config.controller, data=json.dumps(data),
                               headers=self._config.headers)
        except exceptions.ConnectionError:
            _logger.error('Failed to connect with the instance')
            return False
        if res.status_code != 200:
            _logger.error(
                'Failed to connect to the host Error code: %s', res.status_code
            )
            return False
        msg = res.json()
        if not msg.get('result'):
            return False
        if msg.get('result').get('error'):
            _logger.error('Error retrieving a message: %s %s',
                          msg.get('result').get('error').get('code'),
                          msg.get('result').get('error').get('message'))
            return False
        callback(msg.get('result'))

    def stop(self):
        _logger.info('Stopping')
        self.active = False
        _logger.info('Stopped')
