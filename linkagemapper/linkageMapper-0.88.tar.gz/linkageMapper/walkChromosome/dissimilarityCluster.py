#!/bin/python

import json
import re
from sklearn.cluster import dbscan


# First way of obtaining cluster data: From MeShCluSt .clst file.
def parseMeshcluster(clusterFilePath):
    clusterData = open(clusterFilePath).read().split("\n")
    clusterOutputData = {}
    for line in clusterData:
        if ">Cluster" in line:
            key = int(re.findall(">Cluster (\d+)", line)[0])
        if "nt," in line:
            if key not in clusterOutputData.keys():
                clusterOutputData[key] = []
            _line = line.replace("...", "")
            Individual = re.findall(">([^\s]+)", _line)[0]
            clusterOutputData[key].append(Individual)
    # print(clusterOutputData)
    return clusterOutputData


# Second way of obtaining cluster data: From Dissimilarity Matrix.
def fromDissimilarityMatrix(Matrix, matrixLabels):
    r = dbscan(Matrix, metric='precomputed', min_samples=1, eps=0.0001)
    clusters = {}
    sortedClusters = sorted(list(set(r[1])))

    # first loop to pick clustered members;
    for cluster in sortedClusters:
        if cluster < 0:
            continue
        Members = []
        for i, v in enumerate(r[1]):
            if v == cluster:
                Members.append(matrixLabels[i])

        clusters[cluster] = Members

    # now we pick the unindentified members;
    for c, cluster in enumerate(r[1]):
        if cluster == -1:
            clusters[len(list(clusters.keys()))] = [matrixLabels[c]]

    return clusters


