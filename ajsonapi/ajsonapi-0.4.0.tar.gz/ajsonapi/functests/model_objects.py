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
"""Module model_objects provides uuids and json objects for testing."""

# pylint: disable=too-many-lines

JSON_CENTERS_1 = {
    'data': {
        'type': 'centers',
        'attributes': {
            'attr_int': 1,
            'attr_str': 'one',
        },
    },
}

UUID_1 = '01234567-89ab-cdef-0123-000000000001'

JSON_CENTERS_UUID_1 = {
    'data': {
        'type': 'centers',
        'id': UUID_1,
        'attributes': {
            'attr_int': 1,
            'attr_str': 'one',
        },
    },
}

UUID_2 = '01234567-89ab-cdef-0123-000000000002'

JSON_CENTERS_UUID_2 = {
    'data': {
        'type': 'centers',
        'id': UUID_2,
        'attributes': {
            'attr_int': 2,
            'attr_str': 'two',
        },
    },
}

UUID_3 = '01234567-89ab-cdef-0123-000000000003'

JSON_CENTERS_UUID_3 = {
    'data': {
        'type': 'centers',
        'id': UUID_3,
        'attributes': {
            'attr_int': 3,
            'attr_str': 'three',
        },
    },
}

UUID_11 = '01234567-89ab-cdef-0123-000000000011'

JSON_ONE_ONE_LOCALS_UUID_11 = {
    'data': {
        'type': 'one_one_locals',
        'id': UUID_11,
        'attributes': {
            'attr_int': 211,
            'attr_str': '11L-one',
        },
    },
}

JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11 = {
    'data': {
        'type': 'one_one_locals',
        'id': UUID_11,
    }
}

UUID_12 = '01234567-89ab-cdef-0123-000000000012'

JSON_ONE_ONE_LOCALS_UUID_12 = {
    'data': {
        'type': 'one_one_locals',
        'id': UUID_12,
        'attributes': {
            'attr_int': 212,
            'attr_str': '11L-two',
        },
    },
}

JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_12 = {
    'data': {
        'type': 'one_one_locals',
        'id': UUID_12,
    }
}

UUID_21 = '01234567-89ab-cdef-0123-000000000021'

JSON_ONE_ONE_REMOTES_UUID_21 = {
    'data': {
        'type': 'one_one_remotes',
        'id': UUID_21,
        'attributes': {
            'attr_int': 121,
            'attr_str': '11R-one',
        },
    },
}

JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21 = {
    'data': {
        'type': 'one_one_remotes',
        'id': UUID_21,
    }
}

UUID_22 = '01234567-89ab-cdef-0123-000000000022'

JSON_ONE_ONE_REMOTES_UUID_22 = {
    'data': {
        'type': 'one_one_remotes',
        'id': UUID_22,
        'attributes': {
            'attr_int': 122,
            'attr_str': '11R-two',
        },
    },
}

JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_22 = {
    'data': {
        'type': 'one_one_remotes',
        'id': UUID_22,
    }
}

UUID_31 = '01234567-89ab-cdef-0123-000000000031'

JSON_MANY_ONES_UUID_31 = {
    'data': {
        'type': 'many_ones',
        'id': UUID_31,
        'attributes': {
            'attr_int': 811,
            'attr_str': 'M1-one',
        },
    },
}

JSON_IDENTIFIER_MANY_ONES_UUID_31 = {
    'data': {
        'type': 'many_ones',
        'id': UUID_31,
    }
}

UUID_32 = '01234567-89ab-cdef-0123-000000000032'

JSON_MANY_ONES_UUID_32 = {
    'data': {
        'type': 'many_ones',
        'id': UUID_32,
        'attributes': {
            'attr_int': 812,
            'attr_str': 'M1-two',
        },
    },
}

JSON_IDENTIFIER_MANY_ONES_UUID_32 = {
    'data': {
        'type': 'many_ones',
        'id': UUID_32,
    }
}

UUID_41 = '01234567-89ab-cdef-0123-000000000041'

JSON_ONE_MANYS_UUID_41 = {
    'data': {
        'type': 'one_manys',
        'id': UUID_41,
        'attributes': {
            'attr_int': 181,
            'attr_str': '1M-one',
        },
    },
}

JSON_IDENTIFIERS_ONE_MANYS_UUID_41 = {
    'data': [
        {
            'type': 'one_manys',
            'id': UUID_41,
        },
    ]
}

UUID_42 = '01234567-89ab-cdef-0123-000000000042'

