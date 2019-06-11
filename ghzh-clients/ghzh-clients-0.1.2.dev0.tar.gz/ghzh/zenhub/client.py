import logging
import time
from datetime import datetime

import backoff
import requests

LOGS = logging.getLogger(__name__)


class ZenHubClient(object):
    def __init__(self, token, session=requests.Session):
        self.base_url = 'https://api.zenhub.io/p1'
        self.token = token
        self.session = session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Authentication-Token': self.token,
        })

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.Timeout, requests.exceptions.ConnectionError),
        max_tries=8
    )
    def request(self, method, url, **kwargs):
        LOGS.debug('%s %s with %s', method, url, kwargs)
        request_method = getattr(self.session, method)
        response = request_method(url, **kwargs)
        response.raise_for_status()
        self._deal_with_limits(response)

        return response.json()

    def post(self, url, **kwargs):
        """Sends a post request"""
        return self.request('post', url, **kwargs)

    def get(self, url, **kwargs):
        """Sends a get request"""
        return self.request('get', url, **kwargs)

    def _build_url(self, *args):
        parts = [self.base_url]

        parts.extend(args)
        parts = [str(p) for p in parts]

        return '/'.join(parts)

    def get_board(self, repo_id):
        url = self._build_url('repositories', repo_id, 'board')
        return self.get(url)

    def get_issue(self, repo_id, issue_number):
        url = self._build_url('repositories', repo_id, 'issues', issue_number)
        return self.get(url)

    def get_issue_events(self, repo_id, issue_number):
        url = self._build_url('repositories', repo_id, 'issues', issue_number, 'events',)
        return self.get(url)


    @staticmethod
    def _deal_with_limits(response):

        limit = used = wait_until = None

        if 'X-RateLimit-Limit' in response.headers:
            limit = int(response.headers['X-RateLimit-Limit'])

        if 'X-RateLimit-Used' in response.headers:
            used = int(response.headers['X-RateLimit-Used'])

        if 'X-RateLimit-Reset' in response.headers:
            wait_until = int(response.headers['X-RateLimit-Reset'])

        if wait_until:
            wait = (wait_until - datetime.now().timestamp())
            LOGS.info(
                f'Zenhub Request limit: {used} of {limit}, {wait} seconds to reset'
            )

        if limit and used:

            if limit - used <= 5:
                LOGS.warning(f'sleeping {wait} seconds')
                time.sleep(wait)
