import prs_utility as utility

from .request import request
from . import validator

__all__ = [
    'sign_by_token', 'hash_by_password', 'hash_by_filename',
    'hash_by_readable_stream'
]


def sign_by_token(data, token, host):
    validator.assert_exc(data, 'data cannot be null')
    validator.assert_exc(token, 'token cannot be null')
    return request(
        host=host, method='post', path='/sign', data=data,
        auth_opts={'token': token}
    )


def hash_by_password(email, password):
    return utility.keccak256(f'{password}{email}')


def hash_by_filename(filename):
    # FIXME: eth_utils.keccak do not support `update`
    # so, load all data to memory, maybe OOM
    with open(filename, 'rb') as fp:
        data = fp.read()
        sha = utility.keccak256(data)
        return sha


def hash_by_readable_stream(stream):
    data = stream.read()
    sha = utility.keccak256(data)
    return data, sha
