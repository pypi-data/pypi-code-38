import pytest
from mock import Mock

from promium.base import Element
from promium.assertions import BaseSoftAssertion


FALSE_PARAMS = [False, 0, '', [], {}, ()]
TRUE_PARAMS = [True, 1, 'sada', [1], {'k': 'test'}, (1, 2)]
EQUALS_PARAMS = [
    (1, 1), (0, 0), ('t', 't'), ('u', u'u'),
    (False, False), (True, 1), (False, 0),
]
EQUALS_PARAMS_EXTENDED = EQUALS_PARAMS + [
    ([1, 's', []], [1, 's', []]),
    ({'k': 1}, {'k': 1})
]
NOT_EQUALS_PARAMS = [
    (1, 0), (0, 'www'), ('t', 'test'), ('u', u'unicode'), (False, True),
    ([1, 's', []], [1, 's', ['test']]), ({'k': []}, {'k': 1})
]
CONTAIN_PARAMS = [
    (1, [1]), (2, {1, 2}), (12, (6, 12)), (156, list(range(120, 1000))),
    ('str', ['str']), ('str', [u'str']), ('str', {'str'}),
    ('str', ('str',)), ('str', {'str': 1, 'key': 2}),
    ('string', 'test string'), ('string', u'test string'), ('str', 'teststr')
]
NOT_CONTAIN_PARAMS = [
    (1, [0]), (2, {1, 6}), (12, (6, 1)), (156, list(range(120))),
    ('str1', ['str']), ('string', [u'str1']), ('str', {'str1'}),
    ('str', ('tuple',)), ('str', {'str_key': 1, 'key': 2}),
    ('string', 'test '), ('string', u'test')
]
LESS_PARAMS = [(0, 1), ('sss', 'ssss'), (False, True)]
GREATER_PARAMS = [(1, 0), ('sss', 's'), (True, False)]
NOT_LESS_EQUALS_PARAMS = GREATER_PARAMS + [
    ('test', 't'), (u'unicode', 'u'), (True, False)
]
NOT_GREATER_EQUALS_PARAMS = LESS_PARAMS + [
    (0, 1), ('t', 'test'), ('u', u'unicode'), (False, True)
]
INSTANCE_PARAMS = [
    ('', str), (1, int), ([], list), ({'k': False}, dict), ((1, 2), tuple),
    ([1], list), (True, bool), ('1', str), ('666', (int, str))
]
NOT_INSTANCE_PARAMS = [
    (1, str), ('1', int), (1, bool), (0, bool), ({'k': 1}, str),
    ({'k': 1}, int), ([], (set, tuple))
]
SPACES_PARAMS = [
    ('s ', 's'), ('\n\t \r', ''), ('\v|\f |\n', '| |'), (' |    |   ', '| |')
]


class MockElement(object):

    def __init__(self, some_dict):
        self.some_dict = some_dict

    def get_attribute(self, name):
        return self.some_dict.get(name)


@pytest.mark.unit
@pytest.mark.parametrize('expr', TRUE_PARAMS)
def test_soft_assert_true_valid_data(expr):
    soft = BaseSoftAssertion()
    soft.soft_assert_true(expr)
    assert not soft.assertion_errors


@pytest.mark.unit
@pytest.mark.parametrize('expr', FALSE_PARAMS)
def test_soft_assert_true_not_valid_data(expr):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_true(expr)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
@pytest.mark.parametrize('expr', FALSE_PARAMS)
def test_soft_assert_false_valid_data(expr):
    soft = BaseSoftAssertion()
    soft.soft_assert_false(expr)
    assert not soft.assertion_errors


