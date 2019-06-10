import re

from nltk import WordNetLemmatizer
from nltk.corpus import stopwords

from sekg.util.code import CodeElementNameUtil
from .base import Preprocessor


class CodeDocPreprocessor(Preprocessor):
    CLEAN_PATTERN = re.compile(r'[^a-zA-Z_]')
    STOPWORDS = set(stopwords.words('english'))
    code_element_util = CodeElementNameUtil()
    lemmatizer = WordNetLemmatizer()
    lemma_map = {}

    def extract_words_for_query(self, query):
        return set(self.clean(query))

    def lemma(self, word):
        if word in self.lemma_map:
            return self.lemma_map[word]

        lemma = self.lemmatizer.lemmatize(self.lemmatizer.lemmatize(word, "n"), "v")

        if lemma != word:
            self.lemma_map[word] = lemma
        return lemma

    def clean(self, text):
        """
        return a list of token from the text, only remove stopword and lemma the word
        :param text: the text need to preprocess
        :return: list of str
        """

        clean_text = re.sub(self.CLEAN_PATTERN, " ", text)
        old_words_set = set([word.lower() for word in clean_text.split(" ") if word and word not in self.STOPWORDS])
        clean_text = self.code_element_util.uncamelize_from_simple_name(clean_text)
        if not clean_text:
            return []
        new_words = clean_text.lower().split(" ")
        new_words = [self.lemma(word) for word in new_words
                     if word and word not in self.STOPWORDS]

        new_words_set = set(new_words)

        for old_word in old_words_set:
            if old_word not in new_words_set and old_word not in self.lemma_map:
                new_words.append(old_word)

        return new_words
