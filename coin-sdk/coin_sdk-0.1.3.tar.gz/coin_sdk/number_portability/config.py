import logging
import sys


class Config:
    def __init__(self, base_uri, consumer_name, private_key_file, hmac_secret, number_of_retries=3, backoff_period=1):
        self._base_uri = base_uri
        self._consumer_name = consumer_name
        self._private_key_file = private_key_file
        self._hmac_secret = hmac_secret
        self._number_of_retries = number_of_retries
        self._backoff_period = backoff_period

    @property
    def base_uri(self):
        return self._base_uri

    @property
    def api_url(self):
        return self._base_uri + '/number-portability/v1/dossiers'

    @property
    def sse_url(self):
        return self.api_url + '/events'

    @property
    def consumer_name(self):
        return self._consumer_name

    @property
    def private_key_file(self):
        return self._private_key_file

    @property
    def hmac_secret(self):
        return self._hmac_secret

    @property
    def number_of_retries(self):
        return self._number_of_retries

    @property
    def backoff_period(self):
        return self._backoff_period


_format = '%(asctime)s - %(name)-8s - %(levelname)s - %(message)s'


def set_logging(format=_format, level=logging.ERROR, stream=sys.stdout):
    logging.basicConfig(format=format, level=level, stream=stream)
