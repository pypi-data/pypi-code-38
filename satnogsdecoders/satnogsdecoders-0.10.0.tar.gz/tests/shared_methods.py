"""
some commonly used methods
"""

import json
import sys

PY2 = (sys.version_info < (3, 0))


def check_type(result):
    """
    Check return types of decoder
    """

    count = 0
    for value in result:
        count = count + 1
        if PY2:
            assert isinstance(result[value], (unicode, str, int, float))  # noqa: F821,E501 pylint: disable=E0602
        else:
            assert isinstance(result[value], (str, int, float))
    return count


def load_objects(decoder, dut, frame):
    """
    Decode frame and load result into JSON objects
    """

    result = decoder.get_fields(getattr(decoder, dut).from_bytes(frame))
    result = json.dumps(result)
    result = json.loads(result)
    return result
