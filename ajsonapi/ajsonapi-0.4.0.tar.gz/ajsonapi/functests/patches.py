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
"""Common patch operations for functional tests."""

from ajsonapi.functests.asserts.patch_relationships import (
    assert_patch_relationship,
)
from ajsonapi.functests.headers import SEND_HEADERS
from ajsonapi.functests.model_objects import (
    JSON_IDENTIFIER_MANY_ONES_UUID_31,
    JSON_IDENTIFIER_MM_MANY_ONES_UUID_531,
    JSON_IDENTIFIER_MM_ONE_ONE_LOCALS_UUID_511,
    JSON_IDENTIFIER_MM_ONE_ONE_REMOTES_UUID_521,
    JSON_IDENTIFIER_MO_MANY_ONES_UUID_331,
    JSON_IDENTIFIER_MO_ONE_ONE_LOCALS_UUID_311,
    JSON_IDENTIFIER_MO_ONE_ONE_REMOTES_UUID_321,
    JSON_IDENTIFIER_OM_MANY_ONES_UUID_431,
    JSON_IDENTIFIER_OM_ONE_ONE_LOCALS_UUID_411,
    JSON_IDENTIFIER_OM_ONE_ONE_REMOTES_UUID_421,
    JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11,
    JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21,
    JSON_IDENTIFIER_OOL_MANY_ONES_UUID_131,
    JSON_IDENTIFIER_OOL_ONE_ONE_LOCALS_UUID_111,
    JSON_IDENTIFIER_OOL_ONE_ONE_REMOTES_UUID_121,
    JSON_IDENTIFIER_OOR_MANY_ONES_UUID_231,
    JSON_IDENTIFIER_OOR_ONE_ONE_LOCALS_UUID_211,
    JSON_IDENTIFIER_OOR_ONE_ONE_REMOTES_UUID_221,
    JSON_IDENTIFIERS_MANY_MANYS_UUID_51_52,
    JSON_IDENTIFIERS_MANY_MANYS_UUID_51_52_53,
    JSON_IDENTIFIERS_MM_MANY_MANYS_UUID_551_552,
    JSON_IDENTIFIERS_MM_ONE_MANYS_UUID_541_542,
    JSON_IDENTIFIERS_MO_MANY_MANYS_UUID_351_352,
    JSON_IDENTIFIERS_MO_ONE_MANYS_UUID_341_342,
    JSON_IDENTIFIERS_OM_MANY_MANYS_UUID_451_452,
    JSON_IDENTIFIERS_OM_ONE_MANYS_UUID_441_442,
    JSON_IDENTIFIERS_ONE_MANYS_UUID_41_42,
    JSON_IDENTIFIERS_ONE_MANYS_UUID_41_42_43,
    JSON_IDENTIFIERS_OOL_MANY_MANYS_UUID_151_152,
    JSON_IDENTIFIERS_OOL_ONE_MANYS_UUID_141_142,
    JSON_IDENTIFIERS_OOR_MANY_MANYS_UUID_251_252,
    JSON_IDENTIFIERS_OOR_ONE_MANYS_UUID_241_242,
    UUID_1,
    UUID_11,
    UUID_21,
    UUID_31,
    UUID_41,
    UUID_51,
)


