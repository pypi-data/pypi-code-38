#!/bin/python

import numpy as np


def evaluateSetOfAmplicons(LocusAmpliconSet):
    allLengths = []
    allUknownBasePercentages = []

    # ITERATE AMPLICONS;
    for genome in LocusAmpliconSet.keys():
        # MEASURE AMPLICON LENGHTS
        length = len(LocusAmpliconSet[genome])
        allLengths.append(length)

        # MEASURE AMPLICON UKNOWN BASES;
        ns = [base for base in LocusAmpliconSet[genome] if base in ['N', 'n']]
        pct = len(ns) / length * 100
        allUknownBasePercentages.append(pct)

    std = np.std(allLengths) / np.mean(allLengths)

    lenDiff = (max(allLengths) - min(allLengths)) / np.mean(allLengths)

    # Compute Score;
    Score = 100
    Score -= lenDiff * 6
    Score -= sum(allUknownBasePercentages) * 12
    Score = max(0, Score)

    return Score
