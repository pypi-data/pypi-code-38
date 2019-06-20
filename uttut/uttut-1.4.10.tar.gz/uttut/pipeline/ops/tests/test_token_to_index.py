import pytest

from ..token_to_index import Token2Index
from ..tokens import UNK_TOKEN
from .common_tests import OperatorTestTemplate, ParamTuple


class TestToken2Index(OperatorTestTemplate):

    params = [
        ParamTuple(
            ['薄餡', '要', '帶', '櫻花', '妹', '回來'],
            [1, 2, 3, 4, 5, 6],
            [1, 2, 3, 0, 4, 0],
            [1, 2, 3, 4, 5, 6],
            id='zh',
        ),
    ]

    @pytest.fixture
    def op(self):
        return Token2Index({UNK_TOKEN: 0, '薄餡': 1, '要': 2, '帶': 3, '妹': 4})

    @pytest.mark.parametrize(
        'error,token2index,unk_token',
        [
            pytest.param(
                ValueError, {'薄餡': 1, '要': 1, '帶': 3, '妹': 4}, UNK_TOKEN,
                id='duplicated indices',
            ),
            pytest.param(
                ValueError, {'薄餡': 0, '要': 2, '帶': 3, '妹': 4}, UNK_TOKEN,
                id='indices not continuous',
            ),
            pytest.param(
                KeyError, {'薄餡': 0, '要': 1, '帶': 2, '妹': 3}, UNK_TOKEN,
                id='token2index has no unk',
            ),
        ],
    )
    def test_invalid_token2index(self, error, token2index, unk_token):
        with pytest.raises(error):
            Token2Index(token2index=token2index, unk_token=unk_token)

    def test_equal(self, op):
        assert op == Token2Index({UNK_TOKEN: 0, '薄餡': 1, '要': 2, '帶': 3, '妹': 4})

    def test_not_equal(self):
        op1 = Token2Index(
            token2index={'薄餡': 0, '要': 1, '帶': 2, '妹': 3, 'UNK': 4},
            unk_token='UNK',
        )
        op2 = Token2Index(token2index={'薄餡': 0, '要': 1, '帶': 2, '妹': 3, UNK_TOKEN: 4})
        op3 = Token2Index(token2index={'薄餡': 0, UNK_TOKEN: 1})
        assert op1 != op2
        assert op2 != op3


@pytest.mark.parametrize(
    "op, expected_configs",
    [
        pytest.param(
            Token2Index(token2index={'薄餡': 0, '要': 1, '帶': 2, '妹': 3, UNK_TOKEN: 4}),
            {
                'token2index': {'薄餡': 0, '要': 1, '帶': 2, '妹': 3, UNK_TOKEN: 4},
                'unk_token': UNK_TOKEN,
            },
            id="default token",
        ),
        pytest.param(
            Token2Index({'薄餡': 0, '要': 1, '帶': 2, '妹': 3, '<pad>': 4}, '<pad>'),
            {
                'token2index': {'薄餡': 0, '要': 1, '帶': 2, '妹': 3, '<pad>': 4},
                'unk_token': '<pad>',
            },
            id="input without key",
        ),
        pytest.param(
            Token2Index(unk_token='PAD', token2index={'薄餡': 0, 'PAD': 1}),
            {'unk_token': 'PAD', 'token2index': {'薄餡': 0, 'PAD': 1}},
            id="input with key",
        ),
    ],
)
def test_correct_configs(op, expected_configs):
    assert op.configs == expected_configs