async def patch_centers_uuid_1_one_one_locals_uuid_11(client):
    """Successful PATCH /centers/UUID_1/relationships/one_one_local."""

    url = f'/centers/{UUID_1}/relationships/one_one_local'
    json = JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_centers_uuid_1_one_one_remotes_uuid_21(client):
    """Successful PATCH /centers/UUID_1/relationships/one_one_remote."""

    url = f'/centers/{UUID_1}/relationships/one_one_remote'
    json = JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_centers_uuid_1_many_ones_uuid_31(client):
    """Successful PATCH /centers/UUID_1/relationships/many_one."""

    url = f'/centers/{UUID_1}/relationships/many_one'
    json = JSON_IDENTIFIER_MANY_ONES_UUID_31
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_centers_uuid_1_one_manys_uuid_41_42(client):
    """Successful PATCH /centers/UUID_1/relationships/one_manys."""

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41_42
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_centers_uuid_1_one_manys_uuid_41_42_43(client):
    """Successful PATCH /centers/UUID_1/relationships/one_manys."""

    url = f'/centers/{UUID_1}/relationships/one_manys'
    json = JSON_IDENTIFIERS_ONE_MANYS_UUID_41_42_43
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_centers_uuid_1_many_manys_uuid_51_52(client):
    """Successful PATCH /centers/UUID_1/relationships/many_manys."""

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51_52
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_centers_uuid_1_many_manys_uuid_51_52_53(client):
    """Successful PATCH /centers/UUID_1/relationships/many_manys."""

    url = f'/centers/{UUID_1}/relationships/many_manys'
    json = JSON_IDENTIFIERS_MANY_MANYS_UUID_51_52_53
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_one_locals_uuid_11_ool_one_one_locals_uuid_111(client):
    """Successful PATCH /one_one_locals/UUID_11/relationships/ool_one_one_local.
    """

    url = f'/one_one_locals/{UUID_11}/relationships/ool_one_one_local'
    json = JSON_IDENTIFIER_OOL_ONE_ONE_LOCALS_UUID_111
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_one_locals_uuid_11_ool_one_one_remotes_uuid_121(client):
    """Successful PATCH
    /one_one_locals/UUID_11/relationships/ool_one_one_remote.
    """

    url = f'/one_one_locals/{UUID_11}/relationships/ool_one_one_remote'
    json = JSON_IDENTIFIER_OOL_ONE_ONE_REMOTES_UUID_121
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_one_locals_uuid_11_ool_many_ones_uuid_131(client):
    """Successful PATCH /one_one_locals/UUID_11/relationships/ool_many_one."""

    url = f'/one_one_locals/{UUID_11}/relationships/ool_many_one'
    json = JSON_IDENTIFIER_OOL_MANY_ONES_UUID_131
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_one_locals_uuid_11_ool_one_manys_uuid_141_142(client):
    """Successful PATCH /one_one_locals/UUID_11/relationships/ool_one_manys."""

    url = f'/one_one_locals/{UUID_11}/relationships/ool_one_manys'
    json = JSON_IDENTIFIERS_OOL_ONE_MANYS_UUID_141_142
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_one_locals_uuid_11_ool_many_manys_uuid_151_152(client):
    """Successful PATCH /one_one_locals/UUID_11/relationships/ool_many_manys."""

    url = f'/one_one_locals/{UUID_11}/relationships/ool_many_manys'
    json = JSON_IDENTIFIERS_OOL_MANY_MANYS_UUID_151_152
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_one_remotes_uuid_21_oor_one_one_locals_uuid_211(client):
    """Successful PATCH
    /one_one_remotes/UUID_21/relationships/oor_one_one_local.
    """

    url = f'/one_one_remotes/{UUID_21}/relationships/oor_one_one_local'
    json = JSON_IDENTIFIER_OOR_ONE_ONE_LOCALS_UUID_211
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_one_remotes_uuid_21_oor_one_one_remotes_uuid_221(client):
    """Successful PATCH
    /one_one_remotes/UUID_21/relationships/oor_one_one_remote.
    """

    url = f'/one_one_remotes/{UUID_21}/relationships/oor_one_one_remote'
    json = JSON_IDENTIFIER_OOR_ONE_ONE_REMOTES_UUID_221
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_one_remotes_uuid_21_oor_many_ones_uuid_231(client):
    """Successful PATCH /one_one_remotes/UUID_21/relationships/oor_many_one."""

    url = f'/one_one_remotes/{UUID_21}/relationships/oor_many_one'
    json = JSON_IDENTIFIER_OOR_MANY_ONES_UUID_231
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_one_remotes_uuid_21_oor_one_manys_uuid_241_242(client):
    """Successful PATCH /one_one_remotes/UUID_21/relationships/oor_one_manys."""

    url = f'/one_one_remotes/{UUID_21}/relationships/oor_one_manys'
    json = JSON_IDENTIFIERS_OOR_ONE_MANYS_UUID_241_242
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_one_remotes_uuid_21_oor_many_manys_uuid_251_252(client):
    """Successful PATCH /one_one_remotes/UUID_21/relationships/oor_many_manys.
    """

    url = f'/one_one_remotes/{UUID_21}/relationships/oor_many_manys'
    json = JSON_IDENTIFIERS_OOR_MANY_MANYS_UUID_251_252
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_many_ones_uuid_31_mo_one_one_locals_uuid_311(client):
    """Successful PATCH
    /many_ones/UUID_31/relationships/mo_one_one_local.
    """

    url = f'/many_ones/{UUID_31}/relationships/mo_one_one_local'
    json = JSON_IDENTIFIER_MO_ONE_ONE_LOCALS_UUID_311
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_many_ones_uuid_31_mo_one_one_remotes_uuid_321(client):
    """Successful PATCH
    /many_ones/UUID_31/relationships/mo_one_one_remote.
    """

    url = f'/many_ones/{UUID_31}/relationships/mo_one_one_remote'
    json = JSON_IDENTIFIER_MO_ONE_ONE_REMOTES_UUID_321
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_many_ones_uuid_31_mo_many_ones_uuid_331(client):
    """Successful PATCH /many_ones/UUID_31/relationships/mo_many_one."""

    url = f'/many_ones/{UUID_31}/relationships/mo_many_one'
    json = JSON_IDENTIFIER_MO_MANY_ONES_UUID_331
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_many_ones_uuid_31_mo_one_manys_uuid_341_342(client):
    """Successful PATCH /many_ones/UUID_31/relationships/mo_one_manys."""

    url = f'/many_ones/{UUID_31}/relationships/mo_one_manys'
    json = JSON_IDENTIFIERS_MO_ONE_MANYS_UUID_341_342
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_many_ones_uuid_31_mo_many_manys_uuid_351_352(client):
    """Successful PATCH /many_ones/UUID_31/relationships/mo_many_manys.
    """

    url = f'/many_ones/{UUID_31}/relationships/mo_many_manys'
    json = JSON_IDENTIFIERS_MO_MANY_MANYS_UUID_351_352
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_manys_uuid_41_om_one_one_locals_uuid_411(client):
    """Successful PATCH
    /one_manys/UUID_41/relationships/om_one_one_local.
    """

    url = f'/one_manys/{UUID_41}/relationships/om_one_one_local'
    json = JSON_IDENTIFIER_OM_ONE_ONE_LOCALS_UUID_411
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_manys_uuid_41_om_one_one_remotes_uuid_421(client):
    """Successful PATCH
    /one_manys/UUID_41/relationships/om_one_one_remote.
    """

    url = f'/one_manys/{UUID_41}/relationships/om_one_one_remote'
    json = JSON_IDENTIFIER_OM_ONE_ONE_REMOTES_UUID_421
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_manys_uuid_41_om_many_ones_uuid_431(client):
    """Successful PATCH /one_manys/UUID_41/relationships/om_many_one."""

    url = f'/one_manys/{UUID_41}/relationships/om_many_one'
    json = JSON_IDENTIFIER_OM_MANY_ONES_UUID_431
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_manys_uuid_41_om_one_manys_uuid_441_442(client):
    """Successful PATCH /one_manys/UUID_41/relationships/om_one_manys."""

    url = f'/one_manys/{UUID_41}/relationships/om_one_manys'
    json = JSON_IDENTIFIERS_OM_ONE_MANYS_UUID_441_442
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_one_manys_uuid_41_om_many_manys_uuid_451_452(client):
    """Successful PATCH /one_manys/UUID_41/relationships/om_many_manys.
    """

    url = f'/one_manys/{UUID_41}/relationships/om_many_manys'
    json = JSON_IDENTIFIERS_OM_MANY_MANYS_UUID_451_452
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_many_manys_uuid_51_mm_one_one_locals_uuid_511(client):
    """Successful PATCH
    /many_manys/UUID_51/relationships/mm_one_one_local.
    """

    url = f'/many_manys/{UUID_51}/relationships/mm_one_one_local'
    json = JSON_IDENTIFIER_MM_ONE_ONE_LOCALS_UUID_511
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_many_manys_uuid_51_mm_one_one_remotes_uuid_521(client):
    """Successful PATCH
    /many_manys/UUID_51/relationships/mm_one_one_remote.
    """

    url = f'/many_manys/{UUID_51}/relationships/mm_one_one_remote'
    json = JSON_IDENTIFIER_MM_ONE_ONE_REMOTES_UUID_521
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_many_manys_uuid_51_mm_many_ones_uuid_531(client):
    """Successful PATCH /many_manys/UUID_51/relationships/mm_many_one."""

    url = f'/many_manys/{UUID_51}/relationships/mm_many_one'
    json = JSON_IDENTIFIER_MM_MANY_ONES_UUID_531
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_many_manys_uuid_51_mm_one_manys_uuid_541_542(client):
    """Successful PATCH /many_manys/UUID_51/relationships/mm_one_manys."""

    url = f'/many_manys/{UUID_51}/relationships/mm_one_manys'
    json = JSON_IDENTIFIERS_MM_ONE_MANYS_UUID_541_542
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)


async def patch_many_manys_uuid_51_mm_many_manys_uuid_551_552(client):
    """Successful PATCH /many_manys/UUID_51/relationships/mm_many_manys.
    """

    url = f'/many_manys/{UUID_51}/relationships/mm_many_manys'
    json = JSON_IDENTIFIERS_MM_MANY_MANYS_UUID_551_552
    async with client.patch(url, headers=SEND_HEADERS, json=json) as response:
        return await assert_patch_relationship(response)
