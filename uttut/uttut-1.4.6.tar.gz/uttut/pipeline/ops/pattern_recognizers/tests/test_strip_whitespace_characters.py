import pytest

from ...tests.common_tests import OperatorTestTemplate, ParamTuple
from ..strip_whitespace_characters import StripWhiteSpaceCharacters


class TestStripWhiteSpaceCharacters(OperatorTestTemplate):

    params = [
        ParamTuple(
            " \t\n\r\x0b\x0c ",
            [0, 0, 0, 0, 0, 0, 0],
            "",
            [],
            id='all whitespace characters',
        ),
        ParamTuple(
            " abc \n\t ",
            [0, 1, 1, 1, 0, 0, 0, 0],
            "abc",
            [1, 1, 1],
            id='eng with whitespaces',
        ),
        ParamTuple(
            "我想要喝多 多 綠",
            [0, 0, 0, 0, 1, 1, 1, 1, 1],
            "我想要喝多 多 綠",
            [0, 0, 0, 0, 1, 1, 1, 1, 1],
            id='inner whitespace',
        ),
        ParamTuple(
            "GB亂入",
            [1, 1, 2, 2],
            "GB亂入",
            [1, 1, 2, 2],
            id='identity',
        ),
        ParamTuple(
            "",
            [],
            "",
            [],
            id='empty string',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return StripWhiteSpaceCharacters()

    def test_all_whitespaces(self, op):
        # labels are not invertible
        output_seq, label_aligner = op.transform("  \n\n\t\t")
        assert "" == output_seq

        output_labels = label_aligner.transform([1, 2, 3, 4, 5, 6])
        assert [] == output_labels

        output = label_aligner.inverse_transform([])
        assert output == [0, 0, 0, 0, 0, 0]

    def test_equal(self, op):
        assert StripWhiteSpaceCharacters() == op
