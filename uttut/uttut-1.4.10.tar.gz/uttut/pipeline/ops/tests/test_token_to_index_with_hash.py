import pytest

from ..token_to_index_with_hash import Token2IndexwithHash
from ..utils.consistent_hash import consistent_hash
from .common_tests import OperatorTestTemplate, ParamTuple


def hash_unknown(key):
    return consistent_hash(key, 5)


class TestToken2IndexwithHash(OperatorTestTemplate):

    params = [
        ParamTuple(
            ['薄餡', '要', '帶', '櫻花', '妹', '回來'],
            [1, 2, 3, 4, 5, 6],
            [1, 2, 3, hash_unknown('櫻花'), 4, hash_unknown('回來')],
            [1, 2, 3, 4, 5, 6],
            id='zh',
        ),
    ]

    @pytest.fixture(scope='class')
    def token2index(self):
        return {'oh': 0, '薄餡': 1, '要': 2, '帶': 3, '妹': 4}

    @pytest.fixture(scope='class')
    def op(self, token2index):
        return Token2IndexwithHash(token2index)

    @pytest.mark.parametrize(
        'token2index',
        [
            pytest.param(
                {'薄餡': 1, '要': 1, '帶': 3, '妹': 4},
                id='duplicated indices',
            ),
            pytest.param(
                {'薄餡': 0, '要': 2, '帶': 3, '妹': 4},
                id='indices not continuous',
            ),
        ],
    )
    def test_invalid_token2index(self, token2index):
        with pytest.raises(ValueError):
            Token2IndexwithHash(token2index=token2index)

    def test_equal(self, op, token2index):
        assert op == Token2IndexwithHash(token2index)

    def test_not_equal(self, op):
        op1 = Token2IndexwithHash(token2index={'薄餡': 0, '要': 1, '帶': 2, '妹': 3})
        assert op != op1
