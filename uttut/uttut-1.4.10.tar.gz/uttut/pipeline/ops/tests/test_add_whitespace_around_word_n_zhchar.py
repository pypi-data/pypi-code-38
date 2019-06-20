import pytest

from ..add_whitespace_around_word_n_zhchar import AddWhitespaceAroundWordnZhChar
from .common_tests import OperatorTestTemplate, ParamTuple


class TestAddWhitespaceAroundWord(OperatorTestTemplate):

    params = [
        ParamTuple(
            "HSB5改成HSA5，如何辦理？",
            list(range(1, 17)),
            "HSB5 改  成 HSA5， 如  何  辦  理 ？",
            [1, 2, 3, 4, 0, 5, 0, 0, 6, 0, 7, 8, 9, 10, 11,
             0, 12, 0, 0, 13, 0, 0, 14, 0, 0, 15, 0, 16],
            'complex en + zh',
        ),
        ParamTuple(
            "薄餡在喝珍珠椰果奶茶",
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            " 薄  餡  在  喝  珍珠  椰  果  奶茶 ",
            [0, 1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 6, 0, 0, 7, 0, 0, 8, 0, 0, 9, 10, 0],
            'zh choose short',
        ),
        ParamTuple(
            "珍珠是精緻澱粉",
            [1, 2, 3, 4, 5, 6, 7],
            " 珍珠  是  精緻  澱  粉 ",
            [0, 1, 2, 0, 0, 3, 0, 0, 4, 5, 0, 0, 6, 0, 0, 7, 0],
            'zh',
        ),
        ParamTuple(
            "GB亂入",
            [1, 2, 3, 4],
            "GB 亂  入 ",
            [1, 2, 0, 3, 0, 0, 4, 0],
            'not identity in this case',
        ),
        ParamTuple(
            "1234567890",
            list(range(1, 11)),
            "1234567890",
            list(range(1, 11)),
            'digits-identity',
        ),
        ParamTuple(
            "that's awesome!",
            list(range(1, 16)),
            "that's awesome!",
            list(range(1, 16)),
            'en-identity',
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return AddWhitespaceAroundWordnZhChar(user_words=['alvin', '珍珠', '奶茶', '珍珠奶茶', '精緻'])

    def test_equal(self, op):
        assert op == AddWhitespaceAroundWordnZhChar(user_words=['alvin', '珍珠', '奶茶', '珍珠奶茶', '精緻'])

    def test_invalid_op(self):
        with pytest.raises(ValueError):
            AddWhitespaceAroundWordnZhChar(user_words=[])
        with pytest.raises(ValueError):
            AddWhitespaceAroundWordnZhChar(user_words=None)
