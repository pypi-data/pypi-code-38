# encoding: utf-8
# Created by chenghaomou at 2019-05-18
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance as norm_lev
import numpy as np

from elisa_patch.utils import cosine_dist

logger = logging.getLogger("Similarity")

__all__ = ['ExactSimilarity', 'LevSimilarity', 'NGramSimilarity']


class Similarity(ABC):

    def __init__(self, lexicon: dict,
                 romanization: bool = False,
                 romanizer: callable = None,
                 max_edit_dist_ratio: float = 0.2,
                 backup: object = None) -> None:

        super(Similarity, self).__init__()

        self.lexicon = lexicon
        self.max_edit_dist_ratio = max_edit_dist_ratio
        self.backup = backup
        self.memory = {}

        if romanization:
            assert romanizer is not None, "Romanizer not found!"
            self.romanized_lexicon = defaultdict(set)
            keys = list(self.lexicon.keys())
            romanized_keys = romanizer(' ### '.join(keys)).split(' ### ')
            for key, romanized_key in zip(keys, romanized_keys):
                self.romanized_lexicon[romanized_key].update(self.lexicon[key])

    @abstractmethod
    def search(self, token: str, context: str) -> tuple:

        pass


class ExactSimilarity(Similarity):

    def search(self, token: str, context: str) -> tuple:

        if token in self.memory:
            return self.memory[token]

        key = token.lower()
        if key in self.lexicon:
            alternative, translations = key, self.lexicon[key]
            logger.warning(msg=f"exact match: {token} -> {alternative} : {list(translations)}")
        else:
            if self.backup is not None:
                assert getattr(self.backup, 'search', None) is not None, "search function not found in backup"
                alternative, translations = self.backup.search(token, context)
            else:
                alternative, translations = token, {token, }

        self.memory[token] = (alternative, translations)

        return self.memory[token]


class NGramSimilarity(Similarity):

    def __init__(self, model,
                 lexicon: dict,
                 romanization: bool = False,
                 romanizer: callable = None,
                 max_edit_dist_ratio: float = 0.2,
                 backup: object = None):

        super(NGramSimilarity, self).__init__(lexicon,
                                              romanization,
                                              romanizer,
                                              max_edit_dist_ratio,
                                              backup)

        self.model = model
        self.words = list(self.lexicon.keys())
        self.lexicon_vectors = model.transform(self.words).toarray()

    def search(self, token: str, context: str) -> tuple:

        if token in self.memory:
            return self.memory[token]

        query = self.model.transform([token]).toarray()
        distances = cosine_dist(self.lexicon_vectors, query)
        ranking = np.argsort(distances)

        if norm_lev(token, self.words[ranking[0]]) <= self.max_edit_dist_ratio:
            alternative, translations = self.words[ranking[0]], self.lexicon[self.words[ranking[0]]]
            logger.warning(msg=f"n-gram match: {token} -> {alternative} : {list(translations)}")
        else:
            if self.backup is not None:
                alternative, translations = self.backup.search(token, context)
            else:
                alternative, translations = token, {token, }

        self.memory[token] = (alternative, translations)

        return self.memory[token]


class LevSimilarity(Similarity):

    def search(self, token: str, context: str) -> tuple:

        if token in self.memory:
            return self.memory[token]

        ranking = sorted(self.lexicon.keys(), key=lambda x: norm_lev(x, token))
        if norm_lev(ranking[0], token) <= self.max_edit_dist_ratio:
            alternative, translations = ranking[0], self.lexicon[ranking[0]]
            logger.warning(msg=f"levenshtein match: {token} -> {alternative} : {list(translations)}")
        else:
            if self.backup is not None:
                alternative, translations = self.backup.search(token, context)
            else:
                alternative, translations = token, {token, }

        self.memory[token] = (alternative, translations)

        return self.memory[token]

# @lexicon_translation_cache
# def soundex_similarity(token: str,
#                        dictionary: dict = None,
#                        context: str = None,
#                        threshold: float = 0.3,
#                        encoded_english_vocab: dict = None,
#                        romanizer: callable = None,
#                        soundex: callable = None,
#                        backup: callable = None,
#                        ) -> tuple:
#
#     assert encoded_english_vocab is not None
#     assert romanizer is not None
#
#     encoded = soundex(romanizer(token))
#     candidate_vocab = list(filter(lambda x: encoded_english_vocab[x] == encoded, encoded_english_vocab.keys()))
#
#     tree = trie.CharTrie()
#     for v in candidate_vocab:
#         tree[v] = True
#
#     prefixes = Counter()
#     for v in candidate_vocab:
#         for prefix, _ in tree.prefixes(v):
#             prefixes[prefix] += 1
#
#     match = None
#     if prefixes:
#         match = prefixes.most_common(1)[0]
#
#     if match and abs(len(match[0]) - len(romanizer(token))) * 1.0 / len(romanizer(token)) <= threshold:
#         warning.log(level=logging.WARNING, msg=f"soundex match: {token} -> {match[0]} : {[match[0]]}")
#         return match[0], [match[0]]
#     else:
#         return backup(token, dictionary, context) if backup is not None else (token, [token])
