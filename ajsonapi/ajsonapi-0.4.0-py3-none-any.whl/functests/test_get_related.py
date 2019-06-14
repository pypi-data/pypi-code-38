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
"""Functional tests for GET /{collection}/{id}/{related_resource}"""

# pylint: disable=too-many-lines

import ajsonapi.functests.model  # pylint: disable=unused-import
from ajsonapi.functests.asserts.generic import (
    assert_accept_parameters,
    assert_content_type_parameter,
    assert_fields_invalid_field,
    assert_fields_invalid_resource,
    assert_filter_invalid_field,
    assert_include_invalid_path,
    assert_nonexistent,
    assert_query_filter,
    assert_query_page,
    assert_query_sort,
    assert_sort_invalid_field,
)
from ajsonapi.functests.asserts.get_related import (
    assert_get_to_many_related_resource,
    assert_get_to_one_related_resource,
)
from ajsonapi.functests.asserts.model_included import (
    assert_medium_model_included,
)
from ajsonapi.functests.headers import HEADERS
from ajsonapi.functests.model_init import model_extend, model_init
from ajsonapi.functests.model_objects import (
    UUID_1,
    UUID_11,
    UUID_21,
    UUID_31,
    UUID_41,
    UUID_42,
    UUID_51,
    UUID_52,
    UUID_111,
    UUID_121,
    UUID_131,
    UUID_141,
    UUID_142,
    UUID_151,
    UUID_152,
    UUID_211,
    UUID_221,
    UUID_231,
    UUID_241,
    UUID_242,
    UUID_251,
    UUID_252,
    UUID_311,
    UUID_321,
    UUID_331,
    UUID_341,
    UUID_342,
    UUID_351,
    UUID_352,
    UUID_411,
    UUID_421,
    UUID_431,
    UUID_441,
    UUID_442,
    UUID_451,
    UUID_452,
    UUID_511,
    UUID_521,
    UUID_531,
    UUID_541,
    UUID_542,
    UUID_551,
    UUID_552,
)
from ajsonapi.functests.posts import post_centers_1, post_centers_uuid_1


#
# Successful requests/responses
#
async def test_get_related_resource_small_model(client):
    """Functional tests for successful GET
    /{collection}/{id}/{related_resource} requests.
    """
    # pylint: disable=too-many-statements

    await model_init(client)

    url = f'/centers/{UUID_1}/one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        obj = document['data']
        assert obj['type'] == 'one_one_locals'
        assert obj['id'] == UUID_11
        attributes = obj['attributes']
        assert attributes['attr_int'] == 211
        assert attributes['attr_str'] == '11L-one'
        relationships = obj['relationships']
        assert relationships['center']['data'] == {
            'type': 'centers',
            'id': UUID_1
        }
        assert relationships['ool_one_one_local']['data'] is None
        assert relationships['ool_one_one_remote']['data'] is None
        assert relationships['ool_many_one']['data'] is None
        assert relationships['ool_one_manys']['data'] == []
        assert relationships['ool_many_manys']['data'] == []
        assert set(relationships.keys()) == {
            'center', 'ool_one_one_local', 'ool_one_one_remote', 'ool_many_one',
            'ool_one_manys', 'ool_many_manys'
        }
        assert document['links']['self'] == url

    url = f'/centers/{UUID_1}/one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        obj = document['data']
        assert obj['type'] == 'one_one_remotes'
        assert obj['id'] == UUID_21
        attributes = obj['attributes']
        assert attributes['attr_int'] == 121
        assert attributes['attr_str'] == '11R-one'
        relationships = obj['relationships']
        assert relationships['center']['data'] == {
            'type': 'centers',
            'id': UUID_1
        }
        assert relationships['oor_one_one_local']['data'] is None
        assert relationships['oor_one_one_remote']['data'] is None
        assert relationships['oor_many_one']['data'] is None
        assert relationships['oor_one_manys']['data'] == []
        assert relationships['oor_many_manys']['data'] == []
        assert set(relationships.keys()) == {
            'center', 'oor_one_one_local', 'oor_one_one_remote', 'oor_many_one',
            'oor_one_manys', 'oor_many_manys'
        }
        assert document['links']['self'] == url

    url = f'/centers/{UUID_1}/many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        obj = document['data']
        assert obj['type'] == 'many_ones'
        assert obj['id'] == UUID_31
        attributes = obj['attributes']
        assert attributes['attr_int'] == 811
        assert attributes['attr_str'] == 'M1-one'
        relationships = obj['relationships']
        assert relationships['centers']['data'] == [{
            'type': 'centers',
            'id': UUID_1
        }]
        assert relationships['mo_one_one_local']['data'] is None
        assert relationships['mo_one_one_remote']['data'] is None
        assert relationships['mo_many_one']['data'] is None
        assert relationships['mo_one_manys']['data'] == []
        assert relationships['mo_many_manys']['data'] == []
        assert set(relationships.keys()) == {
            'centers', 'mo_one_one_local', 'mo_one_one_remote', 'mo_many_one',
            'mo_one_manys', 'mo_many_manys'
        }
        assert document['links']['self'] == url

    url = f'/centers/{UUID_1}/one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert isinstance(data, list)
        assert len(data) == 2
        for obj in data:
            assert obj['type'] == 'one_manys'
            assert obj['id'] in [UUID_41, UUID_42]
            attributes = obj['attributes']
            if obj['id'] == UUID_41:
                assert attributes['attr_int'] == 181
                assert attributes['attr_str'] == '1M-one'
            else:  # obj['id'] == UUID_42
                assert attributes['attr_int'] == 182
                assert attributes['attr_str'] == '1M-two'
            relationships = obj['relationships']
            assert relationships['center']['data'] == {
                'type': 'centers',
                'id': UUID_1
            }
            assert relationships['om_one_one_local']['data'] is None
            assert relationships['om_one_one_remote']['data'] is None
            assert relationships['om_many_one']['data'] is None
            assert relationships['om_one_manys']['data'] == []
            assert relationships['om_many_manys']['data'] == []
            assert set(relationships.keys()) == {
                'center', 'om_one_one_local', 'om_one_one_remote',
                'om_many_one', 'om_one_manys', 'om_many_manys'
            }
        assert document['links']['self'] == url

    url = f'/centers/{UUID_1}/many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert isinstance(data, list)
        assert len(data) == 2
        for obj in data:
            assert obj['type'] == 'many_manys'
            assert obj['id'] in [UUID_51, UUID_52]
            attributes = obj['attributes']
            if obj['id'] == UUID_51:
                assert attributes['attr_int'] == 881
                assert attributes['attr_str'] == 'MM-one'
            else:  # obj['id'] == UUID_52
                assert attributes['attr_int'] == 882
                assert attributes['attr_str'] == 'MM-two'
            relationships = obj['relationships']
            assert relationships['centers']['data'] == [{
                'type': 'centers',
                'id': UUID_1
            }]
            assert relationships['mm_one_one_local']['data'] is None
            assert relationships['mm_one_one_remote']['data'] is None
            assert relationships['mm_many_one']['data'] is None
            assert relationships['mm_one_manys']['data'] == []
            assert relationships['mm_many_manys']['data'] == []
            assert set(relationships.keys()) == {
                'centers', 'mm_one_one_local', 'mm_one_one_remote',
                'mm_many_one', 'mm_one_manys', 'mm_many_manys'
            }
        assert document['links']['self'] == url


