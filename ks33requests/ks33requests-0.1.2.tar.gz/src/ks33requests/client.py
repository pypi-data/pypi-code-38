import codecs
import io
import os
import sys
from base64 import b64encode
from functools import partial
from hashlib import md5
from pathlib import Path
from typing import Dict, List, Union, Generator, Optional, BinaryIO, TextIO

import requests

from .auth import make_canonical_resource_string, generate_auth_headers
from .errors import raise_for_ks3_status
from .schemas import s3_sub
from .utils import b64md5_bytes


def get_s3obj(resp: requests.Response):
    return s3_sub.parseString(resp.content, True) if resp.content else None


class Client:

    def __init__(
            self,
            access_key: str = None,
            secret_key: str = None,
            endpoint: str = 'kss.ksyun.com',
            session: requests.Session = None,
            use_https: bool = True
    ):
        self._endpoint = endpoint.strip()
        self._access_key = (access_key or '').strip() or os.environ.get('KSYUN_ACCESS_KEY', '')
        self._secret_key = (secret_key or '').strip() or os.environ.get('KSYUN_SECRET_KEY', '')
        self._session = session
        self._use_https = bool(use_https)

    def send(
            self,
            method: str = 'get',
            bucket_name: str = None,
            object_key: str = None,
            sub_resources: Union[str, List[str]] = None,
            data: Union[
                bytes, bytearray, str, Generator, Path,
                BinaryIO, TextIO,
                io.BytesIO, io.StringIO,
                io.BufferedIOBase, io.TextIOBase
            ] = None,
            encoding=None,
            content_md5: str = None,
            headers: Dict[str, str] = None,
            params: Dict[str, str] = None,
            check_status: bool = True,
            session: requests.Session = None,
            **kwargs
    ) -> requests.Response:
        # http verb
        method = method.strip().lower()
        if method in ('post', 'put'):
            # 预处理 data 编码问题，顺便进行b64md5计算
            # text 转 bytes
            if isinstance(data, str):
                data = data.encode(encoding=encoding or sys.getdefaultencoding())
            # text io 转 bytes io
            elif isinstance(data, io.TextIOBase):
                if not encoding:
                    try:
                        encoding = getattr(data, 'encoding')
                    except AttributeError:
                        pass
                new_data = io.BytesIO()
                if content_md5 is None:
                    h = md5()
                else:
                    h = None
                for chunk in iter(partial(data.read, io.DEFAULT_BUFFER_SIZE), ''):
                    chunk = codecs.encode(chunk, encoding=encoding or sys.getdefaultencoding())
                    new_data.write(chunk)
                    if content_md5 is None:
                        h.update(chunk)
                if content_md5 is None:
                    content_md5 = b64encode(h.digest()).decode()
                new_data.seek(0)
                data = new_data
            if content_md5 is None:
                if isinstance(data, (bytes, bytearray)):
                    content_md5 = b64md5_bytes(data)
                elif isinstance(data, io.BufferedIOBase):
                    h = md5()
                    for chunk in iter(partial(data.read, io.DEFAULT_BUFFER_SIZE), b''):
                        h.update(chunk)
                    content_md5 = b64encode(h.digest()).decode()
                    data.seek(0)
                elif isinstance(data, Path):
                    with data.open('rb') as fp:
                        h = md5()
                        for chunk in iter(partial(fp.read, io.DEFAULT_BUFFER_SIZE), b''):
                            h.update(chunk)
                        content_md5 = b64encode(h.digest()).decode()
                else:
                    content_md5 = ''
        else:
            data = None
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
        url = '{}://{}{}'.format('https' if self._use_https else 'http', self._endpoint, canonical_resource)
        # headers
        headers = headers or {}
        headers.update(auth_headers)
        if content_md5:
            headers['Content-MD5'] = content_md5
        # send http request
        # 文件路径的，要特殊处理！
        if isinstance(data, Path):
            with data.open('rb') as fp:
                resp = request(method, url=url, params=params or {}, headers=headers, data=fp, **kwargs)
        else:
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
    def session(self) -> Optional[requests.Session]:
        return self._session
