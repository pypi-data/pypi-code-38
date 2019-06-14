import io
import sys
from base64 import b64encode
from datetime import datetime
from email.utils import formatdate
from functools import partial
from hashlib import md5
from time import mktime
from typing import Union


def http_format_date(dt: datetime = None) -> str:
    if not dt:
        dt = datetime.now()
    stamp = mktime(dt.timetuple())
    return formatdate(timeval=stamp, localtime=False, usegmt=True)


def b64md5_bytes(data: Union[bytes, bytearray]) -> str:
    return b64encode(md5(data).digest()).decode()


def b64md5_text(text: str, encoding: str = sys.getdefaultencoding()) -> str:
    data = text.encode(encoding=encoding)
    return b64md5_bytes(data)


def b64md5_stream(stream: io.BufferedIOBase) -> str:
    h = md5()
    for chunk in iter(partial(stream.read, io.DEFAULT_BUFFER_SIZE), b''):
        h.update(chunk)
    return b64encode(h.digest()).decode()


def b64md5_stream_iterable(stream: io.BufferedIOBase) -> str:
    h = md5()
    for chunk in iter(partial(stream.read, io.DEFAULT_BUFFER_SIZE), b''):
        yield h.update(chunk)
    return b64encode(h.digest()).decode()