async def test_get_related_resource_medium_model(client):
    """Functional tests for successful GET
    /{collection}/{id}/{related_resource} requests.
    """
    # pylint: disable=too-many-statements

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}/one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        obj = document['data']
        assert obj['type'] == 'one_one_locals'
        assert obj['id'] == UUID_11
        attributes = obj['attributes']
        assert attributes['attr_int'] == 211
        assert attributes['attr_str'] == '11L-one'
        relationships = obj['relationships']
        assert relationships['center']['data'] == {
            'type': 'centers',
            'id': UUID_1
        }
        assert relationships['ool_one_one_local']['data'] == {
            'type': 'ool_one_one_locals',
            'id': UUID_111
        }
        assert relationships['ool_one_one_remote']['data'] == {
            'type': 'ool_one_one_remotes',
            'id': UUID_121
        }
        assert relationships['ool_many_one']['data'] == {
            'type': 'ool_many_ones',
            'id': UUID_131
        }
        assert relationships['ool_one_manys']['data'] == [{
            'type': 'ool_one_manys',
            'id': UUID_141
        }, {
            'type': 'ool_one_manys',
            'id': UUID_142
        }]
        assert relationships['ool_many_manys']['data'] == [{
            'type': 'ool_many_manys',
            'id': UUID_151
        }, {
            'type': 'ool_many_manys',
            'id': UUID_152
        }]
        assert set(relationships.keys()) == {
            'center', 'ool_one_one_local', 'ool_one_one_remote', 'ool_many_one',
            'ool_one_manys', 'ool_many_manys'
        }
        assert document['links']['self'] == url

    url = f'/centers/{UUID_1}/one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        obj = document['data']
        assert obj['type'] == 'one_one_remotes'
        assert obj['id'] == UUID_21
        attributes = obj['attributes']
        assert attributes['attr_int'] == 121
        assert attributes['attr_str'] == '11R-one'
        relationships = obj['relationships']
        assert relationships['center']['data'] == {
            'type': 'centers',
            'id': UUID_1
        }
        assert relationships['oor_one_one_local']['data'] == {
            'type': 'oor_one_one_locals',
            'id': UUID_211
        }
        assert relationships['oor_one_one_remote']['data'] == {
            'type': 'oor_one_one_remotes',
            'id': UUID_221
        }
        assert relationships['oor_many_one']['data'] == {
            'type': 'oor_many_ones',
            'id': UUID_231
        }
        assert relationships['oor_one_manys']['data'] == [{
            'type': 'oor_one_manys',
            'id': UUID_241
        }, {
            'type': 'oor_one_manys',
            'id': UUID_242
        }]
        assert relationships['oor_many_manys']['data'] == [{
            'type': 'oor_many_manys',
            'id': UUID_251
        }, {
            'type': 'oor_many_manys',
            'id': UUID_252
        }]
        assert set(relationships.keys()) == {
            'center', 'oor_one_one_local', 'oor_one_one_remote', 'oor_many_one',
            'oor_one_manys', 'oor_many_manys'
        }
        assert document['links']['self'] == url

    url = f'/centers/{UUID_1}/many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        obj = document['data']
        assert obj['type'] == 'many_ones'
        assert obj['id'] == UUID_31
        attributes = obj['attributes']
        assert attributes['attr_int'] == 811
        assert attributes['attr_str'] == 'M1-one'
        relationships = obj['relationships']
        assert relationships['centers']['data'] == [{
            'type': 'centers',
            'id': UUID_1
        }]
        assert relationships['mo_one_one_local']['data'] == {
            'type': 'mo_one_one_locals',
            'id': UUID_311
        }
        assert relationships['mo_one_one_remote']['data'] == {
            'type': 'mo_one_one_remotes',
            'id': UUID_321
        }
        assert relationships['mo_many_one']['data'] == {
            'type': 'mo_many_ones',
            'id': UUID_331
        }
        assert relationships['mo_one_manys']['data'] == [{
            'type': 'mo_one_manys',
            'id': UUID_341
        }, {
            'type': 'mo_one_manys',
            'id': UUID_342
        }]
        assert relationships['mo_many_manys']['data'] == [{
            'type': 'mo_many_manys',
            'id': UUID_351
        }, {
            'type': 'mo_many_manys',
            'id': UUID_352
        }]
        assert set(relationships.keys()) == {
            'centers', 'mo_one_one_local', 'mo_one_one_remote', 'mo_many_one',
            'mo_one_manys', 'mo_many_manys'
        }
        assert document['links']['self'] == url

    url = f'/centers/{UUID_1}/one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert isinstance(data, list)
        assert len(data) == 2
        for obj in data:
            assert obj['type'] == 'one_manys'
            assert obj['id'] in [UUID_41, UUID_42]
            attributes = obj['attributes']
            relationships = obj['relationships']
            if obj['id'] == UUID_41:
                assert attributes['attr_int'] == 181
                assert attributes['attr_str'] == '1M-one'
                assert relationships['center']['data'] == {
                    'type': 'centers',
                    'id': UUID_1
                }
                assert relationships['om_one_one_local']['data'] == {
                    'type': 'om_one_one_locals',
                    'id': UUID_411
                }
                assert relationships['om_one_one_remote']['data'] == {
                    'type': 'om_one_one_remotes',
                    'id': UUID_421
                }
                assert relationships['om_many_one']['data'] == {
                    'type': 'om_many_ones',
                    'id': UUID_431
                }
                assert relationships['om_one_manys']['data'] == [{
                    'type': 'om_one_manys',
                    'id': UUID_441
                }, {
                    'type': 'om_one_manys',
                    'id': UUID_442
                }]
                assert relationships['om_many_manys']['data'] == [{
                    'type': 'om_many_manys',
                    'id': UUID_451
                }, {
                    'type': 'om_many_manys',
                    'id': UUID_452
                }]
            else:  # obj['id] == UUID_42
                assert attributes['attr_int'] == 182
                assert attributes['attr_str'] == '1M-two'
                assert relationships['center']['data'] == {
                    'type': 'centers',
                    'id': UUID_1
                }
                assert relationships['om_one_one_local']['data'] is None
                assert relationships['om_one_one_remote']['data'] is None
                assert relationships['om_many_one']['data'] is None
                assert relationships['om_one_manys']['data'] == []
                assert relationships['om_many_manys']['data'] == []
            assert set(relationships.keys()) == {
                'center', 'om_one_one_local', 'om_one_one_remote',
                'om_many_one', 'om_one_manys', 'om_many_manys'
            }
            assert document['links']['self'] == url

    url = f'/centers/{UUID_1}/many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert isinstance(data, list)
        assert len(data) == 2
        for obj in data:
            assert obj['type'] == 'many_manys'
            assert obj['id'] in [UUID_51, UUID_52]
            attributes = obj['attributes']
            relationships = obj['relationships']
            if obj['id'] == UUID_51:
                assert attributes['attr_int'] == 881
                assert attributes['attr_str'] == 'MM-one'
                assert relationships['centers']['data'] == [{
                    'type': 'centers',
                    'id': UUID_1
                }]
                assert relationships['mm_one_one_local']['data'] == {
                    'type': 'mm_one_one_locals',
                    'id': UUID_511
                }
                assert relationships['mm_one_one_remote']['data'] == {
                    'type': 'mm_one_one_remotes',
                    'id': UUID_521
                }
                assert relationships['mm_many_one']['data'] == {
                    'type': 'mm_many_ones',
                    'id': UUID_531
                }
                assert relationships['mm_one_manys']['data'] == [{
                    'type': 'mm_one_manys',
                    'id': UUID_541
                }, {
                    'type': 'mm_one_manys',
                    'id': UUID_542
                }]
                assert relationships['mm_many_manys']['data'] == [{
                    'type': 'mm_many_manys',
                    'id': UUID_551
                }, {
                    'type': 'mm_many_manys',
                    'id': UUID_552
                }]
            else:  # obj['id'] == UUID_52
                assert attributes['attr_int'] == 882
                assert attributes['attr_str'] == 'MM-two'
                assert relationships['centers']['data'] == [{
                    'type': 'centers',
                    'id': UUID_1
                }]
                assert relationships['mm_one_one_local']['data'] is None
                assert relationships['mm_one_one_remote']['data'] is None
                assert relationships['mm_many_one']['data'] is None
                assert relationships['mm_one_manys']['data'] == []
                assert relationships['mm_many_manys']['data'] == []
            assert set(relationships.keys()) == {
                'centers', 'mm_one_one_local', 'mm_one_one_remote',
                'mm_many_one', 'mm_one_manys', 'mm_many_manys'
            }
        assert document['links']['self'] == url


