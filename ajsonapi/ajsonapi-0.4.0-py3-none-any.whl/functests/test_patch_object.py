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
"""Functional tests for PATCH /{collection}/{id} requests."""

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
    assert_data_missing_id,
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
    assert_get_centers_uuid_1_unrelated,
    assert_get_object,
)
from ajsonapi.functests.asserts.patch_object import (
    assert_patch_centers_uuid_1_related,
    assert_patch_object,
    assert_patch_object_data_invalid_id,
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
# Successful requests/responses
#
async def test_patch_object(client):
    """Functional tests for a successful PATCH /{collection}/{id} request."""

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_object(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        data = document['data']
        assert 'attributes' in data
        attributes = data['attributes']
        assert 'attr_int' in attributes
        assert 'attr_str' in attributes
        assert attributes['attr_int'] == 1
        assert attributes['attr_str'] == '一'


async def test_patch_object_relationships(client):
    """Functional tests for a successful PATCH /{collection}/{id} request
    where the data contains relationships.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_one_manys_uuid_42(client)
    await post_many_manys_uuid_51(client)
    await post_many_manys_uuid_52(client)

    url = f'/centers/{UUID_1}'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_centers_uuid_1_related(response)


async def test_patch_object_accept_no_parameter(client):
    """Functional tests for a PATCH /{collection}/{id} request with an Accept
    header where some (but not all) instances of the JSON API media type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Accept':
        'application/vnd.api+json;xxxxxxxx=0,application/vnd.api+json',
    }
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_patch_object(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        data = document['data']
        assert 'attributes' in data
        attributes = data['attributes']
        assert 'attr_int' in attributes
        assert 'attr_str' in attributes
        assert attributes['attr_int'] == 1
        assert attributes['attr_str'] == '一'


async def test_patch_object_no_accept(client):
    """Functional tests for a PATCH /{collection}/{id} request with an Accept
    header where some (but not all) instances of the JSON API media type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    headers = {
        'Content-Type': 'application/vnd.api+json',
    }
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_patch_object(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        data = document['data']
        assert 'attributes' in data
        attributes = data['attributes']
        assert 'attr_int' in attributes
        assert 'attr_str' in attributes
        assert attributes['attr_int'] == 1
        assert attributes['attr_str'] == '一'


async def test_patch_object_no_attributes_relationships(client):
    """Functional tests for a successful PATCH /{collection}/{id} request
    where the document contains neither attributes nor relationships.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_object(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        data = document['data']
        assert 'attributes' in data
        attributes = data['attributes']
        assert 'attr_int' in attributes
        assert 'attr_str' in attributes
        assert attributes['attr_int'] == 1
        assert attributes['attr_str'] == 'one'


#
# Failed requests/responses
#
async def test_patch_object_content_type_parameter(client):
    """Functional tests for a failed PATCH /{collection}/{id} request where
    the Content-Type header contains a parameter.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    headers = {
        'Content-Type': 'application/vnd.api+json;xxxxxxxx=0',
        'Accept': 'application/vnd.api+json',
    }
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_accept_parameter(client):
    """Functional tests for a failed PATCH /{collection}/{id} request with
    Accept header where all instances of the JSON API media type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Accept': 'application/vnd.api+json;xxxxxxxx=0',
    }
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=headers, json=json) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_nonexistent_collection(client):
    """Functional tests for a failed PATCH /{collection}/{id} request where
    the {collection} does not exist.
    """

    await post_centers_uuid_1(client)

    url = f'/xxxxxxxxs/{UUID_1}'
    json = {
        'data': {
            'type': 'xxxxxxxxs',
            'id': UUID_1,
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_nonexistent_id(client):
    """Functional tests for a failed PATCH /{collection}/{id} request where
    the {id} does not exist.
    """

    url = '/centers/88888888'
    json = {
        'data': {
            'type': 'centers',
            'id': '88888888',
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, url)


async def test_patch_object_malformed_id(client):
    """Functional test for a failed PATCH /{collection}/{id} request where the
    {id} does not exist.
    """

    url = '/centers/8888-8888'
    json = {
        'data': {
            'type': 'centers',
            'id': '8888-8888',
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_nonexistent(response, url, 'Malformed id.')


async def test_patch_object_document_not_json(client):
    """Functional test for a failed PATCH /{collection}/{id} request where the
    request document is not JSON.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    async with client.patch(url, headers=SEND_HEADERS) as response:
        await assert_document_not_json(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_data_missing(client):
    """Functional test for a failed PATCH /{collection}/{id} request where the
    request document does not contain a data member.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = {}
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_data_malformed(client):
    """Functional test for a failed PATCH /{collection}/{id} request where the
    request document's 'data' member is malformed.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = {
        'data': [],
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_data_missing_type(client):
    """Functional test for a failed PATCH /{collection}/{id} request where
    the request document's resource object does not contain a type.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = {
        'data': {
            'id': UUID_1,
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_type(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_data_missing_id(client):
    """Functional test for a failed PATCH /{collection}/{id} request where
    the request document's resource object does not contain an id.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = {
        'data': {
            'type': 'centers',
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_missing_id(response)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_data_invalid_type(client):
    """Functional test for a failed PATCH /{collection}/{id} request where
    the request document's resource object has an invalid type.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = {
        'data': {
            'type': 'xxxxxxxxs',
            'id': UUID_1,
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_invalid_type(response, '/data/type/xxxxxxxxs')

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_data_invalid_id(client):
    """Functional test for a failed PATCH /{collection}/{id} request where
    the request document's resource object has an invalid id.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = {
        'data': {
            'type': 'centers',
            'id': '88888888',
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_patch_object_data_invalid_id(response, '/data/id/88888888')

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_data_invalid_attribute(client):
    """Functional test for a failed PATCH /{collection}/{id} request where
    the request document's resource object contains an invalid attribute.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
            'attributes': {
                'attr_float': 1.0,
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_invalid_attribute(response,
                                            '/data/attributes/attr_float')

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_data_invalid_relationship(client):
    """Functional test for a failed PATCH /{collection}/{id} request where
    the request document's resource object contains an invalid relationship.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
            'relationships': {
                'xxxxxxxx': {
                    'type': 'xxxxxxxxs',
                    'id': '88888888',
                }
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_invalid_relationship(response,
                                               '/data/relationships/xxxxxxxx')

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_data_malformed_relationship(client):
    """Functional test for a failed PATCH /{collection}/{id} request where the
    request document's resource object contains one or more malformed
    relationships.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
            'relationships': {
                'one_one_local': ['xxxxxxxx'],
                'one_one_remote': ['xxxxxxxx'],
                'many_one': ['xxxxxxxx'],
                'one_manys': ['xxxxxxxx'],
                'many_manys': ['xxxxxxxx'],
            }
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed_relationship(
            response, {
                '/data/relationships/one_one_local',
                '/data/relationships/one_one_remote',
                '/data/relationships/many_one',
                '/data/relationships/one_manys',
                '/data/relationships/many_manys',
            })


async def test_patch_object_data_malformed_relationship_data(client):
    """Functional test for a failed PATCH /{collection}/{id} request where the
    request document's resource object contains one or more malformed
    relationship data members.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
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
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_malformed_relationship_data(
            response, {
                '/data/relationships/one_one_local/data',
                '/data/relationships/one_one_remote/data',
                '/data/relationships/many_one/data',
                '/data/relationships/one_manys/data/0',
                '/data/relationships/many_manys/data/0',
            })


async def test_patch_object_data_missing_relationship_type(client):
    """Functional test for a failed PATCH /{collection}/{id} request where
    the request document's resource object contains one or more relationships
    with a missing type.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = JSON_CENTERS_UUID_1_DATA_MISSING_RELATIONSHIP_TYPES
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
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

    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_data_invalid_relationship_type(client):
    """Functional test for a failed PATCH /{collection}/{id} request where
    the request document's resource object contains one or more relationships
    with an invalid type.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = JSON_CENTERS_UUID_1_DATA_INVALID_RELATIONSHIP_TYPES
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
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

    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_data_missing_relationship_id(client):
    """Functional test for a failed PATCH /{collection}/{id} request where the
    request document's resource object contains one or more relationships
    without an id.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = JSON_CENTERS_UUID_1_DATA_MISSING_RELATIONSHIP_IDS
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
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

    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_data_malformed_relationship_id(client):
    """Functonal test for a failed PATCH /{collection}/{id} request where the
    request document's resource object contains one or more relationships with
    a malformed id.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = JSON_CENTERS_UUID_1_DATA_MALFORMED_RELATIONSHIP_IDS
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
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

    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)


async def test_patch_object_data_nonexistent_relationship_id(client):
    """Functional test for a failed PATCH /{collection}/{id} with data that
    contains a relationship with a nonexistent id.
    """

    # pylint: disable=too-many-statements

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
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
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)

    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_one_manys_uuid_42(client)
    await post_many_manys_uuid_51(client)
    await post_many_manys_uuid_52(client)

    await delete_many_manys_uuid_51(client)
    await delete_many_manys_uuid_52(client)
    url = f'/centers/{UUID_1}'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(
            response, {
                f'/data/relationships/many_manys/data/id/{UUID_51}',
                f'/data/relationships/many_manys/data/id/{UUID_52}'
            })
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)
    await post_many_manys_uuid_51(client)
    await post_many_manys_uuid_52(client)

    await delete_one_manys_uuid_41(client)
    await delete_one_manys_uuid_42(client)
    url = f'/centers/{UUID_1}'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(
            response, {
                f'/data/relationships/one_manys/data/id/{UUID_41}',
                f'/data/relationships/one_manys/data/id/{UUID_42}'
            })
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)
    await post_one_manys_uuid_41(client)
    await post_one_manys_uuid_42(client)

    await delete_many_ones_uuid_31(client)
    url = f'/centers/{UUID_1}'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(response, {
            f'/data/relationships/many_one/data/id/{UUID_31}',
        })
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)
    await post_many_ones_uuid_31(client)

    await delete_one_one_remotes_uuid_21(client)
    url = f'/centers/{UUID_1}'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(response, {
            f'/data/relationships/one_one_remote/data/id/{UUID_21}',
        })
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)
    await post_one_one_remotes_uuid_21(client)

    await delete_one_one_locals_uuid_11(client)
    url = f'/centers/{UUID_1}'
    json = JSON_CENTERS_UUID_1_RELATIONSHIPS
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_data_nonexistent_id(response, {
            f'/data/relationships/one_one_local/data/id/{UUID_11}',
        })
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_unrelated(response)
    await post_one_one_locals_uuid_11(client)


async def test_patch_object_query_include(client):
    """Functional test for a failed PATCH /{collection}/{id}?include=x
    request.
    """

    url = f'/centers/{UUID_1}?include=one_one_local'
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_include(response)


async def test_patch_object_query_fields(client):
    """Functional test for a failed PATCH /{collection}/{id}?fields[x]=x
    request.
    """

    url = f'/centers/{UUID_1}?fields[centers]=attr_int'
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_fields(response)


async def test_patch_object_query_sort(client):
    """Functional test for a failed PATCH /{collection}/{id}?sort=x request.
    """

    url = f'/centers/{UUID_1}?sort=attr_int'
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_sort(response)


async def test_patch_object_query_page(client):
    """Functional test for a failed PATCH /{collection}/{id}?page[x]=x
    request.
    """

    url = f'/centers/{UUID_1}?page[number]=0&page[size]=10'
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_page(response)


async def test_patch_object_query_filter(client):
    """Functional test for a failed PATCH /{collection}/{id}?filter[x]=x
    request.
    """

    url = f'/centers/{UUID_1}?filter[x]=x'
    json = {
        'data': {
            'type': 'centers',
            'id': UUID_1,
            'attributes': {
                'attr_str': '一',
            },
        }
    }
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        await assert_query_filter(response)
