import pytest

from ...tests.common_tests import OperatorTestTemplate, ParamTuple
from ..replace_a_with_b import ReplaceAwithB


class TestFloatToken(OperatorTestTemplate):

    params = [
        ParamTuple(
            "12.34.56.78.910",
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            "12 34 56 78 910",
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            id='digits + token to be replaced',
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
        return ReplaceAwithB(a=r"[\.]+", b=" ")

    def test_not_invertiable(self, op):
        # labels are not invertible
        output_seq, label_aligner = op.transform(".....")
        assert " " == output_seq

        output_labels = label_aligner.transform([1, 1, 3, 1, 1])
        assert [1] == output_labels

        output = label_aligner.inverse_transform([1])
        assert output == [1, 1, 1, 1, 1]
