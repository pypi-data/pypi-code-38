import pytest

from .tokenization import WordpieceTokenizer as BertWordpieceTokenizer
from ..word_piece import word_piece_pipe, vocab

from uttut.elements import Datum


test_cases = [
    pytest.param(  # ref: Bert tokenization_test.py#L87
        "unwanted running",
        id="eng",
    ),
    pytest.param(  # ref: Bert tokenization_test.py#L91
        "unwantedX running",
        id="eng with unk",
    ),
]


@pytest.fixture
def tokenizer():
    yield BertWordpieceTokenizer(vocab)


@pytest.mark.parametrize("input_str", test_cases)
def test_all(input_str, tokenizer):
    datum = Datum(input_str)
    output, _, _, _, _ = word_piece_pipe.transform(datum)
    expected_output = tokenizer.tokenize(input_str)
    assert expected_output == output
