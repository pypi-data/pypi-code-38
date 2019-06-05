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
"""Module headers provides parsing of JSON API headers"""

from ajsonapi.errors import NotAcceptableError, UnsupportedMediaTypeError
from ajsonapi.exceptions import ErrorsException


def parse(request):
    """Parses the headers for errors.

    Args:
        request: Request whose headers are parsed.

    Returns:
        The request's headers.

    Raises:
        An ErrorsException containing the found header errors.
    """

    errors = []
    headers = request.headers

    # [https://jsonapi.org/format/#content-negotiation-servers]
    # Servers MUST respond with a '415 Unsupported Media Type' status code if
    # a request specifies the header 'Content-Type: application/vnd.api+json'
    # with any media type parameters.
    try:
        content_type = headers['Content-Type']
        media_type, *parameters = content_type.split(';')
        if media_type != 'application/vnd.api+json' or parameters:
            errors.append(UnsupportedMediaTypeError())
    except KeyError:
        pass

    # [https://jsonapi.org/format/#content-negotiation-servers]
    # Servers MUST respond with a '406 Not Acceptable' status code if a
    # request's 'Accept' header contains the JSON API media type and all
    # instances of that media type are modified with media type parameters.
    accept = headers['Accept']  # aiohttp provides default Accept header
    json_api_params = []
    accept_values = accept.split(',')
    for accept_value in accept_values:
        media_range, *accept_params = accept_value.split(';')
        if media_range == 'application/vnd.api+json':
            json_api_params.append(accept_params)
    if json_api_params != [] and [] not in json_api_params:
        errors.append(NotAcceptableError())

    if errors:
        raise ErrorsException(errors)
    return headers
