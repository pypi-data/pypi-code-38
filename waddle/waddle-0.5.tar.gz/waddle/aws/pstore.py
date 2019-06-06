import sys
from typing import Generator, Tuple
from halo import Halo
from halo.halo import colored_frame
from murmuration.aws import cached_client
from murmuration.helpers import prefix_alias
from .session import ssm_client


__all__ = [
    'yield_parameters',
    'put_parameter',
    'delete_parameters',
    'waddle_key',
    'ssm_key',
]

StrTuple = Tuple[str, str, str]


def waddle_key(prefix, key):
    return key.replace(prefix, '').replace('/', '.')[1:]


def ssm_key(prefix, key):
    prefix = f'/{prefix}' if prefix else ''
    key = key.replace('.', '/')
    return f'{prefix}/{key}'


def yield_parameters(prefix, decrypt=True) -> Generator[StrTuple, None, None]:
    ssm = ssm_client()
    paginator = ssm.get_paginator('get_parameters_by_path')
    for page in paginator.paginate(
            Path=prefix,
            Recursive=True,
            WithDecryption=decrypt,
            PaginationConfig={
                'PageSize': 10,
            }):
        for x in page['Parameters']:
            key = x['Name']
            value = x['Value']
            key = waddle_key(prefix, key)
            yield key, value, x['Type']


def start_notification(action, key):
    if sys.stdout.isatty():  # pragma: no cover
        spinner = Halo(f'{action} {key}', spinner='dots')
        spinner.start()
        return spinner
    message = f'{action} {key}....'
    print(message, end='')
    return None


def end_notification(spinner: Halo, success=True):
    mark = '✔' if success else '✘'
    if sys.stdout.isatty():  # pragma: no-cover
        if success:
            spinner.succeed()
        else:
            mark = colored_frame(mark, 'red')
            spinner.stop_and_persist(mark)
    else:
        print(mark, end='')


def put_parameter(key, value, kms_key, encrypted, verbose=False):
    spinner = None
    if verbose:
        spinner = start_notification('pushing', key)
    ssm = cached_client('ssm')
    params = {}
    if isinstance(value, list):
        value = ','.join([ f'{x}' for x in value ])
        params['Type'] = 'StringList'
    elif encrypted:
        params['Type'] = 'SecureString'
        if kms_key:
            params['KeyId'] = prefix_alias(kms_key)
    else:
        params['Type'] = 'String'
    result = ssm.put_parameter(Name=key, Value=value, Overwrite=True, **params)
    if verbose:
        end_notification(spinner)
    return result


def delete_parameters(*keys, verbose=False):
    ssm = cached_client('ssm')
    n_start, spinner = 1, None
    while keys:
        rg = keys[:10]
        if verbose:
            spinner = start_notification(
                'deleting keys', f'{n_start}=>{n_start + len(rg) - 1}')
        ssm.delete_parameters(Names=rg)
        keys = keys[10:]
        if verbose:
            end_notification(spinner, False)
