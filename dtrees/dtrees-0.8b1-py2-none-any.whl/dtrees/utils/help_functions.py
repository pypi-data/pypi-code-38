import random

def get_unique(labels):
    uniq = []
    for lbl in labels:
        if lbl not in uniq:
            uniq.append(lbl)
    return uniq


def groupSameElements(labels):
    uniqElements = get_unique(labels)
    if len(uniqElements)==1:
        return [[i for i in range(len(labels))]]
    else:
        grouped = []
        for lbl in uniqElements:
            grouped.append([i for i in range(len(labels)) if labels[i] == lbl])
        return grouped

def train_test_split(data, train=0.8, seed=0):
    N = data.shape[0]
    indexes = data.index.values
    random.Random(seed).shuffle(indexes)
    I = int(N*train)
    trainInd = indexes[0:I]
    testInd = indexes[I:]
    # return trainInd, testInd
    return data.iloc[trainInd], data.iloc[testInd]
