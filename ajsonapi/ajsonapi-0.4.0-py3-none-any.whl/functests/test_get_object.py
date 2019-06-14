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
"""Functional tests for GET /{collection}/{id}"""

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
from ajsonapi.functests.asserts.get_object import (
    assert_get_centers_1_unrelated,
    assert_get_centers_uuid_1_related,
    assert_get_object,
)
from ajsonapi.functests.asserts.model_included import (
    assert_medium_model_included,
    assert_small_model_included,
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
async def test_get_object(client):
    """Functional test for a successfull GET /{collection}/{id} request."""

    await model_init(client)

    url = f'/centers/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_uuid_1_related(response)

    await post_centers_1(client)

    url = '/centers/1'
    async with client.get(url, headers=HEADERS) as response:
        await assert_get_centers_1_unrelated(response)


async def test_get_object_query_fields(client):
    """Functional test for a successful GET /{collection}?fields[x]=x request.
    """

    # pylint: disable=too-many-statements

    await model_init(client)

    url = f'/centers/{UUID_1}?fields[centers]='
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id'}
        assert obj['type'] == 'centers'
        assert obj['id'] == UUID_1
    url = f'/centers/{UUID_1}?fields[centers]=attr_int,attr_str'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id', 'attributes'}
        assert obj['type'] == 'centers'
        assert obj['id'] == UUID_1
        assert set(obj['attributes'].keys()) == {'attr_int', 'attr_str'}
    url = (f'/centers/{UUID_1}?fields[centers]=one_one_local,one_one_remote,'
           'many_one,one_manys,many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id', 'relationships'}
        assert obj['type'] == 'centers'
        assert obj['id'] == UUID_1
        assert set(obj['relationships'].keys()) == {
            'one_one_local', 'one_one_remote', 'many_one', 'one_manys',
            'many_manys'
        }
    url = (f'/centers/{UUID_1}?fields[centers]=attr_int,one_one_local,'
           'one_one_remote')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        obj = document['data']
        assert set(obj.keys()) == {'type', 'id', 'attributes', 'relationships'}
        assert obj['type'] == 'centers'
        assert obj['id'] == UUID_1
        assert set(obj['attributes'].keys()) == {'attr_int'}
        assert set(
            obj['relationships'].keys()) == {'one_one_local', 'one_one_remote'}


async def test_get_object_query_include_fields(client):
    """Functional test for a successful GET
    /{collection}/{id}?include=x,fields[x]=x request.
    """

    # pylint: disable=too-many-statements

    await model_init(client)

    url = f'/centers/{UUID_1}?include=one_one_local&fields[one_one_locals]='
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(document['included'],
                                    {'one_one_locals': ({UUID_11}, set())})
    url = (f'/centers/{UUID_1}?include=one_one_local&'
           'fields[one_one_locals]=attr_int,ool_one_one_local')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(
            document['included'],
            {'one_one_locals': ({UUID_11}, {'attr_int', 'ool_one_one_local'})})

    url = f'/centers/{UUID_1}?include=one_one_remote&fields[one_one_remotes]='
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(document['included'],
                                    {'one_one_remotes': ({UUID_21}, set())})
    url = (f'/centers/{UUID_1}?include=one_one_remote&'
           'fields[one_one_remotes]=attr_int,oor_one_one_remote')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(document['included'], {
            'one_one_remotes': ({UUID_21}, {'attr_int', 'oor_one_one_remote'})
        })

    url = f'/centers/{UUID_1}?include=many_one&fields[many_ones]='
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(document['included'],
                                    {'many_ones': ({UUID_31}, set())})
    url = (f'/centers/{UUID_1}?include=many_one&'
           'fields[many_ones]=attr_int,mo_many_one')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(
            document['included'],
            {'many_ones': ({UUID_31}, {'attr_int', 'mo_many_one'})})

    url = f'/centers/{UUID_1}?include=one_manys&fields[one_manys]='
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(document['included'],
                                    {'one_manys': ({UUID_41, UUID_42}, set())})
    url = (f'/centers/{UUID_1}?include=one_manys&'
           'fields[one_manys]=attr_int,om_one_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(
            document['included'],
            {'one_manys': ({UUID_41, UUID_42}, {'attr_int', 'om_one_manys'})})

    url = f'/centers/{UUID_1}?include=many_manys&fields[many_manys]='
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(document['included'],
                                    {'many_manys': ({UUID_51, UUID_52}, set())})
    url = (f'/centers/{UUID_1}?include=many_manys&'
           'fields[many_manys]=attr_int,mm_many_manys')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(
            document['included'],
            {'many_manys': ({UUID_51, UUID_52}, {'attr_int', 'mm_many_manys'})})

    await model_extend(client)

    url = (f'/centers/{UUID_1}?include=one_one_local.ool_one_one_local&'
           'fields[one_one_locals]=&fields[ool_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, set()),
                'ool_one_one_locals': ({UUID_111}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_one_local.ool_one_one_local&'
           'fields[one_one_locals]=attr_int,ool_one_one_local&'
           'fields[ool_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals':
                ({UUID_11}, {'attr_int', 'ool_one_one_local'}),
                'ool_one_one_locals': ({UUID_111}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_one_local.ool_one_one_remote&'
           'fields[one_one_locals]=&fields[ool_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, set()),
                'ool_one_one_remotes': ({UUID_121}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_one_local.ool_one_one_remote&'
           'fields[one_one_locals]=attr_int,ool_one_one_remote&'
           'fields[ool_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals':
                ({UUID_11}, {'attr_int', 'ool_one_one_remote'}),
                'ool_one_one_remotes': ({UUID_121}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_one_local.ool_many_one&'
           'fields[one_one_locals]=&fields[ool_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, set()),
                'ool_many_ones': ({UUID_131}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_one_local.ool_many_one&'
           'fields[one_one_locals]=attr_int,ool_many_one&'
           'fields[ool_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, {'attr_int', 'ool_many_one'}),
                'ool_many_ones': ({UUID_131}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_one_local.ool_one_manys&'
           'fields[one_one_locals]=&fields[ool_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, set()),
                'ool_one_manys': ({UUID_141, UUID_142}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_one_local.ool_one_manys&'
           'fields[one_one_locals]=attr_int,ool_one_manys&'
           'fields[ool_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, {'attr_int', 'ool_one_manys'}),
                'ool_one_manys': ({UUID_141, UUID_142}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_one_local.ool_many_manys&'
           'fields[one_one_locals]=&fields[ool_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, set()),
                'ool_many_manys': ({UUID_151, UUID_152}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_one_local.ool_many_manys&'
           'fields[one_one_locals]=attr_int,ool_many_manys&'
           'fields[ool_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, {'attr_int', 'ool_many_manys'}),
                'ool_many_manys': ({UUID_151, UUID_152}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_one_remote.oor_one_one_local&'
           'fields[one_one_remotes]=&fields[oor_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, set()),
                'oor_one_one_locals': ({UUID_211}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_one_remote.oor_one_one_local&'
           'fields[one_one_remotes]=attr_int,oor_one_one_local&'
           'fields[oor_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes':
                ({UUID_21}, {'attr_int', 'oor_one_one_local'}),
                'oor_one_one_locals': ({UUID_211}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_one_remote.oor_one_one_remote&'
           'fields[one_one_remotes]=&fields[oor_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, set()),
                'oor_one_one_remotes': ({UUID_221}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_one_remote.oor_one_one_remote&'
           'fields[one_one_remotes]=attr_int,oor_one_one_remote&'
           'fields[oor_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes':
                ({UUID_21}, {'attr_int', 'oor_one_one_remote'}),
                'oor_one_one_remotes': ({UUID_221}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_one_remote.oor_many_one&'
           'fields[one_one_remotes]=&fields[oor_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, set()),
                'oor_many_ones': ({UUID_231}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_one_remote.oor_many_one&'
           'fields[one_one_remotes]=attr_int,oor_many_one&'
           'fields[oor_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, {'attr_int', 'oor_many_one'}),
                'oor_many_ones': ({UUID_231}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_one_remote.oor_one_manys&'
           'fields[one_one_remotes]=&fields[oor_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, set()),
                'oor_one_manys': ({UUID_241, UUID_242}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_one_remote.oor_one_manys&'
           'fields[one_one_remotes]=attr_int,oor_one_manys&'
           'fields[oor_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, {'attr_int', 'oor_one_manys'}),
                'oor_one_manys': ({UUID_241, UUID_242}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_one_remote.oor_many_manys&'
           'fields[one_one_remotes]=&fields[oor_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, set()),
                'oor_many_manys': ({UUID_251, UUID_252}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_one_remote.oor_many_manys&'
           'fields[one_one_remotes]=attr_int,oor_many_manys&'
           'fields[oor_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, {'attr_int', 'oor_many_manys'}),
                'oor_many_manys': ({UUID_251, UUID_252}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=many_one.mo_one_one_local&'
           'fields[many_ones]=&fields[mo_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, set()),
                'mo_one_one_locals': ({UUID_311}, set())
            })
    url = (f'/centers/{UUID_1}?include=many_one.mo_one_one_local&'
           'fields[many_ones]=attr_int,mo_one_one_local&'
           'fields[mo_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, {'attr_int', 'mo_one_one_local'}),
                'mo_one_one_locals': ({UUID_311}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=many_one.mo_one_one_remote&'
           'fields[many_ones]=&fields[mo_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, set()),
                'mo_one_one_remotes': ({UUID_321}, set())
            })
    url = (f'/centers/{UUID_1}?include=many_one.mo_one_one_remote&'
           'fields[many_ones]=attr_int,mo_one_one_remote&'
           'fields[mo_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, {'attr_int', 'mo_one_one_remote'}),
                'mo_one_one_remotes': ({UUID_321}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=many_one.mo_many_one&'
           'fields[many_ones]=&fields[mo_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(document['included'], {
            'many_ones': ({UUID_31}, set()),
            'mo_many_ones': ({UUID_331}, set())
        })
    url = (f'/centers/{UUID_1}?include=many_one.mo_many_one&'
           'fields[many_ones]=attr_int,mo_many_one&'
           'fields[mo_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, {'attr_int', 'mo_many_one'}),
                'mo_many_ones': ({UUID_331}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=many_one.mo_one_manys&'
           'fields[many_ones]=&fields[mo_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, set()),
                'mo_one_manys': ({UUID_341, UUID_342}, set())
            })
    url = (f'/centers/{UUID_1}?include=many_one.mo_one_manys&'
           'fields[many_ones]=attr_int,mo_one_manys&'
           'fields[mo_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, {'attr_int', 'mo_one_manys'}),
                'mo_one_manys': ({UUID_341, UUID_342}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=many_one.mo_many_manys&'
           'fields[many_ones]=&fields[mo_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, set()),
                'mo_many_manys': ({UUID_351, UUID_352}, set())
            })
    url = (f'/centers/{UUID_1}?include=many_one.mo_many_manys&'
           'fields[many_ones]=attr_int,mo_many_manys&'
           'fields[mo_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, {'attr_int', 'mo_many_manys'}),
                'mo_many_manys': ({UUID_351, UUID_352}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_manys.om_one_one_local&'
           'fields[one_manys]=&fields[om_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, set()),
                'om_one_one_locals': ({UUID_411}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_manys.om_one_one_local&'
           'fields[one_manys]=attr_int,om_one_one_local&'
           'fields[om_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys':
                ({UUID_41, UUID_42}, {'attr_int', 'om_one_one_local'}),
                'om_one_one_locals': ({UUID_411}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_manys.om_one_one_remote&'
           'fields[one_manys]=&fields[om_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, set()),
                'om_one_one_remotes': ({UUID_421}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_manys.om_one_one_remote&'
           'fields[one_manys]=attr_int,om_one_one_remote&'
           'fields[om_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys':
                ({UUID_41, UUID_42}, {'attr_int', 'om_one_one_remote'}),
                'om_one_one_remotes': ({UUID_421}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_manys.om_many_one&'
           'fields[one_manys]=&fields[om_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, set()),
                'om_many_ones': ({UUID_431}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_manys.om_many_one&'
           'fields[one_manys]=attr_int,om_many_one&'
           'fields[om_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, {'attr_int', 'om_many_one'}),
                'om_many_ones': ({UUID_431}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_manys.om_one_manys&'
           'fields[one_manys]=&fields[om_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, set()),
                'om_one_manys': ({UUID_441, UUID_442}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_manys.om_one_manys&'
           'fields[one_manys]=attr_int,om_one_manys&'
           'fields[om_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, {'attr_int', 'om_one_manys'}),
                'om_one_manys': ({UUID_441, UUID_442}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=one_manys.om_many_manys&'
           'fields[one_manys]=&fields[om_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, set()),
                'om_many_manys': ({UUID_451, UUID_452}, set())
            })
    url = (f'/centers/{UUID_1}?include=one_manys.om_many_manys&'
           'fields[one_manys]=attr_int,om_many_manys&'
           'fields[om_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys':
                ({UUID_41, UUID_42}, {'attr_int', 'om_many_manys'}),
                'om_many_manys': ({UUID_451, UUID_452}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=many_manys.mm_one_one_local&'
           'fields[many_manys]=&fields[mm_one_one_locals]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, set()),
                'mm_one_one_locals': ({UUID_511}, set())
            })
    url = (f'/centers/{UUID_1}?include=many_manys.mm_one_one_local&'
           'fields[many_manys]=attr_int,mm_one_one_local&'
           'fields[mm_one_one_locals]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys':
                ({UUID_51, UUID_52}, {'attr_int', 'mm_one_one_local'}),
                'mm_one_one_locals': ({UUID_511}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=many_manys.mm_one_one_remote&'
           'fields[many_manys]=&fields[mm_one_one_remotes]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, set()),
                'mm_one_one_remotes': ({UUID_521}, set())
            })
    url = (f'/centers/{UUID_1}?include=many_manys.mm_one_one_remote&'
           'fields[many_manys]=attr_int,mm_one_one_remote&'
           'fields[mm_one_one_remotes]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys':
                ({UUID_51, UUID_52}, {'attr_int', 'mm_one_one_remote'}),
                'mm_one_one_remotes': ({UUID_521}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=many_manys.mm_many_one&'
           'fields[many_manys]=&fields[mm_many_ones]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, set()),
                'mm_many_ones': ({UUID_531}, set())
            })
    url = (f'/centers/{UUID_1}?include=many_manys.mm_many_one&'
           'fields[many_manys]=attr_int,mm_many_one&'
           'fields[mm_many_ones]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, {'attr_int', 'mm_many_one'}),
                'mm_many_ones': ({UUID_531}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=many_manys.mm_one_manys&'
           'fields[many_manys]=&fields[mm_one_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, set()),
                'mm_one_manys': ({UUID_541, UUID_542}, set())
            })
    url = (f'/centers/{UUID_1}?include=many_manys.mm_one_manys&'
           'fields[many_manys]=attr_int,mm_one_manys&'
           'fields[mm_one_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys':
                ({UUID_51, UUID_52}, {'attr_int', 'mm_one_manys'}),
                'mm_one_manys': ({UUID_541, UUID_542}, {'attr_str'})
            })

    url = (f'/centers/{UUID_1}?include=many_manys.mm_many_manys&'
           'fields[many_manys]=&fields[mm_many_manys]=')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, set()),
                'mm_many_manys': ({UUID_551, UUID_552}, set())
            })
    url = (f'/centers/{UUID_1}?include=many_manys.mm_many_manys&'
           'fields[many_manys]=attr_int,mm_many_manys&'
           'fields[mm_many_manys]=attr_str')
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys':
                ({UUID_51, UUID_52}, {'attr_int', 'mm_many_manys'}),
                'mm_many_manys': ({UUID_551, UUID_552}, {'attr_str'})
            })


async def test_get_object_accept_no_parameter(client):
    """Functional test for a GET /{collection}/{id} request with an Accept
    header where some (but not all) instances of the JSON API media type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    headers = {
        'Accept':
        'application/vnd.api+json;xxxxxxxx=0,application/vnd.api+json',
    }
    async with client.get(url, headers=headers) as response:
        document = await assert_get_object(response)
        data = document['data']
        assert data['id'] == UUID_1
        attributes = data['attributes']
        assert attributes['attr_int'] == 1
        assert attributes['attr_str'] == 'one'


async def test_get_object_no_accept(client):
    """Functional test for a GET /{collection}/{id} request without an Accept
    header.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    headers = {}
    async with client.get(url, headers=headers) as response:
        document = await assert_get_object(response)
        data = document['data']
        assert data['id'] == UUID_1
        attributes = data['attributes']
        assert attributes['attr_int'] == 1
        assert attributes['attr_str'] == 'one'


#
# Failed requests/responses
#
async def test_get_object_nonexistent_collection(client):
    """Functional test for a failed GET /{collection}/{id} request where the
    {collection} does not exist.
    """

    url = f'/xxxxxxxxs/{UUID_1}'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, '/xxxxxxxxs')


async def test_get_object_nonexistent_id(client):
    """Functional test for a failed GET /{collection}/{id} request where the
    {id} does not exist.
    """

    url = '/centers/88888888'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url)


async def test_get_object_malformed_id(client):
    """Functional test for a failed GET /{collection}/{id} request where the
    {id} does not exist.
    """

    url = '/centers/8888-8888'
    async with client.get(url, headers=HEADERS) as response:
        await assert_nonexistent(response, url, 'Malformed id.')


async def test_get_object_content_type_parameter(client):
    """Functional test for a failed GET /{collection}/{id} request where the
    Content-Type header contains a parameter.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    headers = {
        'Content-Type': 'application/vnd.api+json;xxxxxxxx=0',
    }
    async with client.get(url, headers=headers) as response:
        await assert_content_type_parameter(response)


async def test_get_object_accept_parameters(client):
    """Functional test for a failed GET /{collection}/{id} request with the
    Accept header where all instances of the JSON API media type
    ('application/vnd.api+json') are modified with media type parameters.
    """

    await post_centers_uuid_1(client)

    url = f'/centers/{UUID_1}'
    headers = {
        'Accept': 'application/vnd.api+json;xxxxxxxx=0',
    }
    async with client.get(url, headers=headers) as response:
        await assert_accept_parameters(response)


async def test_get_object_include_invalid_path(client):
    """Functional test for a failed GET /{collection}/{id}?include=x request
    due to an invalid relationship path.
    """

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}?include=xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_include_invalid_path(response, 'xxxxxxxx')
    url = f'/centers/{UUID_1}?include=one_one_local.xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_include_invalid_path(response, 'one_one_local.xxxxxxxx')
    url = f'/centers/{UUID_1}?include=one_one_local.ool_one_one_local.xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_include_invalid_path(
            response, 'one_one_local.ool_one_one_local.xxxxxxxx')


async def test_get_object_query_include(client):
    """Functional test for a failed GET /{collection}/{id}?include=x request.
    """

    # pylint: disable=too-many-statements

    await model_init(client)

    url = f'/centers/{UUID_1}?include=one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(document['included'],
                                    {'one_one_locals': ({UUID_11}, None)})

    url = f'/centers/{UUID_1}?include=one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(document['included'],
                                    {'one_one_remotes': ({UUID_21}, None)})

    url = f'/centers/{UUID_1}?include=many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(document['included'],
                                    {'many_ones': ({UUID_31}, None)})

    url = f'/centers/{UUID_1}?include=one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(document['included'],
                                    {'one_manys': ({UUID_41, UUID_42}, None)})

    url = f'/centers/{UUID_1}?include=many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_small_model_included(document['included'],
                                    {'many_manys': ({UUID_51, UUID_52}, None)})

    await model_extend(client)

    url = f'/centers/{UUID_1}?include=one_one_local.ool_one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, None),
                'ool_one_one_locals': ({UUID_111}, None)
            })

    url = f'/centers/{UUID_1}?include=one_one_local.ool_one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, None),
                'ool_one_one_remotes': ({UUID_121}, None)
            })

    url = f'/centers/{UUID_1}?include=one_one_local.ool_many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, None),
                'ool_many_ones': ({UUID_131}, None)
            })

    url = f'/centers/{UUID_1}?include=one_one_local.ool_one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, None),
                'ool_one_manys': ({UUID_141, UUID_142}, None)
            })

    url = f'/centers/{UUID_1}?include=one_one_local.ool_many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_locals': ({UUID_11}, None),
                'ool_many_manys': ({UUID_151, UUID_152}, None)
            })

    url = f'/centers/{UUID_1}?include=one_one_remote.oor_one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, None),
                'oor_one_one_locals': ({UUID_211}, None)
            })

    url = f'/centers/{UUID_1}?include=one_one_remote.oor_one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, None),
                'oor_one_one_remotes': ({UUID_221}, None)
            })

    url = f'/centers/{UUID_1}?include=one_one_remote.oor_many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, None),
                'oor_many_ones': ({UUID_231}, None)
            })

    url = f'/centers/{UUID_1}?include=one_one_remote.oor_one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, None),
                'oor_one_manys': ({UUID_241, UUID_242}, None)
            })

    url = f'/centers/{UUID_1}?include=one_one_remote.oor_many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_one_remotes': ({UUID_21}, None),
                'oor_many_manys': ({UUID_251, UUID_252}, None)
            })

    url = f'/centers/{UUID_1}?include=many_one.mo_one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(document['included'], {
            'many_ones': ({UUID_31}, None),
            'mo_one_one_locals': ({UUID_311}, None)
        })

    url = f'/centers/{UUID_1}?include=many_one.mo_one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, None),
                'mo_one_one_remotes': ({UUID_321}, None)
            })

    url = f'/centers/{UUID_1}?include=many_one.mo_many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(document['included'], {
            'many_ones': ({UUID_31}, None),
            'mo_many_ones': ({UUID_331}, None)
        })

    url = f'/centers/{UUID_1}?include=many_one.mo_one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, None),
                'mo_one_manys': ({UUID_341, UUID_342}, None)
            })

    url = f'/centers/{UUID_1}?include=many_one.mo_many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_ones': ({UUID_31}, None),
                'mo_many_manys': ({UUID_351, UUID_352}, None)
            })

    url = f'/centers/{UUID_1}?include=one_manys.om_one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, None),
                'om_one_one_locals': ({UUID_411}, None)
            })

    url = f'/centers/{UUID_1}?include=one_manys.om_one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, None),
                'om_one_one_remotes': ({UUID_421}, None)
            })

    url = f'/centers/{UUID_1}?include=one_manys.om_many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, None),
                'om_many_ones': ({UUID_431}, None)
            })

    url = f'/centers/{UUID_1}?include=one_manys.om_one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, None),
                'om_one_manys': ({UUID_441, UUID_442}, None)
            })

    url = f'/centers/{UUID_1}?include=one_manys.om_many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'one_manys': ({UUID_41, UUID_42}, None),
                'om_many_manys': ({UUID_451, UUID_452}, None)
            })

    url = f'/centers/{UUID_1}?include=many_manys.mm_one_one_local'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, None),
                'mm_one_one_locals': ({UUID_511}, None)
            })

    url = f'/centers/{UUID_1}?include=many_manys.mm_one_one_remote'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, None),
                'mm_one_one_remotes': ({UUID_521}, None)
            })

    url = f'/centers/{UUID_1}?include=many_manys.mm_many_one'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, None),
                'mm_many_ones': ({UUID_531}, None)
            })

    url = f'/centers/{UUID_1}?include=many_manys.mm_one_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, None),
                'mm_one_manys': ({UUID_541, UUID_542}, None)
            })

    url = f'/centers/{UUID_1}?include=many_manys.mm_many_manys'
    async with client.get(url, headers=HEADERS) as response:
        document = await assert_get_object(response)
        assert_medium_model_included(
            document['included'], {
                'many_manys': ({UUID_51, UUID_52}, None),
                'mm_many_manys': ({UUID_551, UUID_552}, None)
            })


async def test_get_object_fields_invalid_resource(client):
    """Functional test for a failed GET /{collection}?fields[x]=x request
    where the resource does not exist.
    """

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}?fields[xxxxxxxx]=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_resource(response, 'xxxxxxxx')


async def test_get_object_fields_invalid_field(client):
    """Functional test for a failed GET /{collection}?fields[x]=x request
    where the field does not exist.
    """

    await model_init(client)
    await model_extend(client)

    url = f'/centers/{UUID_1}?fields[centers]=xxxxxxxx'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'centers', 'xxxxxxxx')

    url = f'/centers/{UUID_1}?fields[centers]=type'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'centers', 'type')

    url = f'/centers/{UUID_1}?fields[centers]=id'
    async with client.get(url, headers=HEADERS) as response:
        await assert_fields_invalid_field(response, 'centers', 'id')


async def test_get_object_query_sort(client):
    """Functional test for a failed GET /{collection}/{id}?fields[x]=x request.
    """

    url = f'/centers/{UUID_1}?sort=attr_int'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_sort(response)


async def test_get_object_query_page(client):
    """Functional test for a failed GET /{collection}/{id}?page[x]=x request.
    """

    url = f'/centers/{UUID_1}?page[number]=0&page[size]=10'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_page(response)


async def test_get_object_query_filter(client):
    """Functional test for a failed GET /{collection}/{id}?filter[x]=x request.
    """

    url = f'/centers/{UUID_1}?filter[x]=x'
    async with client.get(url, headers=HEADERS) as response:
        await assert_query_filter(response)
