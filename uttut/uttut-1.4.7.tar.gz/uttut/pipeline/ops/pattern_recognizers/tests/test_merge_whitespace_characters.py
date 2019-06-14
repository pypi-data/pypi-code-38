import pytest

from ...tests.common_tests import OperatorTestTemplate, ParamTuple
from ..merge_whitespace_characters import MergeWhiteSpaceCharacters


class TestMergeWhiteSpaceCharacters(OperatorTestTemplate):

    params = [
        ParamTuple(
            " \t\n\r\x0b\x0c ",
            [0, 0, 0, 0, 0, 0, 0],
            " ",
            [0],
            id='all whitespace characters',
        ),
        ParamTuple(
            " _int_   _int_   _int_ ",
            [0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0],
            " _int_ _int_ _int_ ",
            [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
            id='result of int token with space op',
        ),
        ParamTuple(
            "GB亂入  _int_  次",
            [1, 1, 2, 2, 0, 0, 3, 3, 3, 3, 3, 0, 0, 4],
            "GB亂入 _int_ 次",
            [1, 1, 2, 2, 0, 3, 3, 3, 3, 3, 0, 4],
            id='zh + int token',
        ),
        ParamTuple(
            "我想要喝多 多 綠",
            [0, 0, 0, 0, 1, 1, 1, 1, 1],
            "我想要喝多 多 綠",
            [0, 0, 0, 0, 1, 1, 1, 1, 1],
            id='label identity',
        ),
        ParamTuple(
            "GB亂入",
            [1, 1, 2, 2],
            "GB亂入",
            [1, 1, 2, 2],
            id='identity',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return MergeWhiteSpaceCharacters()

    def test_equal(self, op):
        assert MergeWhiteSpaceCharacters() == op
