
from unittest import TestCase, main
import pickle
from string import punctuation
from co_words.utilities import *


class TestData(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.stop_words = create_stop_words(user_defined=['user_defined_words'])

        # ----- Grab Data
        with open('animal_farm_chapters.pickle', 'rb') as handle:
            cls.wc_data = pickle.load(handle)

        # ----- Clean Data
        cls.wc_data['text_column'] = clean_text(cls.wc_data['text_column'], stop_words=cls.stop_words)

        # ----- Create the wc dictionary
        cls.wc_dict = create_wc_dict(cls.wc_data, text_column='text_column', min_df=.0005)

    # ------------------------------------------------------------------------------------------------------------------
    # ----- The Setup tests
    # ------------------------------------------------------------------------------------------------------------------
    def test_stop_words(self):
        """ Stopwords should have words included from NLTK, SKLEARN, and custom added

        """
        self.assertIn('wherever', self.stop_words)              # only from: NLTK
        self.assertIn('mightn', self.stop_words)                # only from: SKLEARN
        self.assertIn('zz', self.stop_words)                    # from from: package specific
        self.assertIn('user_defined_words', self.stop_words)    # only from: User added

    def test_wc_data(self):
        """ clean_text should have removed capitals, punctuation, and digits

        """
        self.assertListEqual([letter for letter in self.wc_data['text_column'][0] if letter.isupper()], [],
                             'list should be empty - there should be no capital letters.')
        self.assertListEqual([letter for letter in self.wc_data['text_column'][0] if letter.isdigit()], [],
                             'list should be empty - there should be no digits.')
        self.assertListEqual([letter for letter in self.wc_data['text_column'][0] if letter in punctuation], [],
                             'list should be empty - there should be no punctuation.')
        self.assertListEqual([item for item in self.wc_data['text_column'][0].split() if item in self.stop_words], [],
                             'list should be empty - there should be no stop words in the string.')

    def test_wc_dict(self):
        """
        # TODO
        """
        self.assertEqual(1, 1)


if __name__ == '__main__':
    main()
