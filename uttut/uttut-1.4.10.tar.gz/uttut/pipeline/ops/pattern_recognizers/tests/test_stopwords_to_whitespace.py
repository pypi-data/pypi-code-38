import pytest
import os

from ...tests.common_tests import OperatorTestTemplate, ParamTuple
from ..stopwords_to_whitespace import StopwordsToWhitespace


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT_DIR, 'stopwords.txt'), 'r') as f:
    STOPWORDS = f.read().split("\n")

STOPWORDS_STR = "".join(STOPWORDS)


class TestStopwordsToWhitespace(OperatorTestTemplate):

    params = [
        ParamTuple(
            STOPWORDS_STR,
            [0 for _ in range(len(STOPWORDS_STR))],
            "".join([" " for _ in range(len(STOPWORDS))]),
            [0 for _ in range(len(STOPWORDS))],
            id='all stopwords',
        ),
        ParamTuple(
            "你好嗎",
            [1, 2, 0],
            "你好 ",
            [1, 2, 0],
            id='stopwords at end',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return StopwordsToWhitespace()

    def test_not_invertiable(self, op):
        # labels are not invertible
        output_seq, label_aligner = op.transform("哎呀,你好嗎")
        assert " ,你好 " == output_seq

        output_labels = label_aligner.transform([1, 2, 3, 4, 5, 6])
        assert [0, 3, 4, 5, 0] == output_labels

        output = label_aligner.inverse_transform([0, 3, 4, 5, 0])
        assert output == [0, 0, 3, 4, 5, 0]

    def test_equal(self, op):
        assert StopwordsToWhitespace() == op
