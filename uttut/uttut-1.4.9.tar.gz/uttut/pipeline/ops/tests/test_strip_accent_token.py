import pytest

from ..strip_accent_token import StripAccentToken
from .common_tests import OperatorTestTemplate, ParamTuple


class TestStripAccentToken(OperatorTestTemplate):

    params = [
        ParamTuple(  # ref: Bert tokenization_test.py#L64
            u"H\u00E9llo",
            [1, 2, 3, 4, 5],
            "Hello",
            [1, 2, 3, 4, 5],
            id='eng',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return StripAccentToken()

    def test_equal(self, op):
        assert op == StripAccentToken()
