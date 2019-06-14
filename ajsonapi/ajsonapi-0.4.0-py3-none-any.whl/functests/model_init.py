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
"""Module model_init provides a simple initial model for testing."""

from ajsonapi.functests.patches import (
    patch_centers_uuid_1_many_manys_uuid_51_52,
    patch_centers_uuid_1_many_ones_uuid_31,
    patch_centers_uuid_1_one_manys_uuid_41_42,
    patch_centers_uuid_1_one_one_locals_uuid_11,
    patch_centers_uuid_1_one_one_remotes_uuid_21,
    patch_many_manys_uuid_51_mm_many_manys_uuid_551_552,
    patch_many_manys_uuid_51_mm_many_ones_uuid_531,
    patch_many_manys_uuid_51_mm_one_manys_uuid_541_542,
    patch_many_manys_uuid_51_mm_one_one_locals_uuid_511,
    patch_many_manys_uuid_51_mm_one_one_remotes_uuid_521,
    patch_many_ones_uuid_31_mo_many_manys_uuid_351_352,
    patch_many_ones_uuid_31_mo_many_ones_uuid_331,
    patch_many_ones_uuid_31_mo_one_manys_uuid_341_342,
    patch_many_ones_uuid_31_mo_one_one_locals_uuid_311,
    patch_many_ones_uuid_31_mo_one_one_remotes_uuid_321,
    patch_one_manys_uuid_41_om_many_manys_uuid_451_452,
    patch_one_manys_uuid_41_om_many_ones_uuid_431,
    patch_one_manys_uuid_41_om_one_manys_uuid_441_442,
    patch_one_manys_uuid_41_om_one_one_locals_uuid_411,
    patch_one_manys_uuid_41_om_one_one_remotes_uuid_421,
    patch_one_one_locals_uuid_11_ool_many_manys_uuid_151_152,
    patch_one_one_locals_uuid_11_ool_many_ones_uuid_131,
    patch_one_one_locals_uuid_11_ool_one_manys_uuid_141_142,
    patch_one_one_locals_uuid_11_ool_one_one_locals_uuid_111,
    patch_one_one_locals_uuid_11_ool_one_one_remotes_uuid_121,
    patch_one_one_remotes_uuid_21_oor_many_manys_uuid_251_252,
    patch_one_one_remotes_uuid_21_oor_many_ones_uuid_231,
    patch_one_one_remotes_uuid_21_oor_one_manys_uuid_241_242,
    patch_one_one_remotes_uuid_21_oor_one_one_locals_uuid_211,
    patch_one_one_remotes_uuid_21_oor_one_one_remotes_uuid_221,
)
from ajsonapi.functests.posts import (
    post_centers_uuid_1,
    post_centers_uuid_2,
    post_centers_uuid_3,
    post_many_manys_uuid_51,
    post_many_manys_uuid_52,
    post_many_ones_uuid_31,
    post_mm_many_manys_uuid_551,
    post_mm_many_manys_uuid_552,
    post_mm_many_ones_uuid_531,
    post_mm_one_manys_uuid_541,
    post_mm_one_manys_uuid_542,
    post_mm_one_one_locals_uuid_511,
    post_mm_one_one_remotes_uuid_521,
    post_mo_many_manys_uuid_351,
    post_mo_many_manys_uuid_352,
    post_mo_many_ones_uuid_331,
    post_mo_one_manys_uuid_341,
    post_mo_one_manys_uuid_342,
    post_mo_one_one_locals_uuid_311,
    post_mo_one_one_remotes_uuid_321,
    post_om_many_manys_uuid_451,
    post_om_many_manys_uuid_452,
    post_om_many_ones_uuid_431,
    post_om_one_manys_uuid_441,
    post_om_one_manys_uuid_442,
    post_om_one_one_locals_uuid_411,
    post_om_one_one_remotes_uuid_421,
    post_one_manys_uuid_41,
    post_one_manys_uuid_42,
    post_one_one_locals_uuid_11,
    post_one_one_remotes_uuid_21,
    post_ool_many_manys_uuid_151,
    post_ool_many_manys_uuid_152,
    post_ool_many_ones_uuid_131,
    post_ool_one_manys_uuid_141,
    post_ool_one_manys_uuid_142,
    post_ool_one_one_locals_uuid_111,
    post_ool_one_one_remotes_uuid_121,
    post_oor_many_manys_uuid_251,
    post_oor_many_manys_uuid_252,
    post_oor_many_ones_uuid_231,
    post_oor_one_manys_uuid_241,
    post_oor_one_manys_uuid_242,
    post_oor_one_one_locals_uuid_211,
    post_oor_one_one_remotes_uuid_221,
)


