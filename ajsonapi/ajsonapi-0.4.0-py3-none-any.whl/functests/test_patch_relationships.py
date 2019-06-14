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
"""Functional tests for PATCH /{collection}/{id}/relationships/{relationship}.
"""
# pylint: disable=too-many-lines

import ajsonapi.functests.model  # pylint: disable=unused-import
from ajsonapi.functests.asserts.generic import (
    assert_accept_parameters,
    assert_content_type_parameter,
    assert_data_invalid_type,
    assert_data_malformed,
    assert_data_malformed_id,
    assert_data_missing,
    assert_data_missing_id,
    assert_data_missing_type,
    assert_data_nonexistent_id,
    assert_document_not_json,
    assert_nonexistent,
    assert_query_fields,
    assert_query_filter,
    assert_query_include,
    assert_query_page,
    assert_query_sort,
)
from ajsonapi.functests.asserts.get_relationships import (
    assert_get_to_many_relationship,
    assert_get_to_one_relationship,
)
from ajsonapi.functests.asserts.patch_relationships import (
    assert_patch_relationship,
    assert_patch_relationship_conflict,
)
from ajsonapi.functests.headers import HEADERS, SEND_HEADERS
from ajsonapi.functests.model_objects import (
    JSON_IDENTIFIER_MANY_ONES_UUID_31,
    JSON_IDENTIFIER_MANY_ONES_UUID_32,
    JSON_IDENTIFIER_NONE,
    JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11,
    JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_12,
    JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21,
    JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_22,
    JSON_IDENTIFIERS_MANY_MANYS_88888888_999999999,
    JSON_IDENTIFIERS_MANY_MANYS_UUID_51,
    JSON_IDENTIFIERS_MANY_MANYS_UUID_51_52,
    JSON_IDENTIFIERS_MANY_MANYS_UUID_52_53,
    JSON_IDENTIFIERS_NONE,
    JSON_IDENTIFIERS_ONE_MANYS_88888888_999999999,
    JSON_IDENTIFIERS_ONE_MANYS_UUID_41,
    JSON_IDENTIFIERS_ONE_MANYS_UUID_41_42,
    JSON_IDENTIFIERS_ONE_MANYS_UUID_42_43,
    UUID_1,
    UUID_2,
    UUID_11,
    UUID_12,
    UUID_21,
    UUID_22,
    UUID_31,
    UUID_32,
    UUID_41,
    UUID_42,
    UUID_43,
    UUID_51,
    UUID_52,
    UUID_53,
)
from ajsonapi.functests.posts import (
    post_centers_uuid_1,
    post_centers_uuid_2,
    post_many_manys_uuid_51,
    post_many_manys_uuid_52,
    post_many_manys_uuid_53,
    post_many_ones_uuid_31,
    post_many_ones_uuid_32,
    post_one_manys_uuid_41,
    post_one_manys_uuid_42,
    post_one_manys_uuid_43,
    post_one_one_locals_uuid_11,
    post_one_one_locals_uuid_12,
    post_one_one_remotes_uuid_21,
    post_one_one_remotes_uuid_22,
)


