import pytest

from ..add_sos_eos import AddSosEos
from ..tokens import START_TOKEN, END_TOKEN
from .common_tests import OperatorTestTemplate, ParamTuple


class TestAddSosEos(OperatorTestTemplate):

    params = [
        ParamTuple(
            ['alvin', '喜歡', '吃', '榴槤'],
            [1, 2, 3, 4],
            ['<sos>', 'alvin', '喜歡', '吃', '榴槤', '<eos>'],
            [0, 1, 2, 3, 4, 0],
            'zh',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return AddSosEos()

    def test_not_equal(self, op):
        custom_op = AddSosEos(start_token='custom_SOS', end_token='custom_EOS')
        assert custom_op != op


@pytest.mark.parametrize(
    "op, expected_configs",
    [
        pytest.param(
            AddSosEos(),
            {'start_token': START_TOKEN, 'end_token': END_TOKEN},
            id="default",
        ),
        pytest.param(
            AddSosEos('1', '2'),
            {'start_token': '1', 'end_token': '2'},
            id="no keywords",
        ),
        pytest.param(
            AddSosEos('1'),
            {'start_token': '1', 'end_token': END_TOKEN},
            id="partial input",
        ),
        pytest.param(
            AddSosEos(end_token='2', start_token='1'),
            {'start_token': '1', 'end_token': '2'},
            id="input with key",
        ),
    ],
)
def test_correct_configs(op, expected_configs):
    assert op.configs == expected_configs