async def test_get_related_resource_tiny_model(client):
    """Functional tests for successful GET
    /{collection}/{id}/{related_resource} requests.
    """
    await post_centers_1(client)

    url = '/centers/1/one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        obj = document['data']
        assert obj is None
        assert document['links']['self'] == url

    url = '/centers/1/one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        obj = document['data']
        assert obj is None
        assert document['links']['self'] == url

    url = '/centers/1/many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        obj = document['data']
        assert obj is None
        assert document['links']['self'] == url

    url = '/centers/1/one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []
        assert document['links']['self'] == url

    url = '/centers/1/many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []
        assert document['links']['self'] == url


async def test_get_related_resource_query_include(client):
    """Functional test for a successful GET
    /{collection}/{id}/{related_resource}?include=x request.
    """

    # pylint: disable=too-many-statements

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}/one_one_local?include=ool_one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'ool_one_one_locals': ({UUID_111}, None)})

    url = f'/centers/{UUID_1}/one_one_local?include=ool_one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'], {'ool_one_one_remotes': ({UUID_121}, None)})

    url = f'/centers/{UUID_1}/one_one_local?include=ool_many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'ool_many_ones': ({UUID_131}, None)})

    url = f'/centers/{UUID_1}/one_one_local?include=ool_one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'ool_one_manys': ({UUID_141, UUID_142}, None)})

    url = f'/centers/{UUID_1}/one_one_local?include=ool_many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'ool_many_manys': ({UUID_151, UUID_152}, None)})

    url = f'/centers/{UUID_1}/one_one_remote?include=oor_one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'oor_one_one_locals': ({UUID_211}, None)})

    url = f'/centers/{UUID_1}/one_one_remote?include=oor_one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'], {'oor_one_one_remotes': ({UUID_221}, None)})

    url = f'/centers/{UUID_1}/one_one_remote?include=oor_many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'oor_many_ones': ({UUID_231}, None)})

    url = f'/centers/{UUID_1}/one_one_remote?include=oor_one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'oor_one_manys': ({UUID_241, UUID_242}, None)})

    url = f'/centers/{UUID_1}/one_one_remote?include=oor_many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'oor_many_manys': ({UUID_251, UUID_252}, None)})

    url = f'/centers/{UUID_1}/many_one?include=mo_one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'mo_one_one_locals': ({UUID_311}, None)})

    url = f'/centers/{UUID_1}/many_one?include=mo_one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'mo_one_one_remotes': ({UUID_321}, None)})

    url = f'/centers/{UUID_1}/many_one?include=mo_many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'mo_many_ones': ({UUID_331}, None)})

    url = f'/centers/{UUID_1}/many_one?include=mo_one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mo_one_manys': ({UUID_341, UUID_342}, None)})

    url = f'/centers/{UUID_1}/many_one?include=mo_many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mo_many_manys': ({UUID_351, UUID_352}, None)})

    url = f'/centers/{UUID_1}/one_manys?include=om_one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'om_one_one_locals': ({UUID_411}, None)})

    url = f'/centers/{UUID_1}/one_manys?include=om_one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'om_one_one_remotes': ({UUID_421}, None)})

    url = f'/centers/{UUID_1}/one_manys?include=om_many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'om_many_ones': ({UUID_431}, None)})

    url = f'/centers/{UUID_1}/one_manys?include=om_one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'om_one_manys': ({UUID_441, UUID_442}, None)})

    url = f'/centers/{UUID_1}/one_manys?include=om_many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'om_many_manys': ({UUID_451, UUID_452}, None)})

    url = f'/centers/{UUID_1}/many_manys?include=mm_one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'mm_one_one_locals': ({UUID_511}, None)})

    url = f'/centers/{UUID_1}/many_manys?include=mm_one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'mm_one_one_remotes': ({UUID_521}, None)})

    url = f'/centers/{UUID_1}/many_manys?include=mm_many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'mm_many_ones': ({UUID_531}, None)})

    url = f'/centers/{UUID_1}/many_manys?include=mm_one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mm_one_manys': ({UUID_541, UUID_542}, None)})

    url = f'/centers/{UUID_1}/many_manys?include=mm_many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mm_many_manys': ({UUID_551, UUID_552}, None)})


