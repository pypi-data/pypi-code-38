from unittest import TestCase
from ievv_opensource.ievvtasks_common import cli


class TestUnknownArgsParser(TestCase):
    def test_nothing_to_fix(self):
        self.assertEqual(
            ['a', '--test1=10', '--test2', 'c'],
            cli.UnknownArgsParser(['a', '--test1=10', '--test2', 'c']).resultlist()
        )

    def test_handle_equals_multiword_long_option(self):
        self.assertEqual(
            ["--test='Hello Cruel World'"],
            cli.UnknownArgsParser(['--test=Hello Cruel World']).resultlist()
        )

    def test_handle_equals_multiword_short_option(self):
        self.assertEqual(
            ["-t='Hello Cruel World'"],
            cli.UnknownArgsParser(['-t=Hello Cruel World']).resultlist()
        )

    def test_handle_equals_multiword_no_option(self):
        self.assertEqual(
            ["'Hello Cruel World'"],
            cli.UnknownArgsParser(['Hello Cruel World']).resultlist()
        )

    def test_resultlist(self):
        self.assertEqual(
            [
                "simple",
                "'Hello Cruel World'",
                "--test='A Test'",
                "-t='Another Test'",
                "--othertest", "'Other Test'"
            ],
            cli.UnknownArgsParser([
                'simple',
                'Hello Cruel World',
                '--test=A Test',
                '-t=Another Test',
                '--othertest', 'Other Test',
            ]).resultlist()
        )

    def test_resultstring(self):
        self.assertEqual(
            "simple 'Hello Cruel World' --test='A Test' "
            "-t='Another Test' --othertest 'Other Test'",
            cli.UnknownArgsParser([
                'simple',
                'Hello Cruel World',
                '--test=A Test',
                '-t=Another Test',
                '--othertest', 'Other Test',
            ]).resultstring()
        )
