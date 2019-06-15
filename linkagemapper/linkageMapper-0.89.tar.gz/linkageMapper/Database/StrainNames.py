#!/bin/python

import re


def fetchStrainName(genomeDescriptor, organismName=None, Verbose=False):

    strainName = None

    def scoreCandidateStrainName(word):
        Roman = set("IVX")
        if set(word).issubset(Roman):
            return 0

        return sum([w.isupper() + w.isdigit() for w in word]) / len(word)


    # RENAMING CRITERIA 1:
    def renamingCriteria1():
        words = genomeDescriptor.replace(",", "")
        words = words.split(" ")[1:]
        wordWeights = [scoreCandidateStrainName(w) for w in words]
        if Verbose:
            print(wordWeights)
        if sum(wordWeights) > 0:
            return words[wordWeights.index(max(wordWeights))]

    allCriteria = [
        renamingCriteria1
    ]

    # unsafe;
    genomeDescriptor = genomeDescriptor.replace("isolate ", "")

    for renamingCriteria in allCriteria:
        strainName = renamingCriteria()
        if strainName is not None:
            if Verbose:
                print(renamingCriteria.__name__)
            return strainName.replace(" ", "_")

    return None
