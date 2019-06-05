# Copyright © 2018-2019 Roel van der Goot
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""Module responses provides helper functions for different response types."""

from functools import partial
from json import dumps as json_dumps

from aiohttp import web


def document_response(document=None,
                      status=200,
                      reason=None,
                      headers=None,
                      content_type='application/vnd.api+json',
                      dumps=partial(json_dumps, default=str)):
    """Creates a response from a document."""

    # pylint: disable=too-many-arguments

    if headers is None:
        headers = {}
    return web.Response(body=dumps(document),
                        status=status,
                        reason=reason,
                        headers=headers,
                        content_type=content_type)


def no_data_response(status=204,
                     reason=None,
                     headers=None,
                     content_type='application/vnd.api+json'):
    """Create a 204 NO DATA response."""

    if headers is None:
        headers = {}
    return web.Response(body='',
                        status=status,
                        reason=reason,
                        headers=headers,
                        content_type=content_type)


def errors_response(errors,
                    reason=None,
                    headers=None,
                    content_type='application/vnd.api+json',
                    dumps=partial(json_dumps, default=str)):
    """Creates a response from errors."""

    statuses = {int(error.status) for error in errors}
    if len(statuses) == 1:
        status = next(iter(statuses))
    else:
        status_classes = {status // 100 for status in statuses}
        status = min(status_classes) * 100
    document = {'errors': [error.to_error() for error in errors]}
    return web.Response(body=dumps(document),
                        status=status,
                        reason=reason,
                        headers=headers,
                        content_type=content_type)
