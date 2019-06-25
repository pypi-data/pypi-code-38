import logging
import requests
import threading
import time
import urlparse

from requests.exceptions import ConnectionError, ConnectTimeout, Timeout

from collabi.auth import Auth

class Accelerator(object):

    def __init__(self, config, rest, project):
        self._logger = logging.getLogger('unity.accelerator')
        self._collab_url = config.collab
        self._service_url = config['collab-accelerator']
        self._rest = rest
        self._org_id = project['org_id']
        self._project_id = project['guid']
        self._lock = threading.Lock()
        self._raise_on_connect_failures = False
        self._auth_ready = threading.Event()
        super(Accelerator, self).__init__()

    def discover(self, accelerator_url='discover'):
        self._reset()

        self._start(target=self._get_protected_token)

        if accelerator_url == 'discover':
            urls = self._urls()
        elif accelerator_url:
            self._raise_on_connect_failures = True
            parts = urlparse.urlsplit(accelerator_url)
            urls = [(parts.scheme+'://'+parts.netloc, parts.path)]
        else:
            urls = []

        threads = []
        for (base, path) in urls:
            self._logger.debug('Trying '+base+path)
            threads.append(self._start(target=self._try, args=(base, path)))

        for t in threads:
            t.join()

        if self._exception:
            raise self._exception

        return self.url

    def get_auth(self, default_auth):
        if self._service_url:
            # prefer use of protected web tokens
            self._auth_ready.wait()
            return Auth(self)

        return default_auth

    def get_authorization_header(self):
        return self._auth_header

    ######################################################################
    # private

    def _reset(self):
        self.url = self._collab_url
        self.discovered = False
        self._auth_header = None
        self._timeout = 0.5
        self._exception = None

    def _start(self, **kwargs):
        t = threading.Thread(**kwargs)
        t.daemon = True # kill on interrupt
        t.start()
        return t

    def _urls(self):
        if not self._service_url:
            return []

        resp = self._rest.request('get', 'v1/orgs/'+self._org_id+'/accelerators')
        json = resp.json()
        self._timeout = json['maximum_discovery_timeout_ms'] / 1000.0
        return [(a['url'], a['health_endpoint']) for a in json['accelerators'] if len(a['url']) > 0]

    def _try(self, base, path):
        try:
            resp = requests.get(base+path, timeout=self._timeout)
            resp.raise_for_status()
        except (ConnectionError, ConnectTimeout, Timeout) as exc:
            if self._raise_on_connect_failures:
                self._exception = exc
            else:
                self._logger.debug("Ignoring connection failure:", exc_info=True)
            return

        with self._lock:
            if not self.discovered:
                self.url = base
                self.discovered = True
                self._logger.info('Discovered accelerator: %s', self.url)

    def _get_protected_token(self):
        if not self._service_url:
            return

        # run forever (in a thread) to refresh the token for long-running uploads/downloads
        while True:
            resp = self._rest.request('get', 'v1/projects/'+self._project_id+'/get_token')
            json = resp.json()
            self._auth_header = json['protected_bearer_token']
            self._auth_ready.set()
            expires_in = json['expires_in']
            self._logger.debug('Protected bearer token expires in %d seconds', expires_in)
            time.sleep(expires_in - 300)
