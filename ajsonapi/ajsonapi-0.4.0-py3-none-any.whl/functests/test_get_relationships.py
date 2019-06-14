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
"""Functional tests for GET /{collection}/{id}/relationships/{relationship}"""

# pylint: disable=too-many-lines

import ajsonapi.functests.model  # pylint: disable=unused-import
from ajsonapi.functests.asserts.generic import (
    assert_accept_parameters,
    assert_content_type_parameter,
    assert_fields_invalid_field,
    assert_fields_invalid_resource,
    assert_include_invalid_path,
    assert_nonexistent,
    assert_query_filter,
    assert_query_page,
    assert_query_sort,
)
from ajsonapi.functests.asserts.get_relationships import (
    assert_centers_uuid_1_many_manys_none,
    assert_centers_uuid_1_many_manys_uuid_51_52,
    assert_centers_uuid_1_many_one_none,
    assert_centers_uuid_1_many_one_uuid_31,
    assert_centers_uuid_1_one_manys_none,
    assert_centers_uuid_1_one_manys_uuid_41_42,
    assert_centers_uuid_1_one_one_local_none,
    assert_centers_uuid_1_one_one_local_uuid_11,
    assert_centers_uuid_1_one_one_remote_none,
    assert_centers_uuid_1_one_one_remote_uuid_21,
    assert_get_to_many_relationship,
    assert_get_to_one_relationship,
    assert_many_manys_uuid_51_centers_uuid_1,
    assert_many_manys_uuid_52_centers_uuid_1,
    assert_many_ones_uuid_31_centers_uuid_1,
    assert_one_manys_uuid_41_center_uuid_1,
    assert_one_manys_uuid_42_center_uuid_1,
    assert_one_one_locals_uuid_11_center_uuid_1,
    assert_one_one_remotes_uuid_21_center_uuid_1,
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
from ajsonapi.functests.patches import (
    patch_centers_uuid_1_many_manys_uuid_51_52,
    patch_centers_uuid_1_many_ones_uuid_31,
    patch_centers_uuid_1_one_manys_uuid_41_42,
    patch_centers_uuid_1_one_one_locals_uuid_11,
    patch_centers_uuid_1_one_one_remotes_uuid_21,
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
async def test_get_one_to_one_local_relationship(client):
    """Functional tests for successful GET
    /{collection}/{id}/relationships/{relationship} requests.
    """

    await post_centers_uuid_1(client)
    await post_one_one_locals_uuid_11(client)

    await assert_centers_uuid_1_one_one_local_none(client)

    await patch_centers_uuid_1_one_one_locals_uuid_11(client)

    await assert_centers_uuid_1_one_one_local_uuid_11(client)
    await assert_one_one_locals_uuid_11_center_uuid_1(client)


async def test_get_one_to_one_remote_relationship(client):
    """Functional tests for successful GET
    /{collection}/{id}/relationships/{relationship} requests.
    """

    await post_centers_uuid_1(client)
    await post_one_one_remotes_uuid_21(client)

    await assert_centers_uuid_1_one_one_remote_none(client)

    await patch_centers_uuid_1_one_one_remotes_uuid_21(client)

    await assert_centers_uuid_1_one_one_remote_uuid_21(client)
    await assert_one_one_remotes_uuid_21_center_uuid_1(client)


async def test_get_many_to_one_relationship(client):
    """Functional tests for successful GET
    /{collection}/{id}/relationships/{relationship} requests.
    """

    await post_centers_uuid_1(client)
    await post_many_ones_uuid_31(client)

    await assert_centers_uuid_1_many_one_none(client)

    await patch_centers_uuid_1_many_ones_uuid_31(client)

    await assert_centers_uuid_1_many_one_uuid_31(client)
    await assert_many_ones_uuid_31_centers_uuid_1(client)


async def test_get_one_to_many_relationship(client):
    """Functional tests for successful GET
    /{collection}/{id}/relationships/{relationship} requests.
    """

    await post_centers_uuid_1(client)
    await post_one_manys_uuid_41(client)
    await post_one_manys_uuid_42(client)

    await assert_centers_uuid_1_one_manys_none(client)

    await patch_centers_uuid_1_one_manys_uuid_41_42(client)

    await assert_centers_uuid_1_one_manys_uuid_41_42(client)
    await assert_one_manys_uuid_41_center_uuid_1(client)
    await assert_one_manys_uuid_42_center_uuid_1(client)


async def test_get_many_to_many_relationship(client):
    """Functional tests for successful GET
    /{collection}/{id}/relationships/{relationship} requests.
    """

    await post_centers_uuid_1(client)
    await post_many_manys_uuid_51(client)
    await post_many_manys_uuid_52(client)

    await assert_centers_uuid_1_many_manys_none(client)

    await patch_centers_uuid_1_many_manys_uuid_51_52(client)

    await assert_centers_uuid_1_many_manys_uuid_51_52(client)
    await assert_many_manys_uuid_51_centers_uuid_1(client)
    await assert_many_manys_uuid_52_centers_uuid_1(client)


async def test_get_relationship_query_include(client):
    """Functional test for a successful GET
    /{collection}/{id}/relationships/{relationship}?include=x request.
    """

    # pylint: disable=too-many-statements

    await model_init(client)
    await model_extend(client)

    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_one_one_local')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, None),
                'ool_one_one_locals': ({UUID_111}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_one_one_remote')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, None),
                'ool_one_one_remotes': ({UUID_121}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_many_one')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, None),
                'ool_many_ones': ({UUID_131}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_one_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, None),
                'ool_one_manys': ({UUID_141, UUID_142}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, None),
                'ool_many_manys': ({UUID_151, UUID_152}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_one_one_local')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, None),
                'oor_one_one_locals': ({UUID_211}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_one_one_remote')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, None),
                'oor_one_one_remotes': ({UUID_221}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_many_one')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, None),
                'oor_many_ones': ({UUID_231}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_one_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, None),
                'oor_one_manys': ({UUID_241, UUID_242}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, None),
                'oor_many_manys': ({UUID_251, UUID_252}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_one_one_local')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(document['included'], {
            'many_ones': ({UUID_31}, None),
            'mo_one_one_locals': ({UUID_311}, None)
        })

    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_one_one_remote')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, None),
                'mo_one_one_remotes': ({UUID_321}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_many_one')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(document['included'], {
            'many_ones': ({UUID_31}, None),
            'mo_many_ones': ({UUID_331}, None)
        })

    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_one_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, None),
                'mo_one_manys': ({UUID_341, UUID_342}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, None),
                'mo_many_manys': ({UUID_351, UUID_352}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_one_one_local')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, None),
                'om_one_one_locals': ({UUID_411}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_one_one_remote')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, None),
                'om_one_one_remotes': ({UUID_421}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_many_one')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, None),
                'om_many_ones': ({UUID_431}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_one_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, None),
                'om_one_manys': ({UUID_441, UUID_442}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, None),
                'om_many_manys': ({UUID_451, UUID_452}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_one_one_local')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, None),
                'mm_one_one_locals': ({UUID_511}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_one_one_remote')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, None),
                'mm_one_one_remotes': ({UUID_521}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_many_one')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, None),
                'mm_many_ones': ({UUID_531}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_one_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, None),
                'mm_one_manys': ({UUID_541, UUID_542}, None)
            })

    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, None),
                'mm_many_manys': ({UUID_551, UUID_552}, None)
            })


async def test_get_relationship_query_fields(client):
    """Functional test for a successful GET
    /{collection}/{id}/relationships/{relationship}?fields[x]=x request.
    """

    # pylint: disable=too-many-statements

    await model_init(client)
    await model_extend(client)

    url = (f'/centers/{UUID_1}/relationships/one_one_local?'
           'fields[one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id'}
        assert obj['type'] == 'one_one_locals'
        assert obj['id'] == UUID_11
    url = (f'/centers/{UUID_1}/relationships/one_one_local?'
           'fields[one_one_locals]=attr_int,attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id'}
        assert obj['type'] == 'one_one_locals'
        assert obj['id'] == UUID_11
    url = (f'/centers/{UUID_1}/relationships/one_one_local?'
           'fields[one_one_locals]=ool_one_one_local,ool_one_one_remote,'
           'ool_many_one,ool_one_manys,ool_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id'}
        assert obj['type'] == 'one_one_locals'
        assert obj['id'] == UUID_11
    url = (f'/centers/{UUID_1}/relationships/one_one_local?'
           'fields[one_one_locals]=attr_int,attr_str,ool_one_one_local,'
           'ool_one_one_remote,ool_many_one,ool_one_manys,ool_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id'}
        assert obj['type'] == 'one_one_locals'
        assert obj['id'] == UUID_11

    url = (f'/centers/{UUID_1}/relationships/one_one_remote?'
           'fields[one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id'}
        assert obj['type'] == 'one_one_remotes'
        assert obj['id'] == UUID_21
    url = (f'/centers/{UUID_1}/relationships/one_one_remote?'
           'fields[one_one_remotes]=attr_int,attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id'}
        assert obj['type'] == 'one_one_remotes'
        assert obj['id'] == UUID_21
    url = (f'/centers/{UUID_1}/relationships/one_one_remote?'
           'fields[one_one_remotes]=oor_one_one_local,oor_one_one_remote,'
           'oor_many_one,oor_one_manys,oor_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id'}
        assert obj['type'] == 'one_one_remotes'
        assert obj['id'] == UUID_21
    url = (f'/centers/{UUID_1}/relationships/one_one_remote?'
           'fields[one_one_remotes]=attr_int,attr_str,oor_one_one_local,'
           'oor_one_one_remote,oor_many_one,oor_one_manys,oor_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id'}
        assert obj['type'] == 'one_one_remotes'
        assert obj['id'] == UUID_21

    url = f'/centers/{UUID_1}/relationships/many_one?fields[many_ones]='
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id'}
        assert obj['type'] == 'many_ones'
        assert obj['id'] == UUID_31
    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?fields[many_ones]=attr_int,attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id'}
        assert obj['type'] == 'many_ones'
        assert obj['id'] == UUID_31
    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?fields[many_ones]=mo_one_one_local,mo_one_one_remote,'
           'mo_many_one,mo_one_manys,mo_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id'}
        assert obj['type'] == 'many_ones'
        assert obj['id'] == UUID_31
    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?fields[many_ones]=attr_int,attr_str,mo_one_one_local,'
           'mo_one_one_remote,mo_many_one,mo_one_manys,mo_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id'}
        assert obj['type'] == 'many_ones'
        assert obj['id'] == UUID_31

    url = f'/centers/{UUID_1}/relationships/one_manys?fields[one_manys]='
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        for obj in data:
            assert set(obj.keys()) == {'type', 'id'}
            assert obj['type'] == 'one_manys'
            assert obj['id'] in {UUID_41, UUID_42}
    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?fields[one_manys]=attr_int,attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        for obj in data:
            assert set(obj.keys()) == {'type', 'id'}
            assert obj['type'] == 'one_manys'
            assert obj['id'] in {UUID_41, UUID_42}
    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?fields[one_manys]=om_one_one_local,om_one_one_remote,'
           'om_many_one,om_one_manys,om_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        for obj in data:
            assert set(obj.keys()) == {'type', 'id'}
            assert obj['type'] == 'one_manys'
            assert obj['id'] in {UUID_41, UUID_42}
    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?fields[one_manys]=attr_int,attr_str,om_one_one_local,'
           'om_one_one_remote,om_many_one,om_one_manys,om_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        for obj in data:
            assert set(obj.keys()) == {'type', 'id'}
            assert obj['type'] == 'one_manys'
            assert obj['id'] in {UUID_41, UUID_42}

    url = f'/centers/{UUID_1}/relationships/many_manys?fields[many_manys]='
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        for obj in data:
            assert set(obj.keys()) == {'type', 'id'}
            assert obj['type'] == 'many_manys'
            assert obj['id'] in {UUID_51, UUID_52}
    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?fields[many_manys]=attr_int,attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        for obj in data:
            assert set(obj.keys()) == {'type', 'id'}
            assert obj['type'] == 'many_manys'
            assert obj['id'] in {UUID_51, UUID_52}
    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?fields[many_manys]=mm_one_one_local,mm_one_one_remote,'
           'mm_many_one,mm_one_manys,mm_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        for obj in data:
            assert set(obj.keys()) == {'type', 'id'}
            assert obj['type'] == 'many_manys'
            assert obj['id'] in {UUID_51, UUID_52}
    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?fields[many_manys]=attr_int,attr_str,mm_one_one_local,'
           'mm_one_one_remote,mm_many_one,mm_one_manys,mm_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        for obj in data:
            assert set(obj.keys()) == {'type', 'id'}
            assert obj['type'] == 'many_manys'
            assert obj['id'] in {UUID_51, UUID_52}


async def test_get_relationship_query_include_fields(client):
    """Functional test for a successful GET
    /{collection}/{id}/relationships/{relationship}?include=x request.
    """

    # pylint: disable=too-many-statements

    await model_init(client)
    await model_extend(client)

    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.center'
           '&fields[one_one_locals]=&fields[centers]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(document['included'], {
            'one_one_locals': ({UUID_11}, set()),
            'centers': ({UUID_1}, set())
        })
    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.center'
           '&fields[one_one_locals]=attr_int,center&fields[centers]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, {'attr_int', 'center'}),
                'centers': ({UUID_1}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_one_one_local'
           '&fields[one_one_locals]=&fields[ool_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, set()),
                'ool_one_one_locals': ({UUID_111}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_one_one_local'
           '&fields[one_one_locals]=attr_int,ool_one_one_local'
           '&fields[ool_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals':
                ({UUID_11}, {'attr_int', 'ool_one_one_local'}),
                'ool_one_one_locals': ({UUID_111}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_one_one_remote'
           '&fields[one_one_locals]=&fields[ool_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, set()),
                'ool_one_one_remotes': ({UUID_121}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_one_one_remote'
           '&fields[one_one_locals]=attr_int,ool_one_one_remote'
           '&fields[ool_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals':
                ({UUID_11}, {'attr_int', 'ool_one_one_remote'}),
                'ool_one_one_remotes': ({UUID_121}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_many_one'
           '&fields[one_one_locals]=&fields[ool_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, set()),
                'ool_many_ones': ({UUID_131}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_many_one'
           '&fields[one_one_locals]=attr_int,ool_many_one'
           '&fields[ool_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, {'attr_int', 'ool_many_one'}),
                'ool_many_ones': ({UUID_131}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_one_manys'
           '&fields[one_one_locals]=&fields[ool_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, set()),
                'ool_one_manys': ({UUID_141, UUID_142}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_one_manys'
           '&fields[one_one_locals]=attr_int,ool_one_manys'
           '&fields[ool_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, {'attr_int', 'ool_one_manys'}),
                'ool_one_manys': ({UUID_141, UUID_142}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_many_manys'
           '&fields[one_one_locals]=&fields[ool_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, set()),
                'ool_many_manys': ({UUID_151, UUID_152}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?include=one_one_local.ool_many_manys'
           '&fields[one_one_locals]=attr_int,ool_many_manys'
           '&fields[ool_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, {'attr_int', 'ool_many_manys'}),
                'ool_many_manys': ({UUID_151, UUID_152}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.center'
           '&fields[one_one_remotes]=&fields[centers]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(document['included'], {
            'one_one_remotes': ({UUID_21}, set()),
            'centers': ({UUID_1}, set())
        })
    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.center'
           '&fields[one_one_remotes]=attr_int,center'
           '&fields[centers]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, {'attr_int', 'center'}),
                'centers': ({UUID_1}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_one_one_local'
           '&fields[one_one_remotes]=&fields[oor_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, set()),
                'oor_one_one_locals': ({UUID_211}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_one_one_local'
           '&fields[one_one_remotes]=attr_int,oor_one_one_local'
           '&fields[oor_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes':
                ({UUID_21}, {'attr_int', 'oor_one_one_local'}),
                'oor_one_one_locals': ({UUID_211}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_one_one_remote'
           '&fields[one_one_remotes]=&fields[oor_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, set()),
                'oor_one_one_remotes': ({UUID_221}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_one_one_remote'
           '&fields[one_one_remotes]=attr_int,oor_one_one_remote'
           '&fields[oor_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes':
                ({UUID_21}, {'attr_int', 'oor_one_one_remote'}),
                'oor_one_one_remotes': ({UUID_221}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_many_one'
           '&fields[one_one_remotes]=&fields[oor_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, set()),
                'oor_many_ones': ({UUID_231}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_many_one'
           '&fields[one_one_remotes]=attr_int,oor_many_one'
           '&fields[oor_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, {'attr_int', 'oor_many_one'}),
                'oor_many_ones': ({UUID_231}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_one_manys'
           '&fields[one_one_remotes]=&fields[oor_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, set()),
                'oor_one_manys': ({UUID_241, UUID_242}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_one_manys'
           '&fields[one_one_remotes]=attr_int,oor_one_manys'
           '&fields[oor_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, {'attr_int', 'oor_one_manys'}),
                'oor_one_manys': ({UUID_241, UUID_242}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_many_manys'
           '&fields[one_one_remotes]=&fields[oor_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, set()),
                'oor_many_manys': ({UUID_251, UUID_252}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?include=one_one_remote.oor_many_manys'
           '&fields[one_one_remotes]=attr_int,oor_many_manys'
           '&fields[oor_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, {'attr_int', 'oor_many_manys'}),
                'oor_many_manys': ({UUID_251, UUID_252}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.centers'
           '&fields[many_ones]=&fields[centers]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(document['included'], {
            'many_ones': ({UUID_31}, set()),
            'centers': ({UUID_1}, set())
        })
    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.centers'
           '&fields[many_ones]=attr_int,centers'
           '&fields[centers]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, {'attr_int', 'centers'}),
                'centers': ({UUID_1}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_one_one_local'
           '&fields[many_ones]=&fields[mo_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, set()),
                'mo_one_one_locals': ({UUID_311}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_one_one_local'
           '&fields[many_ones]=attr_int,mo_one_one_local'
           '&fields[mo_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, {'attr_int', 'mo_one_one_local'}),
                'mo_one_one_locals': ({UUID_311}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_one_one_remote'
           '&fields[many_ones]=&fields[mo_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, set()),
                'mo_one_one_remotes': ({UUID_321}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_one_one_remote'
           '&fields[many_ones]=attr_int,mo_one_one_remote'
           '&fields[mo_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, {'attr_int', 'mo_one_one_remote'}),
                'mo_one_one_remotes': ({UUID_321}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_many_one'
           '&fields[many_ones]=&fields[mo_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(document['included'], {
            'many_ones': ({UUID_31}, set()),
            'mo_many_ones': ({UUID_331}, set())
        })
    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_many_one'
           '&fields[many_ones]=attr_int,mo_many_one'
           '&fields[mo_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, {'attr_int', 'mo_many_one'}),
                'mo_many_ones': ({UUID_331}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_one_manys'
           '&fields[many_ones]=&fields[mo_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, set()),
                'mo_one_manys': ({UUID_341, UUID_342}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_one_manys'
           '&fields[many_ones]=attr_int,mo_one_manys'
           '&fields[mo_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, {'attr_int', 'mo_one_manys'}),
                'mo_one_manys': ({UUID_341, UUID_342}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_many_manys'
           '&fields[many_ones]=&fields[mo_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, set()),
                'mo_many_manys': ({UUID_351, UUID_352}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?include=many_one.mo_many_manys'
           '&fields[many_ones]=attr_int,mo_many_manys'
           '&fields[mo_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_one_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, {'attr_int', 'mo_many_manys'}),
                'mo_many_manys': ({UUID_351, UUID_352}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.center'
           '&fields[one_manys]=&fields[centers]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(document['included'], {
            'one_manys': ({UUID_41, UUID_42}, set()),
            'centers': ({UUID_1}, set())
        })
    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.center'
           '&fields[one_manys]=attr_int,center'
           '&fields[centers]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, {'attr_int', 'center'}),
                'centers': ({UUID_1}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_one_one_local'
           '&fields[one_manys]=&fields[om_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, set()),
                'om_one_one_locals': ({UUID_411}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_one_one_local'
           '&fields[one_manys]=attr_int,om_one_one_local'
           '&fields[om_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys':
                ({UUID_41, UUID_42}, {'attr_int', 'om_one_one_local'}),
                'om_one_one_locals': ({UUID_411}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_one_one_remote'
           '&fields[one_manys]=&fields[om_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, set()),
                'om_one_one_remotes': ({UUID_421}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_one_one_remote'
           '&fields[one_manys]=attr_int,om_one_one_remote'
           '&fields[om_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys':
                ({UUID_41, UUID_42}, {'attr_int', 'om_one_one_remote'}),
                'om_one_one_remotes': ({UUID_421}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_many_one'
           '&fields[one_manys]=&fields[om_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, set()),
                'om_many_ones': ({UUID_431}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_many_one'
           '&fields[one_manys]=attr_int,om_many_one'
           '&fields[om_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, {'attr_int', 'om_many_one'}),
                'om_many_ones': ({UUID_431}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_one_manys'
           '&fields[one_manys]=&fields[om_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, set()),
                'om_one_manys': ({UUID_441, UUID_442}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_one_manys'
           '&fields[one_manys]=attr_int,om_one_manys'
           '&fields[om_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, {'attr_int', 'om_one_manys'}),
                'om_one_manys': ({UUID_441, UUID_442}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_many_manys'
           '&fields[one_manys]=&fields[om_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, set()),
                'om_many_manys': ({UUID_451, UUID_452}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?include=one_manys.om_many_manys'
           '&fields[one_manys]=attr_int,om_many_manys'
           '&fields[om_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys':
                ({UUID_41, UUID_42}, {'attr_int', 'om_many_manys'}),
                'om_many_manys': ({UUID_451, UUID_452}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.centers'
           '&fields[many_manys]=&fields[centers]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(document['included'], {
            'many_manys': ({UUID_51, UUID_52}, set()),
            'centers': ({UUID_1}, set())
        })
    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.centers'
           '&fields[many_manys]=attr_int,centers'
           '&fields[centers]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, {'attr_int', 'centers'}),
                'centers': ({UUID_1}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_one_one_local'
           '&fields[many_manys]=&fields[mm_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, set()),
                'mm_one_one_locals': ({UUID_511}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_one_one_local'
           '&fields[many_manys]=attr_int,mm_one_one_local'
           '&fields[mm_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys':
                ({UUID_51, UUID_52}, {'attr_int', 'mm_one_one_local'}),
                'mm_one_one_locals': ({UUID_511}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_one_one_remote'
           '&fields[many_manys]=&fields[mm_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, set()),
                'mm_one_one_remotes': ({UUID_521}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_one_one_remote'
           '&fields[many_manys]=attr_int,mm_one_one_remote'
           '&fields[mm_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys':
                ({UUID_51, UUID_52}, {'attr_int', 'mm_one_one_remote'}),
                'mm_one_one_remotes': ({UUID_521}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_many_one'
           '&fields[many_manys]=&fields[mm_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, set()),
                'mm_many_ones': ({UUID_531}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_many_one'
           '&fields[many_manys]=attr_int,mm_many_one'
           '&fields[mm_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, {'attr_int', 'mm_many_one'}),
                'mm_many_ones': ({UUID_531}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_one_manys'
           '&fields[many_manys]=&fields[mm_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, set()),
                'mm_one_manys': ({UUID_541, UUID_542}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_one_manys'
           '&fields[many_manys]=attr_int,mm_one_manys'
           '&fields[mm_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys':
                ({UUID_51, UUID_52}, {'attr_int', 'mm_one_manys'}),
                'mm_one_manys': ({UUID_541, UUID_542}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_many_manys'
           '&fields[many_manys]=&fields[mm_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, set()),
                'mm_many_manys': ({UUID_551, UUID_552}, set())
            })
    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?include=many_manys.mm_many_manys'
           '&fields[many_manys]=attr_int,mm_many_manys'
           '&fields[mm_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_to_many_relationship(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys':
                ({UUID_51, UUID_52}, {'attr_int', 'mm_many_manys'}),
                'mm_many_manys': ({UUID_551, UUID_552}, {'attr_str'})
            })


async def test_get_relationship_accept_no_parameter(client):
    """Functional tests for a GET
    /{collection}/{id}/relationships/{relationship} request with an Accept
    header where some (but not all) instances of the JSON API media type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    await post_centers_uuid_1(client)

    headers = {
        'Accept':
        'application/vnd.api+json:xxxxxxxx=0,application/vnd.api+json',
    }

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_one_relationship(response)
        data = document['data']
        assert data is None

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_one_relationship(response)
        data = document['data']
        assert data is None

    url = f'/centers/{UUID_1}/relationships/many_one'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_one_relationship(response)
        data = document['data']
        assert data is None

    url = f'/centers/{UUID_1}/relationships/one_manys'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/relationships/many_manys'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        assert data == []


async def test_get_relationship_no_accept(client):
    """Functional tests for a GET
    /{collection}/{id}/relationships/{relationship} request without an Accept
    header.
    """

    await post_centers_uuid_1(client)

    headers = {}

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_one_relationship(response)
        data = document['data']
        assert data is None

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_one_relationship(response)
        data = document['data']
        assert data is None

    url = f'/centers/{UUID_1}/relationships/many_one'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_one_relationship(response)
        data = document['data']
        assert data is None

    url = f'/centers/{UUID_1}/relationships/one_manys'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        assert data == []

    url = f'/centers/{UUID_1}/relationships/many_manys'
    async with client.get(url, headers=headers) as response:
        document = await assert_get_to_many_relationship(response)
        data = document['data']
        assert data == []


#
# Failed requests/responses
#
async def test_get_relationship_content_type_parameter(client):
    """Functional test for a failed GET
    /{collection}/{id}/relationships/{relationship} request where the
    Content-Type header contains a parameter.
    """

    headers = {
        'Content-Type': 'application/vnd.api_json;xxxxxxxx=0',
    }

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    async with client.get(url, headers=headers) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    async with client.get(url, headers=headers) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}/relationships/many_one'
    async with client.get(url, headers=headers) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    async with client.get(url, headers=headers) as response:
        await assert_content_type_parameter(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    async with client.get(url, headers=headers) as response:
        await assert_content_type_parameter(response)


async def test_get_relationship_accept_parameters(client):
    """Functional tests for a failed GET
    /{collection}/{id}/relationships/{relationship} request with an Accept
    header where all instances of the JSON API media type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    headers = {
        'Accept': 'application/vnd.api+json;xxxxxxxx=0',
    }

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    async with client.get(url, headers=headers) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    async with client.get(url, headers=headers) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}/relationships/many_one'
    async with client.get(url, headers=headers) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}/relationships/one_manys'
    async with client.get(url, headers=headers) as response:
        await assert_accept_parameters(response)

    url = f'/centers/{UUID_1}/relationships/many_manys'
    async with client.get(url, headers=headers) as response:
        await assert_accept_parameters(response)


async def test_get_relationship_include_invalid_path(client):
    """Functional test for a failed GET
    /{collection}/{id}/relationships/{relationship}?include=x request due to
    an invalid relationship path.
    """

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}/relationships/one_one_local?include=xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_include_invalid_path(response, 'xxxxxxxx')
    url = (f'/centers/{UUID_1}/relationships/one_one_local?'
           'include=one_one_local.xxxxxxxx')
    async with client.get(url, headers=HEADERS) as response:
        await assert_include_invalid_path(response, 'one_one_local.xxxxxxxx')
    url = (f'/centers/{UUID_1}/relationships/one_one_local?'
           'include=one_one_local.ool_one_one_local.xxxxxxxx')
    async with client.get(url, headers=HEADERS) as response:
        await assert_include_invalid_path(
            response, 'one_one_local.ool_one_one_local.xxxxxxxx')


async def test_get_relationship_nonexistent_collection(client):
    """Functional tests for a failed GET
    /{collection}/{id}/relationships/{relationship} request where {collection}
    does not exist.
    """

    url = f'/xxxxxxxxs/{UUID_1}/relationships/one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/xxxxxxxxs/{UUID_1}/relationships/one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/xxxxxxxxs/{UUID_1}/relationships/many_one'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/xxxxxxxxs/{UUID_1}/relationships/one_manys'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')

    url = f'/xxxxxxxxs/{UUID_1}/relationships/many_manys'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')


async def test_get_relationship_nonexistent_id(client):
    """Functional tests for a failed GET
    /{collection}/{id}/relationships/{relationship} request where {id} does
    not exist.
    """

    url = '/centers/88888888/relationships/one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/relationships/one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/relationships/many_one'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/relationships/one_manys'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/centers/88888888')

    url = '/centers/88888888/relationships/many_manys'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/centers/88888888')


async def test_get_relationship_malformed_id(client):
    """Functional tests for a failed GET
    /{collection}/{id}/relationships/{relationship} request where {id} is
    malformed.
    """

    url = '/centers/8888-8888/relationships/one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response,
                                 '/centers/8888-8888',
                                 detail='Malformed id.')

    url = '/centers/8888-8888/relationships/one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response,
                                 '/centers/8888-8888',
                                 detail='Malformed id.')

    url = '/centers/8888-8888/relationships/many_one'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response,
                                 '/centers/8888-8888',
                                 detail='Malformed id.')

    url = '/centers/8888-8888/relationships/one_manys'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response,
                                 '/centers/8888-8888',
                                 detail='Malformed id.')

    url = '/centers/8888-8888/relationships/many_manys'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response,
                                 '/centers/8888-8888',
                                 detail='Malformed id.')


async def test_get_relationship_nonexistent_relationship(client):
    """Functional tests for a failed GET
    /{collection}/{id}/relationships/{relationship} request where
    {relationship} does not exist.
    """

    url = f'/centers/{UUID_1}/relationships/xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_get_relationship_fields_invalid_resource(client):
    """Functional test for a failed GET /{collection}?fields[x]=x request
    where the resource does not exist.
    """

    await model_init(client)
    await model_extend(client)

    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?fields[xxxxxxxx]=attr_int')
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_resource(response, 'xxxxxxxx')

    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?fields[xxxxxxxx]=attr_int')
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_resource(response, 'xxxxxxxx')

    url = (f'/centers/{UUID_1}/relationships/many_one'
           '?fields[xxxxxxxx]=attr_int')
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_resource(response, 'xxxxxxxx')

    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?fields[xxxxxxxx]=attr_int')
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_resource(response, 'xxxxxxxx')

    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?fields[xxxxxxxx]=attr_int')
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_resource(response, 'xxxxxxxx')


async def test_get_relationship_fields_invalid_field(client):
    """Functional test for a failed GET /{collection}?fields[x]=x request
    where the field does not exist.
    """

    await model_init(client)
    await model_extend(client)

    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?fields[one_one_locals]=xxxxxxxx')
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_one_locals',
                                          'xxxxxxxx')
    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?fields[one_one_locals]=type')
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_one_locals', 'type')
    url = (f'/centers/{UUID_1}/relationships/one_one_local'
           '?fields[one_one_locals]=id')
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_one_locals', 'id')

    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?fields[one_one_remotes]=xxxxxxxx')
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_one_remotes',
                                          'xxxxxxxx')
    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?fields[one_one_remotes]=type')
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_one_remotes', 'type')
    url = (f'/centers/{UUID_1}/relationships/one_one_remote'
           '?fields[one_one_remotes]=id')
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_one_remotes', 'id')

    url = f'/centers/{UUID_1}/relationships/many_one?fields[many_ones]=xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'many_ones', 'xxxxxxxx')
    url = f'/centers/{UUID_1}/relationships/many_one?fields[many_ones]=type'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'many_ones', 'type')
    url = f'/centers/{UUID_1}/relationships/many_one?fields[many_ones]=id'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'many_ones', 'id')

    url = (f'/centers/{UUID_1}/relationships/one_manys'
           '?fields[one_manys]=xxxxxxxx')
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_manys', 'xxxxxxxx')
    url = f'/centers/{UUID_1}/relationships/one_manys?fields[one_manys]=type'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_manys', 'type')
    url = f'/centers/{UUID_1}/relationships/one_manys?fields[one_manys]=id'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'one_manys', 'id')

    url = (f'/centers/{UUID_1}/relationships/many_manys'
           '?fields[many_manys]=xxxxxxxx')
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'many_manys', 'xxxxxxxx')
    url = f'/centers/{UUID_1}/relationships/many_manys?fields[many_manys]=type'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'many_manys', 'type')
    url = f'/centers/{UUID_1}/relationships/many_manys?fields[many_manys]=id'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'many_manys', 'id')


async def test_get_relationship_query_sort(client):
    """Functional test for a failed GET
    /{collection}/{id}/relationships/{relationship}?sort=x request.
    """

    url = f'/centers/{UUID_1}/relationships/one_one_local?sort=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_sort(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote?sort=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_sort(response)

    url = f'/centers/{UUID_1}/relationships/many_one?sort=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_sort(response)

    url = f'/centers/{UUID_1}/relationships/one_manys?sort=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_sort(response)

    url = f'/centers/{UUID_1}/relationships/many_manys?sort=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_sort(response)


async def test_get_relationship_query_page(client):
    """Functional test for a failed GET
    /{collection}/{id}/relationships/{relationship}?page[x]=x request.
    """

    url = (f'/centers/{UUID_1}/relationships/one_one_local?'
           'page[number]=0&page[size]=10')
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_page(response)

    url = (f'/centers/{UUID_1}/relationships/one_one_remote?'
           'page[number]=0&page[size]=10')
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_page(response)

    url = (f'/centers/{UUID_1}/relationships/many_one?'
           'page[number]=0&page[size]=10')
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_page(response)

    url = (f'/centers/{UUID_1}/relationships/one_manys?'
           'page[number]=0&page[size]=10')
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_page(response)

    url = (f'/centers/{UUID_1}/relationships/many_manys?'
           'page[number]=0&page[size]=10')
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_page(response)


async def test_get_relationship_query_filter(client):
    """Functional test for a failed GET
    /{collection}/{id}/relationships/{relationship}?filter[x]=x request.
    """

    url = f'/centers/{UUID_1}/relationships/one_one_local?filter[x]=x'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_filter(response)

    url = f'/centers/{UUID_1}/relationships/one_one_remote?filter[x]=x'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_filter(response)

    url = f'/centers/{UUID_1}/relationships/many_one?filter[x]=x'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_filter(response)

    url = f'/centers/{UUID_1}/relationships/one_manys?filter[x]=x'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_filter(response)

    url = f'/centers/{UUID_1}/relationships/many_manys?filter[x]=x'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_filter(response)
