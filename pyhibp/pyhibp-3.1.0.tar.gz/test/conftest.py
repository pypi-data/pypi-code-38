import time

import pytest

import pyhibp


@pytest.fixture(autouse=True)
def dev_user_agent(monkeypatch):
    ua_string = pyhibp.pyHIBP_USERAGENT
    monkeypatch.setattr(pyhibp, 'pyHIBP_USERAGENT', ua_string + " (Testing Suite)")


@pytest.fixture(name="sleep")
def sleep_test(request):
    """
    For the endpoints where a rate limit is specified, or we want to be kind to the endpoint and not
    needlessly execute requests too quickly, this specifies a test module-configurable sleep duration.

    Usage: Specify a module-level variable named `_PYTEST_SLEEP_DURATION`, and the value is an int,
    specifying the number of seconds to sleep between test invocations.
    """
    sleep_duration = getattr(request.module, "_PYTEST_SLEEP_DURATION", 0)
    time.sleep(sleep_duration)
