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
Utilities for dealing with static file content
"""
from __future__ import absolute_import

import mimetypes
import os
from email.utils import formatdate, parsedate_tz, mktime_tz

from fresco import context
from fresco.response import Response, STATUS_OK, STATUS_NOT_MODIFIED
from fresco.util.wsgi import ClosingIterator

__all__ = 'serve_static_file',


def serve_static_file(path, content_type=None, bufsize=8192, **kwargs):
    """
    Serve a static file located at ``path``.

    :returns: A :class:`~fresco.response.Response` object for the file at
              ``path``
    """

    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return Response.not_found()

    request = context.request
    mod_since = request.get_header('if-modified-since')
    if mod_since is not None:
        try:
            mod_since = mktime_tz(parsedate_tz(mod_since))
        except (TypeError, OverflowError, ValueError):
            return Response.bad_request()
        if int(mtime) <= int(mod_since):
            return Response(status=STATUS_NOT_MODIFIED)

    if content_type is None:
        content_type = mimetypes.guess_type(path)[0]
        if content_type is None:
            content_type = 'application/octet-stream'

    file_wrapper = request.environ.get('wsgi.file_wrapper')
    if file_wrapper is not None:
        content_iterator = lambda f: file_wrapper(f, bufsize)
    else:
        content_iterator = lambda f: \
                ClosingIterator(iter(lambda: f.read(bufsize), ''), f.close)

    try:
        _file = open(path, 'rb')
    except IOError:
        return Response.forbidden()

    return Response(
        status=STATUS_OK,
        content_length=str(os.path.getsize(path)),
        last_modified=formatdate(mtime, localtime=False, usegmt=True),
        content_type=content_type,
        content=content_iterator(_file),
        passthrough=True,
        **kwargs)
