# -*- coding: utf-8 -*-

import yaml


class Translator():

    def __init__(self, dict_path):
        try:
            dictFile = open(dict_path, mode="r", encoding="utf-8")
        except IOError as e:
            print("There was an error reading the dictionary file: {}".format(e))
            return
        self.dictionary = {}
        self.lookup = {}    # inverted dictionary
        self.conseq = {}    # list of words after which other words can appear
        self.alternativeWords = []
        self.__parseDict(yaml.full_load(dictFile))

    def __parseDict(self, d):
        if "listMode" in d:
            self.listMode = d["listMode"]
        else:
            self.listMode = "hmps"
        dictionary = d["dictionary"]

        for (word, alts) in dictionary.items():
            alternatives, hmps, syms = [], [], []
            if isinstance(alts, dict):
                keys = list(alts.keys())
                if "hmps" in keys:
                    hmps = alts["hmps"]
                    keys.remove("hmps")
                if "syms" in keys:
                    syms = alts["syms"]
                    keys.remove("syms")

                # prevent from misspelling hmps or syms
                if len(keys) > 0:
                    raise Exception("Warning, unknown word variation(s) in the dictionary: {}".format(str(keys)))
            elif isinstance(alts, list):
                if self.listMode == "hmps":
                    hmps = alts
                elif self.listMode == "syms":
                    syms = alts
            else:
                raise Exception("Error: unsupported form ({}) in which alternatives to the word {} have been presented.".format(type(alts), word))

            alternatives = hmps + syms

            if word not in self.dictionary:
                self.dictionary[word] = {}
                self.dictionary[word]["hmps"] = hmps
                self.dictionary[word]["syms"] = syms
                self.dictionary[word]["alts"] = alternatives
            else:
                self.dictionary[word]["hmps"] += hmps
                self.dictionary[word]["syms"] += syms
                self.dictionary[word]["alts"] += alternatives

            for alt in alternatives:
                if " " in alt:
                    altsplit = alt.split(" ")
                    self.__addConsecutiveAlts(altsplit, self.conseq)
                if alt in self.lookup:
                    raise Exception("Error: ambiguous alternative. The word {} was provided as an alternative to {} but it was already assigned as an alternative to {}!".format(alt, word, self.lookup[alt]))
                self.lookup[alt] = word

            self.alternativeWords += self.lookup.keys()

    def __addConsecutiveAlts(self, altRemainder, conseq):
        """ Recursion warning - this function is awful and attempt to understand it requires high amounts of caffeine and carbohydrates
        But essentially, it just traverses a nested dictionary and tries to put words in the right place to create
        chains of words that will be used when parsing phrases in the sentences.
        """
        alt = altRemainder[0]
        nextAlt = altRemainder[1]
        lastPair = len(altRemainder) == 2
        if alt in conseq:
            wcsq = conseq[alt]
            if isinstance(wcsq, str):
                if wcsq == nextAlt:
                    if lastPair:
                        pass  # this should not happen as it means the same phrase was added twice
                    else:
                        conseq[alt] = {wcsq: {".": None}}
                else:
                    if lastPair:
                        conseq[alt] = {wcsq: ".", nextAlt: "."}
                    else:
                        conseq[alt] = {wcsq: ".", nextAlt: {}}
            else:  # wcsq is a dictionary
                if lastPair:
                    if nextAlt in wcsq:
                        if isinstance(wcsq[nextAlt], str):
                            wcsq[nextAlt] = {wcsq[nextAlt]: ".", ".": None}
                        else:
                            wcsq[nextAlt]["."] = None
                    else:
                        wcsq[nextAlt] = "."
        else:  # alt is not in conseq
            if lastPair:
                conseq[alt] = nextAlt
            else:
                conseq[alt] = {}

        if not lastPair:
            self.__addConsecutiveAlts(altRemainder[1:], conseq[alt])

    def __checkConsecutiveWords(self, sentRemainder, conseq):
        """ Recursion warning - this function is awful and attempt to understand it requires high amounts of caffeine and carbohydrates
        But all it does is it tries to traverse the nested dictionary created by the "__addConsecutiveAlts" function
        to properly parse the sentence and attempt to find predefined phrases.
        """
        w = sentRemainder[0]
        if conseq is None or not sentRemainder:
            return []  # if there are no words remaining in the sentence - this should only happen in case of error
        elif isinstance(conseq, str):
            if w == conseq:
                return [conseq]  # if the consecutives is just a single word, then return that word and end
            elif '.' == conseq:
                return True  # current word is not in consequtives but the previous word can be terminal
            else:

                return []
        else:  # else, there are some consecutives to be processed
            followers = []  # words following this word in the phrase
            if w in conseq:
                if len(sentRemainder) > 1:
                    followers = self.__checkConsecutiveWords(sentRemainder[1:], conseq[w])
                elif '.' in conseq[w]:  # dot in the consecutives dictionary means this word can be terminal
                    return [w]  # valid last word in the phrase (not necessarily in the sentence)
                else:
                    return []
            elif '.' in conseq:
                return True  # current word is not in consequtives but the previous word can be terminal
            else:
                return []

            if not followers:
                return []
            elif isinstance(followers, list):
                return [w] + followers
            else:
                return [w]  # the word has no followers in the sentence but was recognized as a valid terminal word

    def translate(self, words):
        """ words - a single word or a list of words
            returns a list of translated words
        """
        if isinstance(words, str) and " " in words:
            return self.translate(words.split(" "))
        elif isinstance(words, list):
            sentence = []
            n = len(words)
            i = 0
            while i < n:
                w = words[i]
                if w in self.conseq and i < n - 1:  # checks for alternative multiwords phrases (instead of a single word)
                    phrase = self.__checkConsecutiveWords(words[i+1:], self.conseq[w])
                    if len(phrase) > 0:  # length check to prevent boolean True from sneaking in, which should only happen in case of an error
                        phrase = [w] + phrase
                        i += len(phrase) - 1
                        w = ' '.join(phrase)
                        sentence.append(self.lookup[w])
                else:
                    sentence.append(self.translate(w))
                i += 1
            return sentence
        else:
            if words in self.alternativeWords:
                return self.lookup[words]
            else:
                return words
