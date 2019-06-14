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
"""Common post operations for functional tests."""

from ajsonapi.functests.asserts.post_collection import (
    assert_post_collection_with_id,
    assert_post_collection_without_id,
)
from ajsonapi.functests.headers import SEND_HEADERS
from ajsonapi.functests.model_objects import (
    JSON_CENTERS_1,
    JSON_CENTERS_UUID_1,
    JSON_CENTERS_UUID_2,
    JSON_CENTERS_UUID_3,
    JSON_MANY_MANYS_UUID_51,
    JSON_MANY_MANYS_UUID_52,
    JSON_MANY_MANYS_UUID_53,
    JSON_MANY_ONES_UUID_31,
    JSON_MANY_ONES_UUID_32,
    JSON_MM_MANY_MANYS_UUID_551,
    JSON_MM_MANY_MANYS_UUID_552,
    JSON_MM_MANY_ONES_UUID_531,
    JSON_MM_ONE_MANYS_UUID_541,
    JSON_MM_ONE_MANYS_UUID_542,
    JSON_MM_ONE_ONE_LOCALS_UUID_511,
    JSON_MM_ONE_ONE_REMOTES_UUID_521,
    JSON_MO_MANY_MANYS_UUID_351,
    JSON_MO_MANY_MANYS_UUID_352,
    JSON_MO_MANY_ONES_UUID_331,
    JSON_MO_ONE_MANYS_UUID_341,
    JSON_MO_ONE_MANYS_UUID_342,
    JSON_MO_ONE_ONE_LOCALS_UUID_311,
    JSON_MO_ONE_ONE_REMOTES_UUID_321,
    JSON_OM_MANY_MANYS_UUID_451,
    JSON_OM_MANY_MANYS_UUID_452,
    JSON_OM_MANY_ONES_UUID_431,
    JSON_OM_ONE_MANYS_UUID_441,
    JSON_OM_ONE_MANYS_UUID_442,
    JSON_OM_ONE_ONE_LOCALS_UUID_411,
    JSON_OM_ONE_ONE_REMOTES_UUID_421,
    JSON_ONE_MANYS_UUID_41,
    JSON_ONE_MANYS_UUID_42,
    JSON_ONE_MANYS_UUID_43,
    JSON_ONE_ONE_LOCALS_UUID_11,
    JSON_ONE_ONE_LOCALS_UUID_12,
    JSON_ONE_ONE_REMOTES_UUID_21,
    JSON_ONE_ONE_REMOTES_UUID_22,
    JSON_OOL_MANY_MANYS_UUID_151,
    JSON_OOL_MANY_MANYS_UUID_152,
    JSON_OOL_MANY_ONES_UUID_131,
    JSON_OOL_ONE_MANYS_UUID_141,
    JSON_OOL_ONE_MANYS_UUID_142,
    JSON_OOL_ONE_ONE_LOCALS_UUID_111,
    JSON_OOL_ONE_ONE_REMOTES_UUID_121,
    JSON_OOR_MANY_MANYS_UUID_251,
    JSON_OOR_MANY_MANYS_UUID_252,
    JSON_OOR_MANY_ONES_UUID_231,
    JSON_OOR_ONE_MANYS_UUID_241,
    JSON_OOR_ONE_MANYS_UUID_242,
    JSON_OOR_ONE_ONE_LOCALS_UUID_211,
    JSON_OOR_ONE_ONE_REMOTES_UUID_221,
)


async def post_centers_uuid_1(client):
    """Successful POST /centers with id=UUID_1."""

    url = '/centers'
    json = JSON_CENTERS_UUID_1
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_centers_uuid_2(client):
    """Successful POST /centers with id=UUID_2."""

    url = '/centers'
    json = JSON_CENTERS_UUID_2
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_centers_uuid_3(client):
    """Successful POST /centers with id=UUID_3."""

    url = '/centers'
    json = JSON_CENTERS_UUID_3
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_centers_1(client):
    """Successful POST /centers without id."""

    url = '/centers'
    json = JSON_CENTERS_1
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        document = await assert_post_collection_without_id(response)
        assert document['data']['id'] == '1'
    return document


