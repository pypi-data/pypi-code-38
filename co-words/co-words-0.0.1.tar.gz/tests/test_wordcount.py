
from unittest import TestCase, main
import pickle
from cowords.wordcount import *
from cowords.utilities import *


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

        # ----- Create the WordCount object for testing
        cls.wc = WordCount(cls.wc_dict, stop_words=cls.stop_words)

        # ----- Create a WordCount class for each season, for testing
        cls.wc_objects = {}
        for i in make_ordered_list(cls.wc_dict['wc_data']['season']):
            temp_info = filter_wc_dict(cls.wc_dict, column='season', value=i)
            cls.wc_objects[i] = WordCount(temp_info, stop_words=cls.stop_words)

    # ------------------------------------------------------------------------------------------------------------------
    # ----- The Setup tests
    # ------------------------------------------------------------------------------------------------------------------
    def test_wc_objects(self):
        """ Test if wc_objects has the right amount of documents in each wc_object

        Manual Validation
        -----------------
        There are 2 (Fall), 3 (Spring), 3 (Summer), and 2 (Winter) documents.

        """
        cols = self.wc_dict['wc_data'].shape[0]
        counts = []
        for item in self.wc_objects:
            counts.append(self.wc_objects[item].wc_data.shape[0])
        self.assertEqual(sum(counts), cols, 'There are only {} documents.'.format(cols))
        self.assertListEqual(counts, [2, 3, 3, 2])

    # ------------------------------------------------------------------------------------------------------------------
    # ----- The Functionality Tests
    # ------------------------------------------------------------------------------------------------------------------
    def test_words_occurring_with_unigrams(self):
        """ Unigrams: Given a keyword, find counts of other words in the same document as that word

        Manual Validation
        -----------------
        For each test, we identified which chapters the list of words occurred in and counted the values

        Code Validation
        ---------------
        count = 0
        for doc in wc_objects['Fall'].data['text_column']:
            words = doc.split()
            if 'battle' in words:
                count += len([item for item in words if item == 'snowball'])
        print(count)
        34

        count = 0
        for doc in wc.data['text_column']:
            words = doc.split()
            if 'battle' in words:
                count += len([item for item in words if item == 'animals'])
        print(count)
        137

        counts = []
        for doc in wc.data['text_column']:
            words = doc.split()
            if 'battle' in words:
                counts.append(len([item for item in words if item == 'animal']))
        print(len(counts))
        5

        """
        self.assertEqual(self.wc_objects['Fall'].words_occurring_with(['battle'], doc_count=False,
                                                                      return_bigrams=False)['words'][0],
                         ('snowball', 34), 'function did not correctly count the top word')

        self.assertEqual(self.wc.words_occurring_with(['battle'], doc_count=False, return_bigrams=False)['words'][0],
                         ('animals', 137), 'function did not correctly count the top word')

        self.assertEqual(self.wc.words_occurring_with(['battle'], doc_count=True)['words'][0],
                         ('animal farm', 5), 'function did not correctly count the top word')

    def test_words_occurring_with_bigrams(self):
        """ Bigrams: Given a keyword, find counts of other words in the same document as that word

        Manual Validation
        -----------------
        For each test, we identified which chapters the list of words occurred in and counted the values

        Code Validation
        ---------------
        count = 0
        for doc in wc_objects['Fall'].data['text_column']:
            words = doc.split()
            if 'battle' in words:
                count += len([item for item in words if item == 'snowball'])
        print(count)
        34

        """
        self.assertEqual(self.wc.words_occurring_with(['battle'], doc_count=False, return_bigrams=True)['words'][0],
                         ('animal farm', 26), 'function did not correctly count the top word')

        self.assertEqual(self.wc.words_occurring_with(['battle'], return_bigrams=True, doc_count=True)['words'][0],
                         ('animal farm', 5), 'function did not correctly count the top word')

    def test_words_occurring_with_options(self):
        """ Given a keyword(s), find counts of other words in the same document as that word. Test different options

        Manual Validation
        -----------------
        For each test, we identified which chapters the list of words occurred in and counted the values

        """
        self.assertEqual(self.wc.words_occurring_with(['snowball', 'jones'], when_multiple='OR',
                                                      return_bigrams=True, doc_count=False, invert=False)['words'][0],
                         ('animal farm', 49))
        self.assertEqual(self.wc.words_occurring_with(['snowball', 'jones'], when_multiple='AND',
                                                      return_bigrams=True, doc_count=True, invert=False)['words'][0],
                         ('animal farm', 9))
        self.assertEqual(self.wc.words_occurring_with(['snowball', 'jones'], when_multiple='AND',
                                                      return_bigrams=False, doc_count=True, invert=False)['words'][0],
                         ('animal', 9))
        self.assertEqual(self.wc.words_occurring_with(['snowball', 'jones'], when_multiple='AND',
                                                      return_bigrams=False, doc_count=False, invert=False)['words'][0],
                         ('animals', 235))
        self.assertEqual(self.wc.words_occurring_with(['snowball', 'jones', 'frederick'], when_multiple='AND',
                                                      return_bigrams=False, doc_count=False, invert=True)['words'][0],
                         ('comrades', 15))

    def test_top_used_words_unigrams(self):
        """ Test if top_used_words returns the most common word

        Manual Validation
        -----------------
        Text search via sublime return 43 occurrences of snow for chapter 3 and chapter 7

        Code Validation
        ---------------
        counts = []
        for item in wc_objects['Fall'].data['text_column']:
            counts.append(len([word for word in item.split() if word == 'snowball']))
        print(sum(counts))
        43

        text = wc_objects['Fall'].data['text_column'][0].split() + wc_objects['Fall'].data['text_column'][1].split()
        print(len(set(text)))
        1256

        """
        self.assertEqual(self.wc_objects['Fall'].top_words(bigrams=False)[0],
                         ('snowball', 43), 'function did not find the most commonly used word')
        self.assertEqual(len([item for item in self.wc_objects['Fall'].top_words(bigrams=False) if item[1] > 0]),
                         1256, 'function did not find total number of unique words from Fall')

    def test_top_words_bigrams(self):
        """ Test is top_words returns the most common bigram

        Manual Validation
        -----------------
        Manual search through 10 chapters found 43 occurrences of 'animal farm'. 6 additional occurrence were found
        of the form "animal <stop_word> <stop_word> farm", totally 49 occurrences.
        'animal farm' occurred in all 10 chapters

        Code Validation
        ---------------
        counts = []
        for item in wc.data['text_column']:
            words = item.split()
            count = 0
            if 'animal' in item:
                for word in range(len(words) - 1):
                    if words[word] + " " + words[word+1] == 'animal farm':
                        count += 1
                counts.append(count)
        print(sum(counts))
        print(len(counts))
        49
        10
        """
        self.assertEqual(self.wc.top_words(bigrams=True, doc_count=False)[0],
                         ('animal farm', 49), 'function did not find "animal farm" 49 times')
        self.assertEqual(self.wc.top_words(bigrams=True, doc_count=True)[0],
                         ('animal farm', 10), 'function did not find "animal farm" in all 10 documents')

    def test_cooccur_counts(self):
        """ Given two words, how often do they occur?

        Manual Validation
        -----------------
        'animal' and 'farm' occur in all 10 chapters

        'animal farm' and 'battle cowshed' occur in 5 chapters

        'animal farm' and 'battle' occur in 5 chapters

        """
        self.assertEqual(self.wc.co_occur_counts(['animal', 'farm']), (['animal', 'farm'], 10),
                         'function did not correctly count occurrences of keywords')
        self.assertEqual(self.wc.co_occur_counts(['animal farm', 'battle cowshed']),
                         (['animal farm', 'battle cowshed'], 5),
                         'function did not correctly count occurrences of keywords')
        self.assertEqual(self.wc.co_occur_counts(['animal farm', 'battle']), (['animal farm', 'battle'], 5),
                         'function did not correctly count occurrences of keywords')

    def test_find_document_ids(self):
        """ Given a word, return the documents the word is in

        Manual Validation
        -----------------
        For each test we checked the chapters for the word

        """
        self.assertListEqual(self.wc.find_document_ids('battle'), [3, 4, 6, 7, 8],
                             'Document numbers were not found successfully')
        self.assertListEqual(self.wc.find_document_ids('animal farm', invert=True), [],
                             'List should be empty as "animal farm" is in all chapters.')
        self.assertListEqual(self.wc.find_document_ids(['animal farm', 'snowball'], when_multiple='AND'),
                             [1, 2, 3, 4, 5, 6, 7, 8, 9],
                             'All chapters but the first chapter (0) contain both "animal farm" and "snowball".')

    # ------------------------------------------------------------------------------------------------------------------
    # ----- The Support Functionality Tests
    # ------------------------------------------------------------------------------------------------------------------
    def test_word_counts(self):
        """
        # TODO
        """
        self.assertEqual(1, 1)

    def test_find_document_ids_one_word(self):
        """
        # TODO
        """
        self.assertEqual(1, 1)

    def test_filter_wc_dict(self):
        """ SKIP: This is completed with test_wc_objects above
        """
        self.assertEqual(1, 1)

    def test_make_ordered_list(self):
        """ SKIP: This is completed with test_wc_objects above
        """
        self.assertEqual(1, 1)

    # ------------------------------------------------------------------------------------------------------------------
    # ----- The Loop Tests
    # ------------------------------------------------------------------------------------------------------------------
    def test_words_occurring_with_loop(self):
        """ Tests the functionality of the 'words_occurring_with' loop

        Manual Validation
        -----------------
        For each test, we compared the output to the expected output

        """
        df = words_occurring_with_loop(self.wc_objects, {'word_list': ['animal farm']})[0]
        self.assertListEqual(list(df.columns), ['Fall', 'Spring', 'Summer', 'Winter', 'total'])
        self.assertEqual(df.iloc[0].name, 'animal farm')
        self.assertEqual(df.iloc[0].Spring, 3)

    def test_merge_loop_results(self):
        """ SKIP: This is completed with words_occurring_with_loop tests above
        """
        self.assertEqual(1, 1)

    def test_co_occur_count_loop(self):
        df = co_occur_count_loop(self.wc_objects, ['jones', 'pig'])
        self.assertListEqual(list(df.values[0]), [1, 3, 3, 1, 8])

    def test_top_words_loop(self):
        df = top_words_loop(self.wc_objects, {'bigrams': True})
        self.assertEqual(df.iloc[0].total, 49)
        self.assertEqual(df.iloc[0].name, 'animal farm')

    def test_find_document_ids_loop(self):
        df = find_document_ids_loop(self.wc_objects, {'words': ['snowball']})
        self.assertEqual(df.Count.sum(), 9)
        self.assertEqual(df.shape, (4, 2))


if __name__ == '__main__':
    main()
