"""
N-Gram algorithm is a text generation unsupervised machine learning algorithm. As an input it takes N previous words
and gives the next "Most Likely" word(s).
"""

from __future__ import print_function

from collections import defaultdict
from aitools.utils import util, constant

import random
import operator


class NGram:

    """
        NGram takes training requires a data frame that is a string, technically lots of paragraphs, ideal texts
        from five-six books.
        As an input it takes a string.
        As an output it gives to five most occurring words with there frequency.

        ** word length of input string should be more then or equal to N.
    """

    def __init__(self, data_frame, n, regex=constant.REGEX_ALL_SPECIAL_ALPHA_NUMERIC):

        """
        :param data_frame: plain text
        :param n: number of grams N
        :param regex: regular expression for text tokenizing (wil be used through out the class)
        """

        self.data_frame = util.tokenizer(regex, data_frame)
        self.n = n
        self.regex = regex
        self.grams = None
        self.starts = None

    def build(self):

        """
        Use for building/training the N Gram

        :return: stores grams corpus and start corpus in class variables
        """

        self.grams, self.starts = n_grams(self.data_frame, self.n)

    def predict(self, words):

        """
        Use for testing/predicting the N Gram

        :param words: words can be a text or int.
        :return: if words is int it uses the N Gram paragraph generation and if text it will use the N Gram next
            words Prediction.
        """

        if isinstance(words, int):
            return generate_text_using_n_gram(self.grams, self.starts, words)
        else:
            words = tuple(util.tokenizer(self.regex, words))[-self.n:]
            probables = self.grams[words]
            return gram_probabilities(probables)


def n_grams(data, n):
    """
        Used for creating N Gram text and start corpus.
    """
    n_gram = zip(*generate_n_gram_array(data, n))
    n_gram_transitions = defaultdict(list)
    starts = []
    index_nex, index_zero, index_one = -1, 0, 1
    n_gram_tuple = None
    for ns in n_gram:

        if ns[index_zero] == '.':
            starts.append(ns[index_one:])

        n_gram_transitions[(ns[:index_nex])].append(ns[index_nex])

    return n_gram_transitions, starts


def generate_n_gram_array(data, n):
    """
        Used for creating dynamic array of arrays.
    """
    return [data[ran:] for ran in range(n + 1)]


def generate_text_using_n_gram(transitions, starts, words):

    """
        Used for generating the text.
    """

    current = random.choice(starts)
    index_nex, index_zero = -1, 0
    result = []

    while len(result) < words:
        #try:
        next_word_candidate = transitions[(current[:])]
        next_word = random.choice(next_word_candidate)
        result.append((current[index_zero]))
        current = get_new_current(index_zero, next_word, list(current))
        #except IndexError:
        #    print_function("Index Error... Closing the loop with current Info.")
        #finally:
        #    return ' '.join(result)

    return ' '.join(result)


def get_new_current(index, word, current):
    """
        Used for fetching new current value/tuple of strings.
    """
    current.pop(index)
    current.append(word)
    return tuple(current)


def gram_probabilities(probables):
    """
        Used for generating and returning top five text frequencies.
    """
    prob = {}

    for x in set(probables):
        prob[x] = probables.count(x)

    return sorted(prob.items(), key=operator.itemgetter(1), reverse=True)[:5]


def grams_probabilities(probables):
    """
        UNDER DEVELOPMENT FOR V2
    """
    prob = defaultdict(list)

    for x in set(probables):
        prob[x] = probables.count(x)

    return sorted(prob.items(), reverse=True)[:5]
