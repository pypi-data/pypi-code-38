import os
import os.path
import warnings

import pytest

MARKER = "deprecated"


def get_fslocation_from_item(item):
    """
    :rtype: a tuple of (str|LocalPath, int) with filename and line number.
    """
    location, line = item.location[:2]
    location = os.path.realpath(location)
    return location, line


@pytest.mark.tryfirst
def pytest_load_initial_conftests(early_config, parser, args):
    """
    :param early_config:
    :param parser:
    :param args:
    :type args: tuple|list
    :return:
    """
    early_config.addinivalue_line(
        "markers", "%s: Mark the test as testing a deprecated feature." "" % MARKER
    )


def _process_marker(request, reason, *_args, **_kwargs):
    module_name = request.node.module.__name__
    test_name = request.node.name
    path, lineno = get_fslocation_from_item(request.node)
    warning = UserWarning(
        "%s:%s is testing a deprecated feature: %s" % (module_name, test_name, reason)
    )
    warnings.warn_explicit(
        warning,
        category=None,
        filename=str(path),
        lineno=lineno + 1 if lineno is not None else None,
    )


@pytest.fixture(autouse=True)
def _pytest_deprecated_test_marker(request):
    marker = request.node.get_closest_marker(MARKER)
    if marker:
        _process_marker(request, *marker.args, **marker.kwargs)
