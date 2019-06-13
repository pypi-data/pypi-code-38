import pytest


pytest_plugins = [
    "tests.fixtures.fixture_engine_schemas",
    "tests.fixtures.fixture_engine_structures",
    "tests.fixtures.fixture_engine",
]


@pytest.fixture
def is_named_tuple_class():
    def _(t):
        b = t.__bases__
        if len(b) != 1 or b[0] != tuple:
            bb = b[0].__bases__
            if len(bb) != 1 or bb[0] != tuple:
                return False
        f = getattr(t, '_fields', None)
        if not isinstance(f, tuple):
            return False
        return all(type(n) == str for n in f)

    return _
