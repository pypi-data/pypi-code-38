import pytest

from ...tests.common_tests import OperatorTestTemplate, ParamTuple
from ..num_token_with_space import NumTokenWithSpace


class TestNumTokenWithSpace(OperatorTestTemplate):

    params = [
        ParamTuple(
            "12 24 3666",
            [1, 1, 0, 2, 2, 0, 3, 3, 3, 3],
            " _num_   _num_   _num_ ",
            [0, 1, 1, 1, 1, 1, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 3, 3, 3, 3, 3, 0],
            id='num num num',
        ),
        ParamTuple(
            "１２ ２４ ３６６６",
            [1, 1, 0, 2, 2, 0, 3, 3, 3, 3],
            " _num_   _num_   _num_ ",
            [0, 1, 1, 1, 1, 1, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 3, 3, 3, 3, 3, 0],
            id='fullwidth-fnum num num',
        ),
        ParamTuple(
            "12.3 1000 3.5",
            [1, 1, 1, 1, 0, 2, 2, 2, 2, 0, 3, 3, 3],
            "12.3  _num_  3.5",
            [1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 2, 0, 0, 3, 3, 3],
            id='float num float',
        ),
        ParamTuple(
            "１２.３ １０００ ３.５",
            [1, 1, 1, 1, 0, 2, 2, 2, 2, 0, 3, 3, 3],
            "１２.３  _num_  ３.５",
            [1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 2, 0, 0, 3, 3, 3],
            id='fullwidth-float num float',
        ),
        ParamTuple(
            "999",
            [0, 0, 0],
            " _num_ ",
            [0, 0, 0, 0, 0, 0, 0],
            id='num with label 0',
        ),
        ParamTuple(
            "９９９",
            [0, 0, 0],
            " _num_ ",
            [0, 0, 0, 0, 0, 0, 0],
            id='fullwidth-num with label 0',
        ),
        ParamTuple(
            "０１2３４5６7８９",
            [3 for _ in range(10)],
            " _num_ ",
            [0, 3, 3, 3, 3, 3, 0],
            id='fullwidth, halfwidth mixture',
        ),
        ParamTuple(
            "GB亂入",
            [1, 1, 2, 2],
            "GB亂入",
            [1, 1, 2, 2],
            id='identity',
        ),
        ParamTuple(
            "GB亂入10次",
            [1, 1, 2, 2, 3, 3, 4],
            "GB亂入 _num_ 次",
            [1, 1, 2, 2, 0, 3, 3, 3, 3, 3, 0, 4],
            id='zh with num',
        ),
        ParamTuple(
            "GB亂入１０次",
            [1, 1, 2, 2, 3, 3, 4],
            "GB亂入 _num_ 次",
            [1, 1, 2, 2, 0, 3, 3, 3, 3, 3, 0, 4],
            id='zh with fullwidth-num',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return NumTokenWithSpace()

    def test_equal(self, op):
        assert NumTokenWithSpace() == op
