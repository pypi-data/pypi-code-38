from unittest import TestCase

from sekg.text.extractor.domain_entity.word_util import WordUtil


class TestWordUtil(TestCase):
    def test_couldBeVerb(self):
        self.fail()

    def test_couldBeNoun(self):
        self.fail()

    def test_couldBeADJ(self):
        test_cases = [
            ("red", True),
            ("file", False),
            ("readable", True),

        ]
        for word, result in test_cases:
            self.assertEqual(result, WordUtil.couldBeADJ(word))
