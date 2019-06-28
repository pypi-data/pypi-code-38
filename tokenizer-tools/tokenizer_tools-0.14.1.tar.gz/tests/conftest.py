# -*- coding: utf-8 -*-

pytest_plugins = ['helpers_namespace']

import pytest


@pytest.helpers.register
def assert_sequence_equals(test_value, gold_value):
    assert len(test_value) == len(gold_value)

    element_result = [test_value[i] == gold_value[i] for i in range(len(gold_value))]
    assert all(element_result)


@pytest.helpers.register
def tokenizer_test_cases():
    test_cases = [
        '.',
        '人',
        '人们',
        '盖浇饭'
    ]

    # return as list of list
    return test_cases
