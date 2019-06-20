import pytest

from ..add_whitespace_around_punctuation import AddWhitespaceAroundPunctuation
from .common_tests import OperatorTestTemplate, ParamTuple


class TestAddWhitespaceAroundPunctuation(OperatorTestTemplate):

    params = [
        ParamTuple(
            "^$`",
            [1, 2, 3],
            " ^  $  ` ",
            [0, 1, 0, 0, 2, 0, 0, 3, 0],
            id='punct in range',
        ),
        ParamTuple(
            "⁕⁇※࡞",  # These are just a small portion of punctuations in P category.
            [1, 2, 3, 4],
            " ⁕  ⁇  ※  ࡞ ",
            [0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0],
            id='puncts in P category only',
        ),
        ParamTuple(
            "a,b",
            [1, 2, 3],
            "a , b",
            [1, 0, 2, 0, 3],
            id='eng',
        ),
        ParamTuple(
            "隼興亂入",
            [2, 3, 4, 5],
            "隼興亂入",
            [2, 3, 4, 5],
            id='all chinese',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return AddWhitespaceAroundPunctuation()

    def test_equal(self, op):
        assert op == AddWhitespaceAroundPunctuation()