async def test_get_related_resource_query_fields(client):
    """Functional test for a successful GET
    /{collection}/{id}/{related_resource}?fields[x]=x request.
    """

    # pylint: disable=too-many-statements

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}/one_one_local?fields[one_one_locals]=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id', 'attributes'}
        assert obj['type'] == 'one_one_locals'
        assert obj['id'] == UUID_11
        attributes = obj['attributes']
        assert set(attributes.keys()) == {'attr_int'}
        assert attributes['attr_int'] == 211

    url = f'/centers/{UUID_1}/one_one_remote?fields[one_one_remotes]=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id', 'attributes'}
        assert obj['type'] == 'one_one_remotes'
        assert obj['id'] == UUID_21
        attributes = obj['attributes']
        assert set(attributes.keys()) == {'attr_int'}
        assert attributes['attr_int'] == 121

    url = f'/centers/{UUID_1}/many_one?fields[many_ones]=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id', 'attributes'}
        assert obj['type'] == 'many_ones'
        assert obj['id'] == UUID_31
        attributes = obj['attributes']
        assert set(attributes.keys()) == {'attr_int'}
        assert attributes['attr_int'] == 811

    url = f'/centers/{UUID_1}/one_manys?fields[one_manys]=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        for obj in data:
            assert set(obj.keys()) == {'type', 'id', 'attributes'}
            assert obj['type'] == 'one_manys'
            assert obj['id'] in {UUID_41, UUID_42}
            attributes = obj['attributes']
            assert set(attributes.keys()) == {'attr_int'}
            if obj['id'] == UUID_41:
                assert attributes['attr_int'] == 181
            else:
                assert attributes['attr_int'] == 182

    url = f'/centers/{UUID_1}/many_manys?fields[many_manys]=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        for obj in data:
            assert set(obj.keys()) == {'type', 'id', 'attributes'}
            assert obj['type'] == 'many_manys'
            assert obj['id'] in {UUID_51, UUID_52}
            attributes = obj['attributes']
            assert set(attributes.keys()) == {'attr_int'}
            if obj['id'] == UUID_51:
                assert attributes['attr_int'] == 881
            else:
                assert attributes['attr_int'] == 882