JSON_ONE_MANYS_UUID_42 = {
    'data': {
        'type': 'one_manys',
        'id': UUID_42,
        'attributes': {
            'attr_int': 182,
            'attr_str': '1M-two',
        },
    },
}

JSON_IDENTIFIERS_ONE_MANYS_UUID_42 = {
    'data': [
        {
            'type': 'one_manys',
            'id': UUID_42,
        },
    ]
}

JSON_IDENTIFIERS_ONE_MANYS_UUID_41_42 = {
    'data': [
        {
            'type': 'one_manys',
            'id': UUID_41,
        },
        {
            'type': 'one_manys',
            'id': UUID_42,
        },
    ]
}

UUID_43 = '01234567-89ab-cdef-0123-000000000043'

JSON_ONE_MANYS_UUID_43 = {
    'data': {
        'type': 'one_manys',
        'id': UUID_43,
        'attributes': {
            'attr_int': 183,
            'attr_str': '1M-three',
        },
    },
}

JSON_IDENTIFIERS_ONE_MANYS_UUID_43 = {
    'data': [
        {
            'type': 'one_manys',
            'id': UUID_43,
        },
    ]
}

JSON_IDENTIFIERS_ONE_MANYS_UUID_42_43 = {
    'data': [
        {
            'type': 'one_manys',
            'id': UUID_42,
        },
        {
            'type': 'one_manys',
            'id': UUID_43,
        },
    ]
}

JSON_IDENTIFIERS_ONE_MANYS_UUID_41_42_43 = {
    'data': [
        {
            'type': 'one_manys',
            'id': UUID_41,
        },
        {
            'type': 'one_manys',
            'id': UUID_42,
        },
        {
            'type': 'one_manys',
            'id': UUID_43,
        },
    ]
}

JSON_IDENTIFIERS_ONE_MANYS_88888888_999999999 = {
    'data': [
        {
            'type': 'one_manys',
            'id': '88888888',
        },
        {
            'type': 'one_manys',
            'id': '999999999',
        },
    ]
}

UUID_51 = '01234567-89ab-cdef-0123-000000000051'

JSON_MANY_MANYS_UUID_51 = {
    'data': {
        'type': 'many_manys',
        'id': UUID_51,
        'attributes': {
            'attr_int': 881,
            'attr_str': 'MM-one',
        },
    },
}

JSON_IDENTIFIERS_MANY_MANYS_UUID_51 = {
    'data': [
        {
            'type': 'many_manys',
            'id': UUID_51,
        },
    ]
}

UUID_52 = '01234567-89ab-cdef-0123-000000000052'

JSON_MANY_MANYS_UUID_52 = {
    'data': {
        'type': 'many_manys',
        'id': UUID_52,
        'attributes': {
            'attr_int': 882,
            'attr_str': 'MM-two',
        },
    },
}

JSON_IDENTIFIERS_MANY_MANYS_UUID_52 = {
    'data': [
        {
            'type': 'many_manys',
            'id': UUID_52,
        },
    ]
}

JSON_IDENTIFIERS_MANY_MANYS_UUID_51_52 = {
    'data': [
        {
            'type': 'many_manys',
            'id': UUID_51,
        },
        {
            'type': 'many_manys',
            'id': UUID_52,
        },
    ]
}

UUID_53 = '01234567-89ab-cdef-0123-000000000053'

JSON_MANY_MANYS_UUID_53 = {
    'data': {
        'type': 'many_manys',
        'id': UUID_53,
        'attributes': {
            'attr_int': 883,
            'attr_str': 'MM-three',
        },
    },
}

JSON_IDENTIFIERS_MANY_MANYS_UUID_53 = {
    'data': [
        {
            'type': 'many_manys',
            'id': UUID_53,
        },
    ]
}

JSON_IDENTIFIERS_MANY_MANYS_UUID_52_53 = {
    'data': [
        {
            'type': 'many_manys',
            'id': UUID_52,
        },
        {
            'type': 'many_manys',
            'id': UUID_53,
        },
    ]
}

JSON_IDENTIFIERS_MANY_MANYS_UUID_51_52_53 = {
    'data': [
        {
            'type': 'many_manys',
            'id': UUID_51,
        },
        {
            'type': 'many_manys',
            'id': UUID_52,
        },
        {
            'type': 'many_manys',
            'id': UUID_53,
        },
    ]
}

JSON_IDENTIFIERS_MANY_MANYS_88888888_999999999 = {
    'data': [
        {
            'type': 'many_manys',
            'id': '88888888',
        },
        {
            'type': 'many_manys',
            'id': '999999999',
        },
    ]
}