# well... this function can be..... simplified.
def matchPairOfClusterOutputData(clusterOutputData, Verbose=False):
    masterData = clusterOutputData[0]
    slaveData = clusterOutputData[1]

    if Verbose:
        print("Reordering Cluster Groups...")
        print()
        print("Original:")
        print(json.dumps(clusterOutputData, indent=2))
        print()

    # STEP ZERO: REORDER BY GROUP SIZE;
    def byGroupSize(Data):
        _Data = [(k, v) for k, v in Data.items()]
        _Data = sorted(_Data, key=lambda x: len(x[1]), reverse=True)
        _Data = [(idx, value[1]) for idx, value in enumerate(_Data)]
        _Data = dict(_Data)

        return _Data

    masterData = byGroupSize(masterData)
    slaveData = byGroupSize(slaveData)

    # 1st STEP: COMPUTE SCORES;
    def computeScores(masterData, slaveData, Verbose=False):
        keyScores = [[0 for y in slaveData if len(slaveData[y]) > 1]
                     for x in masterData if len(masterData[x]) > 1]
        for mkey in range(len(keyScores)):
            for skey in range(len(keyScores[mkey])):
                score = 0
                for ind in masterData[mkey]:
                    if ind in slaveData[skey]:
                        score += 1
                #score = score / len(masterData[mkey])
                keyScores[mkey][skey] = score

        return keyScores

    keyScores = computeScores(masterData, slaveData)

    # DEBUG: VIEW SCORES;
    # clusterOutputData = [masterData, slaveData]
    # print(json.dumps(clusterOutputData, indent=2))
    if Verbose:
        for i in keyScores:
            for j in i:
                print("%i " % j, end="")
            print()

    if Verbose:
        print(keyScores)

    # 2nd STEP: SWAP POSITIONS @ SLAVE;
    TargetReplacementCount = (1, 4)
    ReplacementCount = 0
    Replaced = []
    for k in range(TargetReplacementCount[1]):
        for mkey in range(len(keyScores)):
            if mkey in Replaced:
                continue

            MAX = max(keyScores[mkey])
            MIN = min(keyScores[mkey])
            if len(keyScores[mkey]) >= len(keyScores):
                if keyScores[mkey][mkey] == max(keyScores[mkey]):
                    if Verbose:
                        print("GOOD!")
                    continue
            for skey in range(len(keyScores[mkey])):
                if keyScores[mkey][skey] == MAX:
                    try:
                        poorIndex = mkey
                        goodIndex = skey

                        good = slaveData[goodIndex]
                        poor = slaveData[poorIndex]

                        slaveData[poorIndex] = good
                        slaveData[goodIndex] = poor

                        keyScores = computeScores(masterData, slaveData)
                        if Verbose:
                            print("Replaced! %i %i" % (mkey, skey))
                    except KeyError as e:
                        if Verbose:
                            print(e)

                    ReplacementCount += 1
                    Replaced.append(mkey)
        ReplacementCount += 1
        if ReplacementCount >= TargetReplacementCount[0]:
            break

    # 3rd STEP: CREATE NEW GROUPS @ SLAVE TO NOT REPEAT GROUPS FROM MASTER;
    # IF THEY DON'T SHARE A SINGLE GENOME;

    def doShareCommon(masterDataEntry, slaveDataEntry, Verbose=False):
        shareCommon = False
        for Individue in masterDataEntry:
            if Individue in slaveDataEntry:
                shareCommon = True
                break
        return shareCommon

    masterDataLength = len(list(masterData.keys()))
    slaveDataLength = len(list(slaveData.keys()))
    for k in range(min(masterDataLength, slaveDataLength)):
        if not len(masterData[k]) > 1 or k not in masterData.keys():
            continue
        if not len(slaveData[k]) > 1 or k not in slaveData.keys():
            continue

        shareCommon = doShareCommon(masterData[k], slaveData[k], Verbose=Verbose)

        # IF NO GENOME IS SHARED, THIS STEP WILL END WITH THE DELETION OF K KEY FROM SLAVE DATA;
        # AND SLAVE DATA [K] WILL BE REASSIGNED TO RIGHT BEFORE THE LONE INDIVIDUES ARE, OR TO THE LAST POSITION;
        if not shareCommon:
            # Reassign possible existing group key to new:
            reassignedKey = None
            lastResourceKey = max(list(slaveData.keys())) + 1
            for skey in range(lastResourceKey):
                if skey in slaveData.keys():
                    if len(slaveData[skey]) == 1:
                        reassignedKey = skey
                        slaveData[lastResourceKey] = slaveData[reassignedKey]
                        slaveData[reassignedKey] = slaveData[k]
                        break
                elif skey in masterData.keys():
                    if doShareCommon(masterData[skey], slaveData[k], Verbose=Verbose):
                        reassignedKey = skey
                        slaveData[skey] = slaveData[k]
                        break

            if reassignedKey is None:
                slaveData[lastResourceKey] = slaveData[k]

            if k in slaveData.keys():
                del slaveData[k]

    # clusterOutputData = [masterData, slaveData]
    # print(json.dumps(clusterOutputData, indent=2))

    #keyScores = computeScores(masterData, slaveData)
    # DEBUG: VIEW SCORES;
    clusterOutputData = [masterData, slaveData]
    if Verbose:
        print(json.dumps(clusterOutputData, indent=2))
        print()
        for i in keyScores:
            for j in i:
                print("%i " % j, end="")
            print()

        print(keyScores)

    return clusterOutputData


"""
checkRecombination

This checks for recombination, by checking the members of a pair of cluster groups.
algorithm: Otsuka-Ochiai coefficient on those clusters;
clusterPair <list>: Two sets of clusters.
"""


def checkRecombination(clusterPair, locusNames, Threshold=0.1):
    recombination = []
    for locusName in locusNames:
        clusterKeys = [None, None]
        clusterSizes = [None, None]

        for cidx, clusterSet in enumerate(clusterPair):
            for cluster in clusterSet.keys():
                if locusName in clusterSet[cluster]:
                    clusterSizes[cidx] = len(clusterSet[cluster])
                    clusterKeys[cidx] = cluster
                    break

        if None in clusterKeys:
            K = 1
        else:
            A = clusterPair[0][clusterKeys[0]]
            B = clusterPair[1][clusterKeys[1]]

            if any([len(X) == 1 for X in [A, B]]):
                K = 1
            else:
                intersect = [x for x in A if x in B]
                K = len(intersect) / (len(A) + len(B)) ** 0.5

        print("%s -> %.2f" % (locusName, K))

        recomb = True if K < Threshold else False
        recombination.append(recomb)

    assert(len(recombination) == len(locusNames))

    return recombination
