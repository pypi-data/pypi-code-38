'''Python logging module allowing you to log directly to Datadog via https.'''

# pylint: disable=too-many-arguments

from datetime import datetime
import logging
from logging import StreamHandler

import requests


class DatadogHttpHandler:
    '''Logging Handler class for sending logs to Datadog'''

    def __init__(self, api_key, service, host='', source='', tags=None,
                 logger_name='', level=None, raise_exception=False):

        self.api_key = api_key
        self.host = host
        self.source = source
        self.service = service
        self.tags = '' if tags is None else ','.join([f"{k}:{v}" for k, v in tags.items()])
        self.raise_exception = raise_exception
        self.setup_logger(logger_name, level)

    def setup_logger(self, logger_name, level):
        '''Create the DataDogHandler and assign to the logger.'''

        if level is None:
            level = logging.INFO

        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)
        self.logger.addHandler(self.setup_handler(level))

    def setup_handler(self, level):
        '''Send log messages to Datadog via http requests.'''

        handler = DataDogHandler(self.api_key, self.service, self.host, self.source,
            tags=self.tags, raise_exception=self.raise_exception)
        handler.setLevel(level)
        return handler


class DataDogHandler(StreamHandler):
    '''Send log messages to Datadog via http requests.'''

    def __init__(self, api_key, service, host, source, tags=None, raise_exception=False):
        StreamHandler.__init__(self)
        self.service = service
        self.host = host
        self.source = source
        if tags is None:
            self.tags = ''
        elif isinstance(tags, str):
            self.tags = tags
        else:
            self.tags = ','.join([f"{k}:{v}" for k, v in tags.items()])
        self.raise_exception = raise_exception
        self.headers = {'Content-Type': 'application/json'}
        self.url = f"https://http-intake.logs.datadoghq.com/v1/input/{api_key}"

    def emit(self, record):
        date = datetime.utcfromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        payload = {'message': self.format(record), 'level': record.levelname}
        payload['ddtags'] = self.tags + f",datetime:{date}" if self.tags else f"datetime:{date}"
        if self.service:
            payload['service'] = self.service
        if self.host:
            payload['hostname'] = self.host
        if self.source:
            payload['ddsource'] = self.source

        try:
            response = requests.post(self.url, json=payload, headers=self.headers)
            if response.status_code != 200 and self.raise_exception:
                raise Exception('Failed sending logs to Datadog')
        except requests.exceptions.RequestException as err:
            if self.raise_exception:
                raise Exception(err)
