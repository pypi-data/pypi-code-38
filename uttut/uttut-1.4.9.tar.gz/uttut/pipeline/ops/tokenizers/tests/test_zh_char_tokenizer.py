import pytest

from ...tests.common_tests import OperatorTestTemplate, ParamTuple
from ..zh_char_tokenizer import ZhCharTokenizer


class TestZhCharTokenizer(OperatorTestTemplate):

    params = [
        ParamTuple(
            "How's it going today, Mr.Smith?",
            [1, 1, 1, 1, 1, 0, 2, 2, 0, 3, 3, 3, 3, 3, 0, 4, 4, 4, 4, 4, 5, 0,
             6, 6, 6, 6, 6, 6, 6, 6, 7],
            ['How', "'", 's', 'it', 'going', 'today', ',', 'Mr', '.', 'Smith', '?'],
            [1, 1, 1, 2, 3, 4, 5, 6, 6, 6, 7],
            id='eng',
        ),
        ParamTuple(
            "薄餡的櫻花妹呢？",
            [1, 1, 0, 2, 2, 2, 3, 4],
            ['薄', '餡', '的', '櫻', '花', '妹', '呢', '？'],
            [1, 1, 0, 2, 2, 2, 3, 4],
            id='zh',
        ),
        ParamTuple(
            "GB亂入",
            [1, 1, 2, 2],
            ['GB', '亂', '入'],
            [1, 2, 2],
            id='eng + zh',
        ),
        ParamTuple(
            "GB亂入!!!",
            [1, 1, 2, 2, 3, 4, 5],
            ['GB', '亂', '入', '!', '!', '!'],
            [1, 2, 2, 3, 4, 5],
            id='eng + zh + punct',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return ZhCharTokenizer()

    def test_equal(self, op):
        assert op == ZhCharTokenizer()