async def test_get_related_query_include_fields(client):
    """Functional tests for a successful GET
    /{collection}/{id}/{related_resource}?include=x,fields[x]=x request.
    """

    # pylint: disable=too-many-statements

    await model_init(client)
    await model_extend(client)

    url = (f'/centers/{UUID_1}/one_one_local?include=ool_one_one_local&'
           'fields[ool_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'], {'ool_one_one_locals': ({UUID_111}, set())})
    url = (f'/centers/{UUID_1}/one_one_local?include=ool_one_one_local&'
           'fields[ool_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'ool_one_one_locals': ({UUID_111}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_one_local?include=ool_one_one_remote&'
           'fields[ool_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'], {'ool_one_one_remotes': ({UUID_121}, set())})
    url = (f'/centers/{UUID_1}/one_one_local?include=ool_one_one_remote&'
           'fields[ool_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'ool_one_one_remotes': ({UUID_121}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_one_local?include=ool_many_one&'
           'fields[ool_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'ool_many_ones': ({UUID_131}, set())})
    url = (f'/centers/{UUID_1}/one_one_local?include=ool_many_one&'
           'fields[ool_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'], {'ool_many_ones': ({UUID_131}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_one_local?include=ool_one_manys&'
           'fields[ool_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'ool_one_manys': ({UUID_141, UUID_142}, set())})
    url = (f'/centers/{UUID_1}/one_one_local?include=ool_one_manys&'
           'fields[ool_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'ool_one_manys': ({UUID_141, UUID_142}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_one_local?include=ool_many_manys&'
           'fields[ool_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'ool_many_manys': ({UUID_151, UUID_152}, set())})
    url = (f'/centers/{UUID_1}/one_one_local?include=ool_many_manys&'
           'fields[ool_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'ool_many_manys': ({UUID_151, UUID_152}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_one_remote?include=oor_one_one_local&'
           'fields[oor_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'], {'oor_one_one_locals': ({UUID_211}, set())})
    url = (f'/centers/{UUID_1}/one_one_remote?include=oor_one_one_local&'
           'fields[oor_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'oor_one_one_locals': ({UUID_211}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_one_remote?include=oor_one_one_remote&'
           'fields[oor_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'], {'oor_one_one_remotes': ({UUID_221}, set())})
    url = (f'/centers/{UUID_1}/one_one_remote?include=oor_one_one_remote&'
           'fields[oor_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'oor_one_one_remotes': ({UUID_221}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_one_remote?include=oor_many_one&'
           'fields[oor_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'oor_many_ones': ({UUID_231}, set())})
    url = (f'/centers/{UUID_1}/one_one_remote?include=oor_many_one&'
           'fields[oor_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'], {'oor_many_ones': ({UUID_231}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_one_remote?include=oor_one_manys&'
           'fields[oor_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'oor_one_manys': ({UUID_241, UUID_242}, set())})
    url = (f'/centers/{UUID_1}/one_one_remote?include=oor_one_manys&'
           'fields[oor_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'oor_one_manys': ({UUID_241, UUID_242}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_one_remote?include=oor_many_manys&'
           'fields[oor_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'oor_many_manys': ({UUID_251, UUID_252}, set())})
    url = (f'/centers/{UUID_1}/one_one_remote?include=oor_many_manys&'
           'fields[oor_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'oor_many_manys': ({UUID_251, UUID_252}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/many_one?include=mo_one_one_local&'
           'fields[mo_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'mo_one_one_locals': ({UUID_311}, set())})
    url = (f'/centers/{UUID_1}/many_one?include=mo_one_one_local&'
           'fields[mo_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mo_one_one_locals': ({UUID_311}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/many_one?include=mo_one_one_remote&'
           'fields[mo_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'], {'mo_one_one_remotes': ({UUID_321}, set())})
    url = (f'/centers/{UUID_1}/many_one?include=mo_one_one_remote&'
           'fields[mo_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mo_one_one_remotes': ({UUID_321}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/many_one?include=mo_many_one&'
           'fields[mo_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'mo_many_ones': ({UUID_331}, set())})
    url = (f'/centers/{UUID_1}/many_one?include=mo_many_one&'
           'fields[mo_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'], {'mo_many_ones': ({UUID_331}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/many_one?include=mo_one_manys&'
           'fields[mo_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mo_one_manys': ({UUID_341, UUID_342}, set())})
    url = (f'/centers/{UUID_1}/many_one?include=mo_one_manys&'
           'fields[mo_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mo_one_manys': ({UUID_341, UUID_342}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/many_one?include=mo_many_manys&'
           'fields[mo_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mo_many_manys': ({UUID_351, UUID_352}, set())})
    url = (f'/centers/{UUID_1}/many_one?include=mo_many_manys&'
           'fields[mo_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mo_many_manys': ({UUID_351, UUID_352}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_manys?include=om_one_one_local&'
           'fields[om_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'om_one_one_locals': ({UUID_411}, set())})
    url = (f'/centers/{UUID_1}/one_manys?include=om_one_one_local&'
           'fields[om_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'om_one_one_locals': ({UUID_411}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_manys?include=om_one_one_remote&'
           'fields[om_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'], {'om_one_one_remotes': ({UUID_421}, set())})
    url = (f'/centers/{UUID_1}/one_manys?include=om_one_one_remote&'
           'fields[om_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'om_one_one_remotes': ({UUID_421}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_manys?include=om_many_one&'
           'fields[om_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'om_many_ones': ({UUID_431}, set())})
    url = (f'/centers/{UUID_1}/one_manys?include=om_many_one&'
           'fields[om_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'], {'om_many_ones': ({UUID_431}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_manys?include=om_one_manys&'
           'fields[om_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'om_one_manys': ({UUID_441, UUID_442}, set())})
    url = (f'/centers/{UUID_1}/one_manys?include=om_one_manys&'
           'fields[om_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'om_one_manys': ({UUID_441, UUID_442}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/one_manys?include=om_many_manys&'
           'fields[om_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'om_many_manys': ({UUID_451, UUID_452}, set())})
    url = (f'/centers/{UUID_1}/one_manys?include=om_many_manys&'
           'fields[om_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'om_many_manys': ({UUID_451, UUID_452}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/many_manys?include=mm_one_one_local&'
           'fields[mm_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'mm_one_one_locals': ({UUID_511}, set())})
    url = (f'/centers/{UUID_1}/many_manys?include=mm_one_one_local&'
           'fields[mm_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mm_one_one_locals': ({UUID_511}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/many_manys?include=mm_one_one_remote&'
           'fields[mm_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'], {'mm_one_one_remotes': ({UUID_521}, set())})
    url = (f'/centers/{UUID_1}/many_manys?include=mm_one_one_remote&'
           'fields[mm_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mm_one_one_remotes': ({UUID_521}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/many_manys?include=mm_many_one&'
           'fields[mm_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(document['included'],
                                     {'mm_many_ones': ({UUID_531}, set())})
    url = (f'/centers/{UUID_1}/many_manys?include=mm_many_one&'
           'fields[mm_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'], {'mm_many_ones': ({UUID_531}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/many_manys?include=mm_one_manys&'
           'fields[mm_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mm_one_manys': ({UUID_541, UUID_542}, set())})
    url = (f'/centers/{UUID_1}/many_manys?include=mm_one_manys&'
           'fields[mm_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mm_one_manys': ({UUID_541, UUID_542}, {'attr_str'})})

    url = (f'/centers/{UUID_1}/many_manys?include=mm_many_manys&'
           'fields[mm_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mm_many_manys': ({UUID_551, UUID_552}, set())})
    url = (f'/centers/{UUID_1}/many_manys?include=mm_many_manys&'
           'fields[mm_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        assert_medium_model_included(
            document['included'],
            {'mm_many_manys': ({UUID_551, UUID_552}, {'attr_str'})})


async def test_get_to_many_related_resource_query_filter(client):
    """Functional test for a successful GET
    /{collection}/{id}/{related_resource}?filter[x]=x request.
    """

    # pylint: disable=too-many-statements

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}/one_manys?filter[attr_int]=181'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        one_many = data[0]
        assert one_many['id'] == UUID_41

    url = f'/centers/{UUID_1}/one_manys?filter[attr_int]=182'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        one_many = data[0]
        assert one_many['id'] == UUID_42

    url = f'/centers/{UUID_1}/one_manys?filter[attr_int]=181,182'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 2
        assert {obj['id'] for obj in data} == {UUID_41, UUID_42}

    url = f'/centers/{UUID_1}/one_manys?filter[attr_int]=88888888'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f"/centers/{UUID_1}/one_manys?filter[attr_str]='1M-one'"
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        one_many = data[0]
        assert one_many['id'] == UUID_41

    url = f"/centers/{UUID_1}/one_manys?filter[attr_str]='1M-two'"
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        one_many = data[0]
        assert one_many['id'] == UUID_42

    url = f"/centers/{UUID_1}/one_manys?filter[attr_str]='1M-one','1M-two'"
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 2
        assert {obj['id'] for obj in data} == {UUID_41, UUID_42}

    url = f"/centers/{UUID_1}/one_manys?filter[attr_str]='xxxxxxxx'"
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/one_manys?filter[om_one_one_local]={UUID_411}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        one_many = data[0]
        assert one_many['id'] == UUID_41

    url = f'/centers/{UUID_1}/one_manys?filter[om_one_one_local]=88888888'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/one_manys?filter[om_one_one_remote]={UUID_421}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        one_many = data[0]
        assert one_many['id'] == UUID_41

    url = f'/centers/{UUID_1}/one_manys?filter[om_one_one_remote]=88888888'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/one_manys?filter[om_many_one]={UUID_431}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        one_many = data[0]
        assert one_many['id'] == UUID_41

    url = f'/centers/{UUID_1}/one_manys?filter[om_many_one]=88888888'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/one_manys?filter[om_one_manys]={UUID_441}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        one_many = data[0]
        assert one_many['id'] == UUID_41

    url = f'/centers/{UUID_1}/one_manys?filter[om_one_manys]={UUID_442}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        one_many = data[0]
        assert one_many['id'] == UUID_41

    url = (f'/centers/{UUID_1}/one_manys'
           f'?filter[om_one_manys]={UUID_441},{UUID_442}')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        one_many = data[0]
        assert one_many['id'] == UUID_41

    url = f'/centers/{UUID_1}/one_manys?filter[om_one_manys]=88888888'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/one_manys?filter[om_many_manys]={UUID_451}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        one_many = data[0]
        assert one_many['id'] == UUID_41

    url = f'/centers/{UUID_1}/one_manys?filter[om_many_manys]={UUID_452}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        one_many = data[0]
        assert one_many['id'] == UUID_41

    url = (f'/centers/{UUID_1}/one_manys'
           f'?filter[om_many_manys]={UUID_451},{UUID_452}')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        one_many = data[0]
        assert one_many['id'] == UUID_41

    url = f'/centers/{UUID_1}/one_manys?filter[om_many_manys]=88888888'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/many_manys?filter[attr_int]=881'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        assert {obj['id'] for obj in data} == {UUID_51}

    url = f'/centers/{UUID_1}/many_manys?filter[attr_int]=882'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        assert {obj['id'] for obj in data} == {UUID_52}

    url = f'/centers/{UUID_1}/many_manys?filter[attr_int]=881,882'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 2
        assert {obj['id'] for obj in data} == {UUID_51, UUID_52}

    url = f'/centers/{UUID_1}/many_manys?filter[attr_int]=88888888'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f"/centers/{UUID_1}/many_manys?filter[attr_str]='MM-one'"
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        assert {obj['id'] for obj in data} == {UUID_51}

    url = f"/centers/{UUID_1}/many_manys?filter[attr_str]='MM-two'"
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        assert {obj['id'] for obj in data} == {UUID_52}

    url = f"/centers/{UUID_1}/many_manys?filter[attr_str]='MM-one','MM-two'"
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 2
        assert {obj['id'] for obj in data} == {UUID_51, UUID_52}

    url = f"/centers/{UUID_1}/many_manys?filter[attr_str]='xxxxxxxx'"
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/many_manys?filter[mm_one_one_local]={UUID_511}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        assert {obj['id'] for obj in data} == {UUID_51}

    url = f'/centers/{UUID_1}/many_manys?filter[mm_one_one_local]=88888888'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/many_manys?filter[mm_one_one_remote]={UUID_521}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        assert {obj['id'] for obj in data} == {UUID_51}

    url = f'/centers/{UUID_1}/many_manys?filter[mm_one_one_remote]=88888888'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/many_manys?filter[mm_many_one]={UUID_531}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        assert {obj['id'] for obj in data} == {UUID_51}

    url = f'/centers/{UUID_1}/many_manys?filter[mm_many_one]=88888888'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/many_manys?filter[mm_one_manys]={UUID_541}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        assert {obj['id'] for obj in data} == {UUID_51}

    url = f'/centers/{UUID_1}/many_manys?filter[mm_one_manys]={UUID_542}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        assert {obj['id'] for obj in data} == {UUID_51}

    url = (f'/centers/{UUID_1}/many_manys?'
           f'filter[mm_one_manys]={UUID_541},{UUID_542}')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        assert {obj['id'] for obj in data} == {UUID_51}

    url = f'/centers/{UUID_1}/many_manys?filter[mm_one_manys]=88888888'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/many_manys?filter[mm_many_manys]={UUID_551}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        assert {obj['id'] for obj in data} == {UUID_51}

    url = f'/centers/{UUID_1}/many_manys?filter[mm_many_manys]={UUID_552}'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        assert {obj['id'] for obj in data} == {UUID_51}

    url = (f'/centers/{UUID_1}/many_manys?'
           f'filter[mm_many_manys]={UUID_551},{UUID_552}')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 1
        assert {obj['id'] for obj in data} == {UUID_51}

    url = f'/centers/{UUID_1}/many_manys?filter[mm_many_manys]=88888888'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []


async def test_get_to_many_related_resource_query_sort(client):
    """Functional test for a successful GET
    /{collection}/{id}/{related_resource}?sort=x request.
    """

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}/one_manys?sort=attr_int,-attr_str'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 2
        assert [obj['id'] for obj in data] == [UUID_41, UUID_42]

    url = f'/centers/{UUID_1}/one_manys?sort=-attr_str,attr_int'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 2
        assert [obj['id'] for obj in data] == [UUID_42, UUID_41]

    url = f'/centers/{UUID_1}/many_manys?sort=attr_int,-attr_str'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 2
        assert [obj['id'] for obj in data] == [UUID_51, UUID_52]

    url = f'/centers/{UUID_1}/many_manys?sort=-attr_str,attr_int'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert len(data) == 2
        assert [obj['id'] for obj in data] == [UUID_52, UUID_51]


async def test_get_related_resource_no_accept(client):
    """Functional tests for a GET /{collection}/{id}/{related_resource}
    request without an Accept header.
    """

    await post_centers_uuid_1(client)

    headers = {}

    url = f'/centers/{UUID_1}/one_one_local'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_one_related_resource(response)
        data = document['data']
        assert data is None

    url = f'/centers/{UUID_1}/one_one_remote'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_one_related_resource(response)
        data = document['data']
        assert data is None

    url = f'/centers/{UUID_1}/many_one'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_one_related_resource(response)
        data = document['data']
        assert data is None

    url = f'/centers/{UUID_1}/one_manys'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/many_manys'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_many_related_resource(response)
        data = document['data']
        assert data == []


#
# Failed requests/responses
#
async def test_get_related_resource_content_type_parameter(client):
    """Functional test for a failed GET
    /{collection}/{id}/{related_resource} request where the
    Content-Type header contains a parameter.
    """

    headers = {
        'Content-Type': 'application/vnd.api_json;xxxxxxxx=0',
    }

    url = f'/centers/{UUID_1}/one_one_local'
    async with client.get(url, headers=headers) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}/one_one_remote'
    async with client.get(url, headers=headers) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}/many_one'
    async with client.get(url, headers=headers) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}/one_manys'
    async with client.get(url, headers=headers) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}/many_manys'
    async with client.get(url, headers=headers) as response:
        await assert_content_type_parameter(response)


async def test_get_related_resource_accept_parameters(client):
    """Functional tests for a failed GET /{collection}/{id}/{related_resource}
    request with an Accept header where all instances of the JSON API media
    type ('application/vnd.api+json') are modified with media type parameters.
    """

    headers = {
        'Accept': 'application/vnd.api+json;xxxxxxxx=0',
    }

    url = f'/centers/{UUID_1}/one_one_local'
    async with client.get(url, headers=headers) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}/one_one_remote'
    async with client.get(url, headers=headers) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}/many_one'
    async with client.get(url, headers=headers) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}/one_manys'
    async with client.get(url, headers=headers) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}/many_manys'
    async with client.get(url, headers=headers) as response:
        await assert_accept_parameters(response)


async def test_get_related_resource_include_invalid_path(client):
    """Functional test for a failed GET /{collection}?include=x request due to
    an invalid relationship path.
    """

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}/one_one_local?include=xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_include_invalid_path(response, 'xxxxxxxx')
    url = f'/centers/{UUID_1}/one_one_local?include=ool_one_one_local.xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_include_invalid_path(response,
                                          'ool_one_one_local.xxxxxxxx')


async def test_get_related_resource_nonexistent_collection(client):
    """Functional tests for a failed GET /{collection}/{id}/{related_resource}
    request where {collection} does not exist.
    """

    url = f'/xxxxxxxxs/{UUID_1}/one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/xxxxxxxxs/{UUID_1}/one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/xxxxxxxxs/{UUID_1}/many_one'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/xxxxxxxxs/{UUID_1}/one_manys'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/xxxxxxxxs/{UUID_1}/many_manys'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')


async def test_get_related_resource_nonexistent_id(client):
    """Functional tests for a failed GET /{collection}/{id}/{related_resource}
    request where {id} does not exist.
    """

    url = '/centers/88888888/one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/many_one'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/one_manys'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/many_manys'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/centers/88888888')


async def test_get_related_resource_malformed_id(client):
    """Functional tests for a failed GET /{collection}/{id}/{related_resource}
    request where {id} is malformed.
    """

    url = '/centers/8888-8888/one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response,
                                 '/centers/8888-8888',
                                 detail='Malformed id.')

    url = '/centers/8888-8888/one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response,
                                 '/centers/8888-8888',
                                 detail='Malformed id.')

    url = '/centers/8888-8888/many_one'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response,
                                 '/centers/8888-8888',
                                 detail='Malformed id.')

    url = '/centers/8888-8888/one_manys'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response,
                                 '/centers/8888-8888',
                                 detail='Malformed id.')

    url = '/centers/8888-8888/many_manys'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response,
                                 '/centers/8888-8888',
                                 detail='Malformed id.')