@pytest.mark.unit
@pytest.mark.parametrize('expr', TRUE_PARAMS)
def test_soft_assert_false_not_valid_data(expr):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_false(expr)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', EQUALS_PARAMS_EXTENDED)
def test_soft_assert_equals_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.soft_assert_equals(cur, exp)
    assert not soft.assertion_errors


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', NOT_EQUALS_PARAMS)
def test_soft_assert_equals_not_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_equals(cur, exp)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', NOT_EQUALS_PARAMS)
def test_soft_assert_not_equals_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.soft_assert_not_equals(cur, exp)
    assert not soft.assertion_errors


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', EQUALS_PARAMS_EXTENDED)
def test_soft_assert_not_equals_not_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_not_equals(cur, exp)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', CONTAIN_PARAMS)
def test_soft_assert_in_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.soft_assert_in(cur, exp)
    assert not soft.assertion_errors


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', NOT_CONTAIN_PARAMS)
def test_soft_assert_in_not_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_in(cur, exp)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', NOT_CONTAIN_PARAMS)
def test_soft_assert_not_in_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.soft_assert_not_in(cur, exp)
    assert not soft.assertion_errors


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', CONTAIN_PARAMS)
def test_soft_assert_not_in_not_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_not_in(cur, exp)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', LESS_PARAMS + EQUALS_PARAMS)
def test_soft_assert_less_equal_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.soft_assert_less_equal(cur, exp)
    assert not soft.assertion_errors


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', NOT_LESS_EQUALS_PARAMS)
def test_soft_assert_less_equal_not_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_less_equal(cur, exp)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', LESS_PARAMS)
def test_soft_assert_less_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.soft_assert_less(cur, exp)
    assert not soft.assertion_errors


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', GREATER_PARAMS)
def test_soft_assert_less_not_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_less(cur, exp)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', GREATER_PARAMS + EQUALS_PARAMS)
def test_soft_assert_greater_equal_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.soft_assert_greater_equal(cur, exp)
    assert not soft.assertion_errors


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', NOT_GREATER_EQUALS_PARAMS)
def test_soft_assert_greater_equal_not_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_greater_equal(cur, exp)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', GREATER_PARAMS)
def test_soft_assert_greater_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.soft_assert_greater(cur, exp)
    assert not soft.assertion_errors


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', LESS_PARAMS)
def test_soft_assert_greater_not_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_greater(cur, exp)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
def test_soft_assert_regexp_matches_valid_data():
    soft = BaseSoftAssertion()
    soft.soft_assert_regexp_matches('test text #43', r'\w{2}')
    assert not soft.assertion_errors


@pytest.mark.unit
def test_soft_assert_regexp_matches_not_valid_data():
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_regexp_matches('test text #43', r'\w{3:5}')
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
def test_soft_assert_disable_valid_data():
    element = Mock(Element, **{'get_attribute.return_value': True})
    soft = BaseSoftAssertion()
    soft.soft_assert_disable(element)
    assert not soft.assertion_errors


@pytest.mark.unit
def test_soft_assert_disable_not_valid_data():
    element = Mock(Element, **{'get_attribute.return_value': False})
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_disable(element)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
def test_soft_assert_is_none_valid_data():
    soft = BaseSoftAssertion()
    soft.soft_assert_is_none(None)
    assert not soft.assertion_errors


@pytest.mark.unit
@pytest.mark.parametrize('param', ['none', 0, False, 1, '', [], {}])
def test_soft_assert_is_none_not_valid_data(param):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_is_none(param)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
@pytest.mark.parametrize('param', ['none', 0, False, 1, '', [], {}])
def test_soft_assert_is_not_none_valid_data(param):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_is_not_none(param)
    assert not soft.assertion_errors


@pytest.mark.unit
def test_soft_assert_is_not_none_not_valid_data():
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_is_not_none(None)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', INSTANCE_PARAMS)
def test_soft_assert_is_instance_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_is_instance(cur, exp)
    assert not soft.assertion_errors


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', NOT_INSTANCE_PARAMS)
def test_soft_assert_is_instance_not_valid_data(cur, exp):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_is_instance(cur, exp)
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
@pytest.mark.parametrize('cur, exp', SPACES_PARAMS)
def test_soft_assert_equals_text_with_ignore_spaces_and_register(cur, exp):
    soft = BaseSoftAssertion()
    soft.assertion_errors = []
    soft.soft_assert_equals_text_with_ignore_spaces_and_register(cur, exp)
    assert not soft.assertion_errors


@pytest.mark.unit
def test_soft_assert_schemas_valid_data():
    soft = BaseSoftAssertion()
    soft.soft_assert_schemas(
        current={'key': 1, 'key2': [1, 2, 3], 'key3': '3'},
        expected={'key': int, 'key2': [int], 'key3': str}
    )
    assert not soft.assertion_errors


@pytest.mark.unit
def test_soft_assert_schemas_not_valid_data():
    soft = BaseSoftAssertion()
    soft.soft_assert_schemas(
        current={'key': 1, 'key2': [1, None, 3], 'key3': None},
        expected={'key': str, 'key2': [int], 'key3': dict}
    )
    assert soft.assertion_errors
    assert len(soft.assertion_errors) == 1


@pytest.mark.unit
@pytest.mark.skip("Not implemented")
def test_assert_keys_and_instances_valid_data():
    soft = BaseSoftAssertion()
    soft.assert_keys_and_instances(
        actual_dict={'key': 1, 'key2': [1, None, 3], 'key3': None},
        expected_dict={'key': str, 'key2': list, 'key3': dict}
    )
    assert soft.assertion_errors


@pytest.mark.unit
@pytest.mark.skip("Not implemented")
def test_assert_keys_and_instances_not_valid_data():
    soft = BaseSoftAssertion()
    soft.assert_keys_and_instances(
        actual_dict={'key': 1, 'key2': [1, None, 3], 'key3': None},
        expected_dict={'key': int, 'key2': list, 'key3': str}
    )
    assert soft.assertion_errors
