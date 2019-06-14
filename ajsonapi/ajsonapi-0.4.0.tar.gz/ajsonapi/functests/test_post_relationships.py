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
"""Functional tests for POST /{collection}/{id}/relationships/{relationship}.
"""

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
    assert_centers_uuid_1_many_manys_none,
    assert_centers_uuid_1_many_manys_uuid_51,
    assert_centers_uuid_1_many_manys_uuid_51_52,
    assert_centers_uuid_1_one_manys_none,
    assert_centers_uuid_1_one_manys_uuid_41,
    assert_centers_uuid_1_one_manys_uuid_41_42,
    assert_many_manys_uuid_51_centers_uuid_1,
    assert_many_manys_uuid_52_centers_uuid_1,
    assert_one_manys_uuid_41_center_uuid_1,
    assert_one_manys_uuid_42_center_uuid_1,
)
from ajsonapi.functests.asserts.post_relationships import (
    assert_post_relationship,
    assert_post_to_one_relationship,
)
from ajsonapi.functests.headers import SEND_HEADERS
from ajsonapi.functests.model_objects import (
    JSON_IDENTIFIER_MANY_ONES_UUID_31,
    JSON_IDENTIFIER_NONE,
    JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11,
    JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21,
    JSON_IDENTIFIERS_MANY_MANYS_88888888_999999999,
    JSON_IDENTIFIERS_MANY_MANYS_UUID_51,
    JSON_IDENTIFIERS_MANY_MANYS_UUID_51_52,
    JSON_IDENTIFIERS_NONE,
    JSON_IDENTIFIERS_ONE_MANYS_88888888_999999999,
    JSON_IDENTIFIERS_ONE_MANYS_UUID_41,
    JSON_IDENTIFIERS_ONE_MANYS_UUID_41_42,
    UUID_1,
    UUID_41,
    UUID_51,
)
from ajsonapi.functests.posts import (
    post_centers_uuid_1,
    post_many_manys_uuid_51,
    post_many_manys_uuid_52,
    post_many_ones_uuid_31,
    post_one_manys_uuid_41,
    post_one_manys_uuid_42,
    post_one_one_locals_uuid_11,
    post_one_one_remotes_uuid_21,
)