JSON_IDENTIFIER_NONE = {
    'data': None,
}

JSON_IDENTIFIERS_NONE = {
    'data': [],
}

UUID_111 = '01234567-89ab-cdef-0123-000000000111'

JSON_OOL_ONE_ONE_LOCALS_UUID_111 = {
    'data': {
        'type': 'ool_one_one_locals',
        'id': UUID_111,
        'attributes': {
            'attr_int': 21211,
            'attr_str': '11L-11L-one',
        },
    },
}

JSON_IDENTIFIER_OOL_ONE_ONE_LOCALS_UUID_111 = {
    'data': {
        'type': 'ool_one_one_locals',
        'id': UUID_111,
    }
}

UUID_121 = '01234567-89ab-cdef-0123-000000000121'

JSON_OOL_ONE_ONE_REMOTES_UUID_121 = {
    'data': {
        'type': 'ool_one_one_remotes',
        'id': UUID_121,
        'attributes': {
            'attr_int': 21121,
            'attr_str': '11L-11R-one',
        },
    },
}

JSON_IDENTIFIER_OOL_ONE_ONE_REMOTES_UUID_121 = {
    'data': {
        'type': 'ool_one_one_remotes',
        'id': UUID_121,
    }
}

UUID_131 = '01234567-89ab-cdef-0123-000000000131'

JSON_OOL_MANY_ONES_UUID_131 = {
    'data': {
        'type': 'ool_many_ones',
        'id': UUID_131,
        'attributes': {
            'attr_int': 21811,
            'attr_str': '11L-M1-one',
        },
    },
}

JSON_IDENTIFIER_OOL_MANY_ONES_UUID_131 = {
    'data': {
        'type': 'ool_many_ones',
        'id': UUID_131,
    }
}

UUID_141 = '01234567-89ab-cdef-0123-000000000141'

JSON_OOL_ONE_MANYS_UUID_141 = {
    'data': {
        'type': 'ool_one_manys',
        'id': UUID_141,
        'attributes': {
            'attr_int': 21181,
            'attr_str': '11L-1M-one',
        },
    },
}

JSON_IDENTIFIERS_OOL_ONE_MANYS_UUID_141 = {
    'data': [
        {
            'type': 'ool_one_manys',
            'id': UUID_141,
        },
    ]
}

UUID_142 = '01234567-89ab-cdef-0123-000000000142'

JSON_OOL_ONE_MANYS_UUID_142 = {
    'data': {
        'type': 'ool_one_manys',
        'id': UUID_142,
        'attributes': {
            'attr_int': 21182,
            'attr_str': '11L-1M-two',
        },
    },
}

JSON_IDENTIFIERS_OOL_ONE_MANYS_UUID_142 = {
    'data': [
        {
            'type': 'ool_one_manys',
            'id': UUID_142,
        },
    ]
}

JSON_IDENTIFIERS_OOL_ONE_MANYS_UUID_141_142 = {
    'data': [
        {
            'type': 'ool_one_manys',
            'id': UUID_141,
        },
        {
            'type': 'ool_one_manys',
            'id': UUID_142,
        },
    ]
}

UUID_151 = '01234567-89ab-cdef-0123-000000000151'

JSON_OOL_MANY_MANYS_UUID_151 = {
    'data': {
        'type': 'ool_many_manys',
        'id': UUID_151,
        'attributes': {
            'attr_int': 21881,
            'attr_str': '11L-MM-one',
        },
    },
}

JSON_IDENTIFIERS_OOL_MANY_MANYS_UUID_151 = {
    'data': [
        {
            'type': 'ool_many_manys',
            'id': UUID_151,
        },
    ]
}

UUID_152 = '01234567-89ab-cdef-0123-000000000152'

JSON_OOL_MANY_MANYS_UUID_152 = {
    'data': {
        'type': 'ool_many_manys',
        'id': UUID_152,
        'attributes': {
            'attr_int': 21882,
            'attr_str': '11L-MM-two',
        },
    },
}

JSON_IDENTIFIERS_OOL_MANY_MANYS_UUID_152 = {
    'data': [
        {
            'type': 'ool_many_manys',
            'id': UUID_152,
        },
    ]
}

JSON_IDENTIFIERS_OOL_MANY_MANYS_UUID_151_152 = {
    'data': [
        {
            'type': 'ool_many_manys',
            'id': UUID_151,
        },
        {
            'type': 'ool_many_manys',
            'id': UUID_152,
        },
    ]
}

