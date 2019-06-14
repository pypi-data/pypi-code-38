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
"""Common delete operations for functional tests."""

from ajsonapi.functests.asserts.delete_object import assert_delete_object
from ajsonapi.functests.headers import HEADERS
from ajsonapi.functests.model_objects import (
    UUID_11,
    UUID_21,
    UUID_31,
    UUID_41,
    UUID_42,
    UUID_51,
    UUID_52,
)


async def delete_one_one_locals_uuid_11(client):
    """Successful DELETE /one_one_locals/UUID_11."""
    url = f'/one_one_locals/{UUID_11}'
    async with client.delete(url, headers=HEADERS) as response:
        return await assert_delete_object(response)


async def delete_one_one_remotes_uuid_21(client):
    """Successful DELETE /one_one_remotes/UUID_21."""
    url = f'/one_one_remotes/{UUID_21}'
    async with client.delete(url, headers=HEADERS) as response:
        return await assert_delete_object(response)


async def delete_many_ones_uuid_31(client):
    """Successful DELETE /many_ones/UUID_31."""
    url = f'/many_ones/{UUID_31}'
    async with client.delete(url, headers=HEADERS) as response:
        return await assert_delete_object(response)


async def delete_one_manys_uuid_41(client):
    """Successful DELETE /one_manys/UUID_41."""
    url = f'/one_manys/{UUID_41}'
    async with client.delete(url, headers=HEADERS) as response:
        return await assert_delete_object(response)


async def delete_one_manys_uuid_42(client):
    """Successful DELETE /one_manys/UUID_42."""
    url = f'/one_manys/{UUID_42}'
    async with client.delete(url, headers=HEADERS) as response:
        return await assert_delete_object(response)


async def delete_many_manys_uuid_51(client):
    """Successful DELETE /many_manys/UUID_51."""
    url = f'/many_manys/{UUID_51}'
    async with client.delete(url, headers=HEADERS) as response:
        return await assert_delete_object(response)


async def delete_many_manys_uuid_52(client):
    """Successful DELETE /many_manys/UUID_52."""
    url = f'/many_manys/{UUID_52}'
    async with client.delete(url, headers=HEADERS) as response:
        return await assert_delete_object(response)
