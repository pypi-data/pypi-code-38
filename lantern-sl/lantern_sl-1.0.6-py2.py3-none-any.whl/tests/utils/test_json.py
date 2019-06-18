import copy
import json
import pytest
from lantern_sl.utils.json import json_float_to_decimal, json_decimal_to_float

from tests.utils.test_json_payload import (
    FLOATS_SIMPLE, DECIMALS_SIMPLE,
    FLOATS_LIST_1, DECIMALS_LIST_1,
    FLOATS_LIST_2, DECIMALS_LIST_2,
    FLOATS_LIST_3, DECIMALS_LIST_3,
    )


@pytest.mark.parametrize("float_obj, decimal_obj, expected", [
        (FLOATS_SIMPLE, DECIMALS_SIMPLE, True),
        (FLOATS_LIST_1, DECIMALS_LIST_1, True),
        (FLOATS_LIST_2, DECIMALS_LIST_2, True),
        (FLOATS_LIST_3, DECIMALS_LIST_3, True),
    ])
def test_json_float_to_decimal(float_obj, decimal_obj, expected):
    _tot_decimal = json_float_to_decimal(copy.deepcopy(float_obj))
    assert (decimal_obj == _tot_decimal) == expected, "Expected Conversion OK"



@pytest.mark.parametrize("decimal_obj, float_obj, expected", [
        (DECIMALS_SIMPLE, FLOATS_SIMPLE, True),
        (DECIMALS_LIST_1, FLOATS_LIST_1, True),
        (DECIMALS_LIST_2, FLOATS_LIST_2, True),
        (DECIMALS_LIST_3, FLOATS_LIST_3, True),
    ])
def test_json_decimal_to_float(decimal_obj, float_obj, expected):
    _tot_float = json_decimal_to_float(copy.deepcopy(decimal_obj))
    assert (float_obj == _tot_float) == expected, "Expected Conversion OK"