UUID_211 = '01234567-89ab-cdef-0123-000000000211'

JSON_OOR_ONE_ONE_LOCALS_UUID_211 = {
    'data': {
        'type': 'oor_one_one_locals',
        'id': UUID_211,
        'attributes': {
            'attr_int': 12211,
            'attr_str': '11R-11L-one',
        },
    },
}

JSON_IDENTIFIER_OOR_ONE_ONE_LOCALS_UUID_211 = {
    'data': {
        'type': 'oor_one_one_locals',
        'id': UUID_211,
    }
}

UUID_221 = '01234567-89ab-cdef-0123-000000000221'

JSON_OOR_ONE_ONE_REMOTES_UUID_221 = {
    'data': {
        'type': 'oor_one_one_remotes',
        'id': UUID_221,
        'attributes': {
            'attr_int': 12121,
            'attr_str': '11R-11R-one',
        },
    },
}

JSON_IDENTIFIER_OOR_ONE_ONE_REMOTES_UUID_221 = {
    'data': {
        'type': 'oor_one_one_remotes',
        'id': UUID_221,
    }
}

UUID_231 = '01234567-89ab-cdef-0123-000000000231'

JSON_OOR_MANY_ONES_UUID_231 = {
    'data': {
        'type': 'oor_many_ones',
        'id': UUID_231,
        'attributes': {
            'attr_int': 12811,
            'attr_str': '11R-M1-one',
        },
    },
}

JSON_IDENTIFIER_OOR_MANY_ONES_UUID_231 = {
    'data': {
        'type': 'oor_many_ones',
        'id': UUID_231,
    }
}

UUID_241 = '01234567-89ab-cdef-0123-000000000241'

JSON_OOR_ONE_MANYS_UUID_241 = {
    'data': {
        'type': 'oor_one_manys',
        'id': UUID_241,
        'attributes': {
            'attr_int': 12181,
            'attr_str': '11R-1M-one',
        },
    },
}

JSON_IDENTIFIERS_OOR_ONE_MANYS_UUID_241 = {
    'data': [
        {
            'type': 'oor_one_manys',
            'id': UUID_241,
        },
    ]
}

UUID_242 = '01234567-89ab-cdef-0123-000000000242'

JSON_OOR_ONE_MANYS_UUID_242 = {
    'data': {
        'type': 'oor_one_manys',
        'id': UUID_242,
        'attributes': {
            'attr_int': 12182,
            'attr_str': '11R-1M-two',
        },
    },
}

JSON_IDENTIFIERS_OOR_ONE_MANYS_UUID_242 = {
    'data': [
        {
            'type': 'oor_one_manys',
            'id': UUID_242,
        },
    ]
}

JSON_IDENTIFIERS_OOR_ONE_MANYS_UUID_241_242 = {
    'data': [
        {
            'type': 'oor_one_manys',
            'id': UUID_241,
        },
        {
            'type': 'oor_one_manys',
            'id': UUID_242,
        },
    ]
}

UUID_251 = '01234567-89ab-cdef-0123-000000000251'

JSON_OOR_MANY_MANYS_UUID_251 = {
    'data': {
        'type': 'oor_many_manys',
        'id': UUID_251,
        'attributes': {
            'attr_int': 12881,
            'attr_str': '11R-MM-one',
        },
    },
}

JSON_IDENTIFIERS_OOR_MANY_MANYS_UUID_251 = {
    'data': [
        {
            'type': 'oor_many_manys',
            'id': UUID_251,
        },
    ]
}

UUID_252 = '01234567-89ab-cdef-0123-000000000252'

JSON_OOR_MANY_MANYS_UUID_252 = {
    'data': {
        'type': 'oor_many_manys',
        'id': UUID_252,
        'attributes': {
            'attr_int': 12882,
            'attr_str': '11R-MM-two',
        },
    },
}

JSON_IDENTIFIERS_OOR_MANY_MANYS_UUID_252 = {
    'data': [
        {
            'type': 'oor_many_manys',
            'id': UUID_252,
        },
    ]
}

JSON_IDENTIFIERS_OOR_MANY_MANYS_UUID_251_252 = {
    'data': [
        {
            'type': 'oor_many_manys',
            'id': UUID_251,
        },
        {
            'type': 'oor_many_manys',
            'id': UUID_252,
        },
    ]
}

UUID_311 = '01234567-89ab-cdef-0123-000000000311'

