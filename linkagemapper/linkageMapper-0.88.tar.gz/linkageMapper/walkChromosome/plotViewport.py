#!/bin/python

import matplotlib.pyplot as plt
import numpy as np
import os
import math

from . import matrixOperations, dissimilarityCluster, MatrixPlot


class LabelGroup():
    def __init__(self, baseNames):
        self.base = baseNames
        self.cropped = self.crop(self.base)

        # lowercase greek letters for niceness;
        self.clusterSymbolMap = [chr(945 + x) for x in range(20)]
        print(self.cropped)

    @staticmethod
    def crop(Labels, maxSize=13, Replacer="..."):
        croppedLabels = []
        maxSize -= len(Replacer)
        for label in Labels:
            if len(label) > maxSize:
                crop_size = len(label) - maxSize
                crop_size += crop_size % 2
                crop_size //= 2

                mid_point = len(label) // 2

                allowed_side_size = mid_point - crop_size

                cropped = label[:allowed_side_size]
                cropped += Replacer
                cropped += label[-allowed_side_size:]

            else:
                cropped = label

            croppedLabels.append(cropped)

        return croppedLabels

    def clusterize(self, clusterGroup):
        Cluster = [None for z in self.base]
        for n in clusterGroup.keys():
            if len(clusterGroup[n]) > 1:
                for member in clusterGroup[n]:
                    idx = None
                    for l, label in enumerate(self.base):
                        if label == member or label == member[:30]:
                            idx = l
                    if idx is not None:
                        Cluster[idx] = n

        return Cluster

    def get_labels(self, Cluster=[], symbolSide=0):
        Output = []

        symbolSideFormat = [
            "{symbol}{spacer}{label}",
            "{label}{spacer}{symbol}"
        ]

        for k, label in enumerate(self.cropped):
            if Cluster and Cluster[k] is not None:
                symbol = self.clusterSymbolMap[Cluster[k]]
            else:
                symbol = " "

            label_content = {
                'label': label,
                'spacer': " " * (15 - len(label)),
                'symbol': symbol
            }

            output_label = symbolSideFormat[symbolSide].format(**label_content)
            Output.append(output_label)

        return Output

    def get_ordered(self, reorderIndexes, **kwargs):
        r = np.array(self.get_labels(**kwargs))
        r = r[reorderIndexes]
        r = list(r)
        return r


def fixArrayFilename(f):
    return f.split('.')[0]


def reorderList(List, index_map):
    lst = np.array(List)[index_map]
    return list(lst)


def singleLocusStatus(alnData, axis, locus_name):

    # FETCH HEALTH SCORE FOR LOCUS;
    locus_identifier = locus_name.replace("LOCI_", "")
    Health = alnData.MatchData[alnData.MatchData.LocusName == locus_identifier]
    if not Health.empty:
        Health = Health.iloc[0]["AlignmentHealth"]

    # DECLARE DISPLAY COLORS;
    colorRanges = {
        "red": (0, 50),
        "orange": (50, 70),
        "green": (70, 100)
    }

    # SELECT DISPLAY COLORS;
    color = "black"
    for anycolor in colorRanges.keys():
        v = colorRanges[anycolor]
        if v[0] <= Health <= v[1]:
            color = anycolor

    # PRINT ADJACENT TEXT;
    axis.text(-0.2,
              0.6,
              s="Amplicon Health:",
              clip_on=False,
              fontsize=12)

    # PRINT COLORED HEALTH VALUE TEXT;
    axis.text(0.4,
              0.6,
              s="%.2f%%" % Health,
              clip_on=False,
              color=color,
              fontsize=15)

    # DISABLE AXIS XY RULERS;
    axis.axis("off")


def createMatrixSubplot(fig, position,
                        name, matrix,
                        xlabels, ylabels,
                        fontsize=9,
                        MatrixParameters=None):
    new_ax = fig.add_subplot(position)

    MatrixPlot.heatmapToAxis(
        matrix,
        new_ax,
        xlabels=xlabels,
        ylabels=ylabels,
        fontsize=fontsize,
        MatrixName=name,
        MatrixParameters=MatrixParameters
    )

    return new_ax


