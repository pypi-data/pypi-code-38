import pytest

from ..pad import Pad
from ..tokens import PAD_TOKEN
from .common_tests import OperatorTestTemplate, ParamTuple


class TestPad(OperatorTestTemplate):

    params = [
        ParamTuple(
            ['alvin', '喜歡', '吃', '榴槤', '!'],
            [1, 2, 3, 4, 5],
            ['alvin', '喜歡', '吃', '榴槤', '!'],
            [1, 2, 3, 4, 5],
            id='equal',
        ),
        ParamTuple(
            ['alvin'],
            [1],
            ['alvin', PAD_TOKEN, PAD_TOKEN, PAD_TOKEN, PAD_TOKEN],
            [1, 0, 0, 0, 0],
            id='shorter',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return Pad(5)

    def test_longer_case(self, op):
        # labels are not invertible
        output_seq, label_aligner = op.transform(
            ['alvin', '喜歡', '吃', '榴槤', '和', '蟲', '!'],
        )
        assert ['alvin', '喜歡', '吃', '榴槤', '和'] == output_seq

        output_labels = label_aligner.transform([1, 2, 3, 4, 5, 6, 7])
        assert [1, 2, 3, 4, 5] == output_labels

        output = label_aligner.inverse_transform(output_labels)
        assert [1, 2, 3, 4, 5, 0, 0] == output

    def test_equal(self, op):
        assert Pad(5) == op

    def test_not_equal(self):
        op1 = Pad(pad_token='PAD', maxlen=10)
        op2 = Pad(pad_token='PAD', maxlen=15)
        op3 = Pad(maxlen=10)
        assert op1 != op2
        assert op2 != op3


@pytest.mark.parametrize(
    "op, expected_configs",
    [
        pytest.param(
            Pad(5),
            {'pad_token': PAD_TOKEN, 'maxlen': 5},
            id="default token",
        ),
        pytest.param(
            Pad(10, 'PAD'),
            {'pad_token': 'PAD', 'maxlen': 10},
            id="input without key",
        ),
        pytest.param(
            Pad(pad_token='PAD', maxlen=1),
            {'pad_token': 'PAD', 'maxlen': 1},
            id="input with key",
        ),
    ],
)
def test_correct_configs(op, expected_configs):
    assert op.configs == expected_configs
