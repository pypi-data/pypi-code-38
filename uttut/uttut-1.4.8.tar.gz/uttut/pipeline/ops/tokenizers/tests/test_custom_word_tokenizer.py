import pytest

from ...tests.common_tests import OperatorTestTemplate, ParamTuple
from ..custom_word_tokenizer import CustomWordTokenizer


@pytest.fixture(scope='module')
def user_words():
    return ['珍奶', '珍奶去冰', '去冰']


@pytest.fixture(scope='module')
def op(user_words):
    return CustomWordTokenizer(user_words)


class TestCustomWordTokenizer(OperatorTestTemplate):

    params = [
        ParamTuple(
            "珍奶",
            [1, 1],
            ["珍奶"],
            [1],
            id='exactly fit',
        ),
        ParamTuple(
            "去冰珍奶謝謝",
            [1, 1, 2, 2, 3, 4],
            ["去冰", "珍奶", "謝", "謝"],
            [1, 2, 3, 4],
            id='multiple',
        ),
        ParamTuple(
            "我想要珍奶去冰",
            [1, 2, 3, 4, 4, 4, 4],
            ["我", "想", "要", "珍奶去冰"],
            [1, 2, 3, 4],
            id='fit end',
        ),
        ParamTuple(
            "GB亂入",
            [1, 2, 3, 4],
            ["G", "B", "亂", "入"],
            [1, 2, 3, 4],
            id='not fit',
        ),
    ]

    def op(self):
        pass

    def test_equal(self, op, user_words):
        assert CustomWordTokenizer(user_words) == op

    @pytest.mark.parametrize(  # type: ignore
        "user_words",
        [
            pytest.param([], id='empty'),
            pytest.param(None, id='none'),
        ],
    )
    def test_invalid_init(self, user_words):
        with pytest.raises(ValueError):
            CustomWordTokenizer(user_words)


@pytest.mark.parametrize(
    "input_str,input_labels,expected_output_seq,"
    "expected_output_labels,expected_realigned_labels",
    [
        pytest.param(
            "我想要珍奶去冰",
            [1, 2, 3, 4, 4, 0, 4],
            ["我", "想", "要", "珍奶去冰"],
            [1, 2, 3, 4],
            [1, 2, 3, 4, 4, 4, 4],
            id='word has different labels',
        ),
    ],
)
def test_invertible_cases(
        input_str, input_labels,
        expected_output_seq, expected_output_labels,
        expected_realigned_labels,
        op,
    ):
    output_seq, label_aligner = op.transform(input_str)
    assert expected_output_seq == output_seq

    output_labels = label_aligner.transform(input_labels)
    assert expected_output_labels == output_labels

    realigned_labels = label_aligner.inverse_transform(expected_output_labels)
    assert expected_realigned_labels == realigned_labels
