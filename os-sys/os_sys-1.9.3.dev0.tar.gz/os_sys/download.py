from __future__ import absolute_import
"""Download files using requests and save them to a target path
Usage example::
    import hashlib
    # progressbar is provided by progressbar2 on PYPI.
    from progressbar import DataTransferBar
    from requests_download import download, HashTracker, ProgressTracker
    hasher = HashTracker(hashlib.sha256())
    progress = ProgressTracker(DataTransferBar())
    download('https://github.com/takluyver/requests_download/archive/master.zip',
             'requests_download.zip', trackers=(hasher, progress))
    assert hasher.hashobj.hexdigest() == '...'
"""

import requests

__version__ = '0.1.2'

import sys
import requests
import tqdm

def download(url, filename):
    with open(filename, 'wb') as f:
        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')
        print(response)
        go = True
        if go:
            bar = tqdm.tqdm(requests.get(url, stream=True).iter_content(chunk_size=max(int(total/1000), 1024*1024)))
            for data in bar:
                downloaded += len(data)
                f.write(data)
                bar.next()
                done = int(50*downloaded/total)
            bar.close()




import cgi
import email.utils
import getpass
import json
import logging
import mimetypes
import os
import platform
import re
import shutil
import sys


import inspect as _ins
import __main__ as my_module
__all__ = [o[0] for o in _ins.getmembers(my_module) if _ins.isfunction(o[1])]

