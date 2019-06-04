"""Test features of :mod:`moretools.func` not covered by doc-tests."""

import pytest
from six import PY3

from moretools import getfunc, isfunc


def test_isfunc_with_methods():
    """
    Test if :func:`moretools.isfunc` correctly checks methods.

    And returns ``False`` when called with any kind of method wrapper for
    ``function`` objects
    """
    class SomeType(object):
        def method(self):
            pass

        @classmethod
        def clsmethod(cls):
            pass

        @staticmethod
        def static():
            pass

    instance = SomeType()
    for obj in [instance.method, instance.clsmethod]:
        assert isfunc(obj) is False

    for obj in [SomeType.static, instance.static]:
        assert isfunc(obj) is True

    assert isfunc(SomeType.method) is (True if PY3 else False)
    assert isfunc(SomeType.clsmethod) is False


def test_getfunc_with_non_callable():
    """
    Test if :func:`moretools.getfunc` correctly raises a ``TypeError``.

    When called with a non-callable argument, which is therefore not
    associated with a ``function`` object
    """
    for value, repr_regex in [
            (42, r"42"),
            ({}, r"{}"),
            (object(), r"<object [^>]+>"),
    ]:
        with pytest.raises(TypeError, match=(
                r"<apifunction moretools.getfunc{}> arg is not callable: {}"
                .format(r"\(obj\)" if PY3 else r"", repr_regex))):

            getfunc(value)


def test_getfunc_with_hidden_function():
    """
    Test if :func:`moretools.getfunc` correctly raises a ``ValueError``.

    When called with an argument associated with a function implementation
    that is not accessible from Python
    """
    for value, repr_regex in [
            (object, r"<(class|type) 'object'>"),
            (object.__init__, r"<slot wrapper '__init__' [^>]+>"),
    ]:
        with pytest.raises(ValueError, match=(
                r"<apifunction moretools.getfunc{}> can't access function "
                r"object of callable arg {}"
                .format(r"\(obj\)" if PY3 else r"", repr_regex))):

            getfunc(value)