JSON_MO_ONE_ONE_LOCALS_UUID_311 = {
    'data': {
        'type': 'mo_one_one_locals',
        'id': UUID_311,
        'attributes': {
            'attr_int': 81211,
            'attr_str': 'M1-11L-one',
        },
    },
}

JSON_IDENTIFIER_MO_ONE_ONE_LOCALS_UUID_311 = {
    'data': {
        'type': 'mo_one_one_locals',
        'id': UUID_311,
    }
}

UUID_321 = '01234567-89ab-cdef-0123-000000000321'

JSON_MO_ONE_ONE_REMOTES_UUID_321 = {
    'data': {
        'type': 'mo_one_one_remotes',
        'id': UUID_321,
        'attributes': {
            'attr_int': 81121,
            'attr_str': 'M1-11R-one',
        },
    },
}

JSON_IDENTIFIER_MO_ONE_ONE_REMOTES_UUID_321 = {
    'data': {
        'type': 'mo_one_one_remotes',
        'id': UUID_321,
    }
}

UUID_331 = '01234567-89ab-cdef-0123-000000000331'

JSON_MO_MANY_ONES_UUID_331 = {
    'data': {
        'type': 'mo_many_ones',
        'id': UUID_331,
        'attributes': {
            'attr_int': 81811,
            'attr_str': 'M1-M1-one',
        },
    },
}

JSON_IDENTIFIER_MO_MANY_ONES_UUID_331 = {
    'data': {
        'type': 'mo_many_ones',
        'id': UUID_331,
    }
}

UUID_341 = '01234567-89ab-cdef-0123-000000000341'

JSON_MO_ONE_MANYS_UUID_341 = {
    'data': {
        'type': 'mo_one_manys',
        'id': UUID_341,
        'attributes': {
            'attr_int': 81181,
            'attr_str': 'M1-1M-one',
        },
    },
}

JSON_IDENTIFIERS_MO_ONE_MANYS_UUID_341 = {
    'data': [
        {
            'type': 'mo_one_manys',
            'id': UUID_341,
        },
    ]
}

UUID_342 = '01234567-89ab-cdef-0123-000000000342'

JSON_MO_ONE_MANYS_UUID_342 = {
    'data': {
        'type': 'mo_one_manys',
        'id': UUID_342,
        'attributes': {
            'attr_int': 81182,
            'attr_str': 'M1-1M-two',
        },
    },
}

JSON_IDENTIFIERS_MO_ONE_MANYS_UUID_342 = {
    'data': [
        {
            'type': 'mo_one_manys',
            'id': UUID_342,
        },
    ]
}

JSON_IDENTIFIERS_MO_ONE_MANYS_UUID_341_342 = {
    'data': [
        {
            'type': 'mo_one_manys',
            'id': UUID_341,
        },
        {
            'type': 'mo_one_manys',
            'id': UUID_342,
        },
    ]
}

UUID_351 = '01234567-89ab-cdef-0123-000000000351'

JSON_MO_MANY_MANYS_UUID_351 = {
    'data': {
        'type': 'mo_many_manys',
        'id': UUID_351,
        'attributes': {
            'attr_int': 81881,
            'attr_str': 'M1-MM-one',
        },
    },
}

JSON_IDENTIFIERS_MO_MANY_MANYS_UUID_351 = {
    'data': [
        {
            'type': 'mo_many_manys',
            'id': UUID_351,
        },
    ]
}

UUID_352 = '01234567-89ab-cdef-0123-000000000352'

JSON_MO_MANY_MANYS_UUID_352 = {
    'data': {
        'type': 'mo_many_manys',
        'id': UUID_352,
        'attributes': {
            'attr_int': 81882,
            'attr_str': 'M1-MM-two',
        },
    },
}

JSON_IDENTIFIERS_MO_MANY_MANYS_UUID_352 = {
    'data': [
        {
            'type': 'mo_many_manys',
            'id': UUID_352,
        },
    ]
}

JSON_IDENTIFIERS_MO_MANY_MANYS_UUID_351_352 = {
    'data': [
        {
            'type': 'mo_many_manys',
            'id': UUID_351,
        },
        {
            'type': 'mo_many_manys',
            'id': UUID_352,
        },
    ]
}

UUID_411 = '01234567-89ab-cdef-0123-000000000411'

JSON_OM_ONE_ONE_LOCALS_UUID_411 = {
    'data': {
        'type': 'om_one_one_locals',
        'id': UUID_411,
        'attributes': {
            'attr_int': 18211,
            'attr_str': '1M-11L-one',
        },
    },
}

