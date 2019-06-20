import pytest

from ..lowercase import Lowercase
from .common_tests import OperatorTestTemplate, ParamTuple


class TestLowercase(OperatorTestTemplate):

    params = [
        ParamTuple(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            list(range(26)),
            "abcdefghijklmnopqrstuvwxyz",
            list(range(26)),
            id='all a-z',
        ),
        ParamTuple(
            "Hello hoW are U",
            [1, 2, 3, 4, 5, 0, 6, 7, 8, 0, 9, 10, 11, 0, 12],
            "hello how are u",
            [1, 2, 3, 4, 5, 0, 6, 7, 8, 0, 9, 10, 11, 0, 12],
            id='mixed uppercase and lowercase eng',
        ),
        ParamTuple(
            "薄餡亂入",
            [0, 1, 2, 3],
            "薄餡亂入",
            [0, 1, 2, 3],
            id='zh',
        ),
        ParamTuple(
            "0123456789",
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "0123456789",
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            id='digits',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return Lowercase()

    def test_equal(self, op):
        assert op == Lowercase()
