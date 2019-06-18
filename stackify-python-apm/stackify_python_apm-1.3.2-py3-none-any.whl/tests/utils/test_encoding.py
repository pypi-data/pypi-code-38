from unittest import TestCase

from stackifyapm.utils.encoding import keyword_field


class KeywordFieldTest(TestCase):

    def test_should_return_value_given_if_not_string(self):
        value = 1

        new_value = keyword_field(value)

        assert new_value == value

    def test_should_return_value_given_if_length_doesnt_exceed_1024(self):
        value = 'S' * 1024

        new_value = keyword_field(value)

        assert new_value == value

    def test_should_return_truncated_value_if_length_exceeds_1024(self):
        value = 'S' * 1025

        new_value = keyword_field(value)

        assert not new_value == value
        assert len(new_value) == 1024
