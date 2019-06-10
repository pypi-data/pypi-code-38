import os
from urllib.parse import quote_plus, urljoin, urlencode

import prs_utility as utility
import requests

__all__ = ['hash_request', 'sign_request', 'get_auth_header', 'request']


def hash_request(path, payload):
    prefix = 'path={}'.format(quote_plus(path))
    sorted_qs = utility.get_sorted_qs(payload or {})
    sep = '&' if sorted_qs else ''
    data = f'{prefix}{sep}{sorted_qs}'
    return utility.keccak256(data)


def sign_request(path, payload, private_key):
    return utility.sign_hash(hash_request(path, payload), private_key)


def get_auth_header(path, payload, private_key):
    sign = sign_request(path, payload, private_key)
    signature, _hash = sign['signature'], sign['hash']
    address = utility.sig_to_address(_hash, signature)
    return {
        'Content-Type': 'application/json',
        'X-Po-Auth-Address': address,
        'X-Po-Auth-Sig': signature,
        'X-Po-Auth-Msghash': _hash
    }


def create_api_url(host, version='v2', path=None):
    if version == 'v1':
        version = None
    lst = ['api', version, path]
    query_path = '/'.join(x for x in lst if x)
    return urljoin(host, query_path)


def create_api_path(path, query=None):
    if path[0] != '/':
        path = f'/{path}'
    if query:
        query_string = urlencode(query, doseq=True, quote_via=quote_plus)
        path = f'{path}?{query_string}'
    return path


def request(
        host, version='v2', method='GET', path=None, query=None, data=None,
        headers=None, auth_opts=None, fields=None, file_data=None,
        timeout=None, debug=False
):
    """
    :param host: str, host
    :param version: str, the defautl value is `v2`
    :param method: str
    :param path: str
    :param query:
    :param data:
    :param headers:
    :param auth_opts: dict, {'private_key': 'xx', 'token': 'xxx'}
    :param fields:
    :param file_data: {
        'field': 'field name', 'filename': 'file name', 'file': 'file object'
    }
    """
    session = requests.Session()
    headers = headers if headers else {}
    path = create_api_path(path, query)
    url = create_api_url(host, version=version, path=path)
    if data:
        data = {'payload': data}
    if auth_opts and auth_opts.get('private_key'):
        payload = data and data.get('payload')
        headers.update(
            get_auth_header(path, payload, auth_opts['private_key'])
        )
    elif auth_opts and auth_opts.get('token'):
        headers.update({
            'authorization': f'Bearer {auth_opts["token"]}'
        })

    session.headers = headers
    if debug:
        print(
            f'request {method} {url}\n'
            f'query: {query}\ndata: {data}\n'
            f'fields: {fields}\nfile_data: {file_data}\n'
            f'headers: {session.headers}\n'
        )

    if (
            isinstance(file_data, dict)
            and file_data.get('field')
            and file_data.get('file')
            and file_data.get('filename')
    ):
        ext = os.path.splitext(file_data['filename'])[-1].lower()
        mimetype = None
        if ext == '.md':
            mimetype = 'text/markdown'
        elif ext in ['.jpeg', '.jpg']:
            mimetype = 'image/jpeg'
        elif ext == '.png':
            mimetype = 'image/png'
        elif ext == '.gif':
            mimetype = 'image/gif'
        elif ext == '.svg':
            mimetype = 'image/svg+xml'
        elif ext == '.bmp':
            mimetype = 'image/bmp'
        elif ext == '.ico':
            mimetype = 'image/vnd.microsoft.icon'
        elif ext == '.webp':
            mimetype = 'image/webp'
        elif ext in ['.tif', '.tiff']:
            mimetype = 'image/tiff'

        files = {
            file_data['field']: (
                file_data['filename'], file_data['file'], mimetype
            ),
        }
        resp = session.request(
            method, url, data=fields, files=files, timeout=timeout
        )
    else:
        resp = session.request(
            method, url, json=data, timeout=timeout
        )

    if debug:
        print(f'response {resp.content}')

    return resp
