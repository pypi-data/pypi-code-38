import re

import nltk
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords

from sekg.util.code import CodeElementNameUtil
from .base import Preprocessor


class CodeDocPreprocessor(Preprocessor):
    """
    The new way we design for preprocess text containing code element. split camel case and add the camel word back to the text.
    Recommend to use for our KG document.
    """
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

class PureCodePreprocessor(Preprocessor):
    """
    traditional preprocessing way for feature location, split camel word, remove keyword and stop words.
    Todo: Add paper citation.
    """
    stemmer = nltk.PorterStemmer(nltk.PorterStemmer.MARTIN_EXTENSIONS)
    stops = frozenset(nltk.corpus.stopwords.words('english'))
    Java_Keyword = {"abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class", "const",
                    "continue", "default", "do", "double", "else", "enum", "extends", "final", "finally", "float",
                    "for", "goto", "if", "implements", "import", "instanceof", "int", "interface", "long", "native",
                    "new", "package", "private", "protected", "public", "return", "strictfp", "short", "static",
                    "super", "switch", "this", "throw", "throws", "try", "void", "transient", "synchronized",
                    "volatile", "while"}
    remove_list = {"\n", "\t", "\r", "/", "*", ".", ";", "@", "{", "}", "<p>", "(", ")", "#", "=", ":", "+", "-",
                   "!",
                   "[", "]", ",", ":", "<", ">", "|", "\\", "&", "'", "?", "<", ">", "'", "`", "\""}

    def hump_split(self, hunp_str):
        p = re.compile(r'([a-z]|\d)([A-Z])')
        sub = re.sub(p, r'\1_\2', hunp_str).lower()
        if "_" not in sub:
            return [sub]
        sub = sub.split("_")
        return sub

    def stems(self, stops, stemmer, string):
        to_skip = set('()!@#$%^&*-+=|{}[]<>./?;:')
        to_skip.update(self.Java_Keyword)

        numeric_regex = re.compile(r'(^-?\d+\.\d+$)|(^-?\d+$)')

        if string in to_skip:
            raise StopIteration
        for word in nltk.tokenize.word_tokenize(string):
            if word in to_skip:
                continue

            if word in stops or '/' in word:
                continue

            if numeric_regex.match(word) is not None:
                continue

            try:
                yield stemmer.stem(word).lower()
            except Exception:
                continue

    def remove_special_char(self, data):
        """
        input;str
        :return: str
        """
        new_str = data
        for item in self.remove_list:
            new_str = new_str.replace(item, " ").replace("  ", " ")
        return new_str.strip()

    def clean(self, data):
        data = self.remove_special_char(data)
        return_list = []
        for item in data.split(" "):
            return_list = return_list + self.hump_split(item)
        obs = list(self.stems(self.stops, self.stemmer, " ".join(return_list)))
        return obs