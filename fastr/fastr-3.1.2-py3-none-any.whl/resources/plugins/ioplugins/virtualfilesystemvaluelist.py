# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains the VirtualFileSystemValueList plugin for fastr
"""

import urllib.parse
import fastr
from fastr import exceptions, resources
from fastr.core.ioplugin import IOPlugin


class VirtualFileSystemValueList(IOPlugin):
    """
    The VirtualFileSystemValueList an expand-only type of IOPlugin. No URLs
    can actually be fetched, but it can expand a single URL into a larger
    amount of URLs. A ``vfslist://`` URL basically is a url that points to a
    file using vfs. This file then contains a number lines each containing
    another URL.

    If the contents of a file ``vfs://mount/some/path/contents`` would be::

        vfs://mount/some/path/file1.txt
        vfs://mount/some/path/file2.txt
        vfs://mount/some/path/file3.txt
        vfs://mount/some/path/file4.txt

    Then using the URL ``vfslist://mount/some/path/contents`` as source data
    would result in the four files being pulled.

    .. note:: The URLs in a vfslist file do not have to use the ``vfs`` scheme,
              but can use any scheme known to the Fastr system.
    """
    scheme = 'vfslist'

    def __init__(self):
        super(VirtualFileSystemValueList, self).__init__()

    def expand_url(self, url):
        if fastr.data.url.get_url_scheme(url) != 'vfslist':
            raise exceptions.FastrValueError('URL not of vfslist type!')

        # Retrieve base path
        parsed = urllib.parse.urlparse(url)
        listurl = urllib.parse.urlunparse(urllib.parse.ParseResult(scheme='vfs', netloc=parsed.netloc, path=parsed.path, params='', query='', fragment=''))
        listpath = resources.ioplugins.url_to_path(listurl)

        with open(listpath, 'r') as file_handle:
            data = file_handle.read()

        valuelist = tuple((None, x.strip()) for x in data.strip().split('\n'))
        return valuelist