#
# Successful posts
#
async def test_post_one_to_many_relationship(client):
    """Functional tests for a successful POST
    /{collection}/{id}/relationships/{relationship} request where the request
    is a one-to-many relationship.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_one_manys_uuid_42(client)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_NONE
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_post_relationship(response)

    await assert_centers_uuid_1_one_manys_none(client)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_post_relationship(response)

    await assert_centers_uuid_1_one_manys_uuid_41(client)
    await assert_one_manys_uuid_41_center_uuid_1(client)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41_42
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_post_relationship(response)

    await assert_centers_uuid_1_one_manys_uuid_41_42(client)
    await assert_one_manys_uuid_41_center_uuid_1(client)
    await assert_one_manys_uuid_42_center_uuid_1(client)


async def test_post_many_to_many_relationship(client):
    """Functional tests for a successful POST
    /{collection}/{id}/relationships/{relationship} request where the request
    is a many-to-many relationship.
    """

    await post_centers_uuid_1(client)
    await post_many_manys_uuid_51(client)
    await post_many_manys_uuid_52(client)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_NONE
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_post_relationship(response)

    await assert_centers_uuid_1_many_manys_none(client)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_post_relationship(response)

    await assert_centers_uuid_1_many_manys_uuid_51(client)
    await assert_many_manys_uuid_51_centers_uuid_1(client)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51_52
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_post_relationship(response)

    await assert_centers_uuid_1_many_manys_uuid_51_52(client)
    await assert_many_manys_uuid_51_centers_uuid_1(client)
    await assert_many_manys_uuid_52_centers_uuid_1(client)


async def test_post_relationship_accept_no_parameter(client):
    """Functional tests for a POST
    /{collection}/{id}/relationships/{relationship} request with n Accept
    header where some (but not all) instances of the JSON API medi type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Accept':
        'application/vnd.api+json:xxxxxxxx=0,application/vnd.api+json',
    }

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.post(url, headers=headers, json=json) as response:
        await assert_post_relationship(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.post(url, headers=headers, json=json) as response:
        await assert_post_relationship(response)


async def test_post_relationship_no_accept(client):
    """Functional tests for a POST
    /{collection}/{id}/relationships/{relationship} request without an Accept
    header.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)
    headers = {
        'Content-Type': 'application/vnd.api+json',
    }

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.post(url, headers=headers, json=json) as response:
        await assert_post_relationship(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.post(url, headers=headers, json=json) as response:
        await assert_post_relationship(response)


#
# Failed posts
#
async def test_post_relationship_method_not_allowed(client):
    """Functional test for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the
    relationship is a to-one relationship.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = JSON_IDENTIFIER_NONE
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        assert response.status == 405
        assert 'Allow' in response.headers
        allow = response.headers['Allow']
        assert set(allow.split(',')) == {'GET', 'HEAD', 'PATCH'}

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = JSON_IDENTIFIER_NONE
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        assert response.status == 405
        assert 'Allow' in response.headers
        allow = response.headers['Allow']
        assert set(allow.split(',')) == {'GET', 'HEAD', 'PATCH'}

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = JSON_IDENTIFIER_NONE
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        assert response.status == 405
        assert 'Allow' in response.headers
        allow = response.headers['Allow']
        assert set(allow.split(',')) == {'GET', 'HEAD', 'PATCH'}


async def test_post_relationship_content_type_parameter(client):
    """Functional test for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the
    Content-Type header contains a parameter.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    headers = {
        'Content-Type': 'application/vnd.api_json;xxxxxxxx=0',
    }

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.post(url, headers=headers, json=json) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.post(url, headers=headers, json=json) as response:
        await assert_content_type_parameter(response)


async def test_post_relationship_accept_parameters(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request with an Accept
    header where all instances of the JSON API media type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    headers = {
        'Accept': 'application/vnd.api+json;xxxxxxxx=0',
        'Content-Type': 'application/vnd.api+json',
    }

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.post(url, headers=headers, json=json) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.post(url, headers=headers, json=json) as response:
        await assert_accept_parameters(response)


async def test_post_one_to_one_local_relationship(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the request
    is a one-to-one relationship with the foreign key locally.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_post_to_one_relationship(response)


async def test_post_one_to_one_remote_relationship(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the request
    is a one-to-one relationship with the foreign key remotely.
    """

    await post_centers_uuid_1(client)
    await post_one_one_remotes_uuid_21(client)

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_post_to_one_relationship(response)


async def test_post_many_to_one_relationship(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the request
    is a many-to-one relationship.
    """

    await post_centers_uuid_1(client)
    await post_many_ones_uuid_31(client)

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_post_to_one_relationship(response)


async def test_post_relationship_nonexistent_collection(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where {collection}
    does not exist.
    """

    url = f'/xxxxxxxxs/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_NONE
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/xxxxxxxxs/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_NONE
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')


async def test_post_relationship_nonexistent_id(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where {id} does
    not exist.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = '/centers/88888888/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/relationships/one_manys'
    json = JSON_IDENTIFIERS_NONE
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/relationships/many_manys'
    json = JSON_IDENTIFIERS_NONE
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/88888888')


async def test_post_relationship_nonexistent_relationship(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where
    {relationship} does not exist.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}/relationships/xxxxxxxx'
    json = JSON_IDENTIFIERS_NONE
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, url)


async def test_post_relationship_malformed_id(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the {id}
    is malformed.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = '/centers/8888-8888/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/8888-8888',
                                 'Malformed id.')

    url = '/centers/8888-8888/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/centers/8888-8888',
                                 'Malformed id.')


async def test_post_relationship_document_not_json(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the
    request document is not JSON.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    async with client.post(url, headers=SEND_HEADERS) as response:
        await assert_document_not_json(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    async with client.post(url, headers=SEND_HEADERS) as response:
        await assert_document_not_json(response)


async def test_post_relationship_data_missing(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the
    request document does not contain a data member.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = {}
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = {}
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing(response)


async def test_post_relationship_data_malformed(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the
    request document contains a malformed data member.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = {
        'data': None,
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = {
        'data': None,
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed(response)


async def test_post_relationship_data_missing_type(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the request
    document's resource object does not contain a type.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = {
        'data': [
            {
                'id': UUID_41,
            },
        ]
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_type(response, '/data/0')

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = {
        'data': [
            {
                'id': UUID_51,
            },
        ]
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_type(response, '/data/0')


async def test_post_relationship_data_missing_id(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the request
    document's resource object does not contain an id.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = {
        'data': [
            {
                'type': 'one_manys',
            },
        ]
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_id(response, '/data/0')

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = {
        'data': [
            {
                'type': 'many_manys',
            },
        ]
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_id(response, '/data/0')


async def test_post_relationship_data_invalid_type(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the request
    document's resource object contains an invalid type.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_many_manys_uuid_51(client)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = {
        'data': [
            {
                'type': 'xxxxxxxxs',
                'id': UUID_41,
            },
        ]
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
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
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_invalid_type(response, '/data/0/type/xxxxxxxxs')


async def test_post_relationship_data_malformed_id(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the request
    document's resource object contains a malformed type.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = {
        'data': [
            {
                'type': 'one_manys',
                'id': '8888-8888',
            },
        ]
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
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
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed_id(response, '/data/0/id/8888-8888')


async def test_post_relationship_data_nonexistent_id(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship} request where the request
    document's resource object contains a nonexistent id.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_88888888_999999999
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(
            response, {'/data/0/id/88888888', '/data/1/id/999999999'})

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_88888888_999999999
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(
            response, {'/data/0/id/88888888', '/data/1/id/999999999'})


async def test_post_relationship_query_include(client):
    """Functional test for a failed POST
    /{collection}/{id}/relationships/{relationship}?include=x request.
    """

    url = f'/centers/{UUID_1}/relationships/one_manys?include=center'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_include(response)

    url = f'/centers/{UUID_1}/relationships/many_manys?include=centers'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_include(response)


async def test_post_relationships_query_fields(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship}?fields=x request.
    """

    url = f'/centers/{UUID_1}/relationships/one_manys?fields=attr_int'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_fields(response)

    url = f'/centers/{UUID_1}/relationships/many_manys?fields=attr_int'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_fields(response)


async def test_post_relationships_query_sort(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship}?sort=x request.
    """

    url = f'/centers/{UUID_1}/relationships/one_manys?sort=attr_int'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_sort(response)

    url = f'/centers/{UUID_1}/relationships/many_manys?sort=attr_int'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_sort(response)


async def test_post_relationships_query_page(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship}?page[x]=x request.
    """

    url = (f'/centers/{UUID_1}/relationships/one_manys?'
           'page[number]=0&page[size]=10')
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_page(response)

    url = (f'/centers/{UUID_1}/relationships/many_manys?'
           'page[number]=0&page[size]=10')
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_page(response)


async def test_post_relationships_query_filter(client):
    """Functional tests for a failed POST
    /{collection}/{id}/relationships/{relationship}?filter[x]=x request.
    """

    url = f'/centers/{UUID_1}/relationships/one_manys?filter[x]=x'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_filter(response)

    url = f'/centers/{UUID_1}/relationships/many_manys?filter[x]=x'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_filter(response)