JSON_IDENTIFIER_OM_ONE_ONE_LOCALS_UUID_411 = {
    'data': {
        'type': 'om_one_one_locals',
        'id': UUID_411,
    }
}

UUID_421 = '01234567-89ab-cdef-0123-000000000421'

JSON_OM_ONE_ONE_REMOTES_UUID_421 = {
    'data': {
        'type': 'om_one_one_remotes',
        'id': UUID_421,
        'attributes': {
            'attr_int': 18121,
            'attr_str': '1M-11R-one',
        },
    },
}

JSON_IDENTIFIER_OM_ONE_ONE_REMOTES_UUID_421 = {
    'data': {
        'type': 'om_one_one_remotes',
        'id': UUID_421,
    }
}

UUID_431 = '01234567-89ab-cdef-0123-000000000431'

JSON_OM_MANY_ONES_UUID_431 = {
    'data': {
        'type': 'om_many_ones',
        'id': UUID_431,
        'attributes': {
            'attr_int': 18811,
            'attr_str': '1M-M1-one',
        },
    },
}

JSON_IDENTIFIER_OM_MANY_ONES_UUID_431 = {
    'data': {
        'type': 'om_many_ones',
        'id': UUID_431,
    }
}

UUID_441 = '01234567-89ab-cdef-0123-000000000441'

JSON_OM_ONE_MANYS_UUID_441 = {
    'data': {
        'type': 'om_one_manys',
        'id': UUID_441,
        'attributes': {
            'attr_int': 18181,
            'attr_str': '1M-1M-one',
        },
    },
}

JSON_IDENTIFIERS_OM_ONE_MANYS_UUID_441 = {
    'data': [
        {
            'type': 'om_one_manys',
            'id': UUID_441,
        },
    ]
}

UUID_442 = '01234567-89ab-cdef-0123-000000000442'

JSON_OM_ONE_MANYS_UUID_442 = {
    'data': {
        'type': 'om_one_manys',
        'id': UUID_442,
        'attributes': {
            'attr_int': 18182,
            'attr_str': '1M-1M-two',
        },
    },
}

JSON_IDENTIFIERS_OM_ONE_MANYS_UUID_442 = {
    'data': [
        {
            'type': 'om_one_manys',
            'id': UUID_442,
        },
    ]
}

JSON_IDENTIFIERS_OM_ONE_MANYS_UUID_441_442 = {
    'data': [
        {
            'type': 'om_one_manys',
            'id': UUID_441,
        },
        {
            'type': 'om_one_manys',
            'id': UUID_442,
        },
    ]
}

UUID_451 = '01234567-89ab-cdef-0123-000000000451'

JSON_OM_MANY_MANYS_UUID_451 = {
    'data': {
        'type': 'om_many_manys',
        'id': UUID_451,
        'attributes': {
            'attr_int': 18881,
            'attr_str': '1M-MM-one',
        },
    },
}

JSON_IDENTIFIERS_OM_MANY_MANYS_UUID_451 = {
    'data': [
        {
            'type': 'om_many_manys',
            'id': UUID_451,
        },
    ]
}

UUID_452 = '01234567-89ab-cdef-0123-000000000452'

JSON_OM_MANY_MANYS_UUID_452 = {
    'data': {
        'type': 'om_many_manys',
        'id': UUID_452,
        'attributes': {
            'attr_int': 18882,
            'attr_str': '1M-MM-two',
        },
    },
}

JSON_IDENTIFIERS_OM_MANY_MANYS_UUID_452 = {
    'data': [
        {
            'type': 'om_many_manys',
            'id': UUID_452,
        },
    ]
}

JSON_IDENTIFIERS_OM_MANY_MANYS_UUID_451_452 = {
    'data': [
        {
            'type': 'om_many_manys',
            'id': UUID_451,
        },
        {
            'type': 'om_many_manys',
            'id': UUID_452,
        },
    ]
}

UUID_511 = '01234567-89ab-cdef-0123-000000000511'

JSON_MM_ONE_ONE_LOCALS_UUID_511 = {
    'data': {
        'type': 'mm_one_one_locals',
        'id': UUID_511,
        'attributes': {
            'attr_int': 88211,
            'attr_str': 'MM-11L-one',
        },
    },
}

JSON_IDENTIFIER_MM_ONE_ONE_LOCALS_UUID_511 = {
    'data': {
        'type': 'mm_one_one_locals',
        'id': UUID_511,
    }
}

