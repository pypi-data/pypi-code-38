#!/bin/python


import numpy as np
import matrixAnalysis

# ma = np.load("analysisResults/aCHR_VIIa/LOCI_TGME49_280480.aln.npy")
# mb = np.load("analysisResults/aCHR_VIIa/LOCI_TGME49_206570.aln.npy")

fma = np.load("analysisResults/aCHR_VIIa/LOCI_TGME49_205490.aln.npy")
fmb = np.load("analysisResults/aCHR_VIIa/LOCI_ROP12.aln.npy")

# tma = np.load("analysisResults/aCHR_VIIa/LOCI_TGME49_201390.aln.npy")
# tmb = np.load("analysisResults/aCHR_VIIa/LOCI_TGME49_206670.aln.npy")

tma = np.load("analysisResults/aCHR_XII/LOCI_RPP0.aln.npy")
tmb = np.load("analysisResults/aCHR_XII/LOCI_TGME49_218340.aln.npy")

print("False control:")
res = matrixAnalysis.checkRecombination(fma, fmb, Verbose=True)
print(res)

print("\n\n\n")

print("True control:")
res = matrixAnalysis.checkRecombination(tma, tmb, Verbose=True)
print(res)
