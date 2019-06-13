from unittest import TestCase

from sekg.ir.preprocessor.base import SimplePreprocessor


class TestSimplePreprocessor(TestCase):
    def test_remove_special_char(self):
        test_case_list = [
            (
                "This is a ArrayList, it contains all of the classes for creating user interfaces and for painting graphics and images."

                ,
                "This is a ArrayList it contains all of the classes for creating user interfaces and for painting graphics and images"),

            ("how to get File's MD5 checksum",

             "how to get File s MD5 checksum")

        ]
        preprocessor = SimplePreprocessor()
        for old_str, new_str in test_case_list:
            team = preprocessor.remove_special_char(old_str)
            self.assertEqual(team, new_str)

    def test_clean(self):

        test_case_list = [
            (
                "This is a ArrayList, it contains all of the classes for creating user interfaces and for painting graphics and images."

                ,
                "This is a ArrayList it contains all of the classes for creating user interfaces and for painting graphics and images"),

            ("how to get File's MD5 checksum",

             "how to get File s MD5 checksum")

        ]
        preprocessor = SimplePreprocessor()
        for old_str, new_str in test_case_list:
            self.assertEqual(new_str.lower().split(), preprocessor.clean(old_str))
