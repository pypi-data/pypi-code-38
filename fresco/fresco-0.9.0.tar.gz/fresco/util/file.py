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
from __future__ import absolute_import

from contextlib import contextmanager
from os import rename, makedirs
from os.path import dirname, isdir
from tempfile import NamedTemporaryFile


@contextmanager
def atomic_writer(path, mode=0o644):
    """
    Write to path in an atomic operation. Auto creates any directories leading
    up to ``path``
    """
    d = dirname(path)
    if d:
        makedir(d)
    tmpfile = NamedTemporaryFile(delete=False, dir=d)
    yield tmpfile
    tmpfile.close()
    rename(tmpfile.name, path)


def makedir(path):
    """
    Create a directory at ``path``.
    Unlike ``os.makedirs`` don't raise an error if ``path`` already exists.
    """
    try:
        makedirs(path)
    except OSError:
        # Path already exists or cannot be created
        if not isdir(path):
            raise