async def test_get_related_resource_nonexistent_relationship(client):
    """Functional tests for a failed GET /{collection}/{id}/{related_resource}
    request where {related_resource} does not exist.
    """

    url = f'/centers/{UUID_1}/xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_get_related_resource_fields_invalid_resource(client):
    """Functional test for a failed GET
    /{collection}/{id}/{related_resource}?fields[x]=x request where the
    resource does not exist.
    """

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}/one_one_local?fields[xxxxxxxx]=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_resource(response, 'xxxxxxxx')

    url = f'/centers/{UUID_1}/one_one_local?fields[xxxxxxxx]=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_resource(response, 'xxxxxxxx')

    url = f'/centers/{UUID_1}/many_one?fields[xxxxxxxx]=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_resource(response, 'xxxxxxxx')

    url = f'/centers/{UUID_1}/many_one?fields[xxxxxxxx]=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_resource(response, 'xxxxxxxx')

    url = f'/centers/{UUID_1}/many_one?fields[xxxxxxxx]=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_resource(response, 'xxxxxxxx')


async def test_get_related_resource_fields_invalid_field(client):
    """Functional test for a failed GET
    /{collection}/{id}/{related_resource}?fields[x]=x request where the field
    does not exist.
    """

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}/one_one_local?fields[one_one_locals]=xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_one_locals',
                                          'xxxxxxxx')
    url = f'/centers/{UUID_1}/one_one_local?fields[one_one_locals]=type'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_one_locals', 'type')
    url = f'/centers/{UUID_1}/one_one_local?fields[one_one_locals]=id'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_one_locals', 'id')

    url = f'/centers/{UUID_1}/one_one_local?fields[one_one_remotes]=xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_one_remotes',
                                          'xxxxxxxx')
    url = f'/centers/{UUID_1}/one_one_local?fields[one_one_remotes]=type'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_one_remotes', 'type')
    url = f'/centers/{UUID_1}/one_one_local?fields[one_one_remotes]=id'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_one_remotes', 'id')

    url = f'/centers/{UUID_1}/many_one?fields[many_ones]=xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'many_ones', 'xxxxxxxx')
    url = f'/centers/{UUID_1}/many_one?fields[many_ones]=type'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'many_ones', 'type')
    url = f'/centers/{UUID_1}/many_one?fields[many_ones]=id'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'many_ones', 'id')

    url = f'/centers/{UUID_1}/many_one?fields[one_manys]=xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_manys', 'xxxxxxxx')
    url = f'/centers/{UUID_1}/many_one?fields[one_manys]=type'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_manys', 'type')
    url = f'/centers/{UUID_1}/many_one?fields[one_manys]=id'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_manys', 'id')

    url = f'/centers/{UUID_1}/many_one?fields[many_manys]=xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'many_manys', 'xxxxxxxx')
    url = f'/centers/{UUID_1}/many_one?fields[many_manys]=type'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'many_manys', 'type')
    url = f'/centers/{UUID_1}/many_one?fields[many_manys]=id'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'many_manys', 'id')


