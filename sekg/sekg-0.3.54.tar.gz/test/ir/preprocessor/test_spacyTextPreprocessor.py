from unittest import TestCase

from sekg.ir.preprocessor.spacy import SpacyTextPreprocessor


class TestSpacyTextPreprocessor(TestCase):
    def test_extract_words_for_query(self):
        preprocessor = SpacyTextPreprocessor()
        test_case_list = [
            (
                "This is a ArrayList, it contains all of the classes for creating user interfaces and for painting graphics and images."
                , ['ArrayList',
                   'class',
                   'user',
                   'interface',
                   'painting',
                   'graphic',
                   'image',
                   'contain',
                   'create']
            ),

            (
                "how to get File's MD5 checksum",
                ['File', 'md5', 'checksum']

            )

        ]

        for old_str, new_str in test_case_list:
            team = preprocessor.extract_words_for_query(old_str)
            self.assertEqual(team, new_str)

    def test_clean(self):

        test_case_list = [
            (
                "This is a ArrayList, it contains all of the classes for creating user interfaces and for painting graphics and images."
                ,
                ['arraylist',
                 'contain',
                 'class',
                 'create',
                 'user',
                 'interface',
                 'painting',
                 'graphic',
                 'image']
            ),

            ("how to get File's MD5 checksum",
             ["file", "md5", "checksum"])
        ]
        preprocessor = SpacyTextPreprocessor()

        for old_str, keywords in test_case_list:
            self.assertEqual(keywords, preprocessor.clean(old_str))
