import time


import requests
import requests_cache
from requests.exceptions import ConnectionError
from fake_useragent import FakeUserAgent

from scrapgo import settings
from scrapgo.lib.time.time import get_random_second
from scrapgo.utils.shortcuts import filter_params

from .helper import retry


class CachedRequests(object):
    USER_AGENT_NAME = settings.USER_AGENT_NAME  # default to 'chrome'
    HEADERS = None
    REQUEST_DELAY = settings.REQUEST_DELAY
    CACHE_NAME = settings.CACHE_NAME
    CACHE_BACKEND = settings.CACHE_BACKEND
    CACHE_EXPIRATION = settings.CACHE_EXPIRATION
    CACHE_METHODS = settings.CACHE_METHODS
    REQUEST_LOGGING = True
    RETRY_INTERVAL_SECONDS = settings.RETRY_INTERVAL_SECONDS

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headers = {
            'User-Agent': getattr(FakeUserAgent(), self.USER_AGENT_NAME)
        }
        if self.HEADERS:
            self.headers.update(self.HEADERS)

        self.requests = requests_cache.CachedSession(
            cache_name=self.CACHE_NAME,
            backend=self.CACHE_BACKEND,
            expire_after=self.CACHE_EXPIRATION,
            allowable_methods=self.CACHE_METHODS
        )

    def get_request_log(self, url, from_cache, delay, payloads=None, **kwargs):
        if from_cache is False:
            if payloads is not None:
                log = f"POST {url} (delay:{delay}s, payloads:{payloads})"
            else:
                log = f"GET {url} (delay:{delay}s)"
        else:
            if payloads is not None:
                log = f"POST {url} From Cache (payloads:{payloads})"
            else:
                log = f"GET {url} From Cache"
        return log

    def _refresh_cache(self, url, method='get'):
        if method == 'get':
            if self.requests.cache.has_url(url):
                self.requests.cache.delete_url(url)
        else:
            self.requests.remove_expired_responses()

    def _delay_control(self, response):
        if response.from_cache is False:
            delay = self._get_delay()
            time.sleep(delay)
            return delay

    def _get_delay(self):
        if isinstance(self.REQUEST_DELAY, (tuple, list,)) and len(self.REQUEST_DELAY) == 2:
            return get_random_second(*self.REQUEST_DELAY)
        return self.REQUEST_DELAY

    def _validate_response(self, response):
        if not response.content:
            self.requests.cache.delete_url(url)
            print('Warning: {} has no content!'.format(response.url))

    @retry
    def _get(self, url, headers=None, refresh=False, fields=None, **kwargs):
        headers = headers or self.get_header()
        url = filter_params(url, fields)
        if refresh:
            self._refresh_cache(url)

        r = self.requests.get(url, headers=headers)
        r.raise_for_status()
        delay = self._delay_control(r)
        if self.REQUEST_LOGGING is True:
            log = self.get_request_log(url, r.from_cache, delay, **kwargs)
            print(log)
        self._validate_response(r)
        return r

    @retry
    def _post(self, url, payload, headers=None, refresh=True, fields=None, **kwargs):
        headers = headers or self.headers
        url = filter_params(url, fields)
        r = self.requests.post(url, data=payload, headers=headers)
        r.raise_for_status()
        delay = self._delay_control(r)
        if self.REQUEST_LOGGING is True:
            log = self.get_request_log(url, r.from_cache, delay, len(payload), **kwargs)
            print(log)
        return r

    def get_header(self):
        return dict(self.headers)

    def set_header(self, headers):
        self.headers = headers
