#!/bin/python
import os
import pandas as pd
from optparse import OptionParser

import PrimerEngine

parser = OptionParser()
parser.add_option("-l", "--locus", dest="LocusName")
parser.add_option("-r", "--locusref", dest="LocusReference")
parser.add_option("-i", dest="inputFile")

options, args = parser.parse_args()

loci_data = pd.read_csv(options.inputFile)

FastaRows = 80

multifasta = ""

genotypeData = pd.read_csv("genomes_haplogroups.csv")
rflpGenotypes = pd.read_csv("genotypes.csv")

REF = options.LocusReference
ReferenceLocus = REF if REF else options.LocusName

loadedSequences = {}
# ITERATE GENOMES;
for i in range(loci_data.shape[0]):
    d = loci_data.iloc[i]
    sequence = d[options.LocusName]
    name = d["Genome"] + ".fasta"

    loadedSequences[d["Genome"]] = sequence
    try:
        GenotypeNumber = genotypeData[genotypeData.Genome == name].iloc[0].ToxoDB
        RFLPLocus = rflpGenotypes[rflpGenotypes.Genotype==GenotypeNumber].iloc[0][ReferenceLocus]
        name += "___%s" % RFLPLocus
        print("Loci data found for %s" % name)
    except Exception as e:
        pass

    multifasta += ">%s\n" % name
    multifasta += sequence
    multifasta += "\n"


# BUILD OUTPUT FILE NAME AND SAVE;
outputPath = os.path.dirname(options.inputFile)
outputFilePath = os.path.join(outputPath, "LOCI_%s.fasta" % options.LocusName)
open(outputFilePath, "w").write(multifasta)

# SIGNAL FOR UNUSABLE SEQUENCES!
if not PrimerEngine.PrimerDock.evaluateSetOfAmplicons(loadedSequences):
    exit(1)
