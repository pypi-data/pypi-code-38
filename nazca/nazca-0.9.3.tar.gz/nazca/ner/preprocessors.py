# -*- coding: utf-8 -*-
""" Preprocessors for Named Entities Recognition.
"""
from nazca.utils.tokenizer import Token
from nazca.data.stopwords import FRENCH_STOPWORDS, ENGLISH_STOPWORDS

STOPWORDS = {'fr': FRENCH_STOPWORDS,
             'en': ENGLISH_STOPWORDS}


###############################################################################
# NER PREPROCESSORS ###########################################################
###############################################################################
class AbstractNerPreprocessor(object):
    """ Preprocessor
    """

    def __call__(self, token):
        raise NotImplementedError


class NerWordSizeFilterPreprocessor(AbstractNerPreprocessor):
    """ Remove token based on the size of the word
    """

    def __init__(self, min_size=None, max_size=None):
        self.min_size = min_size
        self.max_size = max_size

    def __call__(self, token):
        if ((self.min_size and len(token.word) < self.min_size)
                or (self.max_size and len(token.word) > self.max_size)):
            return None
        return token


class NerLowerCaseFilterPreprocessor(AbstractNerPreprocessor):
    """ Remove token with word in lower case
    """

    def __call__(self, token):
        return None if token.word.islower() else token


class NerLowerFirstWordPreprocessor(AbstractNerPreprocessor):
    """ Lower the first word of each sentence if it is a stopword.
    """

    def __init__(self, lang='en'):
        self.lang = lang

    def __call__(self, token):
        if (token.start == token.sentence.start and
                token.word.split()[0].lower() in STOPWORDS.get(self.lang, ENGLISH_STOPWORDS)):
            word = token.word[0].lower() + token.word[1:]
            return Token(word, token.start, token.end, token.sentence)
        return token


class NerStopwordsFilterPreprocessor(AbstractNerPreprocessor):
    """ Remove stopwords
    """

    def __init__(self, split_words=False, lang='en'):
        self.split_words = split_words
        self.lang = lang

    def __call__(self, token):
        stopwords = STOPWORDS.get(self.lang, ENGLISH_STOPWORDS)
        if self.split_words and not [
                w for w in token.word.split() if w.lower() not in stopwords]:
            return None
        if not self.split_words and token.word.lower() in stopwords:
            return None
        return token


class NerHashTagPreprocessor(AbstractNerPreprocessor):
    """ Cleanup hashtag
    """

    def __call__(self, token):
        if token.word.startswith('@'):
            # XXX Split capitalize letter ?
            # @BarackObama -> Barack Obama
            word = token.word[1:].replace('_', ' ')
            return Token(word, token.start, token.end, token.sentence)
        return token
