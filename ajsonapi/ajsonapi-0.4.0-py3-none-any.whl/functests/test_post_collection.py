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
"""Functional tests for POST /{collection}."""

import ajsonapi.functests.model  # pylint: disable=unused-import
from ajsonapi.functests.asserts.generic import (
    assert_accept_parameters,
    assert_content_type_parameter,
    assert_data_invalid_attribute,
    assert_data_invalid_relationship,
    assert_data_invalid_relationship_type,
    assert_data_invalid_type,
    assert_data_malformed,
    assert_data_malformed_relationship,
    assert_data_malformed_relationship_data,
    assert_data_malformed_relationship_id,
    assert_data_missing,
    assert_data_missing_relationship_id,
    assert_data_missing_relationship_type,
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
from ajsonapi.functests.asserts.get_object import (
    assert_get_centers_1_related,
    assert_get_centers_uuid_1_related,
)
from ajsonapi.functests.asserts.model import assert_centers_1_related
from ajsonapi.functests.asserts.post_collection import (
    assert_post_collection_data_duplicate_id,
    assert_post_collection_data_malformed_uuid,
    assert_post_collection_nonexistent_collection,
    assert_post_collection_with_id,
    assert_post_collection_without_id,
)
from ajsonapi.functests.deletes import (
    delete_many_manys_uuid_51,
    delete_many_manys_uuid_52,
    delete_many_ones_uuid_31,
    delete_one_manys_uuid_41,
    delete_one_manys_uuid_42,
    delete_one_one_locals_uuid_11,
    delete_one_one_remotes_uuid_21,
)
from ajsonapi.functests.headers import HEADERS, SEND_HEADERS
from ajsonapi.functests.model_objects import (
    JSON_CENTERS_1,
    JSON_CENTERS_1_RELATIONSHIPS,
    JSON_CENTERS_UUID_1,
    JSON_CENTERS_UUID_1_DATA_INVALID_RELATIONSHIP_TYPES,
    JSON_CENTERS_UUID_1_DATA_MALFORMED_RELATIONSHIP_IDS,
    JSON_CENTERS_UUID_1_DATA_MISSING_RELATIONSHIP_IDS,
    JSON_CENTERS_UUID_1_DATA_MISSING_RELATIONSHIP_TYPES,
    JSON_CENTERS_UUID_1_RELATIONSHIPS,
    UUID_1,
    UUID_11,
    UUID_21,
    UUID_31,
    UUID_41,
    UUID_42,
    UUID_51,
    UUID_52,
)
from ajsonapi.functests.posts import (
    post_many_manys_uuid_51,
    post_many_manys_uuid_52,
    post_many_ones_uuid_31,
    post_one_manys_uuid_41,
    post_one_manys_uuid_42,
    post_one_one_locals_uuid_11,
    post_one_one_remotes_uuid_21,
)


#
# Successful requests
#
async def test_post_collection_without_id(client):
    """Functional tests for a successful POST /{collection} request where the
    data does not contain an id.
    """

    url = '/centers'
    json = JSON_CENTERS_1
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        document = await assert_post_collection_without_id(response)
        data = document['data']
        assert 'attributes' in data
        attributes = data['attributes']
        assert attributes['attr_int'] == 1
        assert attributes['attr_str'] == 'one'


async def test_post_collection_with_id(client):
    """Functional tests for a successful POST /{collection} request where the
    data contains an id.
    """

    url = '/centers'
    json = JSON_CENTERS_UUID_1
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_post_collection_with_id(response)


async def test_post_collection_without_id_relationships(client):
    """Functional tests for a successful POST /{collection} request where the
    data does not contain an id.
    """

    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_one_manys_uuid_42(client)
    await post_many_manys_uuid_51(client)
    await post_many_manys_uuid_52(client)

    url = '/centers'
    json = JSON_CENTERS_1_RELATIONSHIPS
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        document = await assert_post_collection_without_id(response)
        center = document['data']
        assert_centers_1_related(center)

    url = f'/centers/1'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_1_related(response)


async def test_post_collection_with_id_relationships(client):
    """Functional tests for a successful POST /{collection} request where the
    data contains an id.
    """

    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_one_manys_uuid_42(client)
    await post_many_manys_uuid_51(client)
    await post_many_manys_uuid_52(client)

    url = '/centers'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_post_collection_with_id(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_related(response)


async def test_post_collection_accept_no_parameter(client):
    """Functional tests for a successful POST /{collection} request with an
    Accept header where some (but not all) instances of the JSON API media
    type ('application/vnd.api+json') are modified with media type parameters.
    """

    url = '/centers'
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Accept':
        'application/vnd.api+json;xxxxxxxx=0,application/vnd.api+json',
    }
    json = JSON_CENTERS_1
    async with client.post(url, headers=headers, json=json) as response:
        document = await assert_post_collection_without_id(response)
        data = document['data']
        assert 'attributes' in data
        attributes = data['attributes']
        assert attributes['attr_int'] == 1
        assert attributes['attr_str'] == 'one'


async def test_post_collection_no_accept(client):
    """Functional tests for a successful POST /{collection} request without an
    Accept header.
    """

    url = '/centers'
    headers = {
        'Content-Type': 'application/vnd.api+json',
    }
    json = JSON_CENTERS_UUID_1
    async with client.post(url, headers=headers, json=json) as response:
        await assert_post_collection_with_id(response)


#
# Failed requests
#
async def test_post_collection_content_type_parameter(client):
    """Functional tests for a failed POST /{collection} request where the
    Content-Type header contains a parameter.
    """

    url = '/centers'
    headers = {
        'Content-Type': 'application/vnd.api+json;xxxxxxxx=0',
        'Accept': 'application/vnd.api+json',
    }
    json = JSON_CENTERS_UUID_1
    async with client.post(url, headers=headers, json=json) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_post_collection_accept_parameters(client):
    """Functional tests for a failed GET /{collection} request with the Accept
    header where all instances of the JSON API media type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    url = '/centers'
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Accept': 'application/vnd.api+json;xxxxxxxx=0',
    }
    json = JSON_CENTERS_UUID_1
    async with client.post(url, headers=headers, json=json) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_post_collection_query_include(client):
    """Functional tests for a failed POST /{collection}?include=x request."""

    url = '/centers?include=one_one_local'
    json = JSON_CENTERS_UUID_1
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_include(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_post_collection_query_fields(client):
    """Functional tests for a failed POST /{collection}?fields[x]=x request."""

    url = '/centers?fields[centers]=attr_int'
    json = JSON_CENTERS_UUID_1
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_fields(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_post_collection_query_sort(client):
    """Functional tests for a failed POST /{collection}?sort=x request."""

    url = '/centers?sort=attr_int'
    json = JSON_CENTERS_UUID_1
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_sort(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_post_collection_query_page(client):
    """Functional tests for a failed POST /{collection}?page[x]=x request."""

    url = '/centers?page[number]=0&page[size]=10'
    json = JSON_CENTERS_UUID_1
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_page(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_post_collection_query_filter(client):
    """Functional tests for a failed POST /{collection}?filter[x]=x request."""

    url = '/centers?filter[x]=x'
    json = JSON_CENTERS_UUID_1
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_filter(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_post_collection_data_duplicate_id(client):
    """Functional tests for a failed POST /{collection} request where the data
    contains an id that already exists.
    """

    url = '/centers'
    center_id = UUID_1
    json = JSON_CENTERS_UUID_1
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_post_collection_with_id(response)

    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        pointer = f'/data/id/{center_id}'
        await assert_post_collection_data_duplicate_id(response, pointer)


async def test_post_collection_nonexistent_collection(client):
    """Functional test for a failed POST /{collection} request where
    {collection} does not exist."""

    url = '/xxxxxxxxxs'
    json = {
        'data': {
            'type': 'xxxxxxxxxs',
            'attributes': {
                'attr_int': 1,
                'attr_str': 'one',
            }
        }
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_post_collection_nonexistent_collection(response, url)


async def test_post_collection_document_not_json(client):
    """Functional test for a failed POST /{collection} request where the
    request document is not JSON.
    """

    url = '/centers'
    async with client.post(url, headers=SEND_HEADERS) as response:
        await assert_document_not_json(response)


async def test_post_collection_data_missing(client):
    """Functional test for a failed POST /{collection} request where the
    request document does not contain a data member.
    """

    url = '/centers'
    json = {}
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing(response)


async def test_post_collection_data_invalid_type(client):
    """Functional test for a failed POST /{collection} request where the
    request document's resource object has an invalid type.
    """

    url = '/centers'
    json = {
        'data': {
            'type': 'xxxxxxxxs',
            'attributes': {
                'attr_int': 1,
                'attr_str': 'one',
            }
        }
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        pointer = '/data/type/xxxxxxxxs'
        await assert_data_invalid_type(response, pointer)


async def test_post_collection_data_malformed(client):
    """Functional test for a failed POST /{collection} request where the
    request document's 'data' member is malformed.
    """

    url = '/centers'
    json = {
        'data': [],
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed(response)


async def test_post_collection_data_missing_type(client):
    """Functional test for a failed POST /{collection} request where the
    request document's resource object has a missing type.
    """

    url = '/centers'
    json = {
        'data': {
            'attributes': {
                'attr_int': 1,
                'attr_str': 'one',
            }
        }
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_type(response)


async def test_post_collection_data_malformed_uuid(client):
    """Functional test for a failed POST /{collection} request where the
    request document's resource object contains a malformed UUID.
    """

    url = '/centers'
    center_id = '88888888'
    json = {
        'data': {
            'type': 'centers',
            'id': center_id,
            'attributes': {
                'attr_int': 1,
                'attr_str': 'one',
            }
        }
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        pointer = f'/data/id/{center_id}'
        await assert_post_collection_data_malformed_uuid(response, pointer)


async def test_post_collection_data_invalid_attribute(client):
    """Functional test for a failed POST /{collection} request where the
    request document's resource object contains one or more invalid
    attributes.
    """

    url = '/centers'
    json = {
        'data': {
            'type': 'centers',
            'attributes': {
                'attr_char': 'a',
                'attr_int': 1,
                'attr_str': 'one',
            }
        }
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        pointer = '/data/attributes/attr_char'
        await assert_data_invalid_attribute(response, pointer)


async def test_post_collection_data_invalid_relationship(client):
    """Functional test for a failed POST /{collection} request where the
    request document's resource object contains one or more nonexistent
    relationships.
    """

    url = '/centers'
    json = {
        'data': {
            'type': 'centers',
            'relationships': {
                'xxxxxxxx': {
                    'type': 'xxxxxxxxs',
                    'id': '88888888',
                }
            }
        }
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        pointer = '/data/relationships/xxxxxxxx'
        await assert_data_invalid_relationship(response, pointer)


async def test_post_collection_data_malformed_relationship(client):
    """Functional test for a failed POST /{collection} request where the
    request document's resource object contains one or more malformed
    relationships.
    """

    url = '/centers'
    json = {
        'data': {
            'type': 'centers',
            'relationships': {
                'one_one_local': ['xxxxxxxx'],
                'one_one_remote': ['xxxxxxxx'],
                'many_one': ['xxxxxxxx'],
                'one_manys': ['xxxxxxxx'],
                'many_manys': ['xxxxxxxx'],
            }
        }
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed_relationship(
            response, {
                '/data/relationships/one_one_local',
                '/data/relationships/one_one_remote',
                '/data/relationships/many_one',
                '/data/relationships/one_manys',
                '/data/relationships/many_manys',
            })


async def test_post_collection_data_malformed_relationship_data(client):
    """Functional test for a failed POST /{collection} request where the
    request document's resource object contains one or more malformed
    relationship data members.
    """
    url = '/centers'
    json = {
        'data': {
            'type': 'centers',
            'relationships': {
                'one_one_local': {
                    'data': ['xxxxxxxx']
                },
                'one_one_remote': {
                    'data': ['xxxxxxxx']
                },
                'many_one': {
                    'data': ['xxxxxxxx'],
                },
                'one_manys': {
                    'data': [['xxxxxxxx']],
                },
                'many_manys': {
                    'data': [['xxxxxxxx']],
                },
            }
        }
    }
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed_relationship_data(
            response, {
                '/data/relationships/one_one_local/data',
                '/data/relationships/one_one_remote/data',
                '/data/relationships/many_one/data',
                '/data/relationships/one_manys/data/0',
                '/data/relationships/many_manys/data/0',
            })


async def test_post_collection_data_missing_relationship_type(client):
    """Functional test for a failed POST /{collection} request where the
    request document's resource object contains one or more relationships with
    a missing type.
    """

    url = 'centers'
    json = JSON_CENTERS_UUID_1_DATA_MISSING_RELATIONSHIP_TYPES
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_relationship_type(
            response, {
                '/data/relationships/one_one_local/data',
                '/data/relationships/one_one_remote/data',
                '/data/relationships/many_one/data',
                '/data/relationships/one_manys/data/0',
                '/data/relationships/one_manys/data/1',
                '/data/relationships/many_manys/data/0',
                '/data/relationships/many_manys/data/1'
            })

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_post_collection_data_invalid_relationship_type(client):
    """Functional test for a failed POST /{collection} request where the
    request document's resrource object contains one or more relationships with
    an invalid type.
    """

    url = 'centers'
    json = JSON_CENTERS_UUID_1_DATA_INVALID_RELATIONSHIP_TYPES
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_invalid_relationship_type(
            response, {
                '/data/relationships/one_one_local/data/type/xxxxxxxxs',
                '/data/relationships/one_one_remote/data/type/xxxxxxxxs',
                '/data/relationships/many_one/data/type/xxxxxxxxs',
                '/data/relationships/one_manys/data/0/type/xxxxxxxxs',
                '/data/relationships/one_manys/data/1/type/xxxxxxxxs',
                '/data/relationships/many_manys/data/0/type/xxxxxxxxs',
                '/data/relationships/many_manys/data/1/type/xxxxxxxxs'
            })

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_post_collection_data_missing_relationship_id(client):
    """Functional test for a failed POST /{collection} request where the
    request document's resource object contains one or more relationships
    without an id.
    """

    url = 'centers'
    json = JSON_CENTERS_UUID_1_DATA_MISSING_RELATIONSHIP_IDS
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_relationship_id(
            response, {
                '/data/relationships/one_one_local/data',
                '/data/relationships/one_one_remote/data',
                '/data/relationships/many_one/data',
                '/data/relationships/one_manys/data/0',
                '/data/relationships/one_manys/data/1',
                '/data/relationships/many_manys/data/0',
                '/data/relationships/many_manys/data/1'
            })

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_post_collection_data_malformed_relationship_id(client):
    """Functonal test for a failed POST /{collection} request where the request
    document's resource object contains one or more relationships with a
    malformed id.
    """

    url = 'centers'
    json = JSON_CENTERS_UUID_1_DATA_MALFORMED_RELATIONSHIP_IDS
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed_relationship_id(
            response, {
                '/data/relationships/one_one_local/data/id/8888-8888',
                '/data/relationships/one_one_remote/data/id/8888-8888',
                '/data/relationships/many_one/data/id/8888-8888',
                '/data/relationships/one_manys/data/0/id/8888-8888',
                '/data/relationships/one_manys/data/1/id/8888-8888',
                '/data/relationships/many_manys/data/0/id/8888-8888',
                '/data/relationships/many_manys/data/1/id/8888-8888'
            })

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_post_collection_data_nonexistent_relationship_id(client):
    """Functional test for a failed POST /{collection} with data that contains
    a relationship with a nonexistent id.
    """

    # pylint: disable=too-many-statements

    url = '/centers'
    json = JSON_CENTERS_1_RELATIONSHIPS
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(
            response, {
                f'/data/relationships/one_one_local/data/id/{UUID_11}',
                f'/data/relationships/one_one_remote/data/id/{UUID_21}',
                f'/data/relationships/many_one/data/id/{UUID_31}',
                f'/data/relationships/one_manys/data/id/{UUID_41}',
                f'/data/relationships/one_manys/data/id/{UUID_42}',
                f'/data/relationships/many_manys/data/id/{UUID_51}',
                f'/data/relationships/many_manys/data/id/{UUID_52}'
            })

    url = '/centers'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(
            response, {
                f'/data/relationships/one_one_local/data/id/{UUID_11}',
                f'/data/relationships/one_one_remote/data/id/{UUID_21}',
                f'/data/relationships/many_one/data/id/{UUID_31}',
                f'/data/relationships/one_manys/data/id/{UUID_41}',
                f'/data/relationships/one_manys/data/id/{UUID_42}',
                f'/data/relationships/many_manys/data/id/{UUID_51}',
                f'/data/relationships/many_manys/data/id/{UUID_52}'
            })
    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)

    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_one_manys_uuid_42(client)
    await post_many_manys_uuid_51(client)
    await post_many_manys_uuid_52(client)

    await delete_many_manys_uuid_51(client)
    await delete_many_manys_uuid_52(client)
    url = '/centers'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(
            response, {
                f'/data/relationships/many_manys/data/id/{UUID_51}',
                f'/data/relationships/many_manys/data/id/{UUID_52}'
            })
    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)
    await post_many_manys_uuid_51(client)
    await post_many_manys_uuid_52(client)

    await delete_one_manys_uuid_41(client)
    await delete_one_manys_uuid_42(client)
    url = '/centers'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(
            response, {
                f'/data/relationships/one_manys/data/id/{UUID_41}',
                f'/data/relationships/one_manys/data/id/{UUID_42}'
            })
    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)
    await post_one_manys_uuid_41(client)
    await post_one_manys_uuid_42(client)

    await delete_many_ones_uuid_31(client)
    url = '/centers'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(response, {
            f'/data/relationships/many_one/data/id/{UUID_31}',
        })
    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)
    await post_many_ones_uuid_31(client)

    await delete_one_one_remotes_uuid_21(client)
    url = '/centers'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(response, {
            f'/data/relationships/one_one_remote/data/id/{UUID_21}',
        })
    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)
    await post_one_one_remotes_uuid_21(client)

    await delete_one_one_locals_uuid_11(client)
    url = '/centers'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(response, {
            f'/data/relationships/one_one_local/data/id/{UUID_11}',
        })
    await post_one_one_locals_uuid_11(client)
