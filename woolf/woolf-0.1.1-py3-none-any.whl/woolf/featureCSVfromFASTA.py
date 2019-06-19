#!/usr/bin/env python3

# ############################### #
# featureCSVfromFASTA.py
#
# Creates a feature table with class identificiations from multiple fasta files.
#
# Anna Farrell-Sherman 3/31/19
# ############################### #

#import packages
from Bio import SeqIO #for fasta reading
from Bio.SeqUtils.ProtParam import ProteinAnalysis #for determining percentage composition
import pandas as pd #to create the CSV file
import argparse # to format command line arguments
import sys #for command line parsing
import os #for creating file names

### readfiles - opens files to read sequences
# filename: a file or path to a file containing sequence data in fasta format
# returns: an array of every sequence in the file
def readfasta(filename):
    seqs = list(SeqIO.parse(filename, "fasta"))
    return seqs


### binaryFeatureTable -
def binaryFeatureTable(PosSeqFiles, NegSeqFiles):
	seqDicts = []

	#add sequences from each file in positive group
	sequenceClass = 1
	for file in PosSeqFiles:
		records = readfasta(file)
		for rec in records:
			#aSeq = ProteinAnalysis(str(rec.seq))
			seqDict = ProteinAnalysis(str(rec.seq)).get_amino_acids_percent()
			seqDict['Class'] = sequenceClass
			seqDict['Length'] = len(rec.seq)
			seqDict['ID'] = rec.id
			seqDicts.append(seqDict)

	#add sequences from each file in negative group
	sequenceClass = 0
	for file in NegSeqFiles:
		records = readfasta(file)
		for rec in records:
			#aSeq = ProteinAnalysis(str(rec.seq))
			seqDict = ProteinAnalysis(str(rec.seq)).get_amino_acids_percent()
			seqDict['Class'] = sequenceClass
			seqDict['Length'] = len(rec.seq)
			seqDict['ID'] = rec.id
			seqDicts.append(seqDict)

	return pd.DataFrame(seqDicts)

### predictDataFeatureTable -
def predictDataFeatureTable(sequenceFiles):
	seqDicts = []

	#add each file with NO class identifier
	for file in sequenceFiles:
		records = readfasta(file)
		for rec in records:
			seqDict = ProteinAnalysis(str(rec.seq)).get_amino_acids_percent()
			seqDict['Length'] = len(rec.seq)
			seqDict['ID'] = rec.id
			seqDicts.append(seqDict)

	return pd.DataFrame(seqDicts)

### saveCSV - saves a datatable in a file with a given name
def saveCSV(dataTable, filename):
	return dataTable.to_csv(filename,index=None, header=True)