def sequenceInfoOnAxis(ax, reference=None, nb_snp=0, aln_len=0):
    Message = "nb_snp=%i\nlength=%i" % (nb_snp, aln_len)
    ax.annotate(
        Message,
        # xy=(-0.2, 1.2),
        xy=(0, 5),
        xycoords=reference,
        clip_on=False,
        ha='left',
        va='top'
        )


def colorizeSubplot(ax, Cluster):
    # color map from matplotlib;
    colorMap = plt.get_cmap("tab20")

    ClusterColors = [colorMap(x / 20)
                     for x in range(20)]

    allLabels = enumerate(zip(ax.get_xticklabels(), ax.get_yticklabels()))
    for idx, (xlabel, ylabel) in allLabels:
        cluster = Cluster[idx]
        if cluster is not None:
            xlabel.set_color(ClusterColors[cluster])
            ylabel.set_color(ClusterColors[cluster])


def loadClusterPairData(alnData, a_name, b_name, abmatrix, Labels):

    clusterOutputData = [None for n in range(2)]
    # ITERATE LOCUS NAMES ON VIEW (TWO) iteration to load clusterOutputData;
    for N, region_name in enumerate([a_name, b_name]):
        clusterOutputData[N] = loadClusterData(alnData,
                                               region_name,
                                               abmatrix[N], Labels)

    # REORGANIZE CLUSTER OUTPUT DATA;
    if all(clusterOutputData):
        clusterOutputData =\
            dissimilarityCluster.matchPairOfClusterOutputData(
                clusterOutputData)

    return clusterOutputData


def loadClusterData(alnData, region_name, matrix, Labels):

    # Assign obtained clusters;
    clusterFilePath = alnData.buildArrayPath(region_name) + ".clst"

    # MeShCluSt file exists.
    if os.path.isfile(clusterFilePath):
        locusClusterOutputData =\
            dissimilarityCluster.parseMeshcluster(clusterFilePath)

    # Otherwise...
    else:
        locusClusterOutputData =\
            dissimilarityCluster.fromDissimilarityMatrix(matrix, Labels.base)

    return locusClusterOutputData


def makePlotCode(a, b, c):
    return a * 100 + b * 10 + c


def plotRegionBatch(fig, alnData, regionIndexes,
                    showLabelColors=True, reorganizeIndex=None,
                    MatrixParameters=None):
    data = [
        alnData.MatchData["LocusName"].iloc[i]
        for i in regionIndexes
    ]

    alignmentData = [
        alnData.AlignmentData[
            alnData.AlignmentData["LocusName"] == name].iloc[0]
        for name in data
    ]

    Matrixes = [np.load(alnData.buildArrayPath(a)) for a in data]

    Labels = LabelGroup(alnData.heatmapLabels)
    Clusters = [
        loadClusterData(alnData, data[i], Matrixes[i], Labels)
        for i in range(len(data))
    ]

    # Reorganize matrix logic;
    if reorganizeIndex is not None:
        _, matrix_order, B =\
            matrixOperations.compute_serial_matrix(
                Matrixes[reorganizeIndex],
                method="complete"
            )

        Matrixes = [
            matrixOperations.reorderMatrix(mat, matrix_order)
            for mat in Matrixes
        ]

        Labels = LabelGroup(alnData.heatmapLabels[matrix_order])

    AllAxis = []

    # Compute number of rows and columns for plot figure;
    NBL = len(data)
    NBROWS = min(2, math.ceil(NBL / 2))
    NBCOLS = math.ceil(NBL / NBROWS)

    AllPlots = []
    print("Plot Count: %i\nColumns: %i\nRows: %i" % (NBL, NBCOLS, NBROWS))
    for m, Matrix in enumerate(Matrixes):
        print("Building...")
        PlotCode = makePlotCode(NBROWS, NBCOLS, m + 1)
        print(Clusters[m])
        plotCluster = Labels.clusterize(Clusters[m])
        plotLabels = Labels.get_labels(Cluster=plotCluster)

        fontsize = 12 - 2 * (NBL - 2)

        plot = createMatrixSubplot(
            fig, PlotCode,
            data[m], Matrix,
            plotLabels, plotLabels,
            fontsize=fontsize,
            MatrixParameters=MatrixParameters
        )

        AllPlots.append(plot)
        if showLabelColors:
            colorizeSubplot(plot, plotCluster)

        AllAxis.append(plot)

    for m, Matrix in enumerate(Matrixes):
        axLabels = AllPlots[m].get_yticklabels()
        axLabel = axLabels[0]

        sequenceInfoOnAxis(AllPlots[m],
                           reference=axLabel,
                           nb_snp=alignmentData[m]["SNPCount"],
                           aln_len=alignmentData[m]["AlignmentLength"])

    fig.tight_layout()
    fig.tight_layout()
    fig.tight_layout()
    return fig


