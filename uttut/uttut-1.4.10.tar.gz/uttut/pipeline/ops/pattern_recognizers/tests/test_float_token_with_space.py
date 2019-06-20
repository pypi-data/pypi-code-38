import pytest

from ...tests.common_tests import OperatorTestTemplate, ParamTuple
from ..float_token_with_space import FloatTokenWithSpace


class TestFloatTokenWithSpace(OperatorTestTemplate):

    params = [
        ParamTuple(
            "12.3 2.7 0.7777",
            [1, 1, 1, 1, 0, 2, 2, 2, 0, 3, 3, 3, 3, 3, 3],
            " _float_   _float_   _float_ ",
            [0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 0],
            id='float float float',
        ),
        ParamTuple(
            "１２.３ ２.７ ０.７７７７",
            [1, 1, 1, 1, 0, 2, 2, 2, 0, 3, 3, 3, 3, 3, 3],
            " _float_   _float_   _float_ ",
            [0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 0],
            id='fullwidth-float float float',
        ),
        ParamTuple(
            "1 2.7 1000",
            [1, 0, 2, 2, 2, 0, 3, 3, 3, 3],
            "1  _float_  1000",
            [1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 3, 3, 3, 3],
            id='int float int',
        ),
        ParamTuple(
            "１ ２.７ １０００",
            [1, 0, 2, 2, 2, 0, 3, 3, 3, 3],
            "１  _float_  １０００",
            [1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 3, 3, 3, 3],
            id='fullwidth-int float int',
        ),
        ParamTuple(
            "12.7.7",
            [1, 2, 3, 4, 5, 6],
            "12.7.7",
            [1, 2, 3, 4, 5, 6],
            id='invalid float',
        ),
        ParamTuple(
            "１２.７.７",
            [1, 2, 3, 4, 5, 6],
            "１２.７.７",
            [1, 2, 3, 4, 5, 6],
            id='fullwidth-invalid float',
        ),
        ParamTuple(
            "9.99",
            [0, 0, 0, 0],
            " _float_ ",
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            id='float with label 0',
        ),
        ParamTuple(
            "０１２３４５６７８.９",
            [0 for _ in range(11)],
            " _float_ ",
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            id='fullwidth-float with label 0',
        ),
        ParamTuple(
            "奇利利有12.3億元",
            [1, 1, 1, 2, 3, 3, 3, 3, 3, 3],
            "奇利利有 _float_ 億元",
            [1, 1, 1, 2, 0, 3, 3, 3, 3, 3, 3, 3, 0, 3, 3],
            id='zh with float',
        ),
        ParamTuple(
            "奇利利有１２.３億元",
            [1, 1, 1, 2, 3, 3, 3, 3, 3, 3],
            "奇利利有 _float_ 億元",
            [1, 1, 1, 2, 0, 3, 3, 3, 3, 3, 3, 3, 0, 3, 3],
            id='fullwidth-zh with float',
        ),
        ParamTuple(
            "１2.３",
            [1, 1, 1, 1],
            " _float_ ",
            [0, 1, 1, 1, 1, 1, 1, 1, 0],
            id='fullwidth halfwidth mixture',
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
        return FloatTokenWithSpace()

    def test_equal(self, op):
        assert FloatTokenWithSpace() == op
