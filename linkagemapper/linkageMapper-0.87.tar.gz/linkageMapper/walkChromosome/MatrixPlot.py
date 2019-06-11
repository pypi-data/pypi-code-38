#!/bin/python

import numpy as np


def normalizeMatrix(MATRIX, parameters=None):

    """
    nMATRIX = np.copy(MATRIX)
    s = MATRIX.shape
    for i in range(s[0]):
        for j in range(s[1]):
            V = MATRIX[i, j]
            if V:
                nMATRIX[i, j] = np.log(V)
    return nMATRIX
    """

    if not parameters:
        parameters = {
            "pre_multiplier": 6,
            "normalizer": 2
        }

    MATRIX = MATRIX * parameters["pre_multiplier"]
    MODE = parameters["normalizer"]
    if MODE == 0:
        MATRIX = 1/(1+np.exp(-MATRIX))
    elif MODE == 1:
        MATRIX = np.tanh(MATRIX)
    elif MODE == 2:
        std = np.std(MATRIX)
        MATRIX = MATRIX * std
        MATRIX = np.tanh(MATRIX)

    return MATRIX


def heatmapToAxis(MATRIX, ax, xlabels=None,
                  ylabels=None, fontsize=9,
                  MatrixName=None, MatrixParameters=None):

    MATRIX = normalizeMatrix(MATRIX, MatrixParameters)
    ax.matshow(MATRIX, cmap='binary')

    SIZE = len(MATRIX)


    # MINOR TICKS -> GRID;
    DIV = SIZE // 3
    gridPoints = np.arange(0, SIZE, DIV)[1:-1] + 0.5

    ax.set_xticks(gridPoints, minor=True)
    ax.set_yticks(gridPoints, minor=True)

    # MAJOR TICKS -> LABELS;
    ax.set_xticks(range(SIZE))
    ax.set_yticks(range(SIZE))

    # SET LABELS;
    fontProperties = {
        'family': 'monospace',
        'fontsize': fontsize
    }
    if xlabels is not None:
        ax.set_xticklabels(xlabels, fontProperties, rotation=90)
    if ylabels is not None:
        ax.set_yticklabels(ylabels, fontProperties)

    if MatrixName:
        ax.set_xlabel(MatrixName, fontProperties)
