import pytest

from ..pure_num_to_token import PureNum2Token
from .common_tests import OperatorTestTemplate, ParamTuple
from ..tokens import NUM_TOKEN


class TestPureNum2TokenDefault(OperatorTestTemplate):

    params = [
        ParamTuple(
            ["100", "W9", "300g", "123", "37.6"],
            [1, 2, 3, 4, 5],
            [NUM_TOKEN, "W9", "300g", NUM_TOKEN, "37.6"],
            [1, 2, 3, 4, 5],
            id="simple",
        ),
        ParamTuple(
            ["１００", "W９", "３００g", "１２３", "３７.６"],
            [1, 2, 3, 4, 5],
            [NUM_TOKEN, "W９", "３００g", NUM_TOKEN, "３７.６"],
            [1, 2, 3, 4, 5],
            id="fullwidth-simple",
        ),
        ParamTuple(
            ["繼良", "有", "1234567890", "億", "元"],
            [1, 2, 3, 4, 5],
            ["繼良", "有", NUM_TOKEN, "億", "元"],
            [1, 2, 3, 4, 5],
            id="zh with pure digits",
        ),
        ParamTuple(
            ["繼良", "有", "１２３４５６７８９０", "億", "元"],
            [1, 2, 3, 4, 5],
            ["繼良", "有", NUM_TOKEN, "億", "元"],
            [1, 2, 3, 4, 5],
            id="zh with pure fullwidth digits",
        ),
        ParamTuple(
            ["取消", "HSC5", "改", "HSA5"],
            [1, 2, 3, 4],
            ["取消", "HSC5", "改", "HSA5"],
            [1, 2, 3, 4],
            id="zh with not pure digits",
        ),
        ParamTuple(
            ["取消", "HSC５", "改", "HSA５"],
            [1, 2, 3, 4],
            ["取消", "HSC５", "改", "HSA５"],
            [1, 2, 3, 4],
            id="zh with not pure fullwidth digits",
        ),
        ParamTuple(
            ["1２3４５６78９０"],
            [1],
            [NUM_TOKEN],
            [1],
            id="fullwidth, halfwidth mixture",
        ),
        ParamTuple(
            ["GB", "亂入"],
            [3, 4],
            ["GB", "亂入"],
            [3, 4],
            id="identity",
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return PureNum2Token()


class TestPureNum2TokenCustom(OperatorTestTemplate):

    params = [
        ParamTuple(
            ["100", "W9", "300g", "123"],
            [1, 2, 3, 4],
            ["123", "W9", "300g", "123"],
            [1, 2, 3, 4],
            id="simple",
        ),
        ParamTuple(
            ["繼良", "有", "100", "億", "元"],
            [1, 2, 3, 4, 5],
            ["繼良", "有", "123", "億", "元"],
            [1, 2, 3, 4, 5],
            id="zh with pure digits",
        ),
        ParamTuple(
            ["取消", "HSC5", "改", "HSA5"],
            [1, 2, 3, 4],
            ["取消", "HSC5", "改", "HSA5"],
            [1, 2, 3, 4],
            id="zh with not pure digits",
        ),
        ParamTuple(
            ["GB", "亂入"],
            [3, 4],
            ["GB", "亂入"],
            [3, 4],
            id="identity",
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return PureNum2Token(token='123')
