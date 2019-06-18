from unittest import TestCase

from stackifyapm.instrumentation.packages.dbapi2 import Literal, extract_signature, scan, skip_to, tokenize


class DBAPI2InstrumentationTest(TestCase):

    def test_scan_simple(self):
        sql = "Stackify Python APM"
        expected = ['Stackify', 'Python', 'APM']

        tokens = tokenize(sql)
        actual = [t[1] for t in scan(tokens)]

        assert actual == expected

    def test_scan_complex(self):
        sql = "Stackify 'Python' APM"
        expected = ['Stackify', Literal("'", "Python"), 'APM']

        tokens = tokenize(sql)
        actual = [t[1] for t in scan(tokens)]

        assert actual == expected

    def test_extract_signature_string(self):
        sql = "Stackify Python APM"
        expected = "STACKIFY"

        actual = extract_signature(sql)

        assert actual == expected


class LiteralTest(TestCase):
    def test_literal_repr(self):
        literal = Literal('', 'Hi there')

        assert literal.__repr__() == '<Literal Hi there>'


class SkipToTest(TestCase):
    def test_with_empty_value_sequence(self):
        start = 0
        tokens = "Hello $ there!"
        value_sequence = ''

        res = skip_to(start, tokens, value_sequence)

        assert res == ''

    def test_skip_to(self):
        start = 0
        tokens = "Hello $ there!"
        value_sequence = '$'

        res = skip_to(start, tokens, value_sequence)

        assert res == 'Hello $'

    def test_empty_token(self):
        start = 0
        tokens = ""
        value_sequence = '$'

        res = skip_to(start, tokens, value_sequence)

        assert res is None
