# Copyright © 2019 Roel van der Goot
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
"""Functional tests for PATCH /{collection}/{id}/{related_resource}."""

import ajsonapi.functests.model  # pylint: disable=unused-import
from ajsonapi.functests.headers import SEND_HEADERS
from ajsonapi.functests.model_objects import UUID_1


#
# Failed requests/responses
#
async def test_patch_related_resource_method_not_allowed(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/{related_resource} request.
    """

    url = f'/centers/{UUID_1}/one_one_local'
    async with client.patch(url, headers=SEND_HEADERS) as response:
        assert response.status == 405
        assert 'Allow' in response.headers
        allow = response.headers['Allow']
        assert set(allow.split(',')) == {'GET', 'HEAD'}

    url = f'/centers/{UUID_1}/one_one_remote'
    async with client.patch(url, headers=SEND_HEADERS) as response:
        assert response.status == 405
        assert 'Allow' in response.headers
        allow = response.headers['Allow']
        assert set(allow.split(',')) == {'GET', 'HEAD'}

    url = f'/centers/{UUID_1}/many_one'
    async with client.patch(url, headers=SEND_HEADERS) as response:
        assert response.status == 405
        assert 'Allow' in response.headers
        allow = response.headers['Allow']
        assert set(allow.split(',')) == {'GET', 'HEAD'}

    url = f'/centers/{UUID_1}/one_manys'
    async with client.patch(url, headers=SEND_HEADERS) as response:
        assert response.status == 405
        assert 'Allow' in response.headers
        allow = response.headers['Allow']
        assert set(allow.split(',')) == {'GET', 'HEAD'}

    url = f'/centers/{UUID_1}/many_manys'
    async with client.patch(url, headers=SEND_HEADERS) as response:
        assert response.status == 405
        assert 'Allow' in response.headers
        allow = response.headers['Allow']
        assert set(allow.split(',')) == {'GET', 'HEAD'}
