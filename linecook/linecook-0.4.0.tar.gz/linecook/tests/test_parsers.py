# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

import pytest

from linecook.parsers import create_regex_factory, resolve_match_pattern


class TestCreateRegexFactory:

    def test_no_arguments_gives_basic_regex_compiler(self):
        create_regex = create_regex_factory()
        assert create_regex('hello') == re.compile('hello')

    def test_unknown_regex_type(self):
        with pytest.raises(KeyError):
            create_regex_factory(regex_type='does_not_exist')


class TestResolveSearchPattern:

    def test_plain_string(self):
        assert resolve_match_pattern('text') == re.compile('text')

    def test_create_word_boundary_regex(self):
        assert resolve_match_pattern('w:my-word') == re.compile(r'\bmy-word\b')

    def test_create_exact_regex(self):
        assert resolve_match_pattern('x:hello') == re.compile(r'^hello$')

    def test_regex_input_returned(self):
        regex_pattern = re.compile(r'^hello$')
        assert resolve_match_pattern(regex_pattern) == regex_pattern

    def test_type_prefix_separator_without_type_prefix(self):
        pattern = 'not-a-type:hello'
        assert resolve_match_pattern(pattern) == re.compile(pattern)
