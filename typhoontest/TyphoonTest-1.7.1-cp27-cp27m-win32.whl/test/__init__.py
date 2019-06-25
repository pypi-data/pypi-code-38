from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from typhoon.utils import NoDuplicatesDict
from typhoon.license_typhoontest.manager import lic_check
from pytest import fixture, mark
import pytest as _pytest


def parameter(values=None, table=None):
    if table is not None:
        params = _parse_table(table)
    elif values is not None:
        params = values
    else:
        raise ValueError("Neither value or table specified for parameter!")

    @fixture(scope="session", params=params)
    def parameter_fixture(request):
        return request.param
    return parameter_fixture


# Check for license everytime typhoon.test is imported
lic_check()


def check_if_internal_capture(signal):
    if isinstance(signal, str):
        if _capture is None:
            raise ValueError("Signal given as a string but there is no past captured data available yet.")
        else:
            signal = _capture[signal]
    return signal

_capture = None
marks = NoDuplicatesDict()


class wont_raise(object):
    """Used as a context manager where we don't expect any exception do be raised.
    Pytest still does not provide this out-of-the-box because of disagreements on naming.
    See: https://github.com/pytest-dev/pytest/issues/1830
    """
    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *excinfo):
        pass


def assert_td_list_approx(_list, list_ref, tol):
    if len(_list) != len(list_ref):
        raise AssertionError("Compared lists do not have same length.")
    for val, ref in zip(_list, list_ref):
        if not ref-tol <= val <= ref+tol:
            raise AssertionError("Value {} is not equal to {} within tolerance {}.".format(val, ref, tol))

def process(item):
    # Sanitize
    item = item.strip().replace(" ","_")
    try:
        item = float(item)
    except ValueError:
        pass
    return item


def _parse_table(table):
    lines = table.splitlines()
    if len(lines) < 2:
        raise Exception("Table should have at least two lines, header and value.")

    header_items = None

    param_list = []

    for line in lines:
        items = [process(item) for item in line.split("|")]
        if items == [""]:
            continue
        if not header_items:
            header_items = items
        else:
            assert len(items) == len(header_items), "Table row ({}) has more/less elements than table header ({}).".format(items, header_items)
            # Contains one parameter row in dictionary form
            param_dict = {}
            for n, item in enumerate(items):
                param_dict[header_items[n]] = item

            param_attributes = {}

            id = param_dict.pop('id', None)
            if id:
                param_attributes['id'] = id

            marks_cell = param_dict.pop('marks', None)
            if marks_cell:
                marks = [getattr(_pytest.mark, mark.strip()) for mark in marks_cell.split(";")]
                param_attributes['marks'] = marks

            param = _pytest.param(param_dict, **param_attributes)
            param_list.append(param)

    return param_list


