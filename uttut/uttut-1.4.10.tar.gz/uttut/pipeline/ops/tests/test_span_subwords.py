import pytest

from ..span_subwords import SpanSubwords
from .common_tests import OperatorTestTemplate, ParamTuple


def to_dict(input_list):
    output_dict = {}
    for i, token in enumerate(input_list):
        output_dict[token] = i
    return output_dict


class TestSpanSubwordsNoSubwords(OperatorTestTemplate):

    params = [
        ParamTuple(
            ["I", "like", "apples"],
            [1, 2, 3],
            ["I", "like", "apples"],
            [1, 2, 3],
            id="exactly match",
        ),
        ParamTuple(
            ["I", "like", "bananas"],
            [1, 2, 3],
            ["I", "like", "<unk>"],
            [1, 2, 3],
            id="word not found",
        ),
        ParamTuple(
            ["Ilikebananas"],
            [3],
            ["<unk>"],
            [3],
            id="word too long",
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return SpanSubwords(
            vocab=to_dict(["I", "like", "apples"]),
            unk_token="<unk>",
            maxlen_per_token=10,
        )


class TestSpanSubwordsHasSubwords(OperatorTestTemplate):

    params = [
        ParamTuple(
            ["unwanted", "running"],
            [1, 2],
            ["un", "##want", "##ed", "runn", "##ing"],
            [1, 1, 1, 2, 2],
            id="exactly match",
        ),
        ParamTuple(
            ["unwantedX", "running"],
            [1, 2],
            ["[UNK]", "runn", "##ing"],
            [1, 2, 2],
            id="word not found",
        ),
    ]

    @pytest.fixture(scope='class')
    def op(self):
        return SpanSubwords(
            vocab=to_dict(["[UNK]", "[CLS]", "[SEP]", "want",
                           "##want", "##ed", "wa", "un", "runn", "##ing"]),
            unk_token="[UNK]",
            maxlen_per_token=200,
        )


@pytest.mark.parametrize(
    "obj1,obj2",
    [
        pytest.param(
            SpanSubwords(
                vocab=to_dict(["I", "like", "apples"]),
                unk_token="<unk>",
                maxlen_per_token=10,
            ),
            SpanSubwords(
                vocab=to_dict(["I", "like", "apples"]),
                unk_token="<unk>",
                maxlen_per_token=200,
            ),
            id="different maxlen_per_token",
        ),
        pytest.param(
            SpanSubwords(
                vocab=to_dict(["I", "like", "apples"]),
                unk_token="<unk>",
                maxlen_per_token=10,
            ),
            SpanSubwords(
                vocab=to_dict(["I", "like", "apples"]),
                unk_token="[UNK]",
                maxlen_per_token=10,
            ),
            id="different unk",
        ),
        pytest.param(
            SpanSubwords(
                vocab=to_dict(["I", "like", "apples"]),
                unk_token="<unk>",
                maxlen_per_token=10,
            ),
            SpanSubwords(
                vocab=to_dict(["##apples"]),
                unk_token="<unk>",
                maxlen_per_token=10,
            ),
            id="different vocab",
        ),
    ],
)
def test_not_equal(obj1, obj2):
    assert obj1 != obj2
