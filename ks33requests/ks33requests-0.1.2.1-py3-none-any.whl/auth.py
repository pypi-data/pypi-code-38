import hmac
from base64 import encodebytes
from hashlib import sha1
from typing import Dict, List, Optional, Union
from urllib.parse import quote_plus

from .utils import http_format_date


def make_canonical_resource_string(
        bucket_name: str = '',
        object_key: str = '',
        sub_resources: Optional[Union[str, List[str]]] = None,
) -> str:
    """`CanonicalizedResource` 的计算方法

    :param str bucket_name: 用户请求的Bucket名称。
    :param str object_key: 用户请求的Object名称,需要对Object名称做URL编码。
    :param Optional[Union[str,List[str]]] sub_resources: 用户请求的子资源列表。
    :return: `CanonicalizedResource` 字符串表示用户访问的资源，将作为 HTTP 请求的 URL 的一部分
    :rtype: str

    计算方法如下：

    #. ``CanonicalizedResource="/"``
    #. 如果 ``BucketName`` 不为空,则 ``CanonicalizedResource = CanonicalizedResource + BucketName + "/"``
    #. 如果 ``ObjectKey`` 不为空,则 ``CanonicalizedResource = CanonicalizedResource + ObjectKey``
    #. 替换 ``CanonicalizedResource`` 中的双斜杠(``"//"``)为 ``"/%2F"``
    #. 如果 ``SubResource`` 不为空，则 ``CanonicalizedResource = CanonicalizedResource + "?" + SubResource``

    .. seealso:: https://docs.ksyun.com/documents/2321
    """
    result = '/'
    if sub_resources:
        if isinstance(sub_resources, str):
            sub_resources = [sub_resources]
        if isinstance(sub_resources, (tuple, list)):
            sub_res_text = '&'.join(sorted(sub_resources))
        else:
            raise TypeError('Wrong type {!r} of argument `sub_resources`'.format(type(sub_resources)))
    else:
        sub_res_text = ''
    if bucket_name:
        result += bucket_name + '/'
    if object_key:
        result += quote_plus(object_key)
    if sub_res_text:
        result += '?' + sub_res_text
    return result


def generate_auth_headers(
        http_verb: str,
        access_key: str,
        secret_key: str,
        canonical_resource: str,
        content_md5: str = '',
) -> Dict[str, str]:
    """生成公共响应头的签名

    :param str http_verb: 请求的方法，如： ``GET``, ``PUT``, ``POST``, ``DELETE`` 等
    :param str access_key: `KS3` 颁发给您的 `AccessKey` （长度为20个字符的ASCII字符串）。用于标识客户的身份。

    :param str secret_key: `KS3` 颁发给您的 `SecretKey` （长度为40个字符的ASCII字符串）。作为私钥形式存放于客户服务器不在网络中传递。

    :param str canonical_resource: 表示用户访问的资源

        .. seealso: 这个字符串可由 :func:`make_canonical_resource_string` 生成

    :param str content_md5: 表示请求内容数据的MD5值, 使用Base64编码。

        当请求的header中包含Content-MD5时，需要在StringToSign中包含，否则用("")替代。

        .. note::
            `Content-MD5` 的算法为先对数据做MD5摘要，再将MD5摘要做Base64编码。
            中间不需要做HEX编码，由于部分语言或工具包的MD5是默认做HEX编码的，所以当MD5算出来的结果为HEX编码的，首先需要对算出来的结果做HEX解码，然后再做Base64编码。

            .. seealso:: 详解见 `RFC2616 <https://www.ietf.org/rfc/rfc2616.txt>`_

    :return: HTTP 请求中的 ``Date`` 和 ``Authorization`` 头域

    :rtype: Dict[str,str]

    .. seealso:: https://docs.ksyun.com/documents/2321
    """
    # 参数验证
    http_verb = http_verb.strip().upper()
    content_md5 = (content_md5 or '').strip()
    # Date
    date_text = http_format_date()
    # Canonical KssHeaders
    canonical_kss_headers = ''
    # String to sign
    string_to_sign = http_verb + '\n'  # HTTP-Verb
    string_to_sign += content_md5 + '\n'  # Content-MD5
    string_to_sign += '\n'  # Content-Type
    string_to_sign += date_text + '\n'  # Date
    string_to_sign += canonical_kss_headers + canonical_resource  # Canonical-KssHeaders + Canonical-Resource
    # Signature
    hash_obj = hmac.new(secret_key.encode(), string_to_sign.encode(), sha1)
    sign = encodebytes(hash_obj.digest()).strip()
    # Authorization
    auth_text = 'KSS {}:{}'.format(access_key, sign.decode())
    # 最终返回
    return {'Date': date_text, 'Authorization': auth_text}