UUID_521 = '01234567-89ab-cdef-0123-000000000521'

JSON_MM_ONE_ONE_REMOTES_UUID_521 = {
    'data': {
        'type': 'mm_one_one_remotes',
        'id': UUID_521,
        'attributes': {
            'attr_int': 88121,
            'attr_str': 'MM-11R-one',
        },
    },
}

JSON_IDENTIFIER_MM_ONE_ONE_REMOTES_UUID_521 = {
    'data': {
        'type': 'mm_one_one_remotes',
        'id': UUID_521,
    }
}

UUID_531 = '01234567-89ab-cdef-0123-000000000531'

JSON_MM_MANY_ONES_UUID_531 = {
    'data': {
        'type': 'mm_many_ones',
        'id': UUID_531,
        'attributes': {
            'attr_int': 88811,
            'attr_str': 'MM-M1-one',
        },
    },
}

JSON_IDENTIFIER_MM_MANY_ONES_UUID_531 = {
    'data': {
        'type': 'mm_many_ones',
        'id': UUID_531,
    }
}

UUID_541 = '01234567-89ab-cdef-0123-000000000541'

JSON_MM_ONE_MANYS_UUID_541 = {
    'data': {
        'type': 'mm_one_manys',
        'id': UUID_541,
        'attributes': {
            'attr_int': 88181,
            'attr_str': 'MM-1M-one',
        },
    },
}

JSON_IDENTIFIERS_MM_ONE_MANYS_UUID_541 = {
    'data': [
        {
            'type': 'mm_one_manys',
            'id': UUID_541,
        },
    ]
}

UUID_542 = '01234567-89ab-cdef-0123-000000000542'

JSON_MM_ONE_MANYS_UUID_542 = {
    'data': {
        'type': 'mm_one_manys',
        'id': UUID_542,
        'attributes': {
            'attr_int': 88182,
            'attr_str': 'MM-1M-two',
        },
    },
}

JSON_IDENTIFIERS_MM_ONE_MANYS_UUID_542 = {
    'data': [
        {
            'type': 'mm_one_manys',
            'id': UUID_542,
        },
    ]
}

JSON_IDENTIFIERS_MM_ONE_MANYS_UUID_541_542 = {
    'data': [
        {
            'type': 'mm_one_manys',
            'id': UUID_541,
        },
        {
            'type': 'mm_one_manys',
            'id': UUID_542,
        },
    ]
}

UUID_551 = '01234567-89ab-cdef-0123-000000000551'

JSON_MM_MANY_MANYS_UUID_551 = {
    'data': {
        'type': 'mm_many_manys',
        'id': UUID_551,
        'attributes': {
            'attr_int': 88881,
            'attr_str': 'MM-MM-one',
        },
    },
}

JSON_IDENTIFIERS_MM_MANY_MANYS_UUID_551 = {
    'data': [
        {
            'type': 'mm_many_manys',
            'id': UUID_551,
        },
    ]
}

UUID_552 = '01234567-89ab-cdef-0123-000000000552'

JSON_MM_MANY_MANYS_UUID_552 = {
    'data': {
        'type': 'mm_many_manys',
        'id': UUID_552,
        'attributes': {
            'attr_int': 88882,
            'attr_str': 'MM-MM-two',
        },
    },
}

JSON_IDENTIFIERS_MM_MANY_MANYS_UUID_552 = {
    'data': [
        {
            'type': 'mm_many_manys',
            'id': UUID_552,
        },
    ]
}

JSON_IDENTIFIERS_MM_MANY_MANYS_UUID_551_552 = {
    'data': [
        {
            'type': 'mm_many_manys',
            'id': UUID_551,
        },
        {
            'type': 'mm_many_manys',
            'id': UUID_552,
        },
    ]
}

JSON_CENTERS_1_RELATIONSHIPS = {
    'data': {
        'type': 'centers',
        'attributes': {
            'attr_int': 1,
            'attr_str': 'one',
        },
        'relationships': {
            'one_one_local': JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11,
            'one_one_remote': JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21,
            'many_one': JSON_IDENTIFIER_MANY_ONES_UUID_31,
            'one_manys': JSON_IDENTIFIERS_ONE_MANYS_UUID_41_42,
            'many_manys': JSON_IDENTIFIERS_MANY_MANYS_UUID_51_52,
        },
    },
}