async def test_get_to_one_related_resource_query_sort(client):
    """Functional test for a failed GET
    /{collection}/{id}/{related_resource}?sort=x request.
    """

    url = f'/centers/{UUID_1}/one_one_local?sort=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_sort(response)

    url = f'/centers/{UUID_1}/one_one_remote?sort=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_sort(response)

    url = f'/centers/{UUID_1}/many_one?sort=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_sort(response)


async def test_get_to_many_related_resource_sort_invalid_field(client):
    """Functional test for a failed GET
    /{collection}/{id}/{related_resource}?sort=x request where the field does
    not exist.
    """

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}/one_manys?sort=xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_sort_invalid_field(response, 'xxxxxxxx')

    url = f'/centers/{UUID_1}/one_manys?sort=-xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_sort_invalid_field(response, 'xxxxxxxx')

    url = f'/centers/{UUID_1}/many_manys?sort=xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_sort_invalid_field(response, 'xxxxxxxx')

    url = f'/centers/{UUID_1}/many_manys?sort=-xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_sort_invalid_field(response, 'xxxxxxxx')


async def test_get_related_resource_query_page(client):
    """Functional test for a failed GET
    /{collection}/{id}/{related_resource}?page[x]=x request.
    """

    url = f'/centers/{UUID_1}/one_one_local?page[number]=0&page[size]=10'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_page(response)

    url = f'/centers/{UUID_1}/one_one_remote?page[number]=0&page[size]=10'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_page(response)

    url = f'/centers/{UUID_1}/many_one?page[number]=0&page[size]=10'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_page(response)

    url = f'/centers/{UUID_1}/one_manys?page[number]=0&page[size]=10'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_page(response)

    url = f'/centers/{UUID_1}/many_manys?page[number]=0&page[size]=10'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_page(response)


async def test_get_to_one_related_resource_query_filter(client):
    """Functional test for a failed GET
    /{collection}/{id}/{related_resource}?filter[x]=x request.
    """

    url = f'/centers/{UUID_1}/one_one_local?filter[x]=x'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_filter(response)

    url = f'/centers/{UUID_1}/one_one_remote?filter[x]=x'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_filter(response)

    url = f'/centers/{UUID_1}/many_one?filter[x]=x'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_filter(response)


async def test_get_to_many_related_resource_filter_invalid_field(client):
    """Functional test for a failed GET
    /{collection}/{id}/{related_resource}?filter[x]=x request where the field
    does not exist.
    """

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}/one_manys?filter[xxxxxxxx]=0'
    async with client.get(url, headers=HEADERS) as response:
        await assert_filter_invalid_field(response, 'xxxxxxxx')

    url = f'/centers/{UUID_1}/many_manys?filter[xxxxxxxx]=0'
    async with client.get(url, headers=HEADERS) as response:
        await assert_filter_invalid_field(response, 'xxxxxxxx')
