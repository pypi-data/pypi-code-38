import pytest

from ...tests.common_tests import OperatorTestTemplate, ParamTuple
from ..int_token import IntToken


class TestIntToken(OperatorTestTemplate):

    params = [
        ParamTuple(
            "12 24 3666",
            [1, 1, 0, 2, 2, 0, 3, 3, 3, 3],
            "_int_ _int_ _int_",
            [1, 1, 1, 1, 1, 0, 2, 2, 2, 2, 2, 0, 3, 3, 3, 3, 3],
            id='int int int',
        ),
        ParamTuple(
            "12.3 1000 3.5",
            [1, 1, 1, 1, 0, 2, 2, 2, 2, 0, 3, 3, 3],
            "12.3 _int_ 3.5",
            [1, 1, 1, 1, 0, 2, 2, 2, 2, 2, 0, 3, 3, 3],
            id='float int float',
        ),
        ParamTuple(
            "999",
            [0, 0, 0],
            "_int_",
            [0, 0, 0, 0, 0],
            id='int with label 0',
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
            "GB亂入_int_次",
            [1, 1, 2, 2, 3, 3, 3, 3, 3, 4],
            id='zh with int',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return IntToken()

    def test_equal(self, op):
        assert IntToken() == op
