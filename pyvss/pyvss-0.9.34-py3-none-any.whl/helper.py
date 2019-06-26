"""
This helper module contains complimentary functions
to the :py:mod:`pyvss.manager` module
"""
from base64 import b64decode, b64encode
import gzip

import requests.auth


def compress_encode_string(string_data):
    """
    Compresses and encodes in base64 a given
    string

    :param string_data: string to compress and encode
    :type string_data: str
    :return: compressed and encoded string
    """
    from six import BytesIO

    out = BytesIO()
    with gzip.GzipFile(fileobj=out, mode='w') as f:
        f.write(string_data.encode('utf-8'))
    return b64encode(out.getvalue()).decode()


def decode_uncompress_string(string_gz_encoded):
    """
    Decompress and decodes a given string

    :param string_gz_encoded: string to decompress and decode
    :type string_gz_encoded: str
    :return: string
    """
    from six import BytesIO

    string_gz = b64decode(string_gz_encoded)
    file_obj = BytesIO(string_gz)
    return gzip.GzipFile(mode='rb', fileobj=file_obj).read().decode()


def hash_string(string_to_hash):
    """
    Hashes string using SHA-512

    :param string_to_hash: string to hash
    :type string_to_hash: str
    :return: hashed string
    """
    import crypt

    if hasattr(crypt, 'mksalt'):
        return crypt.crypt(string_to_hash, crypt.mksalt(crypt.METHOD_SHA512))
    else:
        import string
        import random

        rand = random.SystemRandom()
        salt = ''.join(
            [
                rand.choice(string.ascii_letters + string.digits)
                for _ in range(8)
            ]
        )
        return crypt.crypt(
            string_to_hash,
            "$6$rounds={rounds}${salt}".format(rounds=4096, salt=salt),
        )


class HTTPBasicAuth(requests.auth.HTTPBasicAuth):
    def __call__(self, r):
        """
        Override username/password serialization to allow unicode.
        See https://github.com/jakubroztocil/httpie/issues/212
        """
        r.headers['Authorization'] = (
            type(self)
            .make_header(self.username, self.password)
            .encode('latin1')
        )
        return r

    @staticmethod
    def make_header(username, password):
        credentials = u'%s:%s' % (username, password)
        token = b64encode(credentials.encode('utf8')).strip().decode('latin1')
        return 'Basic %s' % token
