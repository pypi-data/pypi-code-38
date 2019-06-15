#!/bin/python

from optparse import OptionParser

import os
import pandas as pd

from Bio import SeqIO

import PrimerEngine


def dataDir(filename):
    return os.path.join(options.inputDirectory, filename)


parser = OptionParser()

parser.add_option("-d",
                  dest="inputDirectory")

options, args = parser.parse_args()

DataFilePath = os.path.join(options.inputDirectory, "MatchedRegions.csv")
LocusData = pd.read_csv(DataFilePath)

Scores = []
for locus in LocusData.LocusName:
    fastaFileName = "LOCI_%s.fasta" % locus
    fastaFilePath = dataDir(fastaFileName)
    sequences = list(SeqIO.parse(fastaFilePath, 'fasta'))
    sequences = {s.id: str(s.seq) for s in sequences}
    score = PrimerEngine.ampliconSanity.evaluateSetOfAmplicons(sequences)
    Scores.append(score)


LocusData["AlignmentHealth"] = Scores
LocusData.to_csv(dataDir("MatchedRegions.csv"), index=False)

print()
print("Amplicon scores updated for %s" % DataFilePath)
