import io
import pathlib
from base64 import b64encode
from codecs import encode
from datetime import datetime
from email.utils import formatdate
from functools import partial
from hashlib import md5
from sys import getdefaultencoding
from time import mktime
from typing import Union, Optional, Tuple

__all__ = ['http_format_date', 'prepare_data', 'get_content_md5']


def http_format_date(dt: datetime = None) -> str:
    """生成 HTTP 头的日期时间字符串

    :param datetime dt: 要转换的时间日期

        :default: ``None`` - 当前时间

    :return: 转换后的满足 HTTP 格式要求的时间日期字符串
    :rtype: str
    """
    if not dt:
        dt = datetime.now()
    stamp = mktime(dt.timetuple())
    return formatdate(timeval=stamp, localtime=False, usegmt=True)


def prepare_data(
        data: Union[bytes, bytearray, str, pathlib.Path, io.BufferedIOBase, io.TextIOBase],
        checking: bool = True,
        encoding: str = None
) -> Tuple[Union[bytes, bytearray, io.BufferedIOBase], Optional[str]]:
    """为 API 准备要进行 POST 或 PUT 的数据，包括 KS3 API 的通用请求部分所需的 `Content-MD5`

    :param data: 要准备的数据
    :type data: Union[bytes, bytearray, str, pathlib.Path, io.BufferedIOBase, io.TextIOBase]

    :param bool checking: 是否计算MD5. 默认 ``True``
    :param str encoding: 如果数据是字符串，使用这个参数指定字符编码。默认自动获取。

    :rtype: Tuple[Union[bytes, bytearray, io.BufferedIOBase], Optional[str]]
    :return: 返回元组 ``(data, md5)``: 转换后的数据，以及该数据的MD5散列值的BASE64编码结果字符串

    为了让 :mod:`requests` 上传数据，这个函数尝试转换 `data` 参数。
    如果传入的 `data` 参数类型不支持，将直接原样返回 `data`，且 MD5 为 ``None``。

    `Content-MD5` 的算法为先对数据做MD5摘要，再将MD5摘要做Base64编码。
    中间不需要做HEX编码，由于部分语言或工具包的MD5是默认做HEX编码的，所以当MD5算出来的结果为HEX编码的，首先需要对算出来的结果做HEX解码，然后再做Base64编码。


    .. seealso:: https://docs.ksyun.com/documents/2321
    """
    result_data = data
    hash_val = None
    default_encoding = getdefaultencoding()

    # 字节数据 - 直接计算
    if isinstance(data, (bytes, bytearray)):
        if checking:
            hash_val = b64encode(md5(data).digest()).decode()

    # 文件路径
    elif isinstance(data, pathlib.Path):
        if checking:
            with data.open('rb') as fp:
                h = md5()
                for chunk in iter(partial(fp.read, io.DEFAULT_BUFFER_SIZE), b''):
                    h.update(chunk)
                hash_val = b64encode(h.digest()).decode()

    # 字节流
    elif isinstance(data, io.BufferedIOBase):
        if checking:
            h = md5()
            p = data.tell()
            try:
                for chunk in iter(partial(data.read, io.DEFAULT_BUFFER_SIZE), b''):
                    h.update(chunk)
            finally:
                data.seek(p)
            hash_val = b64encode(h.digest()).decode()

    # 字符串
    elif isinstance(data, str):
        result_data = encode(data, encoding=encoding or default_encoding)
        if checking:
            hash_val = b64encode(md5(result_data).digest()).decode()

    # 文本流
    elif isinstance(data, io.TextIOBase):
        if not encoding:
            try:
                encoding = getattr(data, 'encoding')
            except AttributeError:
                pass
        if checking:
            h = md5()
        else:
            h = None
        result_data = io.BytesIO()
        for s in iter(partial(data.read, io.DEFAULT_BUFFER_SIZE), ''):
            chunk = encode(s, encoding=encoding or default_encoding)
            result_data.write(chunk)
            if h:
                h.update(chunk)
        result_data.seek(0)
        if h:
            hash_val = b64encode(h.digest()).decode()

    return result_data, hash_val


def get_content_md5(
        data: Union[bytes, bytearray, str, pathlib.Path, io.BufferedIOBase, io.TextIOBase],
        encoding: str = None
) -> str:
    """获取 KS3 API 的通用请求部分所需的 `Content-MD5`

    :param data: 要计算数据
    :type data: Union[bytes, bytearray, str, pathlib.Path, io.BufferedIOBase, io.TextIOBase]

    :param str encoding: 如果数据是字符串，使用这个参数指定字符编码。默认自动获取。

    :rtype: str
    :return: 该数据的MD5散列值的BASE64编码结果字符串

    `Content-MD5` 的算法为先对数据做MD5摘要，再将MD5摘要做Base64编码。
    中间不需要做HEX编码，由于部分语言或工具包的MD5是默认做HEX编码的，所以当MD5算出来的结果为HEX编码的，首先需要对算出来的结果做HEX解码，然后再做Base64编码。

    .. seealso:: https://docs.ksyun.com/documents/2321
    """
    _, result = prepare_data(data, True, encoding)
    return result
