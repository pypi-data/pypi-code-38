import os
import six
import tempfile

import pytest

from .tokenization import FullTokenizer as BertFullTokenizer
from ..full import full_pipe, vocab_tokens
from uttut.elements import Datum


test_cases = [
    pytest.param(  # ref: Bert tokenization_test.py#L45
        u"UNwant\u00E9d,running",
        id='eng + accent',
    ),
]


@pytest.fixture
def tokenizer():
    with tempfile.NamedTemporaryFile(delete=False) as vocab_writer:
        if six.PY2:
            vocab_writer.write("".join([x + "\n" for x in vocab_tokens]))
        else:
            vocab_writer.write("".join(
                [x + "\n" for x in vocab_tokens]).encode("utf-8"))

        vocab_file = vocab_writer.name

    tokenizer = BertFullTokenizer(vocab_file)
    yield tokenizer
    os.unlink(vocab_file)


@pytest.mark.parametrize("input_str", test_cases)
def test_all(input_str, tokenizer):
    datum = Datum(input_str)
    output, _, _, _, _ = full_pipe.transform(datum)
    expected_output = tokenizer.tokenize(input_str)
    assert expected_output == output