async def post_one_one_locals_uuid_11(client):
    """Successful POST /one_one_locals with id=UUID_11."""
    url = '/one_one_locals'
    json = JSON_ONE_ONE_LOCALS_UUID_11
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_one_one_locals_uuid_12(client):
    """Successful POST /one_one_locals with id=UUID_12."""
    url = '/one_one_locals'
    json = JSON_ONE_ONE_LOCALS_UUID_12
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_one_one_remotes_uuid_21(client):
    """Successful POST /one_one_remotes with id=UUID_21."""
    url = '/one_one_remotes'
    json = JSON_ONE_ONE_REMOTES_UUID_21
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_one_one_remotes_uuid_22(client):
    """Successful POST /one_one_remotes with id=UUID_22."""
    url = '/one_one_remotes'
    json = JSON_ONE_ONE_REMOTES_UUID_22
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_many_ones_uuid_31(client):
    """Successful POST /many_ones with id=UUID_31."""
    url = '/many_ones'
    json = JSON_MANY_ONES_UUID_31
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_many_ones_uuid_32(client):
    """Successful POST /many_ones with id=UUID_32."""
    url = '/many_ones'
    json = JSON_MANY_ONES_UUID_32
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_one_manys_uuid_41(client):
    """Successful POST /one_manys with id=UUID_41."""
    url = '/one_manys'
    json = JSON_ONE_MANYS_UUID_41
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_one_manys_uuid_42(client):
    """Successful POST /one_manys with id=UUID_42."""
    url = '/one_manys'
    json = JSON_ONE_MANYS_UUID_42
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_one_manys_uuid_43(client):
    """Successful POST /one_manys with id=UUID_43."""
    url = '/one_manys'
    json = JSON_ONE_MANYS_UUID_43
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_many_manys_uuid_51(client):
    """Successful POST /many_manys with id=UUID_51."""
    url = '/many_manys'
    json = JSON_MANY_MANYS_UUID_51
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_many_manys_uuid_52(client):
    """Successful POST /many_manys with id=UUID_52."""
    url = '/many_manys'
    json = JSON_MANY_MANYS_UUID_52
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_many_manys_uuid_53(client):
    """Successful POST /many_manys with id=UUID_53."""
    url = '/many_manys'
    json = JSON_MANY_MANYS_UUID_53
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_ool_one_one_locals_uuid_111(client):
    """Successful POST /ool_one_one_locals with id=UUID_111."""
    url = '/ool_one_one_locals'
    json = JSON_OOL_ONE_ONE_LOCALS_UUID_111
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_ool_one_one_remotes_uuid_121(client):
    """Successful POST /ool_one_one_remotes with id=UUID_121."""
    url = '/ool_one_one_remotes'
    json = JSON_OOL_ONE_ONE_REMOTES_UUID_121
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_ool_many_ones_uuid_131(client):
    """Successful POST /ool_many_ones with id=UUID_131."""
    url = '/ool_many_ones'
    json = JSON_OOL_MANY_ONES_UUID_131
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_ool_one_manys_uuid_141(client):
    """Successful POST /ool_one_manys with id=UUID_141."""
    url = '/ool_one_manys'
    json = JSON_OOL_ONE_MANYS_UUID_141
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_ool_one_manys_uuid_142(client):
    """Successful POST /ool_one_manys with id=UUID_141."""
    url = '/ool_one_manys'
    json = JSON_OOL_ONE_MANYS_UUID_142
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_ool_many_manys_uuid_151(client):
    """Successful POST /ool_many_manys with id=UUID_151."""
    url = '/ool_many_manys'
    json = JSON_OOL_MANY_MANYS_UUID_151
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_ool_many_manys_uuid_152(client):
    """Successful POST /ool_many_manys with id=UUID_152."""
    url = '/ool_many_manys'
    json = JSON_OOL_MANY_MANYS_UUID_152
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_oor_one_one_locals_uuid_211(client):
    """Successful POST /oor_one_one_locals with id=UUID_211."""
    url = '/oor_one_one_locals'
    json = JSON_OOR_ONE_ONE_LOCALS_UUID_211
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_oor_one_one_remotes_uuid_221(client):
    """Successful POST /oor_one_one_remotes with id=UUID_221."""
    url = '/oor_one_one_remotes'
    json = JSON_OOR_ONE_ONE_REMOTES_UUID_221
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_oor_many_ones_uuid_231(client):
    """Successful POST /oor_many_ones with id=UUID_231."""
    url = '/oor_many_ones'
    json = JSON_OOR_MANY_ONES_UUID_231
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_oor_one_manys_uuid_241(client):
    """Successful POST /oor_one_manys with id=UUID_241."""
    url = '/oor_one_manys'
    json = JSON_OOR_ONE_MANYS_UUID_241
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_oor_one_manys_uuid_242(client):
    """Successful POST /oor_one_manys with id=UUID_242."""
    url = '/oor_one_manys'
    json = JSON_OOR_ONE_MANYS_UUID_242
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_oor_many_manys_uuid_251(client):
    """Successful POST /oor_many_manys with id=UUID_251."""
    url = '/oor_many_manys'
    json = JSON_OOR_MANY_MANYS_UUID_251
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_oor_many_manys_uuid_252(client):
    """Successful POST /oor_many_manys with id=UUID_252."""
    url = '/oor_many_manys'
    json = JSON_OOR_MANY_MANYS_UUID_252
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mo_one_one_locals_uuid_311(client):
    """Successful POST /mo_one_one_locals with id=UUID_311."""
    url = '/mo_one_one_locals'
    json = JSON_MO_ONE_ONE_LOCALS_UUID_311
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mo_one_one_remotes_uuid_321(client):
    """Successful POST /mo_one_one_remotes with id=UUID_321."""
    url = '/mo_one_one_remotes'
    json = JSON_MO_ONE_ONE_REMOTES_UUID_321
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mo_many_ones_uuid_331(client):
    """Successful POST /mo_many_ones with id=UUID_331."""
    url = '/mo_many_ones'
    json = JSON_MO_MANY_ONES_UUID_331
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mo_one_manys_uuid_341(client):
    """Successful POST /mo_one_manys with id=UUID_341."""
    url = '/mo_one_manys'
    json = JSON_MO_ONE_MANYS_UUID_341
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mo_one_manys_uuid_342(client):
    """Successful POST /mo_one_manys with id=UUID_342."""
    url = '/mo_one_manys'
    json = JSON_MO_ONE_MANYS_UUID_342
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mo_many_manys_uuid_351(client):
    """Successful POST /mo_many_manys with id=UUID_351."""
    url = '/mo_many_manys'
    json = JSON_MO_MANY_MANYS_UUID_351
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mo_many_manys_uuid_352(client):
    """Successful POST /mo_many_manys with id=UUID_352."""
    url = '/mo_many_manys'
    json = JSON_MO_MANY_MANYS_UUID_352
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_om_one_one_locals_uuid_411(client):
    """Successful POST /om_one_one_locals with id=UUID_411."""
    url = '/om_one_one_locals'
    json = JSON_OM_ONE_ONE_LOCALS_UUID_411
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_om_one_one_remotes_uuid_421(client):
    """Successful POST /om_one_one_remotes with id=UUID_421."""
    url = '/om_one_one_remotes'
    json = JSON_OM_ONE_ONE_REMOTES_UUID_421
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_om_many_ones_uuid_431(client):
    """Successful POST /om_many_ones with id=UUID_431."""
    url = '/om_many_ones'
    json = JSON_OM_MANY_ONES_UUID_431
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_om_one_manys_uuid_441(client):
    """Successful POST /om_one_manys with id=UUID_441."""
    url = '/om_one_manys'
    json = JSON_OM_ONE_MANYS_UUID_441
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_om_one_manys_uuid_442(client):
    """Successful POST /om_one_manys with id=UUID_442."""
    url = '/om_one_manys'
    json = JSON_OM_ONE_MANYS_UUID_442
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_om_many_manys_uuid_451(client):
    """Successful POST /om_many_manys with id=UUID_451."""
    url = '/om_many_manys'
    json = JSON_OM_MANY_MANYS_UUID_451
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_om_many_manys_uuid_452(client):
    """Successful POST /om_many_manys with id=UUID_452."""
    url = '/om_many_manys'
    json = JSON_OM_MANY_MANYS_UUID_452
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mm_one_one_locals_uuid_511(client):
    """Successful POST /mm_one_one_locals with id=UUID_511."""
    url = '/mm_one_one_locals'
    json = JSON_MM_ONE_ONE_LOCALS_UUID_511
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mm_one_one_remotes_uuid_521(client):
    """Successful POST /mm_one_one_remotes with id=UUID_521."""
    url = '/mm_one_one_remotes'
    json = JSON_MM_ONE_ONE_REMOTES_UUID_521
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mm_many_ones_uuid_531(client):
    """Successful POST /mm_many_ones with id=UUID_531."""
    url = '/mm_many_ones'
    json = JSON_MM_MANY_ONES_UUID_531
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mm_one_manys_uuid_541(client):
    """Successful POST /mm_one_manys with id=UUID_541."""
    url = '/mm_one_manys'
    json = JSON_MM_ONE_MANYS_UUID_541
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mm_one_manys_uuid_542(client):
    """Successful POST /mm_one_manys with id=UUID_542."""
    url = '/mm_one_manys'
    json = JSON_MM_ONE_MANYS_UUID_542
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mm_many_manys_uuid_551(client):
    """Successful POST /mm_many_manys with id=UUID_551."""
    url = '/mm_many_manys'
    json = JSON_MM_MANY_MANYS_UUID_551
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)


async def post_mm_many_manys_uuid_552(client):
    """Successful POST /mm_many_manys with id=UUID_552."""
    url = '/mm_many_manys'
    json = JSON_MM_MANY_MANYS_UUID_552
    async with client.post(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_post_collection_with_id(response)