def plotPwmIndex(fig, alnData, regionIndexes, showLabelColors=True):

    currentPWMData = alnData.findPWMDataRow(*regionIndexes)

    # walk loci by loci mode.

    # EXTRACR LOCUS NAMES;
    a = regionIndexes[0]
    b = regionIndexes[1]

    data = [alnData.MatchData["LocusName"].iloc[i] for i in regionIndexes]
    a_name, b_name = data
    names = data
    print(a_name)

    try:
        data = [
            alnData.PrimerData[
                alnData.PrimerData.Locus == name
            ].iloc[0]
            for name in names
        ]
    except IndexError:
        print("Failure on %s" % a_name)

    # LOAD MATRIX DATA;
    [ma, mb] = [
        np.load(alnData.buildArrayPath(name))
        for name in names
    ]

    # Crop label lengths;
    Labels = LabelGroup(alnData.heatmapLabels)

    ordered_ma, matrix_order, B =\
        matrixOperations.compute_serial_matrix(ma, method="complete")

    ordered_mb = matrixOperations.reorderMatrix(mb, matrix_order)

    # -- CLUSTER INFORMATION TO LABEL;
    abmatrix = [ma, mb]
    clusterOutputData = loadClusterPairData(alnData, a_name,
                                            b_name, abmatrix, Labels)

    LeftCluster = Labels.clusterize(clusterOutputData[0])
    RightCluster = Labels.clusterize(clusterOutputData[1])

    print(LeftCluster)
    print(Labels.base)
    print(clusterOutputData)

    # REORDERED MATRIXES;
    # plot;
    TA1_labels = Labels.get_ordered(matrix_order,
                                    Cluster=LeftCluster, symbolSide=0)
    top_axis1 = createMatrixSubplot(fig, 231,
                                    a_name, ordered_ma,
                                    TA1_labels, TA1_labels)

    TA2_xlabels = Labels.get_ordered(matrix_order,
                                     Cluster=RightCluster, symbolSide=0)
    TA2_ylabels = Labels.get_ordered(matrix_order,
                                     Cluster=RightCluster, symbolSide=1)
    top_axis2 = createMatrixSubplot(fig, 233,
                                    b_name, ordered_mb,
                                    TA2_xlabels, TA2_ylabels)

    # ORIGINAL MATRIXES;
    # plot;
    BA1_labels = Labels.get_labels(Cluster=LeftCluster)
    bottom_axis1 = createMatrixSubplot(fig, 234,
                                       a_name, ma,
                                       BA1_labels, BA1_labels)

    BA2_xlabels = Labels.get_labels(Cluster=RightCluster, symbolSide=0)
    BA2_ylabels = Labels.get_labels(Cluster=RightCluster, symbolSide=1)
    bottom_axis2 = createMatrixSubplot(fig, 236,
                                       b_name, mb,
                                       BA2_xlabels, BA2_ylabels)

    # left plots have yticks on the right side.
    top_axis1.yaxis.tick_right()
    bottom_axis1.yaxis.tick_right()

    # COLORIZE MATRIX LABELS BY MESHCLUSTER;
    if showLabelColors:
        colorizeSubplot(top_axis1, reorderList(LeftCluster, matrix_order))
        colorizeSubplot(bottom_axis1, LeftCluster)

        colorizeSubplot(top_axis2, reorderList(RightCluster, matrix_order))
        colorizeSubplot(bottom_axis2, RightCluster)

    # BUILD SHOWN INFO;
    if currentPWMData is not None:
        color_green = (0.1, 0.8, 0.1)
        color_red = (0.8, 0.1, 0.1)

        distance = abs(data[0].PositionStart - data[1].PositionStart)

        # INF_SYMBOL = chr(8734)
        Title = [
            "Distance = {:,} bp".format(distance),
            "%s vs %s" % (a_name, b_name),
            "Mantel=%.4f     p=%.4f" % (currentPWMData["mantel"],
                                        currentPWMData["mantel_p"]),
            "DIFF=%i" % currentPWMData["matrix_ranking_diff"],
            " "
        ]

        Title = "\n".join(Title)

        # ADDITIONAL INFORMATION FIGURE;
        ax_information = fig.add_subplot(235)

        ax_information.text(
            -0.2,
            0.6,
            s=Title,
            clip_on=False
        )

        ax_information.axis("off")

        # ALIGNMENT HEALTH INFORMATION FIGURE;
        if False and "AlignmentHealth" in alnData.MatchData.keys():
            ax_ha = fig.add_subplot(234)
            ax_hb = fig.add_subplot(236)

            singleLocusStatus(alnData, ax_ha, a_name)
            singleLocusStatus(alnData, ax_hb, b_name)

            # Additional info on secondary axis DEPRECATED;
            if False:
                RecombinationMessage = "True" \
                    if currentPWMData["recombination"] else "False"

                Message = "Recombination? %s" % RecombinationMessage
                ax_hb.text(0.8, 1, s=Message)

        # RECOMBINATION FIGURE;
        # PWM[RECOMBINATION] IS DEPRECATED.
        # if currentPWMData["recombination"]:
        try:
            Recombination = dissimilarityCluster.checkRecombination(
                clusterOutputData,
                Labels.get_ordered(matrix_order),
                Threshold=0.4)
        except Exception as e:
            print(clusterOutputData)
            Recombination = [False]
            print("WARNING: Recombination failure!")
            print(e)
            raise

        def plotRecombinationPanel(ax, baseIndex):
            x_values = np.linspace(0, 10, 100)

            pre = 0.7
            div = 2
            mul = 2.1

            plot_53 = [baseIndex + np.sin(pre + mul * x) / div
                       for x in x_values]

            plot_35 = [baseIndex - np.sin(pre + mul * x) / div
                       for x in x_values]

            ax.plot(x_values, plot_53, color=color_red)
            ax.plot(x_values, plot_35, color=color_green)

        if any(Recombination):
            a = []
            b = []
            for x in range(-50, 50, 1):
                y = x ** 2 + 2 * x + 2
                a.append(x)
                b.append(y)

            ax_recombination = fig.add_subplot(232)
            dm = list(range(len(Labels.base)))

            # Reverse recombination array,
            # because matrix plot indexes
            # and normal plot indexes are reversed.

            for r, rec in enumerate(reversed(Recombination)):
                if rec:
                    plotRecombinationPanel(ax_recombination, r)

            ax_recombination.scatter([0 for x in dm], dm, color=color_green)
            ax_recombination.scatter([10 for x in dm], dm, color=color_red)

            b = np.array(b)
            # d = 500
            # ax_symbol.plot(b - d, a, color='gray')
            # ax_symbol.plot(-b + d, a, color='brown')
            ax_recombination.axis("off")

    plt.title("")

    plt.subplots_adjust(top=0.79, bottom=0.03, left=0.06, right=1.00)
    fig.tight_layout()

    return fig
