import pytest

from .tokenization import BasicTokenizer as BertBasicTokenizer
from ..basic import basic_pipe

from uttut.elements import Datum


test_cases = [
    pytest.param(
        "我想要喝珍奶",
        id='zh',
    ),
    pytest.param(  # ref: Bert tokenization_test.py#L62
        " \tHeLLo!how  \n Are yoU?  ",
        id='eng',
    ),
    pytest.param(  # ref: Bert tokenization_test.py#L64
        u"H\u00E9llo",
        id='eng + unicode',
    ),
    pytest.param(
        u"ah\u535A\u63A8zz",
        id="eng + zh",  # ref: Bert tokenization_test.py#L55
    ),
]


@pytest.fixture
def tokenizer():
    yield BertBasicTokenizer()


@pytest.mark.parametrize("input_str", test_cases)
def test_all(input_str, tokenizer):
    datum = Datum(input_str)
    output, _, _, _, _ = basic_pipe.transform(datum)
    expected_output = tokenizer.tokenize(input_str)
    assert expected_output == output
