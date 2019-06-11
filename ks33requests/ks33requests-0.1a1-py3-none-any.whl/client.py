import codecs
import io
import typing as t
from base64 import b64encode
from functools import partial
from hashlib import md5

import requests

from .auth import make_canonical_resource_string, generate_auth_headers
from .errors import raise_for_ks3_status
from .schemas import s3_sub


def get_s3obj(resp: requests.Response):
    return s3_sub.parseString(resp.content, True) if resp.content else None


class Client:

    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint: str = 'kss.ksyun.com',
            session: requests.Session = None,
            use_https: bool = True
    ):
        self._endpoint = endpoint.strip()
        self._access_key = access_key.strip()
        self._secret_key = secret_key.strip()
        self._session = session
        self._use_https = bool(use_https)

    def send(
            self,
            method: str = 'get',
            bucket_name: str = None,
            object_key: str = None,
            sub_resources: t.Union[str, t.List[str]] = None,
            data: t.Union[
                str, bytes, bytearray,
                t.Generator, t.BinaryIO, t.TextIO,
                io.BufferedIOBase, io.TextIOBase, io.BytesIO, io.StringIO
            ] = None,
            content_md5: str = None,
            headers: t.Dict[str, str] = None,
            params: t.Dict[str, str] = None,
            check_status: bool = True,
            session: requests.Session = None,
            **kwargs
    ) -> requests.Response:
        # http verb
        method = method.strip().lower()
        if method not in ('post', 'put'):
            data = None
            content_md5 = ''
        # Content MD5
        if content_md5 is None and data:
            if isinstance(data, str):
                content_md5 = b64encode(md5(data.encode()).digest()).decode()
            elif isinstance(data, (bytes, bytearray)):
                content_md5 = b64encode(md5(data).digest()).decode()
            elif isinstance(data, (t.BinaryIO, io.BufferedIOBase)):
                h = md5()
                for chunk in iter(partial(data.read, io.DEFAULT_BUFFER_SIZE), b''):
                    h.update(chunk)
                content_md5 = b64encode(h.digest()).decode()
                data.seek(0)
            elif isinstance(data, (t.TextIO, io.TextIOBase)):
                try:
                    code_name = data.encoding
                except AttributeError:
                    code_name = None
                if code_name:
                    fn_encode = partial(codecs.encode, encoding=code_name)
                else:
                    fn_encode = codecs.encode
                h = md5()
                for chunk in iter(partial(data.read, io.DEFAULT_BUFFER_SIZE), ''):
                    h.update(fn_encode(chunk))
                content_md5 = b64encode(h.digest()).decode()
                data.seek(0)
            else:
                content_md5 = ''
        # Signature
        canonical_resource = make_canonical_resource_string(bucket_name, object_key, sub_resources)
        auth_headers = generate_auth_headers(
            http_verb=method,
            access_key=self._access_key,
            secret_key=self._secret_key,
            canonical_resource=canonical_resource,
            content_md5=content_md5
        )
        # requests Session
        if not session:
            session = self._session
        if session:
            request = session.request
        else:
            request = requests.request
        # url
        url = '{}://{}{}'.format(
            'https' if self._use_https else 'http',
            self._endpoint, canonical_resource
        )
        # headers
        headers = headers or {}
        headers.update(auth_headers)
        if content_md5:
            headers['Content-MD5'] = content_md5
        # send http request
        resp = request(method, url=url, params=params or {}, headers=headers, data=data, **kwargs)
        # read response status code
        if check_status:
            raise_for_ks3_status(resp)
            resp.raise_for_status()
        # return
        setattr(resp, 's3obj', lambda: get_s3obj(resp))
        return resp

    @property
    def use_https(self) -> bool:
        return self._use_https

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @property
    def session(self) -> t.Optional[requests.Session]:
        return self._session
