# !/bin/python

import os
import pandas as pd
import numpy as np
from optparse import OptionParser

from . import skdistance as skdist


def matrixRankings(MATRIX):
    orderMatrix = []
    for row in MATRIX:
        row = list(row)

        order = [row.index(v) for v in sorted(row)]
        orderMatrix.append(order)
    return orderMatrix


def compareMatrixRankings(mat0, mat1):
    mat0 = matrixRankings(mat0)
    mat1 = matrixRankings(mat1)

    diff = 0
    for i in range(len(mat0)):
        for j in range(len(mat0)):
            diff += abs(mat0[i][j] - mat1[i][j])

    return diff


def checkRecombination(ma, mb, Verbose=False):

    def isZero(v):
        if v < 0.05:
            return True
        else:
            return False

    RecombinationDetected = False
    for i, row in enumerate(ma):
        Pre1 = False
        Pre2 = False

        for j, v in enumerate(row):
            if isZero(ma[i, j]) and not isZero(mb[i, j]):
                if Verbose:
                    print("Pre1 at %i %i" % (i, j))
                    print(ma[i, j])
                    print(mb[i, j])
                    print()
                if Pre2:
                    RecombinationDetected = True
                    # return True
                Pre1 = True

            if not isZero(ma[i, j]) and isZero(mb[i, j]):
                if Verbose:
                    print("Pre2 at %i %i" % (i, j))
                    print(ma[i, j])
                    print(mb[i, j])
                    print()
                if Pre1:
                    RecombinationDetected = True
                    # return True
                Pre2 = True

    return RecombinationDetected


def Execute(options):
    # CHECK INPUT ARGUMENTS;
    if not options.InputDirectory:
        print("FATAL: No input directory.")
        exit(1)

    # LOAD RESULT FILES;
    matchedLociData = pd.read_csv(os.path.join(options.InputDirectory,
                                               "MatchedRegions.csv"))
    matchedLoci = matchedLociData["LocusName"]

    arrayFiles = ["LOCI_%s.aln.npy" % Locus for Locus in matchedLoci]

    arrayFilePaths = [os.path.join(options.InputDirectory, File)
                      for File in arrayFiles]

    # LOAD HEATMAPS FOR LOCI THAT SUCCEEDED THE ALIGNMENT (SO .aln.npy FILE EXISTS);
    heatmaps = [
        np.load(filePath)
        for filePath in arrayFilePaths
        if os.path.isfile(filePath)
    ]

    heatmapLabels = np.load(os.path.join(options.InputDirectory,
                                         "heatmap_labels.npy"))

    Distances = [skdist.DistanceMatrix(h, heatmapLabels) for h in heatmaps]

    grouping = []
    for l in heatmapLabels:
        g = len(l.split("_")[-1])
        grouping.append(g)

    allResults = []
    for d, D in enumerate(Distances):
        print(arrayFilePaths[d])
        try:
            res = skdist.anosim(D, grouping=grouping)
        # IF ANOSIM FAILS:
        except ValueError:
            print()
            print("Anosim failed:")
            print("Distances are binary, add more genomes and/or regions to the pool.")
            print("Check results at %s" % options.inputDirectory)
            return False

        print(res)
        res["Locus"] = arrayFiles[d]
        allResults.append(res)
        print("\n")

    # LOAD OR BUILD NEW PWM ANALYSIS DATA FRAME;
    pwmPath = os.path.join(options.InputDirectory, "PWMAnalysis.csv")

    PWM = None
    if options.updateOnly:
        if os.path.isfile(pwmPath):
            PWM = pd.read_csv(pwmPath)
            PWM_Index_Labels = [(PWM.iloc[x]["Unnamed: 0"], PWM.iloc[x]["Unnamed: 1"])
                                for x in range(PWM.shape[0])]
            PWM_Index_Indices = [(arrayFiles.index(x[0]), arrayFiles.index(x[1]))
                                 for x in PWM_Index_Labels]

            PWM.index = pd.MultiIndex.from_tuples(PWM_Index_Labels)
            print("PWM File loaded.")
        else:
            print("No PWM file found at %s" % pwmPath)

    if PWM is None:
        print("Executing PWMantel analysis...")
        PWM = skdist.pwmantel(Distances, permutations=0)

        PWM_Index_Indices = [(x[0], x[1]) for x in PWM.index]
        PWM_Index_Labels = [(arrayFiles[x[0]], arrayFiles[x[1]]) for x in PWM.index]
        PWM.index = pd.MultiIndex.from_tuples(PWM_Index_Labels)

    # INITIALIZE RESULT LISTS;
    Associations = []
    Mantels = []
    MantelsP = []
    RankingDiff = []
    Recombinations = []




    # ITERATE pwm_indices;
    for IFA, IFB in PWM_Index_Indices:

        # FIRST EVALUATION;
        D = np.cov(heatmaps[IFA], heatmaps[IFB])
        D = sum(sum(D))
        Associations.append(D)

        # SECOND EVALUATION;
        M = skdist.mantel(heatmaps[IFA], heatmaps[IFB])

        Mantels.append(M[0])
        MantelsP.append(M[1])

        # THIRD EVALUATION;
        MDF = compareMatrixRankings(heatmaps[IFA], heatmaps[IFB])
        RankingDiff.append(MDF)

        # FOURTH EVALUATION;
        REC = checkRecombination(heatmaps[IFA], heatmaps[IFB])
        Recombinations.append(REC)

    PWM["associations"] = Associations

    PWM["mantel"] = Mantels
    PWM["mantel_p"] = MantelsP
    PWM["matrix_ranking_diff"] = RankingDiff
    PWM["recombination"] = Recombinations

    # cleanup dataframe;
    try:
        del PWM["permutations"]
    except Exception:
        pass

    print(PWM.to_string())

    for IFA, IFB in PWM_Index_Indices:
        pass

    print("Writing output files...")
    # WRITE OUTPUT PWM FILE;
    PWM.to_csv(pwmPath)

    outputData = pd.DataFrame(allResults,
                              columns=["Locus"] + list(allResults[0].keys())[:-1])

    outputPath = os.path.join(options.InputDirectory, "HeatmapAnalysis.csv")
    outputData.to_csv(outputPath, index=False)

    print("Wrote %s analysis file." % outputPath)

    return True


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", dest="InputDirectory")
    parser.add_option("--update", dest='updateOnly', action='store_true')

    options, args = parser.parse_args()
    Execute(options)
