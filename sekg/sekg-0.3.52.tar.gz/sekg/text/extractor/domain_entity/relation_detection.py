#!/usr/bin/env python
# -*- coding: utf-8 -*-
import itertools
import re
from enum import Enum, unique


# todo: need refactor, some of the relation name are only for the code, eg. mention in
@unique
class RelationType(Enum):
    IS_A = "is a"
    REPRESENT = "represent"
    SUBCLASS_OF = "subclass of"
    EXTENDED_FROM = "extended from"
    MENTION_IN_COMENT = "mention in comment"
    MENTION_IN_INSIDE_COMENT = "mention in inside comment"
    MENTION_IN_STRING_LITERAL = "mention in string literal"
    MENTION_IN_SHORT_DESCRIPTION = "mention in short description"
    MENTION = "mention"

    HAS_OPERATION = "has operation"
    INSTANCE_OF = "instance of"
    OPERATE = "operate"
    CAN_BE_OPERATED = "can be operated"

    NAME_RELATED_TO = "name related to"


class RelationDetector:
    def __init__(self, nlp):
        self.cache = {}
        self.nlp = nlp
        self.pos_cache = {}

    def expand(self, terms):
        expanded = set()
        addition = set()
        for term in terms:
            tmp = re.sub(r'( and | or )', r' $ ', term)
            parts = tmp.split(" $ ")
            if len(parts) > 1:
                i = 0
                size = len(parts)
                while i < size - 1:
                    p = parts[i].split()
                    n = parts[i + 1].split()
                    if len(p) < len(n):
                        tmp = " ".join(p + n[len(p):])
                        addition.add(tmp)
                        if tmp not in self.cache:
                            self.cache[tmp] = set()
                        self.cache[tmp].add(term)
                        addition.add(parts[i + 1])
                        if parts[i + 1] not in self.cache:
                            self.cache[parts[i + 1]] = set()
                        self.cache[parts[i + 1]].add(term)
                        i += 2
                    else:
                        addition.add(parts[i])
                        if parts[i] not in self.cache:
                            self.cache[parts[i]] = set()
                        self.cache[parts[i]].add(term)
                        i += 1
                        if i == size - 1:
                            addition.add(parts[i])
                            if parts[i] not in self.cache:
                                self.cache[parts[i]] = set()
                            self.cache[parts[i]].add(term)
                expanded.add(term)

            tmp = re.sub(r'( of | \'s )', r' $ ', term)
            parts = tmp.split(" $ ")
            if len(parts) == 2:
                addition.add(parts[0])
                if parts[0] not in self.cache:
                    self.cache[parts[0]] = set()
                self.cache[parts[0]].add(term)
                addition.add(parts[1])
                if parts[1] not in self.cache:
                    self.cache[parts[1]] = set()
                self.cache[parts[1]].add(term)
                expanded.add(term)

        terms.update(addition)
        return expanded

    def detect_relation_by_starfix(self, terms):
        """[summary]

        detect relation by *fix (prefix, infix, suffix)

        Arguments:
            terms {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        expanded = self.expand(terms)
        relations = set()
        for term1, term2 in itertools.combinations(terms - expanded, 2):
            short_term, long_term = (term1.lower(), term2.lower()) if len(term1) <= len(term2) else (
            term2.lower(), term1.lower())

            if long_term.endswith(" " + short_term):
                if long_term in self.pos_cache:
                    long_term_pos = self.pos_cache[long_term]
                else:
                    long_term_pos = tuple([token.pos_ for token in self.nlp(long_term)])
                    self.pos_cache[long_term] = long_term_pos
                if long_term_pos[-1] in {"NOUN", "PROPN"}:
                    relations.add((long_term, RelationType.SUBCLASS_OF.value, short_term))
            elif " {} ".format(short_term) in long_term or long_term.startswith(short_term + " "):
                if long_term in self.pos_cache:
                    long_term_pos = self.pos_cache[long_term]
                else:
                    long_term_pos = tuple([token.pos_ for token in self.nlp(long_term)])
                    self.pos_cache[long_term] = long_term_pos
                if long_term_pos[long_term.split().index(short_term.split()[-1])] in {"NOUN", "PROPN"}:
                    relations.add((long_term, RelationType.EXTENDED_FROM.value, short_term))

        for k, v in self.cache.items():
            for term in v:
                relations.add((term, RelationType.EXTENDED_FROM.value, k))

        relations = set(filter(lambda x: x[0] != x[2], relations))
        return relations


if __name__ == "__main__":
    print(RelationType.IS_A.value)
