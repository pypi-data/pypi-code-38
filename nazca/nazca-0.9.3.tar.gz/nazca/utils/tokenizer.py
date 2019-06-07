# -*- coding: utf-8 -*-
""" Tokenizer for sentences/words segmentation.
"""
import collections
import re

try:
    from nltk.tokenize.punkt import PunktSentenceTokenizer
except ImportError:
    NLTK_AVAILABLE = False
else:
    NLTK_AVAILABLE = True

Token = collections.namedtuple('Token', ['word', 'start', 'end', 'sentence'])
Sentence = collections.namedtuple('Sentence', ['indice', 'start', 'end'])


class RichStringTokenizer(object):
    """Tokenizer for Yams' RichString content.

    The tokenizer uses a variable-length sliding window, i.e. a sliding
    window yielding tokens of N words.
    """

    def __init__(self, text, token_min_size=1, token_max_size=3):
        """
        :token_min_size: minimum number of words required to be a valid token
        :token_max_size: minimum number of words required to be a valid token
        """
        self.text = text
        self.token_min_size = token_min_size
        self.token_max_size = token_max_size

    words_re = r'[\w@-]+'

    def iter_tokens(self, text):
        """ Iterate tokens over a text
        """
        # Compute sentences
        sentences = self.find_sentences(text)
        # Compute words
        words = [m for m in re.finditer(self.words_re, text, re.UNICODE)]
        indice = 0
        while indice < len(words):
            # Choose the current sentence of the first word
            current_sentence = [
                s for s in sentences if s.start <= words[indice].start()][-1]
            # Sliding windows over the different words for each sentence
            remaining = len(words) - indice
            for length in range(
                    min(self.token_max_size, remaining), self.token_min_size - 1, -1):
                _words = words[indice:indice + length]
                if _words[-1].start() > current_sentence.end:
                    # The last word in not in the same sentence anymore, split
                    continue
                normalized_word = ' '.join([w.group() for w in _words]).strip()
                yield Token(normalized_word, _words[0].start(), _words[-1].end(), current_sentence)
            indice += 1

    @staticmethod
    def find_sentences(text):
        """ Find the sentences
        """
        if not NLTK_AVAILABLE:
            raise RuntimeError("find_sentences requires NLTK to be installed")
        sentences = PunktSentenceTokenizer().span_tokenize(text)
        return [Sentence(ind, start, end)
                for ind, (start, end) in enumerate(sentences)]

    def load_text(self, text):
        """ Load the text to be tokenized
        """
        self.text = text

    def __iter__(self):
        """ Iterator over the text given in the object instantiation
        """
        for t in self.iter_tokens(self.text):
            yield t
