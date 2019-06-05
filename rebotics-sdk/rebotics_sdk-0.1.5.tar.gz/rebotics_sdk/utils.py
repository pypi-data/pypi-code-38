import sys
import errno
import hashlib
import os
from functools import partial
from timeit import default_timer

import requests
from six.moves.urllib_parse import urlparse


def hash_file(file, block_size=65536):
    hash_ = hashlib.md5()
    for buf in iter(partial(file.read, block_size), b''):
        hash_.update(buf)

    return hash_.hexdigest()


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def get_filename_from_url(url):
    return urlparse(url).path.split('/')[-1]


def download_file(url, filepath=None):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    if filepath is None:
        # TODO: decode url, get filename
        filepath = get_filename_from_url(url)

    with open(filepath, 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)


class Timer(object):
    def __init__(self):
        self.timer = default_timer

    def __enter__(self):
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        end = self.timer()
        self.elapsed_secs = end - self.start
        self.elapsed = self.elapsed_secs * 1000  # millisecs


def accept_file(self, file_):
    if isinstance(file_, str):
        if '://' in file_:
            # URL supplied
            response = self.requests.get(url=file_)
            file_io = BytesIO(response.content)
        else:
            file_io = open(file_, 'rb')
    else:
        file_io = file_
        assert hasattr(file_io, 'read'), 'Non file like object was supplied'

    return file_io
