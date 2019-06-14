import pytest

from ...tests.common_tests import OperatorTestTemplate, ParamTuple
from ..char_tokenizer import CharTokenizer


class TestCharTokenizer(OperatorTestTemplate):

    params = [
        ParamTuple(
            "GB亂入",
            [1, 1, 2, 2],
            ["G", "B", "亂", "入"],
            [1, 1, 2, 2],
            id='zh',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return CharTokenizer()

    def test_equal(self, op):
        assert CharTokenizer() == op
