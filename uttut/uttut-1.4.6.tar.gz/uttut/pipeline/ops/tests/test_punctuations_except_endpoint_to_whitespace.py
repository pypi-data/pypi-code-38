import pytest

from ..punctuation_except_endpoint_to_whitespace import PunctuationExceptEndpointToWhitespace
from .common_tests import OperatorTestTemplate, ParamTuple


@pytest.fixture(scope='module')
def op():
    return PunctuationExceptEndpointToWhitespace()


class TestPunctuationExceptEndpointToWhitespace(OperatorTestTemplate):

    params = [
        ParamTuple(
            "0.3",
            [1, 2, 3],
            "0.3",
            [1, 2, 3],
            id='float',
        ),
        ParamTuple(
            "O.O",
            [2, 3, 4],
            "O.O",
            [2, 3, 4],
            id='emoji',
        ),
        ParamTuple(
            "abc def",
            [2, 3, 4, 5, 6, 7, 8],
            "abc def",
            [2, 3, 4, 5, 6, 7, 8],
            id='all english',
        ),
        ParamTuple(
            "隼興亂入",
            [2, 3, 4, 5],
            "隼興亂入",
            [2, 3, 4, 5],
            id='all chinese',
        ),
    ]

    def op(self):
        pass

    def test_equal(self, op):
        assert op == PunctuationExceptEndpointToWhitespace()


@pytest.mark.parametrize(
    "input_str,input_labels,expected_output_seq,"
    "expected_output_labels,expected_realigned_labels",
    [
        pytest.param(
            "^$`", [1, 2, 3], "   ", [0, 0, 0], [0, 0, 0],
            id="puncts in the range",
        ),
        pytest.param(
            "⁕⁇※࡞", [1, 2, 3, 4], "    ", [0, 0, 0, 0], [0, 0, 0, 0],
            id="puncts in P category only",
        ),
        pytest.param(
            "西瓜汁一杯多少$$?",
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "西瓜汁一杯多少   ",
            [1, 2, 3, 4, 5, 6, 7, 0, 0, 0],
            [1, 2, 3, 4, 5, 6, 7, 0, 0, 0],
            id="chinese + puncts",
        ),
    ],
)
def test_invertible_cases(
        input_str,
        input_labels,
        expected_output_seq,
        expected_output_labels,
        expected_realigned_labels,
        op,
    ):
    output_seq, label_aligner = op.transform(input_str)
    assert expected_output_seq == output_seq

    output_labels = label_aligner.transform(input_labels)
    assert expected_output_labels == output_labels

    realigned_labels = label_aligner.inverse_transform(expected_output_labels)
    assert expected_realigned_labels == realigned_labels
