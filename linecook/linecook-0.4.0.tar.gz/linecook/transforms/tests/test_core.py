# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from contextlib import contextmanager

import mock
import termcolor

from linecook.transforms import core


class TestDeleteText:

    def test_delete_literal_string(self):
        assert core.delete_text('delete me')('Hi; delete me bye') == 'Hi;  bye'

    def test_delete_regex(self):
        assert core.delete_text(r'\bban\b')('ban banish') == ' banish'

    def test_delete_regex_with_word_prefix(self):
        assert core.delete_text(r'w:ban')('ban banish') == ' banish'

    def test_not_deleted(self):
        assert core.delete_text(r'\bban\b')('banish') == 'banish'


class TestFilterLine:

    def test_remove_line(self):
        assert core.filter_line(r'\bremove\b')('remove this line') is None

    def test_line_not_removed(self):
        assert core.filter_line(r'\bremove\b')('not removed') == 'not removed'

    def test_call_on_match(self):
        on_match = mock.Mock()
        on_mismatch = mock.Mock()
        transform = core.filter_line(r'match', on_match=on_match,
                                     on_mismatch=on_mismatch)

        transform('match this line')
        on_match.assert_called_once_with('match this line')
        on_mismatch.assert_not_called()

    def test_call_on_mismatch(self):
        on_match = mock.Mock()
        on_mismatch = mock.Mock()
        transform = core.filter_line(r'mismatch', on_match=on_match,
                                     on_mismatch=on_mismatch)

        transform('line that does not match')
        on_match.assert_not_called()
        on_mismatch.assert_called_once_with('line that does not match')


class TestSplitOn:

    def test_spilt_on(self):
        assert core.split_on('&')('a=1&b=2') == 'a=1{}b=2'.format(os.linesep)


class TestPartition:

    def test_partition(self):
        match_word = self.create_partition_function(r'[A-z]+')
        match_word('1 match 2')

        self.on_match.assert_called_once_with('match')
        self.on_mismatch.assert_has_calls([mock.call('1 '), mock.call(' 2')])

    def test_partition_exact_match(self):
        match_all = self.create_partition_function(r'\w+')
        match_all('match')

        self.on_match.assert_called_once_with('match')
        self.on_mismatch.assert_not_called()

    def test_partition_with_capture_group(self):
        match_word = self.create_partition_function(r'([A-z]+)')
        match_word('1 match 2')

        self.on_match.assert_called_once_with('match')
        self.on_mismatch.assert_has_calls([mock.call('1 '), mock.call(' 2')])

    def test_partition_with_multiple_capture_groups(self):
        match_word = self.create_partition_function(r'([A-z]+) (\d)')
        match_word('1 match 2')

        self.on_match.assert_called_once_with('match 2')
        self.on_mismatch.assert_called_once_with('1 ')

    def test_partition_output(self):
        match_word = self.create_partition_function(
            '([A-z]+)',
            success_template='yes({})',
            failure_template='no({})',
        )
        assert match_word('1 match 2') == 'no(1 )yes(match)no( 2)'

    def create_partition_function(self, match_pattern,
                                  success_template='{}',
                                  failure_template='{}'):
        self.on_match = create_template_identity_mock(success_template)
        self.on_mismatch = create_template_identity_mock(failure_template)
        return core.partition(match_pattern,
                              on_match=self.on_match,
                              on_mismatch=self.on_mismatch)


class TestColorText:

    def test_color_text(self):
        color_red = core.color_text('match words', color='red')
        assert (color_red('match words in this line') ==
                ascii_red_text('match words') + ' in this line')


class TestCountLines:

    def setup(self):
        self.counter = core.CountLines(count_template='{count}:')

    def test_count(self):
        with mock_colored():
            assert self.counter('first') == '1: first'
            assert self.counter('second') == '2: second'

    def test_reset(self):
        with mock_colored():
            assert self.counter('first') == '1: first'
            self.counter.reset()
            assert self.counter('second') == '1: second'


def ascii_red_text(text):
    return termcolor.colored(text, color='red')


@contextmanager
def mock_colored(module=core):
    with mock.patch.object(module, 'colored') as fake_colored:
        fake_colored.side_effect = colored_text_identity
        yield fake_colored


def colored_text_identity(text, color=None, on_color=None, attrs=None):
    return text


def create_template_identity_mock(template):
    """Return function that returns function input wrapped in template."""
    identity_mock = mock.Mock()
    identity_mock.side_effect = template.format
    return identity_mock
