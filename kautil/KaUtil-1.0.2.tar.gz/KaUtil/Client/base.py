import chardet
from lxml import etree
import requests
from requests.cookies import cookiejar_from_dict
from typing import Union, Dict, Optional
from KaUtil.Client.setting import BASE_HEADER
import pymysql
from pymysql.cursors import SSCursor
from readability import Document
import io
from traceback import print_exc
import json

__all__ = ['Request', 'MySqlClient']


class RequestException(Exception):
    def __init__(self, error: str, status_code: int=500):
        self.status_code = status_code
        self.error = error


class Request(object):
    def __init__(self, url, method='GET', timeout=5, *args, **kwargs):
        self.url = url
        self.method = method
        self.timeout = timeout
        self.args = args
        self.kwargs = kwargs
        self.session = kwargs.setdefault('session', None)
        self._doc = None
        self._response = None

    def set_session(self, **kwargs):
        if self.session:
            headers = kwargs.get('headers')
            cookies = kwargs.get('cookies')
            if headers:
                self.session.headers.update(headers)
            if cookies:
                cookies = cookiejar_from_dict(cookies)
                self.session.cookies = cookies
            del self.kwargs['session']

    @property
    def response(self):
        if self._response:
            return self._response
        resp = self._process_request()
        self._response = resp
        return resp

    def _process_request(self):
        _requests = self.session if self.session else requests

        r = {
            'GET': _requests.get,
            'POST': _requests.post,
        }
        _headers: Optional[Dict[str, str]] = self.kwargs.get('headers')
        _cookies: Optional[Dict[str, str]] = self.kwargs.get('cookies')

        if 'session' in self.kwargs:
            self.kwargs.pop('session')
        if _headers:
            BASE_HEADER.update(_headers)
        self.kwargs['headers'] = BASE_HEADER
        if _cookies:
            self.kwargs['cookies'] = cookiejar_from_dict(_cookies)
        try:
            response = r.get(self.method)(
                self.url, timeout=self.timeout, *self.args, **self.kwargs)
            if 'Connection' in response.headers.keys():
                del response.headers['Connection']
            if response.status_code != 200:
                raise RequestException(error=response.text, status_code=response.status_code)
        except Exception as e:
            response = self.err_response(text=self._error_format())
        response = self.html_code(response)
        return response

    def _error_format(self) -> str:
        with io.StringIO() as sio:
            print_exc(file=sio)
            error = sio.getvalue()
        data: Dict[str, str] = {
            'url': self.url,
            'method': self.method,
            'params': self.kwargs.setdefault('data', None),
            'error': error,
        }
        return json.dumps(data, ensure_ascii=False)

    def err_response(self, text: str):
        class Response:
            error = True
            url = self.url
            status_code = 500

            def __init__(self, text: str=''):
                self.text = text

            def __repr__(self):
                return 'Bad requests'

        return Response(text)

    @classmethod
    def html_code(cls, response):
        if hasattr(response, 'error'):
            return response
        _content_encoding = chardet.detect(response.content)
        CHARSET = 'utf8'
        charset = _content_encoding.get('encoding', CHARSET)
        response.encoding = charset
        return response

    @property
    def text(self) -> str:
        return self.response.text

    @property
    def html(self) -> Union[None, str]:
        if hasattr(self.response, 'error'):
            return None
        text = self.response.text.replace('?xml', 'head')
        try:
            return etree.HTML(text)
        except:
            return None

    @property
    def doc(self):
        if not self._doc:
            self._doc = Document(self.text)
        return self._doc

    @property
    def doc_title(self) -> str:
        return self.doc.title()

    @property
    def doc_summary(self) -> str:
        return ''.join(self.summary_html.xpath('//text()'))

    @property
    def summary_html(self):
        return etree.fromstring(self.doc.summary())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        del self


class MySqlClient(object):
    def __init__(self, connet_msg=None):
        if connet_msg:
            self.db = pymysql.connect(**connet_msg)
        else:
            self.db = pymysql.connect()

    def __enter__(self):
        return self.db.cursor(SSCursor)

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.db.commit()
        self.db.close()