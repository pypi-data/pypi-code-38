#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: zhangkai@cmcm.com
Last modified: 2018-01-04 20:16:00
'''
import asyncio
import cgi
import copy
import gzip
import io
import json
import logging
import math
import mimetypes
import os
import random
import re
import socket
import threading
import time
import urllib.parse
import uuid
import zlib
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from functools import reduce
from http.cookiejar import Cookie
from http.cookiejar import MozillaCookieJar
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urlunparse

import chardet
import pycurl
import requests
import yaml
from bs4 import BeautifulSoup
from requests.cookies import MockRequest
from requests.cookies import MockResponse
from requests.structures import CaseInsensitiveDict
from requests_toolbelt import MultipartEncoder
from requests_toolbelt import MultipartEncoderMonitor
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.wait import TimeoutException
from tornado import httputil
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.escape import native_str
from tornado.httpclient import HTTPClient
from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPResponse

from .utils import Dict
from .utils import DictWrapper
from .utils import property_wraps
from .utils import to_bytes
from .utils import to_str
from .utils import tqdm
logging.getLogger("requests").setLevel(logging.WARNING)
# requests.packages.urllib3.disable_warnings()


__all__ = ['Response', 'Request', 'Chrome']


def patch_connection_pool(num_pools=100, maxsize=100):
    from urllib3 import connectionpool, poolmanager

    class MyHTTPSConnectionPool(connectionpool.HTTPSConnectionPool):
        def __init__(self, *args, **kwargs):
            kwargs.update(dict(num_pools=num_pools, maxsize=maxsize))
            super(MyHTTPSConnectionPool, self).__init__(*args, **kwargs)
    poolmanager.pool_classes_by_scheme['https'] = MyHTTPSConnectionPool

    class MyHTTPConnectionPool(connectionpool.HTTPConnectionPool):
        def __init__(self, *args, **kwargs):
            kwargs.update(dict(num_pools=num_pools, maxsize=maxsize))
            super(MyHTTPConnectionPool, self).__init__(*args, **kwargs)
    poolmanager.pool_classes_by_scheme['http'] = MyHTTPConnectionPool


class MockHeaders(httputil.HTTPHeaders):

    def get_all(self, name, default=[]):
        return super().get_list(name)


class ChunkedMultipartEncoderMonitor(MultipartEncoderMonitor):

    def __init__(self, encoder, callback=None, chunk_size=1048576):
        super().__init__(encoder, callback)
        self.len = None
        self.chunk_size = chunk_size
        self.chunks = int(math.ceil(self.encoder.len / chunk_size))

    def __iter__(self):
        for i in range(self.chunks):
            string = self.encoder.read(self.chunk_size)
            self.bytes_read += len(string)
            self.callback(self)
            yield string


class Response:

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], HTTPResponse):
            self.url = args[0].effective_url
            for key in ['code', 'reason', 'headers', 'body', 'request', 'request_time']:
                setattr(self, key, getattr(args[0], key))
        else:
            kwargs.setdefault('body', b'')
            for key in ['code', 'reason', 'headers', 'body', 'request', 'request_time',
                        'url', 'cookies', 'encoding']:
                if key in kwargs:
                    setattr(self, key, kwargs[key])

        if hasattr(self, 'headers') and isinstance(self.headers, httputil.HTTPHeaders):
            self.cookies = {}
            if self.code == 200:
                for cookie in self.headers.get_list('Set-Cookie'):
                    sc = SimpleCookie(cookie)
                    self.cookies.update(dict(map(lambda x: (x[0], x[1].value), sc.items())))

    @staticmethod
    def _decompress_gzip(body):
        gz = gzip.GzipFile(fileobj=io.BytesIO(body), mode='rb')
        return gz.read()

    @staticmethod
    def _decompress_zlib(body):
        try:
            return zlib.decompress(body, -zlib.MAX_WBITS)
        except Exception:
            return zlib.decompress(body)

    @staticmethod
    def _decompress(headers, body):
        try:
            encoding = headers.get('Content-Encoding')
            if encoding and encoding.lower().find('gzip') >= 0:
                return Response._decompress_gzip(body)
            elif encoding and encoding.lower().find('deflate') >= 0:
                return Response._decompress_zlib(body)
            else:
                try:
                    return Response._decompress_gzip(body)
                except Exception:
                    return Response._decompress_zlib(body)
        except Exception:
            return body

    @property
    @property_wraps
    def encoding(self):
        encoding = None
        content_type = self.headers.get('content-type')
        if content_type and re.match('^text', content_type):
            content_type, params = cgi.parse_header(content_type)
            if 'charset' in params:
                encoding = params['charset'].strip("'\"")
            if encoding is None:
                encoding = chardet.detect(self.body)['encoding']
        return encoding

    @encoding.setter
    def encoding(self, value):
        self._encoding = value

    @property
    @property_wraps
    def text(self):
        if self.encoding:
            return self.body.decode(self.encoding)
        else:
            return self.body.decode()

    def json(self, **kwargs):
        return DictWrapper(json.loads(self.body, **kwargs))

    def soup(self, features='html5lib', **kwargs):
        return BeautifulSoup(self.body, features=features, **kwargs)

    def __repr__(self):
        return f'<Response [{self.code} {self.reason}]>'


class RequestMeta(type):

    _dnscache = {}

    @classmethod
    def _set_dnscache(cls):

        def _getaddrinfo(*args, **kwargs):
            if args in cls._dnscache:
                return cls._dnscache[args]
            else:
                cls._dnscache[args] = socket._getaddrinfo(*args, **kwargs)
                return cls._dnscache[args]

        if not hasattr(socket, '_getaddrinfo'):
            socket._getaddrinfo = socket.getaddrinfo
            socket.getaddrinfo = _getaddrinfo

    def __new__(cls, name, bases, attrs):
        cls._set_dnscache()
        return type.__new__(cls, name, bases, attrs)


class UserAgent:

    def __init__(self):
        filename = Path(__file__).absolute().parent / 'user_agent.json'
        with open(filename) as fp:
            self._user_agents = json.load(fp)
            self._total_agents = reduce(lambda x, y: x + y, self._user_agents.values())

    def __getattr__(self, key):
        if key in self._user_agents:
            return random.choice(self._user_agents[key])
        else:
            return random.choice(self._total_agents)


class BaseRequest(metaclass=RequestMeta):

    def __init__(self, **kwargs):
        '''
        files: dict, { key: filename or file descriptor }
        proxy: str, 'http://user:password@114.112.93.35:8080'
        '''
        self.proxy = kwargs.get('proxy')
        self.cookie = kwargs.get('cookie')
        self.cookies = kwargs.get('cookies', {})
        self.timeout = kwargs.get('timeout', 30)
        self.retry = kwargs.get('retry', 0)
        self.sleep = kwargs.get('sleep', 1)
        self.raise_error = kwargs.get('raise_error', False)
        self.progress = kwargs.get('progress', False)
        self.logger = logging.getLogger()
        self.ua = UserAgent()
        # if not self.logger.handlers:
        #     self.logger.addHandler(logging.NullHandler())

        self.headers = {
            'accept': '*/*',
            'connection': 'keep-alive',
            'accept-encoding': 'gzip,deflate,sdch',
            'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
        }
        if kwargs.get('headers'):
            self.headers.update(kwargs['headers'])

        if self.cookie:
            root = Path(self.cookie).parent
            if not root.exists():
                os.makedirs(root)

    def add_headers(self, headers):
        self.headers.update(headers)

    def add_cookies(self, cookies):
        self.cookies.update(cookies)

    def set_spider_ua(self):
        self.headers['user-agent'] = 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'

    def set_chrome_ua(self):
        self.headers['user-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'

    def set_mobile_ua(self):
        self.headers['user-agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1'

    def set_random_ua(self):
        self.headers['user-agent'] = self.ua.random

    def _prepare(self, url, **kwargs):
        url = to_str(url)
        kwargs = copy.copy(kwargs)
        headers = copy.copy(self.headers)
        headers.update(kwargs.get('headers', {}))
        cookies = copy.copy(self.cookies)
        cookies.update(kwargs.get('cookies', {}))

        kwargs.setdefault('progress', self.progress)
        kwargs.setdefault('proxy', self.proxy)
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('data', {})
        kwargs.setdefault('files', {})
        kwargs.setdefault('method', 'post' if kwargs['data'] or kwargs['files'] else 'get')
        kwargs['method'] = kwargs['method'].upper()
        if kwargs['method'] == 'HEAD':
            kwargs['progress'] = False
            kwargs.setdefault('allow_redirects', False)
        else:
            kwargs.setdefault('allow_redirects', True)

        if kwargs.pop('json', False):
            headers['content-type'] = 'application/json; charset=utf-8'
            if isinstance(kwargs['data'], dict):
                kwargs['data'] = json.dumps(kwargs['data'], ensure_ascii=False).encode('utf-8')

        if isinstance(kwargs['data'], dict):
            # headers['content-type'] = 'application/x-www-form-urlencoded'
            kwargs['data'] = list(kwargs['data'].items())

        if isinstance(kwargs['files'], dict):
            kwargs['files'] = list(kwargs['files'].items())

        for i, (key, value) in enumerate(kwargs['files']):
            if isinstance(value, (str, bytes, Path)):
                value = [str(value), open(value, 'rb')]
            elif isinstance(value, io.IOBase):
                value = [value.name if hasattr(value, 'name') else 'file', value]
            elif isinstance(value, tuple):
                value = list(value)
            if len(value) == 2:
                mtype = mimetypes.guess_type(value[0])[0] or 'application/octet-stream'
                value.append(mtype)
            value[0] = Path(value[0]).name
            kwargs['files'][i] = (key, tuple(value))

        if isinstance(kwargs.get('params'), dict):
            ret = urlparse(url)
            query = parse_qs(ret.query)
            query.update(kwargs['params'])
            url = urlunparse((ret.scheme, ret.netloc, ret.path, ret.params, urlencode(query, doseq=True), ret.fragment))
            kwargs.pop('params')

        if url.startswith('//'):
            url = 'http:' + url
        if kwargs.pop('autoreferer', False):
            ret = urllib.parse.urlparse(url)
            headers.update({
                'referer': f'{ret.scheme}://{ret.netloc}',
            })
        kwargs['headers'] = headers
        kwargs['cookies'] = cookies
        return url, kwargs

    def _request(self, url, **kwargs):
        pass

    def _retry(self, url, retry, kwargs, reason=None):
        try:
            if retry < 0:
                resp = Response(url=url, code=599, reason=str(reason))
            else:
                resp = self._request(url, **kwargs)
            for key, value in kwargs.get('files', []):
                if not value[1].closed:
                    value[1].close()
            return resp
        except Exception as e:
            self.logger.error(f'retry: {retry} {e}')
            time.sleep(self.sleep)
            return self._retry(url, retry - 1, kwargs, e)

    def request(self, url, **kwargs):
        url, kwargs = self._prepare(url, **kwargs)
        if self.raise_error:
            return self._request(url, **kwargs)
        else:
            return self._retry(url, self.retry, kwargs)

    def download(self, url, filename=None, shards=1, **kwargs):
        url, kwargs = self._prepare(url, **kwargs)
        kwargs['headers']['Range'] = 'bytes=0-0'
        resp = self._request(url, **kwargs)
        file_size = int(resp.headers['Content-Range'].split('/')[-1])

        filename = filename or Path(url).name
        if shards > 1:
            with open(filename, 'wb') as fp:
                fp.truncate(file_size)
            block_size = int(math.ceil(file_size / shards))
            with open(filename, 'rb+') as fp:
                lock = threading.Lock()
                func = partial(self._download_thread, url, fp, lock, file_size, block_size, kwargs)
                with ThreadPoolExecutor(shards) as executor:
                    executor.map(func, range(shards))
        else:
            first_byte = os.path.getsize(filename) if os.path.exists(filename) else 0
            kwargs['headers']['Range'] = f'bytes={first_byte}-{file_size}'
            self._download(url, filename, file_size, first_byte, kwargs)

    def get(self, url, **kwargs):
        return self.request(url, method='get', **kwargs)

    def post(self, url, **kwargs):
        return self.request(url, method='post', **kwargs)

    def head(self, url, **kwargs):
        return self.request(url, method='head', **kwargs)

    def put(self, url, **kwargs):
        return self.request(url, method='put', **kwargs)

    def delete(self, url, **kwargs):
        return self.request(url, method='delete', **kwargs)

    def options(self, url, **kwargs):
        return self.request(url, method='options', **kwargs)

    def patch(self, url, **kwargs):
        return self.request(url, method='patch', **kwargs)

    @staticmethod
    def multipart(headers={}, data={}, files={}):
        boundary = uuid.uuid4().hex
        headers['Content-Type'] = 'multipart/form-data; boundary=%s' % boundary
        boundary_bytes = boundary.encode()
        if isinstance(data, dict):
            data = data.items()
        if isinstance(files, dict):
            files = files.items()

        lines = []
        for key, value in data:
            lines.append(b'--%s' % boundary_bytes)
            lines.append(b'Content-Disposition: form-data; name="%s"\r\n' % to_bytes(key))
            lines.append(to_bytes(value))

        for key, value in files:
            lines.append(b'--%s' % boundary_bytes)
            lines.append(b'Content-Disposition: form-data; name="%s"; filename="%s"' %
                         (to_bytes(key), to_bytes(value[0])))
            lines.append(b'Content-Type: %s\r\n' % to_bytes(value[2]))
            value[1].seek(0)
            lines.append(value[1].read())

        lines.append(b'--%s--' % boundary_bytes)
        body = b'\r\n'.join(lines)
        return body


class Requests(BaseRequest):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = requests.session()
        self.session.cookies = MozillaCookieJar(filename=self.cookie)
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.load_cookie()

    def __del__(self):
        self.session.close()

    def load_cookie(self):
        if self.cookie and Path(self.cookie).exists():
            return self.session.cookies.load(ignore_discard=True, ignore_expires=True)
            requests.utils.cookiejar_from_dict(yaml.load(open(self.cookie)),
                                               cookiejar=self.session.cookies,
                                               overwrite=True)

    def save_cookie(self):
        if self.cookie:
            return self.session.cookies.save(ignore_discard=True, ignore_expires=True)
            yaml.dump(requests.utils.dict_from_cookiejar(self.session.cookies),
                      open(self.cookie, 'w'),
                      default_flow_style=False,
                      allow_unicode=True)

    def load_proxy(self):
        if self.proxy:
            self.session.proxies = {'http': self.proxy, 'https': self.proxy}

    def _prepare(self, url, **kwargs):
        url, kwargs = super()._prepare(url, **kwargs)
        kwargs.setdefault('verify', False)
        chunked = kwargs.pop('chunked', False)
        chunk_size = kwargs.pop('chunk_size', 1048576)

        proxy = kwargs.pop('proxy')
        if proxy:
            kwargs['proxies'] = {'http': proxy, 'https': proxy}

        progress = kwargs.pop('progress')
        if progress:
            if kwargs['method'] == 'GET':
                kwargs['stream'] = True
            else:
                data, files = kwargs.pop('data'), kwargs.pop('files')
                encoder = MultipartEncoder(fields=data + files)
                self._pbar = tqdm(unit='B', unit_scale=True, total=encoder.len)
                if chunked:
                    monitor = ChunkedMultipartEncoderMonitor(encoder, lambda m: self._pbar.update(m.bytes_read), chunk_size=chunk_size)
                else:
                    monitor = MultipartEncoderMonitor(encoder, lambda m: self._pbar.update(m.bytes_read))
                kwargs['headers'].update({'Content-Type': encoder.content_type})
                kwargs['data'] = monitor

        return url, kwargs

    def _download_thread(self, url, fp, lock, file_size, block_size, kwargs, thread_id):
        kwargs = copy.copy(kwargs)
        start = block_size * thread_id
        end = min(block_size * (thread_id + 1), file_size) - 1
        pbar = tqdm(total=end - start + 1, unit='B', unit_scale=True, desc=f'{thread_id}')
        kwargs['headers']['Range'] = f'bytes={start}-{end}'
        kwargs['stream'] = True
        method = kwargs.pop('method', 'GET')
        resp = self.session.request(method, url, **kwargs)
        for chunk in resp.iter_content(chunk_size=4096):
            if chunk:
                with lock:
                    fp.seek(start)
                    fp.write(chunk)
                    start += len(chunk)
                    pbar.update(incr=len(chunk))
        pbar.close()

    def _download(self, url, filename, file_size, first_byte, kwargs):
        kwargs['stream'] = True
        pbar = tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True)
        method = kwargs.pop('method', 'GET')
        resp = self.session.request(method, url, **kwargs)
        with open(filename, 'ab') as fp:
            for chunk in resp.iter_content(chunk_size=4096):
                if chunk:
                    fp.write(chunk)
                    pbar.update(incr=len(chunk))
        pbar.close()

    def _request(self, url, **kwargs):
        request_cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
        request_cookies.update(kwargs['cookies'])
        method = kwargs.pop('method', 'GET')
        resp = self.session.request(method, url, **kwargs)
        if hasattr(self, '_pbar'):
            self._pbar.close()
        if kwargs.get('stream') and method == 'GET':
            pbar = tqdm(total=int(resp.headers.get('Content-Length', -1)), unit='B', unit_scale=True)
            content = b''
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    content += chunk
                    pbar.update(incr=len(chunk))
            pbar.close()
        else:
            content = resp.content

        kwargs['method'] = method
        response_cookies = requests.utils.dict_from_cookiejar(resp.cookies)
        self.save_cookie()
        request = Dict(
            url=url,
            headers=kwargs['headers'],
            data=kwargs['data'],
            cookies=request_cookies
        )
        response = Response(
            url=resp.url,
            encoding=resp.encoding,
            headers=resp.headers,
            body=content,
            code=resp.status_code,
            cookies=response_cookies,
            reason=resp.reason,
            request=request,
            request_time=resp.elapsed.microseconds / 1e6,
        )
        return response


class Pycurl(BaseRequest):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.b = io.BytesIO()
        self.h = io.BytesIO()
        self.c = pycurl.Curl()
        self.c.setopt(pycurl.HEADERFUNCTION, self.h.write)
        self.c.setopt(pycurl.WRITEFUNCTION, self.b.write)
        self.cookiejar = MozillaCookieJar(self.cookie)

    def __del__(self):
        self.b.close()
        self.h.close()
        self.c.close()

    def load_cookie(self, curl):
        if self.cookie:
            curl.setopt(pycurl.COOKIEFILE, self.cookie)
            curl.setopt(pycurl.COOKIEJAR, self.cookie)
            if Path(self.cookie).exists():
                self.cookiejar.load(ignore_discard=True, ignore_expires=True)
        else:
            curl.setopt(pycurl.COOKIEFILE, '')

    def save_cookie(self, resp):
        req = MockRequest(resp.request)
        res = MockResponse(MockHeaders(resp.headers))
        self.cookiejar.extract_cookies(res, req)
        if self.cookie:
            self.cookiejar.save(ignore_discard=True, ignore_expires=True)

    def load_proxy(self, curl, proxy):
        if proxy:
            if proxy.startswith('socks4'):
                curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
            elif proxy.startswith('socks5'):
                curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
            else:
                curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
            curl.setopt(pycurl.PROXY, proxy)
            # credentials = httputil.encode_username_password(proxy['username'], proxy['password'])
            # curl.setopt(pycurl.PROXYUSERPWD, credentials)
        else:
            curl.setopt(pycurl.PROXY, '')
            curl.unsetopt(pycurl.PROXYUSERPWD)

    def _curl_setup(self, curl, url, headers={}, cookies={}, data=[], files=[], **kwargs):
        curl.setopt(pycurl.NOSIGNAL, 1)
        curl.setopt(pycurl.MAXREDIRS, 5)
        curl.setopt(pycurl.HEADER, 0)
        curl.setopt(pycurl.VERBOSE, 0)
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl.setopt(pycurl.SSL_VERIFYHOST, 0)
        curl.setopt(pycurl.AUTOREFERER, 1)
        curl.setopt(pycurl.URL, native_str(url))

        curl.setopt(pycurl.TRANSFER_ENCODING, int(kwargs.get('chunked', False)))
        curl.setopt(pycurl.FOLLOWLOCATION, kwargs['allow_redirects'])
        curl.setopt(pycurl.CONNECTTIMEOUT, kwargs['timeout'])
        curl.setopt(pycurl.TIMEOUT, kwargs['timeout'])
        self.load_cookie(curl)
        self.load_proxy(curl, kwargs.get('proxy'))

        curl_options = {
            "GET": pycurl.HTTPGET,
            "POST": pycurl.POST,
            "PUT": pycurl.UPLOAD,
            "HEAD": pycurl.NOBODY,
        }
        custom_methods = set(["DELETE", "OPTIONS", "PATCH"])
        for o in curl_options.values():
            curl.setopt(o, False)
        if kwargs['method'] in curl_options:
            curl.unsetopt(pycurl.CUSTOMREQUEST)
            curl.setopt(curl_options[kwargs['method']], True)
        elif kwargs['method'] in custom_methods:
            curl.setopt(pycurl.CUSTOMREQUEST, kwargs['method'])
        else:
            raise KeyError('unknown method ' + kwargs['method'])

        if files:
            data = self.multipart(headers, data, files)
        elif isinstance(data, (dict, list, tuple)):
            data = urlencode(data)

        if kwargs['method'] in ("POST", "PATCH", "PUT"):
            request_buffer = io.BytesIO(to_bytes(data))
            curl.setopt(pycurl.READFUNCTION, request_buffer.read)
            curl.setopt(pycurl.IOCTLFUNCTION, lambda cmd: cmd == curl.IOCMD_RESTARTREAD and request_buffer.seek(0))
            if kwargs['method'] == 'POST':
                curl.setopt(pycurl.POSTFIELDSIZE, len(data))
            else:
                curl.setopt(pycurl.UPLOAD, True)
                curl.setopt(pycurl.INFILESIZE, len(data))
            '''
            fields = []
            if isinstance(data, collections.Iterable):
                for k, v in data:
                    fields.append((k, (pycurl.FORM_CONTENTS, to_str(v))))
            if isinstance(files, collections.Iterable):
                for k, v in files:
                    fields.append((k, (pycurl.FORM_FILE, to_str(v[1].name))))
            curl.setopt(pycurl.HTTPPOST, fields)
            curl.setopt(pycurl.POSTFIELDS, data)
            '''

        for key in ['Expect', 'Pragma']:
            headers.setdefault(key, '')

        header_list = [f'{to_str(k)}:{to_str(v)}' for k, v in headers.items()]
        curl.setopt(pycurl.HTTPHEADER, header_list)

        if cookies:
            cookie_str = ';'.join([f'{to_str(k)}={to_str(v)}' for k, v in cookies.items()])
            curl.setopt(pycurl.COOKIE, cookie_str)

        if kwargs['progress']:
            curl.setopt(pycurl.NOPROGRESS, 0)
            self._pbar = tqdm(unit='B', unit_scale=True)

            def update(a, b, c, d):
                download_total, downloaded, upload_total, uploaded = int(a), int(b), int(c), int(d)
                if kwargs['method'] == 'GET' and (self._pbar.total is None or download_total >= self._pbar.total):
                    self._pbar.update(downloaded, download_total)
                elif (self._pbar.total is None or upload_total >= self._pbar.total):
                    self._pbar.update(uploaded, upload_total)

            curl.setopt(pycurl.PROGRESSFUNCTION, update)
        else:
            curl.setopt(pycurl.NOPROGRESS, 1)
            curl.setopt(pycurl.PROGRESSFUNCTION, lambda: None)

    def _parse_cookies(self, curl):
        cookie_list = curl.getinfo_raw(pycurl.INFO_COOKIELIST)
        for item in cookie_list:
            domain, domain_specified, path, path_specified, expires, name, value = item.decode().split("\t")
            cookie = Cookie(0, name, value, None, False, domain,
                            domain_specified.lower() == "true",
                            domain.startswith("."), path,
                            path_specified.lower() == "true",
                            False, expires, False, None, None, {})
            self.cookiejar.set_cookie(cookie)

    def _parse_headers(self, text):
        reason = 'OK'
        headers = httputil.HTTPHeaders()
        for header_line in text.split(b'\r\n'):
            header_line = native_str(header_line.decode('latin1'))
            header_line = header_line.rstrip()
            if header_line.startswith("HTTP/"):
                headers.clear()
                try:
                    _, _, reason = httputil.parse_response_start_line(header_line)
                    header_line = "X-Http-Reason: %s" % reason
                except httputil.HTTPInputError:
                    continue
            if header_line:
                headers.parse_line(header_line)
        return reason, headers

    def _download_thread(self, url, fp, lock, file_size, block_size, kwargs, thread_id):
        kwargs = copy.copy(kwargs)
        start = block_size * thread_id
        end = min(block_size * (thread_id + 1), file_size) - 1
        kwargs['headers']['Range'] = f'bytes={start}-{end}'
        pbar = tqdm(total=end - start + 1, unit='B', unit_scale=True, desc=f'{thread_id}')
        with lock:
            fp.seek(start)
            self._curl_setup(self.c, url, **kwargs)
            self.c.setopt(pycurl.WRITEFUNCTION, fp.write)
            self.c.setopt(pycurl.NOPROGRESS, 0)
            self.c.setopt(pycurl.PROGRESSFUNCTION, lambda a, b, c, d: pbar.update(int(b), int(a)))
            self.c.perform()
            pbar.close()

    def _download(self, url, filename, file_size, first_byte, kwargs):
        self._curl_setup(self.c, url, **kwargs)
        fp = open(filename, 'ab')
        self.c.setopt(pycurl.WRITEFUNCTION, fp.write)
        self.c.setopt(pycurl.NOPROGRESS, 0)
        pbar = tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True)
        self.c.setopt(pycurl.PROGRESSFUNCTION, lambda a, b, c, d: pbar.update(first_byte + int(b), int(a)))
        self.c.perform()
        fp.close()
        pbar.close()

    def _request(self, url, **kwargs):
        self._curl_setup(self.c, url, **kwargs)
        request_cookies = requests.utils.dict_from_cookiejar(self.cookiejar)
        request_cookies.update(kwargs['cookies'])
        self.c.perform()
        if hasattr(self, '_pbar'):
            self._pbar.close()

        reason, headers = self._parse_headers(self.h.getvalue())
        request_time = self.c.getinfo(pycurl.TOTAL_TIME)
        body = self.b.getvalue()
        code = self.c.getinfo(pycurl.HTTP_CODE)
        url = self.c.getinfo(pycurl.EFFECTIVE_URL)

        self.b.seek(0)
        self.b.truncate()
        self.h.seek(0)
        self.h.truncate()

        request = Dict(
            url=url,
            headers=kwargs.get('headers'),
            data=kwargs.get('data'),
            cookies=request_cookies,
        )
        resp = Response(
            url=url,
            code=code,
            reason=reason,
            headers=headers,
            body=Response._decompress(headers, body),
            request=request,
            request_time=request_time,
        )
        return resp


class TornadoClient(Pycurl):

    def __init__(self, max_clients=50, **kwargs):
        ''' This cannot handle 301/302 redirection cookies
        '''
        super().__init__(**kwargs)
        self.http = CurlAsyncHTTPClient(max_clients=max_clients)

    async def _retry(self, url, retry, kwargs):
        try:
            return await self._request(url, **kwargs)
        except Exception as e:
            self.logger.error(f'retry: {retry} {e}')
            if retry <= 0:
                return Response(url=url, code=e.code, reason=str(e))
            await asyncio.sleep(self.sleep)
            return await self._retry(url, retry - 1, kwargs)

    async def _request(self, url, **kwargs):
        url, kwargs = self._prepare(url, **kwargs)
        curl_callback = partial(self._curl_setup, url=url, **kwargs)

        resp = Response(await self.http.fetch(url,
                                              prepare_curl_callback=curl_callback,
                                              raise_error=self.raise_error))
        if hasattr(self, '_pbar'):
            self._pbar.close()
        self.save_cookie(resp)
        return resp

    async def download(self, url, filename=None, shards=1, **kwargs):
        filename = filename or Path(url).name
        if shards > 1:
            url, kwargs = self._prepare(url, **kwargs)
            kwargs['headers']['Range'] = 'bytes=0-0'
            resp = await self._request(url, **kwargs)
            file_size = int(resp.headers['Content-Range'].split('/')[-1])
            block_size = int(math.ceil(file_size / shards))
            futures = []
            for i in range(shards):
                start = block_size * i
                end = min(block_size * (i + 1), file_size) - 1
                _kwargs = copy.deepcopy(kwargs)
                _kwargs['headers']['Range'] = f'bytes={start}-{end}'
                futures.append(self._request(url, **_kwargs))
            resps = await asyncio.gather(*futures)
            with open(filename, 'wb') as fp:
                for resp in resps:
                    fp.write(resp.body)
        else:
            resp = await self._request(url, **kwargs)
            with open(filename, 'wb') as fp:
                fp.write(resp.body)


class Fetcher(BaseRequest):

    def __init__(self, phantomjs_proxy='http://localhost:25555', **kwargs):
        super().__init__(**kwargs)
        self.phantomjs_proxy = phantomjs_proxy
        self.default_options = {
            'method': 'GET',
            'headers': self.headers,
            'follow_redirects': True,
            'use_gzip': True,
            'timeout': self.timeout,
        }
        self.http = HTTPClient(max_clients=20)

    def parse_option(self, url, **kwargs):
        fetch = copy.copy(self.default_options)
        fetch['method'] = kwargs['method'].upper()
        fetch['url'] = url
        fetch['data'] = kwargs['data']
        fetch['headers'] = kwargs['headers']
        fetch['timeout'] = kwargs['timeout']
        js_script = kwargs.get('js_script')
        if js_script:
            fetch['js_script'] = js_script
            fetch['js_run_at'] = kwargs.get('js_run_at', 'document-end')
        fetch['load_images'] = kwargs.get('load_images', False)
        return fetch

    def _request(self, url, **kwargs):
        url, kwargs = self._prepare(url, **kwargs)
        body = self.parse_option(url, **kwargs)
        config = {
            'follow_redirects': False,
            'connect_timeout': body['timeout'],
            'request_timeout': body['timeout'] + 1,
        }
        request = HTTPRequest(self.phantomjs_proxy, method='POST', body=json.dumps(body), **config)
        resp = self.http.fetch(request)

        request = Dict(
            url=url,
            headers=kwargs.get('headers'),
            data=kwargs.get('data'),
        )
        doc = Dict(json.loads(resp.body))
        response = Response(
            url=url,
            headers=doc.headers,
            body=doc.content,
            code=doc.status_code,
            cookies=doc.cookies,
            encoding=Response._get_encoding(doc.headers, doc.body),
            reason=doc.error or 'OK',
        )
        return response


class Chrome(webdriver.Chrome):

    def __init__(self, path=None, headless=False, proxy=None, mobile=False):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        options.add_argument('disable-infobars')
        options.add_argument('lang=zh_CN.UTF-8')
        options.add_argument('profile-directory=Default')
        # options.add_extension(Path(__file__).parent / 'Adblock-Plus_v1.8.12.crx')
        # options.add_argument('disable-gpu')
        # options.add_argument('no-sandbox')
        # options.add_argument(f"user-data-dir={Path('~/Library/Application Support/Google/Chrome').expanduser()}")
        if path:
            options.add_argument(f'user-data-dir={path}')
        if headless:
            options.add_argument('headless')
        if proxy:
            options.add_argument(f'proxy-server={proxy}')
        if mobile:
            options.add_argument('user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"')
        d = DesiredCapabilities.CHROME
        d['loggingPrefs'] = {'performance': 'ALL'}
        super().__init__(chrome_options=options, desired_capabilities=d)
        self.wait = WebDriverWait(self, 30)

    def get(self, url):
        super().get(url)
        request = Dict()
        resp = Dict()
        for item in self.get_log('performance'):
            message = Dict(json.loads(item['message'])).message
            if message['method'] == 'Network.responseReceived' and \
                    message.params.response.url.strip('/') == url.strip('/'):
                resp.headers = CaseInsensitiveDict(message.params.response.headers)
                request.headers = CaseInsensitiveDict(message.params.response.requestHeaders)
                code = message.params.response.status

        if resp.headers:
            cookie = SimpleCookie()
            cookie.load(request.headers.get('Cookie', ''))
            request.cookies = dict([(x[0], x[1].value) for x in cookie.items()])
            cookie = SimpleCookie()
            cookie.load(resp.headers.get('Set-Cookie', ''))
            resp.cookies = dict([(x[0], x[1].value) for x in cookie.items()])
            return Response(url=url, request=request, code=code, body=self.page_source,
                            headers=resp.headers, cookies=resp.cookies, reason='OK')

    def find(self, selector):
        try:
            elements = self.wait.until(lambda driver: driver.find_elements_by_css_selector(selector))
            return elements[0] if len(elements) == 1 else elements
        except TimeoutException:
            return None

    def check(self, selector):
        try:
            WebDriverWait(self, 1).until(lambda driver: driver.find_element_by_css_selector(selector))
            return True
        except TimeoutException:
            return False

    def scroll(self, page=1, sleep=1):
        for i in range(page):
            self.execute_script('scrollTo(0, document.body.scrollHeight)')
            if i < page - 1:
                time.sleep(sleep)

    def soup(self):
        return BeautifulSoup(self.page_source, 'html5lib')


def Request(lib='requests', **kwargs):
    module = {
        'pycurl': Pycurl,
        'requests': Requests,
        'fetcher': Fetcher,
        'tornado': TornadoClient,
    }
    return module[lib](**kwargs)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    http = Request(lib='tornado')

    async def fetch():
        await http.get('https://www.baidu.com')
    loop.run_until_complete(fetch())
