import pytest

from ..add_end_token import AddEndToken
from ..tokens import END_TOKEN
from .common_tests import OperatorTestTemplate, ParamTuple


class TestAddEndToken(OperatorTestTemplate):

    params = [
        ParamTuple(
            ['alvin', '喜歡', '吃', '榴槤'],
            [1, 2, 3, 4],
            ['alvin', '喜歡', '吃', '榴槤', '<eos>'],
            [1, 2, 3, 4, 0],
            'zh',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return AddEndToken()

    def test_not_equal(self, op):
        custom_op = AddEndToken(end_token='custom_EOS')
        assert custom_op != op


@pytest.mark.parametrize(
    "op, expected_configs",
    [
        pytest.param(
            AddEndToken(),
            {'end_token': END_TOKEN},
            id="default",
        ),
        pytest.param(
            AddEndToken('1'),
            {'end_token': '1'},
            id="no keywords",
        ),

    ],
)
def test_correct_configs(op, expected_configs):
    assert op.configs == expected_configs


@pytest.mark.parametrize(
    "end_token, error",
    [
        pytest.param(
            None,
            ValueError,
            id="The end token can not be None",
        ),
        pytest.param(
            1,
            TypeError,
            id="wrong type of end token",
        ),
        pytest.param(
            '',
            ValueError,
            id="empty string is not allowed.",
        ),
    ],
)
def test_invalid_end_token(end_token, error):
    with pytest.raises(error):
        AddEndToken(end_token)
