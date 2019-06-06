import os
import json
import hashlib
import requests

from ssl import SSLError


class pycritsFetchError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class pycrits(object):
    _API_VERSION       = '/api/v1/'
    _CAMPAIGNS         = 'campaigns/'
    _INDICATORS        = 'indicators/'
    _SAMPLES           = 'samples/'

    def __init__(self, host, username, api_key, logger):
        self._session = requests.Session()
        self._session.params = {'username': username, 'api_key': api_key}
        self._session.verify = True
        self._session.proxies = False

        self._base_url = host + self._API_VERSION
        self._host = host
        self._retries = 0
        self._logger = logger

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        self._base_url = value + self._API_VERSION

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    @property
    def verify(self):
        return self._session.verify

    # Verify can take True, False or path to .pem file (to verify the server's cert)
    @verify.setter
    def verify(self, value):
        self._session.verify = value

    @property
    def retries(self):
        return self._retries

    @retries.setter
    def retries(self, value):
        self._retries = value

    @property
    def proxies(self):
        return self._session.proxies

    @proxies.setter
    def proxies(self, value):
        self._session.proxies = value

    def post_url(self, url, data, files):
            try:
                return self._session.post(url, data=data, files=files)
            except SSLError:
                try:
                    return self._session.post(url, data=data, files=files)
                except SSLError:
                    self._logger.error("***Unable to add indicator because of SSLError!!!***")

    # Used for posting.
    def _post(self, url, params, files=None):
        url = self._base_url + url
        resp = self.post_url(url, data=params, files=files)
        if resp.status_code != 200:
            raise pycritsFetchError("Response code: %s" % resp.status_code)

        try:
            results = json.loads(resp.text)
        except:
            raise pycritsFetchError("Unable to load JSON.")

        return results

    # Helper to handle file uploads.
    # Take either a path to a file on disk or a file object.
    # If given both, the filepath will take precedence.
    # If we don't have a filename get it from filepath or use
    # the md5 of the data from file_obj.
    def _get_file_data(self, file_obj, filepath, filename):
        if not file_obj and not filepath:
            return None

        if filepath:
            file_obj = open(filepath, 'rb')

        if not filename:
            # Try to generate it from filepath if we have that.
            if filepath:
              filename = os.path.basename(filepath)

            # If someone does something crazy like filepath='/tmp/'
            # then basename() returns ''. Use MD5 in that case.
            if not filename:
                filename = hashlib.md5(file_obj.read()).hexdigest()
                file_obj.seek(0)

        return {'filedata': (filename, file_obj)}

    # Add objects to CRITs.

    def add_campaign(self, name, params):
        params['name'] = name
        return self._post(self._CAMPAIGNS, params)

    def add_indicator(self, type_, value, source, params):
        params['type'] = type_
        params['value'] = value
        params['source'] = source
        return self._post(self._INDICATORS, params)

    def add_sample(self, type_, source, params, file_obj=None, filepath=None,
                   filename=None):
        files = self._get_file_data(file_obj, filepath, filename)

        # Set filename so it is honored for metadata uploads too.
        params['upload_type'] = type_
        params['filename'] = filename
        params['source'] = source
        return self._post(self._SAMPLES, params, files=files)
