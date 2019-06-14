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
"""Functional tests for DELETE /{collection}/{id} requests."""

import ajsonapi.functests.model  # pylint: disable=unused-import
from ajsonapi.functests.asserts.delete_object import (
    assert_delete_object,
    assert_delete_object_remotely_related,
)
from ajsonapi.functests.asserts.generic import (
    assert_accept_parameters,
    assert_content_type_parameter,
    assert_nonexistent,
    assert_query_fields,
    assert_query_filter,
    assert_query_include,
    assert_query_page,
    assert_query_sort,
)
from ajsonapi.functests.headers import HEADERS
from ajsonapi.functests.model_init import model_init
from ajsonapi.functests.model_objects import UUID_1
from ajsonapi.functests.posts import post_centers_uuid_1


#
# Successful reqeusts/responses
#
async def test_delete_object(client):
    """Functional tests for successfull DELETE /{collection}/{id}."""

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    async with client.delete(url, headers=HEADERS) as response:
        await assert_delete_object(response)


async def test_delete_object_accept_no_paramter(client):
    """Functional test for a DELETE /{collection}/{id} request with an Accept
    header where some (but not all) instances of the JSON API media type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    headers = {
        'Accept':
        'application/vnd.api+json;xxxxxxxx=0,application/vnd.api+json',
    }
    async with client.delete(url, headers=headers) as response:
        await assert_delete_object(response)


async def test_delete_object_no_accept(client):
    """Functional test for a DELETE /{collection}/{id} request without an
    Accept header.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    headers = {}
    async with client.delete(url, headers=headers) as response:
        await assert_delete_object(response)


#
# Failed requests/responses
#
async def test_delete_object_remotely_related(client):
    """Functional tests for failed DELETE /{collection}/{id} where the
    resource object has one or more active remote relationships.
    """
    await model_init(client)

    url = f'/centers/{UUID_1}'
    async with client.delete(url, headers=HEADERS) as response:
        await assert_delete_object_remotely_related(response, url)


async def test_delete_object_nonexistent_collection(client):
    """Functional tests for failed DELETE /{collection}/{id} where the
    {collection} does not exist.
    """
    url = f'/xxxxxxxxs/{UUID_1}'
    async with client.delete(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')


async def test_delete_object_nonexistent_id(client):
    """Functional tests for failed DELETE /{collection}/{id} where the
    {id} does not exist.
    """
    url = f'/centers/{UUID_1}'
    async with client.delete(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_delete_object_malformed_id(client):
    """Functional tests for failed DELETE /{collection}/{id} where the
    {id} does not exist because it is malformed.
    """
    url = '/centers/8888-8888'
    async with client.delete(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url, 'Malformed id.')


async def test_delete_object_content_type_parameter(client):
    """Functional test for a failed DELETE /{collection}/{id} request where
    the Content-Type header contains a parameter.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    headers = {
        'Content-Type': 'application/vnd.api+json;xxxxxxxx=0',
    }
    async with client.delete(url, headers=headers) as response:
        await assert_content_type_parameter(response)


async def test_delete_object_accept_parameters(client):
    """Functional test for a failed DELETE /{collection}/{id} request with the
    Accept header where all instances of the JSON API media type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    headers = {
        'Accept': 'application/vnd.api+json;xxxxxxxx=0',
    }
    async with client.delete(url, headers=headers) as response:
        await assert_accept_parameters(response)


async def test_delete_object_query_include(client):
    """Functional test for a failed DELETE /{collection}/{id}?include=x
    request.
    """

    url = f'/centers/{UUID_1}?include=one_one_local'
    async with client.delete(url, headers=HEADERS) as response:
        await assert_query_include(response)


async def test_delete_object_query_fields(client):
    """Functional test for a failed DELETE /{collection}/{id}?fields[x]=x
    request.
    """

    url = f'/centers/{UUID_1}?fields[centers]=attr_int'
    async with client.delete(url, headers=HEADERS) as response:
        await assert_query_fields(response)


async def test_delete_object_query_sort(client):
    """Functional test for a failed DELETE /{collection}/{id}?fields[x]=x
    request.
    """

    url = f'/centers/{UUID_1}?sort=attr_int'
    async with client.delete(url, headers=HEADERS) as response:
        await assert_query_sort(response)


async def test_delete_object_query_page(client):
    """Functional test for a failed DELETE /{collection}/{id}?page[x]=x
    request.
    """

    url = f'/centers/{UUID_1}?page[number]=0&page[size]=10'
    async with client.delete(url, headers=HEADERS) as response:
        await assert_query_page(response)


async def test_delete_object_query_filter(client):
    """Functional test for a failed DELETE /{collection}/{id}?filter[x]=x
    request.
    """

    url = f'/centers/{UUID_1}?filter[x]=x'
    async with client.delete(url, headers=HEADERS) as response:
        await assert_query_filter(response)
