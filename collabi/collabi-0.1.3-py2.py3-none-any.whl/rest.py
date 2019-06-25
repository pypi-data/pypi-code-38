"""Provides common request functionality around REST calls to Unity services.
"""
import os
import re
import logging
import binascii
import grequests

from requests import Request
from collabi import __version__ as collabi_version

class Rest(object):
    REQ_ID_HDR = 'X-Request-Id'

    def __init__(self, session, endpoint, auth=None, verify=True, user_agent=None):
        self._logger = logging.getLogger('unity.rest')
        self._session = session
        self._base_url = endpoint + '/api/'
        self._auth = auth
        self._verify = verify
        self._user_agent = user_agent if user_agent else 'UnityRest/'+collabi_version
        self._async_reqs = []

    def request(self, method, path, **kwargs):
        kwargs['headers'] = self._headers(kwargs.get('headers', {}))
        if 'auth' not in kwargs: kwargs['auth'] = self._auth
        url = self._base_url + path
        req = Request(method.upper(), url, **kwargs)
        prep = req.prepare()
        self._log_with_headers(prep)
        resp = self._session.send(prep, verify=self._verify)
        self._log_with_headers(resp)
        resp.raise_for_status()
        return resp

    def async_request_raw(self, method, url, **kwargs):
        kwargs['headers'] = self._headers(kwargs.get('headers', {}),
                                          content_type='application/octet-stream')
        if 'session' not in kwargs: kwargs['session'] = self._session
        if 'verify' not in kwargs: kwargs['verify'] = self._verify
        if 'stream' not in kwargs: kwargs['stream'] = True
        req = grequests.AsyncRequest(method.upper(), url, **kwargs)
        self._async_reqs.append(req)
        return req

    def async_request(self, method, path, **kwargs):
        kwargs['headers'] = self._headers(kwargs.get('headers', {}))
        if 'auth' not in kwargs: kwargs['auth'] = self._auth
        url = self._base_url + path
        return self.async_request_raw(method, url, **kwargs)

    # returns an iterator of responses (as they are fulfilled)
    def async_request_flush(self, concurrency):
        reqs = self._async_reqs
        self._async_reqs = []
        return grequests.imap(reqs, size=concurrency, exception_handler=self._exception_callback)

    def _exception_callback(self, req, ex):
        self._logger.error('Request failed for '+req.url+': '+str(ex))
        self._logger.error(req.traceback)

    def _headers(self, override_hdrs, content_type='application/json'):
        hdrs = self._session.headers.copy()
        hdrs.update({
            'User-Agent': self._user_agent,
            'Accept': 'application/json'
        })
        req_name = re.sub(r'[^\d\w]+', '', self._user_agent.split('/', 1)[0])
        hdrs[Rest.REQ_ID_HDR] = req_name + binascii.b2a_hex(os.urandom(15))
        if content_type: hdrs['Content-Type'] = content_type
        hdrs.update(override_hdrs)
        return hdrs

    def _log_with_headers(self, http):
        if self._logger.getEffectiveLevel() > logging.DEBUG: return
        body = []
        if hasattr(http, 'method'):
            message = http.method + ' ' + http.url
            direction = '> '
            if http.body and len(http.body) > 0:
                body = [direction + b for b in ([''] + http.body.split('\n'))]
        else:
            message = 'Response from ' + http.url
            direction = '< '
        hdrs = [direction + '%s: %s' % (k,v) for (k,v) in http.headers.iteritems()]
        self._logger.debug(message+'\n'+'\n'.join(hdrs + body))
