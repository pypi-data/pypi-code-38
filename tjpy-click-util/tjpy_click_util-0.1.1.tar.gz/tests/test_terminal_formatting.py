from pytest import fixture
from pytest_mock import MockFixture

import tjpy_click_util.terminal_formatting \
    as mut

mut_name = mut.__name__


@fixture
def _mocked_get_terminal_size(mocker: MockFixture):
    return mocker.patch(mut_name + '.get_terminal_size', lambda: (4 + 4, 1))


def test_basic(_mocked_get_terminal_size):
    filled_text = mut.fill_terminal_columns_on_both_sides_of_text("text", "=", )
    assert filled_text == "==text=="


def test_text_is_too_long_for_filling(_mocked_get_terminal_size):
    filled_text = mut.fill_terminal_columns_on_both_sides_of_text("textiswaytoolong", "=")
    assert filled_text == "textiswaytoolong"


def test_minimum_filling__effective(_mocked_get_terminal_size):
    filled_text = mut.fill_terminal_columns_on_both_sides_of_text("text", "=", minimum_filling_per_side=3)
    assert filled_text == "===text==="


def test_minimum_filling__not_effective(_mocked_get_terminal_size):
    filled_text = mut.fill_terminal_columns_on_both_sides_of_text("text", "=", minimum_filling_per_side=1)
    assert filled_text == "==text=="


def test_minimum_filling__not_effective_because_text_too_long(_mocked_get_terminal_size):
    filled_text = mut.fill_terminal_columns_on_both_sides_of_text("textiswaytoolong", "=",
                                                                  minimum_filling_per_side=1)
    assert filled_text == "textiswaytoolong"