#
# Successful reqeusts/responses
#
async def test_patch_one_to_one_local_relationship(client):
    """Functional tests for a successful PATCH
    /{collection}/{id}/relationships/{relationship} request where the request
    is a one-to-one local relationship.
    """

    await post_centers_uuid_1(client)
    await post_centers_uuid_2(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_locals_uuid_12(client)

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert obj == {'type': 'one_one_locals', 'id': UUID_11}

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_12
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert obj == {'type': 'one_one_locals', 'id': UUID_12}

    url = f'/centers/{UUID_2}/relationships/one_one_local'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_12
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship_conflict(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert obj is None

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = JSON_IDENTIFIER_NONE
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert obj is None


async def test_patch_one_to_one_remote_relationship(client):
    """Functional tests for a successful PATCH
    /{collection}/{id}/relationships/{relationship} request where the request
    is a one-to-one remote relationship.
    """

    await post_centers_uuid_1(client)
    await post_centers_uuid_2(client)
    await post_one_one_remotes_uuid_21(client)
    await post_one_one_remotes_uuid_22(client)

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert obj == {'type': 'one_one_remotes', 'id': UUID_21}

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_22
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert obj == {'type': 'one_one_remotes', 'id': UUID_22}

    url = f'/centers/{UUID_2}/relationships/one_one_remote'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_22
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship_conflict(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert obj is None

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = JSON_IDENTIFIER_NONE
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert obj is None


async def test_patch_many_to_one_relationship(client):
    """Functional tests for a successful PATCH
    /{collection}/{id}/relationships/{relationship} request where the request
    is a many-to-one relationship.
    """

    await post_centers_uuid_1(client)
    await post_centers_uuid_2(client)
    await post_many_ones_uuid_31(client)
    await post_many_ones_uuid_32(client)

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert obj == {'type': 'many_ones', 'id': UUID_31}

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_32
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert obj == {'type': 'many_ones', 'id': UUID_32}

    url = f'/centers/{UUID_2}/relationships/many_one'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_32
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert obj == {'type': 'many_ones', 'id': UUID_32}

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = JSON_IDENTIFIER_NONE
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert obj is None


async def test_patch_one_to_many_relationship(client):
    """Functional tests for a successful PATCH
    /{collection}/{id}/relationships/{relationship} request where the request
    is a one-to-many relationship.
    """

    await post_centers_uuid_1(client)
    await post_centers_uuid_2(client)
    await post_one_manys_uuid_41(client)
    await post_one_manys_uuid_42(client)
    await post_one_manys_uuid_43(client)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41_42
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        assert len(data) == 2
        assert {'type': 'one_manys', 'id': UUID_41} in data
        assert {'type': 'one_manys', 'id': UUID_42} in data

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_42_43
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        assert len(data) == 2
        assert {'type': 'one_manys', 'id': UUID_42} in data
        assert {'type': 'one_manys', 'id': UUID_43} in data

    url = f'/centers/{UUID_2}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41_42
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        assert len(data) == 2
        assert {'type': 'one_manys', 'id': UUID_41} in data
        assert {'type': 'one_manys', 'id': UUID_42} in data

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_NONE
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        assert data == []


async def test_patch_many_to_many_relationship(client):
    """Functional tests for a successful PATCH
    /{collection}/{id}/relationships/{relationship} request where the request
    is a many-to-many relationship.
    """

    await post_centers_uuid_1(client)
    await post_centers_uuid_2(client)
    await post_many_manys_uuid_51(client)
    await post_many_manys_uuid_52(client)
    await post_many_manys_uuid_53(client)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51_52
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        assert len(data) == 2
        assert {'type': 'many_manys', 'id': UUID_51} in data
        assert {'type': 'many_manys', 'id': UUID_52} in data

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_52_53
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        assert len(data) == 2
        assert {'type': 'many_manys', 'id': UUID_52} in data
        assert {'type': 'many_manys', 'id': UUID_53} in data

    url = f'/centers/{UUID_2}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51_52
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        assert len(data) == 2
        assert {'type': 'many_manys', 'id': UUID_51} in data
        assert {'type': 'many_manys', 'id': UUID_52} in data

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_NONE
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_relationship(response)

    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        assert data == []


async def test_patch_relationship_accept_no_parameter(client):
    """Functional tests for a PATCH
    /{collection}/{id}/relationships/{relationship} request with n Accept
    header where some (but not all) instances of the JSON API medi type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Accept':
        'application/vnd.api+json:xxxxxxxx=0,application/vnd.api+json',
    }

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_patch_relationship(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_patch_relationship(response)

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_patch_relationship(response)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_patch_relationship(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_patch_relationship(response)


async def test_patch_relationship_no_accept(client):
    """Functional tests for a PATCH
    /{collection}/{id}/relationships/{relationship} request without an Accept
    header.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)
    headers = {
        'Content-Type': 'application/vnd.api+json',
    }

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_patch_relationship(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_patch_relationship(response)

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_patch_relationship(response)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_patch_relationship(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_patch_relationship(response)


#
# Failed requests/responses
#
async def test_patch_relationship_content_type_parameter(client):
    """Functional test for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request where the
    Content-Type header contains a parameter.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    headers = {
        'Content-Type': 'application/vnd.api_json;xxxxxxxx=0',
    }

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_content_type_parameter(response)


async def test_patch_relationship_accept_parameters(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request with an Accept
    header where all instances of the JSON API media type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    headers = {
        'Accept': 'application/vnd.api+json;xxxxxxxx=0',
        'Content-Type': 'application/vnd.api+json',
    }

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_accept_parameters(response)


async def test_patch_relationship_nonexistent_collection(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request where the
    (collection) does not exist.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = f'/xxxxxxxxs/{UUID_1}/relationships/one_one_local'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/xxxxxxxxs/{UUID_1}/relationships/one_one_remote'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/xxxxxxxxs/{UUID_1}/relationships/many_one'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/xxxxxxxxs/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/xxxxxxxxs/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')


async def test_patch_relationship_nonexistent_id(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request where the {id}
    does not exist.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = '/centers/88888888/relationships/one_one_local'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/relationships/one_one_remote'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/relationships/many_one'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/88888888')


async def test_patch_relationship_nonexistent_relationship(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request where the
    (relationship) does not exist.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}/relationships/xxxxxxxx'
    json = {
        'data': {
            'type': 'xxxxxxxxs',
            'id': UUID_1,
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, url)


async def test_patch_relationship_malformed_id(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request where the {id}
    is malformed.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = '/centers/8888-8888/relationships/one_one_local'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/8888-8888',
                                 'Malformed id.')

    url = '/centers/8888-8888/relationships/one_one_remote'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/8888-8888',
                                 'Malformed id.')

    url = '/centers/8888-8888/relationships/many_one'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/8888-8888',
                                 'Malformed id.')

    url = '/centers/8888-8888/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/8888-8888',
                                 'Malformed id.')

    url = '/centers/8888-8888/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/8888-8888',
                                 'Malformed id.')


async def test_patch_relationship_document_not_json(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request where the
    request document is not JSON.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    async with client.patch(url, headers=SEND_HEADERS) as response:
        await assert_document_not_json(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    async with client.patch(url, headers=SEND_HEADERS) as response:
        await assert_document_not_json(response)

    url = f'/centers/{UUID_1}/relationships/many_one'
    async with client.patch(url, headers=SEND_HEADERS) as response:
        await assert_document_not_json(response)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    async with client.patch(url, headers=SEND_HEADERS) as response:
        await assert_document_not_json(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    async with client.patch(url, headers=SEND_HEADERS) as response:
        await assert_document_not_json(response)


async def test_patch_relationship_data_missing(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request where the
    request document does not contain a data member.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = {}
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = {}
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing(response)

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = {}
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing(response)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = {}
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = {}
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing(response)


async def test_patch_relationship_data_malformed(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request where the
    request document contains a malformed data member.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = {
        'data': [],
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = {
        'data': [],
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed(response)

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = {
        'data': [],
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed(response)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = {
        'data': None,
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = {
        'data': None,
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed(response)


async def test_patch_relationship_data_missing_type(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request where the request
    document's resource object does not contain a type.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = {
        'data': {
            'id': UUID_11,
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_type(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = {
        'data': {
            'id': UUID_21,
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_type(response)

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = {
        'data': {
            'id': UUID_31,
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_type(response)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = {
        'data': [
            {
                'id': UUID_41,
            },
        ]
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_type(response, '/data/0')

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = {
        'data': [
            {
                'id': UUID_51,
            },
        ]
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_type(response, '/data/0')


async def test_patch_relationship_data_missing_id(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request where the request
    document's resource object does not contain an id.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = {
        'data': {
            'type': 'one_one_locals',
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_id(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = {
        'data': {
            'type': 'one_one_remotes',
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_id(response)

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = {
        'data': {
            'type': 'many_ones',
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_id(response)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = {
        'data': [
            {
                'type': 'one_manys',
            },
        ]
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_id(response, '/data/0')

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = {
        'data': [
            {
                'type': 'many_manys',
            },
        ]
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_id(response, '/data/0')


async def test_patch_relationship_data_invalid_type(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request where the request
    document's resource object contains an invalid type.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = {
        'data': {
            'type': 'xxxxxxxxs',
            'id': UUID_11,
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_invalid_type(response, '/data/type/xxxxxxxxs')

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = {
        'data': {
            'type': 'xxxxxxxxs',
            'id': UUID_21,
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_invalid_type(response, '/data/type/xxxxxxxxs')

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = {
        'data': {
            'type': 'xxxxxxxxs',
            'id': UUID_31,
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_invalid_type(response, '/data/type/xxxxxxxxs')

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = {
        'data': [
            {
                'type': 'xxxxxxxxs',
                'id': UUID_41,
            },
        ]
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_invalid_type(response, '/data/0/type/xxxxxxxxs')

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = {
        'data': [
            {
                'type': 'xxxxxxxxs',
                'id': UUID_51,
            },
        ]
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_invalid_type(response, '/data/0/type/xxxxxxxxs')


async def test_patch_relationship_data_malformed_id(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request where the request
    document's resource object contains a malformed type.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = {
        'data': {
            'type': 'one_one_locals',
            'id': '8888-8888',
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed_id(response, '/data/id/8888-8888')

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = {
        'data': {
            'type': 'one_one_remotes',
            'id': '8888-8888',
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed_id(response, '/data/id/8888-8888')

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = {
        'data': {
            'type': 'many_ones',
            'id': '8888-8888',
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed_id(response, '/data/id/8888-8888')

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = {
        'data': [
            {
                'type': 'one_manys',
                'id': '8888-8888',
            },
        ]
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed_id(response, '/data/0/id/8888-8888')

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = {
        'data': [
            {
                'type': 'many_manys',
                'id': '8888-8888',
            },
        ]
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed_id(response, '/data/0/id/8888-8888')


async def test_patch_relationship_data_nonexistent_id(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship} request where the request
    document's resource object contains a nonexistent id.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = {
        'data': {
            'type': 'one_one_locals',
            'id': '88888888',
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(response, {'/data/id/88888888'})

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = {
        'data': {
            'type': 'one_one_remotes',
            'id': '88888888',
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(response, {'/data/id/88888888'})

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = {
        'data': {
            'type': 'many_ones',
            'id': '88888888',
        },
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(response, {'/data/id/88888888'})

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_88888888_999999999
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(
            response, {'/data/0/id/88888888', '/data/1/id/999999999'})

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_88888888_999999999
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(
            response, {'/data/0/id/88888888', '/data/1/id/999999999'})


async def test_patch_relationship_query_include(client):
    """Functional test for a failed PATCH
    /{collection}/{id}/relationships/{relationship}?include=x request.
    """

    url = f'/centers/{UUID_1}/relationships/one_one_local?include=center'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_include(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote?include=center'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_include(response)

    url = f'/centers/{UUID_1}/relationships/many_one?include=centers'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_include(response)

    url = f'/centers/{UUID_1}/relationships/one_manys?include=center'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_include(response)

    url = f'/centers/{UUID_1}/relationships/many_manys?include=centers'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_include(response)


async def test_patch_relationships_query_fields(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship}?fields=x request.
    """

    url = f'/centers/{UUID_1}/relationships/one_one_local?fields=attr_int'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_fields(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote?fields=attr_int'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_fields(response)

    url = f'/centers/{UUID_1}/relationships/many_one?fields=attr_int'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_fields(response)

    url = f'/centers/{UUID_1}/relationships/one_manys?fields=attr_int'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_fields(response)

    url = f'/centers/{UUID_1}/relationships/many_manys?fields=attr_int'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_fields(response)


async def test_patch_relationships_query_sort(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship}?sort=x request.
    """

    url = f'/centers/{UUID_1}/relationships/one_one_local?sort=attr_int'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_sort(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote?sort=attr_int'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_sort(response)

    url = f'/centers/{UUID_1}/relationships/many_one?sort=attr_int'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_sort(response)

    url = f'/centers/{UUID_1}/relationships/one_manys?sort=attr_int'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_sort(response)

    url = f'/centers/{UUID_1}/relationships/many_manys?sort=attr_int'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_sort(response)


async def test_patch_relationships_query_page(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship}?page[x]=x request.
    """

    url = (f'/centers/{UUID_1}/relationships/one_one_local?'
           'page[number]=0&page[size]=10')
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_page(response)

    url = (f'/centers/{UUID_1}/relationships/one_one_remote?'
           'page[number]=0&page[size]=10')
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_page(response)

    url = (f'/centers/{UUID_1}/relationships/many_one?'
           'page[number]=0&page[size]=10')
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_page(response)

    url = (f'/centers/{UUID_1}/relationships/one_manys?'
           'page[number]=0&page[size]=10')
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_page(response)

    url = (f'/centers/{UUID_1}/relationships/many_manys?'
           'page[number]=0&page[size]=10')
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_page(response)


async def test_patch_relationships_query_filter(client):
    """Functional tests for a failed PATCH
    /{collection}/{id}/relationships/{relationship}?filter[x]=x request.
    """

    url = f'/centers/{UUID_1}/relationships/one_one_local?filter[x]=x'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_filter(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote?filter[x]=x'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_filter(response)

    url = f'/centers/{UUID_1}/relationships/many_one?filter[x]=x'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_filter(response)

    url = f'/centers/{UUID_1}/relationships/one_manys?filter[x]=x'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_filter(response)

    url = f'/centers/{UUID_1}/relationships/many_manys?filter[x]=x'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_filter(response)
