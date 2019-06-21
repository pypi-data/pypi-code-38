"""
Utilities
=========
"""
from __future__ import print_function

from pipes import quote
import os
import posixpath
import hashlib

import six

from fabric.api import env, hide, run


def run_as_root(command, *args, **kwargs):
    """
    Run a remote command as the root user.

    When connecting as root to the remote system, this will use Fabric's
    ``run`` function. In other cases, it will use ``sudo``.
    """
    from burlap.common import run_or_dryrun, sudo_or_dryrun
    if env.user == 'root':
        func = run_or_dryrun
    else:
        func = sudo_or_dryrun
    return func(command, *args, **kwargs)


def get_cwd(local=False):

    from fabric.api import local as local_run

    with hide('running', 'stdout'):
        if local:
            return local_run('pwd', capture=True)
        return run('pwd')


def abspath(path, local=False):

    path_mod = os.path if local else posixpath

    if not path_mod.isabs(path):
        cwd = get_cwd(local=local)
        path = path_mod.join(cwd, path)

    return path_mod.normpath(path)


def download(url, retry=10):
#     from burlap.require.curl import command as require_curl
#     require_curl()
    run('curl --silent --retry %s -O %s' % (retry, url))


def read_file(path):
    with hide('running', 'stdout'):
        return run('cat {0}'.format(quote(path)))


def read_lines(path):
    return read_file(path).splitlines()


_oct = oct
def oct(v, **kwargs): # pylint: disable=redefined-builtin
    """
    A backwards compatible version of oct() that works with Python2.7 and Python3.
    """
    v = str(v)
    if six.PY2:
        if v.startswith('0o'):
            v = '0' + v[2:]
    else:
        if not v.starswith('0o'):
            assert v[0] == '0'
            v = '0o' + v[1:]
    return eval('_oct(%s, **kwargs)' % v) # pylint: disable=eval-used


def get_file_hash(fin, block_size=2**20):
    """
    Iteratively builds a file hash without loading the entire file into memory.
    Designed to process an arbitrary binary file.
    """
    if isinstance(fin, six.string_types):
        fin = open(fin)
    h = hashlib.sha512()
    while True:
        data = fin.read(block_size)
        if not data:
            break
        try:
            h.update(data)
        except TypeError:
            # Fixes Python3 error "TypeError: Unicode-objects must be encoded before hashing".
            h.update(data.encode('utf-8'))
    return h.hexdigest()