JSON_CENTERS_UUID_1_DATA_MISSING_RELATIONSHIP_TYPES = {
    'data': {
        'type': 'centers',
        'id': UUID_1,
        'attributes': {
            'attr_int': 1,
            'attr_str': 'one',
        },
        'relationships': {
            'one_one_local': {
                'data': {
                    'id': UUID_11,
                }
            },
            'one_one_remote': {
                'data': {
                    'id': UUID_21,
                }
            },
            'many_one': {
                'data': {
                    'id': UUID_31,
                }
            },
            'one_manys': {
                'data': [{
                    'id': UUID_41,
                }, {
                    'id': UUID_42,
                }]
            },
            'many_manys': {
                'data': [{
                    'id': UUID_51,
                }, {
                    'id': UUID_52,
                }]
            },
        },
    }
}

JSON_CENTERS_UUID_1_DATA_MISSING_RELATIONSHIP_IDS = {
    'data': {
        'type': 'centers',
        'id': UUID_1,
        'attributes': {
            'attr_int': 1,
            'attr_str': 'one',
        },
        'relationships': {
            'one_one_local': {
                'data': {
                    'type': 'one_one_locals',
                }
            },
            'one_one_remote': {
                'data': {
                    'type': 'one_one_remotes',
                }
            },
            'many_one': {
                'data': {
                    'type': 'many_ones',
                }
            },
            'one_manys': {
                'data': [{
                    'type': 'one_manys',
                }, {
                    'type': 'one_manys',
                }]
            },
            'many_manys': {
                'data': [{
                    'type': 'many_manys',
                }, {
                    'type': 'many_manys',
                }]
            },
        },
    }
}

JSON_CENTERS_UUID_1_DATA_INVALID_RELATIONSHIP_TYPES = {
    'data': {
        'type': 'centers',
        'id': UUID_1,
        'attributes': {
            'attr_int': 1,
            'attr_str': 'one',
        },
        'relationships': {
            'one_one_local': {
                'data': {
                    'type': 'xxxxxxxxs',
                    'id': UUID_11,
                }
            },
            'one_one_remote': {
                'data': {
                    'type': 'xxxxxxxxs',
                    'id': UUID_21,
                }
            },
            'many_one': {
                'data': {
                    'type': 'xxxxxxxxs',
                    'id': UUID_31,
                }
            },
            'one_manys': {
                'data': [{
                    'type': 'xxxxxxxxs',
                    'id': UUID_41,
                }, {
                    'type': 'xxxxxxxxs',
                    'id': UUID_42,
                }]
            },
            'many_manys': {
                'data': [{
                    'type': 'xxxxxxxxs',
                    'id': UUID_51,
                }, {
                    'type': 'xxxxxxxxs',
                    'id': UUID_52,
                }]
            },
        },
    }
}

JSON_CENTERS_UUID_1_DATA_MALFORMED_RELATIONSHIP_IDS = {
    'data': {
        'type': 'centers',
        'id': UUID_1,
        'attributes': {
            'attr_int': 1,
            'attr_str': 'one',
        },
        'relationships': {
            'one_one_local': {
                'data': {
                    'type': 'one_one_locals',
                    'id': '8888-8888',
                }
            },
            'one_one_remote': {
                'data': {
                    'type': 'one_one_remotes',
                    'id': '8888-8888',
                }
            },
            'many_one': {
                'data': {
                    'type': 'many_ones',
                    'id': '8888-8888',
                }
            },
            'one_manys': {
                'data': [{
                    'type': 'one_manys',
                    'id': '8888-8888',
                }, {
                    'type': 'one_manys',
                    'id': '8888-8888',
                }]
            },
            'many_manys': {
                'data': [{
                    'type': 'many_manys',
                    'id': '8888-8888',
                }, {
                    'type': 'many_manys',
                    'id': '8888-8888',
                }]
            },
        },
    }
}

JSON_CENTERS_UUID_1_RELATIONSHIPS = {
    'data': {
        'type': 'centers',
        'id': UUID_1,
        'attributes': {
            'attr_int': 1,
            'attr_str': 'one',
        },
        'relationships': {
            'one_one_local': JSON_IDENTIFIER_ONE_ONE_LOCALS_UUID_11,
            'one_one_remote': JSON_IDENTIFIER_ONE_ONE_REMOTES_UUID_21,
            'many_one': JSON_IDENTIFIER_MANY_ONES_UUID_31,
            'one_manys': JSON_IDENTIFIERS_ONE_MANYS_UUID_41_42,
            'many_manys': JSON_IDENTIFIERS_MANY_MANYS_UUID_51_52,
        },
    },
}