async def model_init(client):
    """Initializes a centers UUID_1 object with relationships to one object of
    each related class.
    """

    await post_centers_uuid_1(client)
    await post_centers_uuid_2(client)
    await post_centers_uuid_3(client)
    await post_one_one_locals_uuid_11(client)
    await post_one_one_remotes_uuid_21(client)
    await post_many_ones_uuid_31(client)
    await post_one_manys_uuid_41(client)
    await post_one_manys_uuid_42(client)
    await post_many_manys_uuid_51(client)
    await post_many_manys_uuid_52(client)

    await patch_centers_uuid_1_one_one_locals_uuid_11(client)
    await patch_centers_uuid_1_one_one_remotes_uuid_21(client)
    await patch_centers_uuid_1_many_ones_uuid_31(client)
    await patch_centers_uuid_1_one_manys_uuid_41_42(client)
    await patch_centers_uuid_1_many_manys_uuid_51_52(client)


async def model_extend(client):
    """Initializes a centers UUID_1 object with relationships to one object of
    each related class.
    """
    # pylint: disable=too-many-statements

    await post_ool_one_one_locals_uuid_111(client)
    await post_ool_one_one_remotes_uuid_121(client)
    await post_ool_many_ones_uuid_131(client)
    await post_ool_one_manys_uuid_141(client)
    await post_ool_one_manys_uuid_142(client)
    await post_ool_many_manys_uuid_151(client)
    await post_ool_many_manys_uuid_152(client)

    await patch_one_one_locals_uuid_11_ool_one_one_locals_uuid_111(client)
    await patch_one_one_locals_uuid_11_ool_one_one_remotes_uuid_121(client)
    await patch_one_one_locals_uuid_11_ool_many_ones_uuid_131(client)
    await patch_one_one_locals_uuid_11_ool_one_manys_uuid_141_142(client)
    await patch_one_one_locals_uuid_11_ool_many_manys_uuid_151_152(client)

    await post_oor_one_one_locals_uuid_211(client)
    await post_oor_one_one_remotes_uuid_221(client)
    await post_oor_many_ones_uuid_231(client)
    await post_oor_one_manys_uuid_241(client)
    await post_oor_one_manys_uuid_242(client)
    await post_oor_many_manys_uuid_251(client)
    await post_oor_many_manys_uuid_252(client)

    await patch_one_one_remotes_uuid_21_oor_one_one_locals_uuid_211(client)
    await patch_one_one_remotes_uuid_21_oor_one_one_remotes_uuid_221(client)
    await patch_one_one_remotes_uuid_21_oor_many_ones_uuid_231(client)
    await patch_one_one_remotes_uuid_21_oor_one_manys_uuid_241_242(client)
    await patch_one_one_remotes_uuid_21_oor_many_manys_uuid_251_252(client)

    await post_mo_one_one_locals_uuid_311(client)
    await post_mo_one_one_remotes_uuid_321(client)
    await post_mo_many_ones_uuid_331(client)
    await post_mo_one_manys_uuid_341(client)
    await post_mo_one_manys_uuid_342(client)
    await post_mo_many_manys_uuid_351(client)
    await post_mo_many_manys_uuid_352(client)

    await patch_many_ones_uuid_31_mo_one_one_locals_uuid_311(client)
    await patch_many_ones_uuid_31_mo_one_one_remotes_uuid_321(client)
    await patch_many_ones_uuid_31_mo_many_ones_uuid_331(client)
    await patch_many_ones_uuid_31_mo_one_manys_uuid_341_342(client)
    await patch_many_ones_uuid_31_mo_many_manys_uuid_351_352(client)

    await post_om_one_one_locals_uuid_411(client)
    await post_om_one_one_remotes_uuid_421(client)
    await post_om_many_ones_uuid_431(client)
    await post_om_one_manys_uuid_441(client)
    await post_om_one_manys_uuid_442(client)
    await post_om_many_manys_uuid_451(client)
    await post_om_many_manys_uuid_452(client)

    await patch_one_manys_uuid_41_om_one_one_locals_uuid_411(client)
    await patch_one_manys_uuid_41_om_one_one_remotes_uuid_421(client)
    await patch_one_manys_uuid_41_om_many_ones_uuid_431(client)
    await patch_one_manys_uuid_41_om_one_manys_uuid_441_442(client)
    await patch_one_manys_uuid_41_om_many_manys_uuid_451_452(client)

    await post_mm_one_one_locals_uuid_511(client)
    await post_mm_one_one_remotes_uuid_521(client)
    await post_mm_many_ones_uuid_531(client)
    await post_mm_one_manys_uuid_541(client)
    await post_mm_one_manys_uuid_542(client)
    await post_mm_many_manys_uuid_551(client)
    await post_mm_many_manys_uuid_552(client)

    await patch_many_manys_uuid_51_mm_one_one_locals_uuid_511(client)
    await patch_many_manys_uuid_51_mm_one_one_remotes_uuid_521(client)
    await patch_many_manys_uuid_51_mm_many_ones_uuid_531(client)
    await patch_many_manys_uuid_51_mm_one_manys_uuid_541_542(client)
    await patch_many_manys_uuid_51_mm_many_manys_uuid_551_552(client)
