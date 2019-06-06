"""Validates the 'adapter.py' module"""

from nose.tools import ok_

from urllib3.util.retry import Retry

from termlink.adapter import build


def test_build():
    """Checks that build works be default"""
    adapter = build()
    ok_(adapter)


def test_build_with_custom_retry_policy():
    """Checks that an adapter can be built with a custom retry policy"""
    retry_policy = Retry()
    adapter = build(retry_policy=retry_policy)
    ok_(adapter)
