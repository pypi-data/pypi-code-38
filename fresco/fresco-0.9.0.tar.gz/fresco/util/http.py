# encoding=utf-8
# Copyright 2015 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
"""
Utilities for working with data on the HTTP level
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from binascii import hexlify
from collections import namedtuple
from email.message import Message
from email.header import Header
from io import BytesIO
from itertools import chain
import os
import re
try:
    from email.parser import BytesParser
except ImportError:
    # python 2
    from email.parser import Parser as BytesParser  # NOQA

try:
    from urllib.parse import unquote_plus
except ImportError:
    from urllib import unquote_plus  # NOQA
from shutil import copyfileobj

import fresco
from fresco.compat import PY3, string_types, ustr
from fresco.exceptions import RequestParseError
from fresco.util.io import (ExpandableOutput, SizeLimitedInput, PutbackInput,
                            DelimitedInput)
from fresco.util.wsgi import unicode_to_environ

KB = 1024
MB = 1024 * KB

#: Data chunk size to read from the input stream (wsgi.input)
CHUNK_SIZE = 8 * KB

#: Allowed character encodings.
#: This list is based on the list of standard encodings here:
#:
#:     https://docs.python.org/3.4/library/codecs.html
#:
#: Python specific encodings and binary transformations (eg zlib decompression)
#: are excluded to avoid zip bomb style attacks.
ALLOWED_ENCODINGS = set([
    'ascii', '646', 'us-ascii',
    'big5', 'big5-tw', 'csbig5',
    'big5hkscs', 'big5-hkscs', 'hkscs',
    'cp037', 'IBM037', 'IBM039',
    'cp273', '273', 'IBM273', 'csIBM273',
    'cp424', 'EBCDIC-CP-HE', 'IBM424',
    'cp437', '437', 'IBM437',
    'cp500', 'EBCDIC-CP-BE', 'EBCDIC-CP-CH', 'IBM500',
    'cp720', 'Arabic',
    'cp737', 'Greek',
    'cp775', 'IBM775',
    'cp850', '850', 'IBM850',
    'cp852', '852', 'IBM852',
    'cp855', '855', 'IBM855',
    'cp856', 'Hebrew',
    'cp857', '857', 'IBM857',
    'cp858', '858', 'IBM858',
    'cp860', '860', 'IBM860',
    'cp861', '861', 'CP-IS', 'IBM861',
    'cp862', '862', 'IBM862',
    'cp863', '863', 'IBM863',
    'cp864', 'IBM864',
    'cp865', '865', 'IBM865',
    'cp866', '866', 'IBM866',
    'cp869', '869', 'CP-GR', 'IBM869',
    'cp874', 'Thai',
    'cp875', 'Greek',
    'cp932', '932', 'ms932', 'mskanji', 'ms-kanji',
    'cp949', '949', 'ms949', 'uhc',
    'cp950', '950', 'ms950',
    'cp1006', 'Urdu',
    'cp1026', 'ibm1026',
    'cp1125', '1125', 'ibm1125', 'cp866u', 'ruscii',
    'cp1140', 'ibm1140',
    'cp1250', 'windows-1250',
    'cp1251', 'windows-1251',
    'cp1252', 'windows-1252',
    'cp1253', 'windows-1253',
    'cp1254', 'windows-1254',
    'cp1255', 'windows-1255',
    'cp1256', 'windows-1256',
    'cp1257', 'windows-1257',
    'cp1258', 'windows-1258',
    'cp65001',
    'euc_jp', 'eucjp', 'ujis', 'u-jis',
    'euc_jis_2004', 'jisx0213', 'eucjis2004',
    'euc_jisx0213', 'eucjisx0213',
    'euc_kr', 'euckr', 'korean', 'ksc5601', 'ks_c-5601', 'ks_c-5601-1987',
    'ksx1001', 'ks_x-1001',
    'gb2312', 'chinese', 'csiso58gb231280', 'euc-' 'cn', 'euccn',
    'eucgb2312-cn', 'gb2312-1980', 'gb2312-80', 'iso-' 'ir-58',
    'gbk', '936', 'cp936', 'ms936',
    'gb18030', 'gb18030-2000',
    'hz', 'hzgb', 'hz-gb', 'hz-gb-2312',
    'iso2022_jp', 'csiso2022jp', 'iso2022jp', 'iso-2022-jp',
    'iso2022_jp_1', 'iso2022jp-1', 'iso-2022-jp-1',
    'iso2022_jp_2', 'iso2022jp-2', 'iso-2022-jp-2',
    'iso2022_jp_2004', 'iso2022jp-2004', 'iso-2022-jp-2004',
    'iso2022_jp_3', 'iso2022jp-3', 'iso-2022-jp-3',
    'iso2022_jp_ext', 'iso2022jp-ext', 'iso-2022-jp-ext',
    'iso2022_kr', 'csiso2022kr', 'iso2022kr', 'iso-2022-kr',
    'latin_1', 'iso-8859-1', 'iso8859-1', '8859', 'cp819', 'latin', 'latin1',
    'L1',
    'iso8859_2', 'iso-8859-2', 'latin2', 'L2',
    'iso8859_3', 'iso-8859-3', 'latin3', 'L3',
    'iso8859_4', 'iso-8859-4', 'latin4', 'L4',
    'iso8859_5', 'iso-8859-5', 'cyrillic',
    'iso8859_6', 'iso-8859-6', 'arabic',
    'iso8859_7', 'iso-8859-7', 'greek', 'greek8',
    'iso8859_8', 'iso-8859-8', 'hebrew',
    'iso8859_9', 'iso-8859-9', 'latin5', 'L5',
    'iso8859_10', 'iso-8859-10', 'latin6', 'L6',
    'iso8859_13', 'iso-8859-13', 'latin7', 'L7',
    'iso8859_14', 'iso-8859-14', 'latin8', 'L8',
    'iso8859_15', 'iso-8859-15', 'latin9', 'L9',
    'iso8859_16', 'iso-8859-16', 'latin10', 'L10',
    'johab', 'cp1361', 'ms1361',
    'koi8_r', 'Russian',
    'koi8_u', 'Ukrainian',
    'mac_cyrillic', 'maccyrillic',
    'mac_greek', 'macgreek',
    'mac_iceland', 'maciceland',
    'mac_latin2', 'maclatin2', 'maccentraleurope',
    'mac_roman', 'macroman', 'macintosh',
    'mac_turkish', 'macturkish',
    'ptcp154', 'csptcp154', 'pt154', 'cp154', 'cyrillic-asian',
    'shift_jis', 'csshiftjis', 'shiftjis', 'sjis', 's_jis',
    'shift_jis_2004', 'shiftjis2004', 'sjis_2004', 'sjis2004',
    'shift_jisx0213', 'shiftjisx0213', 'sjisx0213', 's_jisx0213',
    'utf_32', 'U32', 'utf32',
    'utf_32_be', 'UTF-32BE',
    'utf_32_le', 'UTF-32LE',
    'utf_16', 'U16', 'utf16',
    'utf_16_be', 'UTF-16BE',
    'utf_16_le', 'UTF-16LE',
    'utf_7', 'U7', 'unicode-1-1-utf-7',
    'utf_8', 'U8', 'UTF', 'utf8',
    'utf_8_sig'])

# "Notice that spelling alternatives that only differ in case or use a hyphen
# instead of an underscore are also valid aliases; therefore, e.g. 'utf-8' is a
# valid alias for the 'utf_8' codec."
ALLOWED_ENCODINGS = set(item.lower().replace('_', '-')
                        for item in ALLOWED_ENCODINGS)

ParsedContentType = namedtuple(
    'ParsedContentType', 'content_type encoding params')

token_pattern = r'[!#-\'*-.0-9A-Z\^-~]+'
quotedstringparts_pattern = r'(?:(\\.)|([^"\\]+))'
quotedstring_pattern = r'"(?:{})*"'.format(quotedstringparts_pattern)
quotedstring_parser = re.compile(r'{}'.format(quotedstringparts_pattern))

parameter_parser = re.compile(
        r'\s*'
        r'(?P<name>{token})'
        r'\s*=\s*(?:({token})|({quotedstring}))\s*(?:;|$)'
        .format(token=token_pattern,
                quotedstring=quotedstring_pattern))


def get_content_type_info(environ,
                          default_type='application/octet-stream',
                          default_encoding='iso-8859-1'):
    """
    Read and parse the Content-Type header and return a
    :class:`ParsedContentType` object.
    """
    ct, params = parse_header(environ.get('CONTENT_TYPE', default_type))
    encoding = params.get('charset', default_encoding)
    if encoding is None or encoding.lower() not in ALLOWED_ENCODINGS:
        encoding = default_encoding
    return ParsedContentType(ct, encoding, params)


class TooBig(RequestParseError):
    """\
    Request body is too big
    """
    def __init__(self, *args, **kwargs):
        super(TooBig, self).__init__(*args, **kwargs)
        self.response = fresco.response.Response.request_entity_too_large()


class MissingContentLength(RequestParseError):
    """\
    No ``Content-Length`` header given
    """
    def __init__(self, *args, **kwargs):
        super(MissingContentLength, self).__init__(*args, **kwargs)
        self.response = fresco.response.Response.length_required()


def parse_parameters(s,
                     preserve_backslashes=False):
    """
    Return ``s`` parsed as a sequence of semi-colon delimited name=value pairs.

    Example usage::

        >>> from fresco.util.http import parse_parameters
        >>> parse_parameters('foo=bar')
        {'foo': 'bar'}
        >>> parse_parameters('foo="bar\\""')
        {'foo': 'bar"'}

    The ``preserve_backslashes`` flag is used to preserve IE compatibility
    for file upload paths, which it incorrectly encodes without escaping
    backslashes, eg::

        Content-Disposition: form-data; name="file"; filename="C:\tmp\Ext.js"

    (To be RFC compliant, the backslashes should be doubled up).
    """
    remaining = s.strip()
    if remaining == '':
        return {}

    params = {}
    while True:
        m = parameter_parser.match(remaining)
        if m is None:
            raise RequestParseError('{!r}: expected parameter at character {}'
                                    .format(s, len(s) - len(remaining)),
                                    content_type='text/plain')
        groups = m.groups()
        name, value_token, value_qs = groups[:3]

        if value_token:
            params[name] = value_token
        else:
            if preserve_backslashes:
                params[name] = value_qs[1:-1]
            else:
                parts = quotedstring_parser.findall(value_qs)
                value = ''.join((qp[1] if qp else t) for qp, t in parts)
                params[name] = value

        remaining = remaining[m.end():]
        if not remaining:
            break

    return params


def parse_value(s):
    """
    Return ``s`` parsed as a RFC2045 value, ie:

             value := token / quoted-string

    Example usage::

        >>> from fresco.util.http import parse_value
        >>> parse_value('foo')
        'foo'
        >>> dequote('"foo"')
        'foo'
    """
    try:
        # Fast case: no quotes
        if s[0] != '"':
            return s
    except IndexError:
        return s

    return parse_quoted_string(s[1:-1])


def parse_quoted_string(s, pattern=re.compile(r'^(?:\\.|[^"\\]+)*$')):
    parts = (s for item in pattern.finditer(s))
    return ''.join(part[1] if part[0] == '\\' else part for part in parts)


def parse_header(header,
                 ie_workaround=False,
                 _broken_encoding_sniffer=re.compile(r'\\[^"\\]').search):
    """
    Given a header, return a tuple of
    ``(value, [(parameter_name, parameter_value)])``.

    Example usage::

        >>> parse_header("text/html; charset=UTF-8")
        ('text/html', {'charset': 'UTF-8'})
        >>> parse_header("multipart/form-data; boundary=-------7d91772e200be")
        ('multipart/form-data', {'boundary': '-------7d91772e200be'})
    """
    if isinstance(header, Header):
        # Python3's email.parser.Parser returns a Header object (rather than
        # a string) for values containing 8-bit characters. These are then
        # replaced by U+FFFD when converting the header to a string
        header = ustr(header)

    elif isinstance(header, bytes):
        # In Python2 headers come through as raw byte strings. Use 'replace'
        # to emulate the PY3 behaviour:
        header = header.decode('ascii', 'replace')

    if ';' not in header:
        return header, {}

    preserve_backslashes=(ie_workaround and _broken_encoding_sniffer(header))

    value, remaining = header.split(';', 1)
    return value, parse_parameters(remaining.strip(),
                                   preserve_backslashes=preserve_backslashes)


def parse_querystring(data, charset=None, strict=False, keep_blank_values=True,
                      pairsplitter=re.compile('[;&]').split):
    """\
    Return ``(key, value)`` pairs from the given querystring::

        >>> list(parse_querystring('green%20eggs=ham;me=sam+i+am'))
        [(u'green eggs', u'ham'), (u'me', u'sam i am')]

    :param data: The query string to parse.
    :param charset: Character encoding used to decode values. If not specified,
                    ``fresco.DEFAULT_CHARSET`` will be used.

    :param keep_blank_values: if True, keys without associated values will be
                              returned as empty strings. if False, no key,
                              value pair will be returned.

    :param strict: if ``True``, a ``ValueError`` will be raised on parsing
                   errors.
    """

    if charset is None:
        charset = fresco.DEFAULT_CHARSET

    if PY3:
        unquote = lambda s: unquote_plus(s, charset)
    else:
        unquote = lambda s: unquote_plus(s).encode('iso-8859-1')\
                                           .decode(charset)

    for item in pairsplitter(data):
        if not item:
            continue
        try:
            key, value = item.split('=', 1)
        except ValueError:
            if strict:
                raise RequestParseError("bad query field: %r" % (item,))
            if not keep_blank_values:
                continue
            key, value = item, ''

        try:
            yield (unquote(key), unquote(value))
        except UnicodeDecodeError:
            raise RequestParseError("Invalid character data: can't decode"
                                    " as %r" % (charset,))


def parse_post(environ, fp, default_charset=None, max_size=16 * KB,
               max_multipart_size=2 * MB,
               ie_workaround=True):
    """\
    Parse the contents of an HTTP POST request, which may be either
    application/x-www-form-urlencoded or multipart/form-data encoded.

    Returned items are either tuples of (name, value) for simple string values
    or (name, FileUpload) for uploaded files.

    :param max_multipart_size: Maximum size of total data for a multipart form
                               submission

    :param max_size: The maximum size of data allowed to be read into memory.
                     For a application/x-www-form-urlencoded submission, this
                     is the maximum size of the entire data. For a
                     multipart/form-data submission, this is the maximum size
                     of any individual field (except file uploads).
    """
    ct, charset, ct_params = get_content_type_info(
                                environ,
                                'application/x-www-form-urlencoded',
                                default_charset or fresco.DEFAULT_CHARSET)

    try:
        content_length = int(environ['CONTENT_LENGTH'])
    except (TypeError, ValueError, KeyError):
        raise MissingContentLength()

    try:
        if ct == 'application/x-www-form-urlencoded':
            if content_length > max_size:
                raise TooBig("Content Length exceeds permitted size")
            return parse_querystring(SizeLimitedInput(fp, content_length)
                                        .read()
                                        .decode('ASCII'), charset)
        else:
            if content_length > max_multipart_size:
                raise TooBig("Content Length exceeds permitted size")
            try:
                boundary = ct_params['boundary']
            except KeyError:
                raise RequestParseError(
                    "No boundary given in multipart/form-data content-type")
            return parse_multipart(SizeLimitedInput(fp, content_length),
                                   boundary.encode('ASCII'),
                                   charset,
                                   max_size,
                                   ie_workaround=ie_workaround)
    except UnicodeDecodeError:
        raise RequestParseError("Payload contains non ascii data")


def get_body_bytes(environ, max_size=16 * KB):
    """
    Read a single message body from environ['wsgi.input'], returning a bytes
    object.
    """
    try:
        content_length = int(environ['CONTENT_LENGTH'])
    except (TypeError, ValueError, KeyError):
        raise MissingContentLength()

    if content_length > max_size:
        raise TooBig("Content Length exceeds permitted size")
    return SizeLimitedInput(environ['wsgi.input'], content_length).read()


def parse_body(environ, fp, default_charset=None, max_size=16 * KB):
    """
    Parse the message
        (payload as a byte string, content-type, encoding)
        """
    ct, charset, params = get_content_type_info(
        environ.get('CONTENT_TYPE', 'text/plain'))


class HTTPMessage(Message):
    """
    Represent HTTP request message headers
    """


def parse_multipart(fp,
                    boundary,
                    default_charset,
                    max_size,
                    ie_workaround=True):
    """
    Parse data encoded as ``multipart/form-data``. Generate tuples of::

        (<field-name>, <data>)

    Where ``data`` will be a string in the case of a regular input field, or a
    ``FileUpload`` instance if a file was uploaded.

    :param fp: input stream from which to read data
    :param boundary: multipart boundary string, as specified by the
                     ``Content-Disposition`` header
    :param default_charset: character set to use for encoding, if not specified
                            by a content-type header. In practice web browsers
                            don't supply a content-type header so this needs to
                            contain a sensible value.
    :param max_size: Maximum size in bytes for any non file upload part
    :param ie_workaround: If True (the default), enable a work around for IE's
                          broken content-disposition header encoding.
    """
    boundary_size = len(boundary)
    if not boundary.startswith(b'--'):
        raise RequestParseError("Malformed boundary string: "
                                "must start with '--' (rfc 2046)")

    if boundary_size > 72:
        raise RequestParseError("Malformed boundary string: "
                                "must be no more than 70 characters, not "
                                "counting the two leading hyphens (rfc 2046)")

    assert boundary_size + 2 < CHUNK_SIZE, \
          "CHUNK_SIZE cannot be smaller than the boundary string"

    if fp.read(2) != b'--':
        raise RequestParseError("Malformed POST data: expected two hypens")

    if fp.read(boundary_size) != boundary:
        raise RequestParseError("Malformed POST data: expected boundary")

    if fp.read(2) != b'\r\n':
        raise RequestParseError("Malformed POST data: expected CRLF")

    fp = PutbackInput(fp)

    while True:
        headers, data = _read_multipart_field(fp, boundary)
        try:
            _, params = parse_header(headers['Content-Disposition'],
                                     ie_workaround=ie_workaround)
        except KeyError:
            raise RequestParseError("Missing Content-Disposition header")

        try:
            name = params['name']
        except KeyError:
            raise RequestParseError("Missing name parameter in "
                                    "Content-Disposition header")

        is_file_upload = 'Content-Type' in headers and 'filename' in params

        if is_file_upload:
            storage = data.getstorage()
            storage.seek(0)
            yield name, FileUpload(params['filename'], headers, storage)

        else:
            charset = parse_header(headers.get('Content-Type', ''))[1]\
                        .get('charset', default_charset)
            if data.tell() > max_size:
                raise TooBig("Data block exceeds maximum permitted size")
            try:
                data.seek(0)
                yield name, data.read().decode(charset)
            except UnicodeDecodeError:
                raise RequestParseError("Invalid character data: can't decode "
                                        "as %r" % (charset,))

        chunk = fp.read(2)
        if chunk == b'--':
            if fp.peek(3) != b'\r\n':
                raise RequestParseError("Expected terminating CRLF "
                                        "at end of stream")
            break

        if chunk != b'\r\n':
            raise RequestParseError("Expected CRLF after boundary")


def _read_multipart_field(fp, boundary, parser=BytesParser(_class=HTTPMessage)):
    """
    Read a single part from a multipart/form-data message and return a tuple of
    ``(headers, data)``. Stream ``fp`` must be positioned at the start of the
    header block for the field.

    Return a tuple of ('<headers>', '<data>')

    ``headers`` is an instance of ``email.message.Message``.

    ``data`` is an instance of ``ExpandableOutput``.

    Note that this currently cannot handle nested multipart sections.
    """
    data = ExpandableOutput()
    headers = parser.parse(DelimitedInput(fp, b'\r\n\r\n'), headersonly=True)
    fp = DelimitedInput(fp, b'\r\n--' + boundary)

    # XXX: handle base64 encoding etc
    for chunk in iter(lambda: fp.read(CHUNK_SIZE), b''):
        data.write(chunk)
    data.flush()

    # Fallen off the end of the input without having read a complete field?
    if not fp.delimiter_found:
        raise RequestParseError("Incomplete data (expected boundary)")

    return headers, data


class FileUpload(object):
    """\
    Represent a file uploaded in an HTTP form submission
    """

    def __init__(self, filename, headers, fileob):

        self.filename = filename
        self.headers = headers
        self.file = fileob

        # UNC/Windows path
        if self.filename[:2] == '\\\\' or self.filename[1:3] == ':\\':
            self.filename = self.filename[self.filename.rfind('\\') + 1:]

    def save(self, fileob):
        """
        Save the upload to the file object or path ``fileob``

        :param fileob: a file-like object open for writing, or the path to the
                       file to be written
        """
        if isinstance(fileob, string_types):
            with open(fileob, 'wb') as f:
                return self.save(f)

        self.file.seek(0)
        copyfileobj(self.file, fileob)


def encode_multipart(data=None, files=None, charset='UTF-8', **kwargs):
    """
    Encode ``data`` using multipart/form-data encoding, returning a tuple
    of ``(<encoded data>, <environ items>)``.

    :param data: POST data to be encoded, either a dict or list of
                 ``(name, value)`` tuples.

    :param charset: Encoding used for any unicode values encountered in
                    ``data``

    :param files: list of ``(name, filename, content_type, data)`` tuples.
                    ``data`` may be either a byte string, iterator or
                    file-like object.

    :param kwargs: other data items as keyword arguments
    :returns: a tuple of ``(<encoded_data>, <environ_items>)``,
              where ``encoded_data`` is a BytesIO object
              and ``environ`` is a dict containing the Content-Type and
              Content-Length headers encoded for inclusion in a WSGI environ
              dict.
    """

    def header_block(name):
        return [('Content-Disposition', 'form-data; name="%s"' % (name,))]

    def file_header_block(name, filename, content_type):
        return [('Content-Disposition',
                 'form-data; name="%s"; filename="%s"' % (name, filename)),
                ('Content-Type', content_type)]

    def write_payload(stream, data):
        "Write ``data`` to ``stream``, encoding as required"
        if hasattr(data, 'read'):
            copyfileobj(data, stream)
        elif isinstance(data, bytes):
            stream.write(data)
        elif isinstance(data, string_types):
            stream.write(data.encode(charset))
        else:
            raise ValueError(data)

    if data is None:
        data = {}

    if files is None:
        files = []

    try:
        data = data.items()
    except AttributeError:
        pass

    data = chain(data, kwargs.items())

    boundary = b'-------' + hexlify(os.urandom(16))
    alldata = chain(
        ((header_block(k), payload) for k, payload in data),
        ((file_header_block(k, fn, ct), payload)
         for k, fn, ct, payload in files))

    CRLF = b'\r\n'
    post_data = BytesIO()
    post_data.write(b'--' + boundary)
    for headers, payload in alldata:
        post_data.write(CRLF)
        for name, value in headers:
            post_data.write('{0}: {1}\r\n'.format(name, value).encode('ascii'))
        post_data.write(CRLF)
        write_payload(post_data, payload)
        post_data.write(b'\r\n--' + boundary)
    post_data.write(b'--\r\n')
    length = post_data.tell()
    post_data.seek(0)
    wsgienv = {
        'CONTENT_LENGTH': str(length),
        'CONTENT_TYPE': unicode_to_environ(
                'multipart/form-data; boundary=' + boundary.decode('ascii'))}

    return (post_data, wsgienv)
