from contextlib import contextmanager

import pytest

from linecook.config import parsers


def test_register_transform_parser():
    with mock_transform_parser_registry() as fake_registry:
        assert len(fake_registry) == 0

        @parsers.register_transform_parser('test')
        def fake_parser(*args, **kwargs):
            pass

        assert len(fake_registry) == 1
        assert fake_registry['test'] == fake_parser


class TestResolveRecipe:

    def test_transform_name_not_found(self):
        with pytest.raises(RuntimeError):
            list(parsers.resolve_recipe(['missing-transform-name'], {}))


@contextmanager
def mock_transform_parser_registry():
    original_registry = parsers.TRANSFORM_PARSERS
    parsers.TRANSFORM_PARSERS = {}
    try:
        yield parsers.TRANSFORM_PARSERS
    finally:
        parsers.TRANSFORM_PARSERS = original_registry
