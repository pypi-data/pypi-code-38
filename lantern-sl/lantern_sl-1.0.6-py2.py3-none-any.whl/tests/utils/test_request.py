import copy
import json
import pytest
from lantern_sl.utils.request import http_response, http_error

from tests.utils.test_request_payload import (
    RESPONSE_DATA_ORIGINAL_DICT, RESPONSE_DATA_RESULT_FILTER_SYSTEM_COLS, 
    RESPONSE_DATA_RESULT_DECIMAL_TO_FLOAT, RESPONSE_DATA_RESULT_FILTER_SYSTEM_TO_FLOAT
    )


@pytest.mark.parametrize("cleanup_system_cols, convert_json_decimal_to_float, response, expected", [
        (True, False, RESPONSE_DATA_ORIGINAL_DICT, RESPONSE_DATA_RESULT_FILTER_SYSTEM_COLS),
        (False, True, RESPONSE_DATA_ORIGINAL_DICT, RESPONSE_DATA_RESULT_DECIMAL_TO_FLOAT),
        (True, True, RESPONSE_DATA_ORIGINAL_DICT, RESPONSE_DATA_RESULT_FILTER_SYSTEM_TO_FLOAT),
    ])
def test_http_response(cleanup_system_cols, convert_json_decimal_to_float, response, expected):
    _res = http_response(data=copy.deepcopy(response), cleanup_system_cols=cleanup_system_cols, convert_json_decimal_to_float=convert_json_decimal_to_float)
    assert "status" in _res, "status column in response"
    assert "data" in _res, "data column in response"
    assert _res["status"] == "OK", "Status is OK"
    assert _res["data"] == expected, "data expected is OK"



@pytest.mark.parametrize("message, detail, e", [
        ("Error", "detail", None),
        ("Error", "detail", Exception("My Custom Error")),
    ])
def test_http_error(message, detail, e):
    try:
        http_error(message=message, detail=detail, e=e)
        assert False, "It should fail"
    except Exception as ex:
        pass
        #print(e)
        #assert "status" in ex, "status column in response"
        #assert "message" in ex, "message column in response"
        #assert "detail" in ex, "detail column in response"
        #if e:
        #    assert "raw" in ex, "exception detail"