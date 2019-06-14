import pytest

from ...tests.common_tests import OperatorTestTemplate, ParamTuple
from ..whitespace_tokenizer import WhiteSpaceTokenizer


class TestWhiteSpaceTokenizer(OperatorTestTemplate):

    params = [
        ParamTuple(
            "a \t \t \nb c",
            [1, 0, 0, 0, 0, 0, 0, 2, 0, 3],
            ["a", "b", "c"],
            [1, 2, 3],
            id='eng',
        ),
        ParamTuple(
            "  a \t \t \nb c\n\r",
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 3, 0, 0],
            ["a", "b", "c"],
            [1, 2, 3],
            id='eng with whitespace at head and tail',
        ),
        ParamTuple(
            "GB亂入",
            [2, 2, 2, 2],
            ["GB亂入"],
            [2],
            id='zh',
        ),
        ParamTuple(
            "",
            [],
            [],
            [],
            id='empty string',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return WhiteSpaceTokenizer()

    def test_equal(self, op):
        assert WhiteSpaceTokenizer() == op
